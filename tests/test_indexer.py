"""Tests for the ChromaDB indexer module."""

import pytest
import chromadb

from agent_skills_server.indexer import (
    _build_document,
    _index_skills,
    get_or_create_collection,
    search_skills_in_collection,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _DummyEmbeddingFn:
    """Deterministic 16-dim embedding function for testing.

    Converts each character to a float value so embeddings are reproducible
    and require no model download.  Not semantically meaningful, but sufficient
    to exercise all ChromaDB code paths.

    ChromaDB >= 1.5 requires:
    - ``name()``        — for conflict validation on ``get_or_create_collection``.
    - ``embed_query()`` — dispatched separately at query time.
    - ``is_legacy``     — attribute flag to suppress a ``DeprecationWarning``.
    """

    DIM = 16
    is_legacy = False

    def name(self) -> str:
        """Return the canonical name used by ChromaDB for conflict validation.

        Returns:
            A fixed string identifier for this embedding function.
        """
        return "dummy-embedding-fn"

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Shared embedding logic used by both __call__ and embed_query.

        Args:
            texts: List of input strings to embed.

        Returns:
            A list of 16-dimensional float vectors.
        """
        result = []
        for text in texts:
            vec = [0.0] * self.DIM
            for i, ch in enumerate(text[: self.DIM]):
                vec[i] = ord(ch) / 128.0
            result.append(vec)
        return result

    def __call__(self, input: list[str]) -> list[list[float]]:  # noqa: A002
        """Embed a batch of documents (called at index/upsert time).

        Args:
            input: List of text strings to embed.

        Returns:
            A list of 16-dimensional float vectors.
        """
        return self._embed(input)

    def embed_query(self, input: list[str]) -> list[list[float]]:  # noqa: A002
        """Embed a query string (called at query time by ChromaDB >= 1.5).

        Args:
            input: List of query strings to embed.

        Returns:
            A list of 16-dimensional float vectors.
        """
        return self._embed(input)


def _make_skill(
    category: str, skill_name: str, name: str, description: str
) -> dict[str, str]:
    """Return a minimal skill metadata dict for test fixtures.

    Args:
        category: Skill category string (e.g. ``solidity``).
        skill_name: Directory identifier for the skill.
        name: Human-readable skill name.
        description: Short description text.

    Returns:
        A dictionary matching the shape produced by ``discover_skills``.
    """
    return {
        "category": category,
        "skill_name": skill_name,
        "name": name,
        "description": description,
        "path": f"resources/{category}/{skill_name}/SKILL.md",
    }


@pytest.fixture()
def skill_fixtures(
    tmp_path: pytest.TempPathFactory,
) -> tuple[list[dict[str, str]], str]:
    """Create temporary SKILL.md files and return (skills, resources_dir).

    Writes three minimal skill files under ``tmp_path/resources/`` so that
    ``_index_skills`` can read them without touching the real repository.

    Args:
        tmp_path: Pytest built-in fixture providing a temporary directory.

    Returns:
        A tuple of (skills list, resources directory path string).
    """
    skills = [
        _make_skill(
            "solidity",
            "foundry-project-init",
            "foundry-project-init",
            "Initialize an EVM project with Foundry",
        ),
        _make_skill(
            "langgraph",
            "langgraph-project-init",
            "langgraph-project-init",
            "Initialize a LangGraph Python agent project",
        ),
        _make_skill(
            "docker",
            "docker-lifecycle",
            "docker-lifecycle",
            "Manage Docker container lifecycle",
        ),
    ]

    res_dir = tmp_path / "resources"
    for skill in skills:
        skill_dir = res_dir / skill["category"] / skill["skill_name"]
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill['name']}\ndescription: {skill['description']}\n---\n"
            f"# {skill['name']}\nThis skill helps you with {skill['description'].lower()}.",
            encoding="utf-8",
        )

    return skills, str(res_dir)


_collection_counter = 0


@pytest.fixture()
def populated_collection(
    skill_fixtures: tuple[list[dict[str, str]], str],
) -> chromadb.Collection:
    """Return an ephemeral ChromaDB collection pre-populated with test skills.

    Uses the dummy embedding function so no model download is required.
    A unique collection name is generated per test invocation to avoid
    ChromaDB ``InternalError: Collection already exists`` conflicts.

    Args:
        skill_fixtures: The (skills, resources_dir) tuple from the fixture.

    Returns:
        A ChromaDB ``Collection`` with three indexed test skills.
    """
    global _collection_counter  # pylint: disable=global-statement
    _collection_counter += 1
    skills, res_dir = skill_fixtures
    client = chromadb.EphemeralClient()
    dummy_ef = _DummyEmbeddingFn()
    collection = client.create_collection(
        name=f"test_skills_{_collection_counter}",
        embedding_function=dummy_ef,  # type: ignore[arg-type]
        metadata={"hnsw:space": "cosine"},
    )
    _index_skills(collection, skills, res_dir)
    return collection


# ---------------------------------------------------------------------------
# _build_document
# ---------------------------------------------------------------------------


def test_build_document_includes_metadata(tmp_path: pytest.TempPathFactory) -> None:
    """_build_document should include the skill name, category, and description."""
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("# Body content\nSome details.", encoding="utf-8")
    skill = _make_skill(
        "solidity",
        "foundry-project-init",
        "foundry-project-init",
        "Deploy EVM contracts",
    )
    doc = _build_document(skill, skill_file)  # type: ignore[arg-type]

    assert "Skill: foundry-project-init" in doc
    assert "Category: solidity" in doc
    assert "Deploy EVM contracts" in doc
    assert "Body content" in doc


def test_build_document_handles_missing_file(tmp_path: pytest.TempPathFactory) -> None:
    """_build_document should return a document even when the file is missing."""
    missing = tmp_path / "SKILL.md"
    skill = _make_skill(
        "docker", "docker-lifecycle", "docker-lifecycle", "Manage containers"
    )
    doc = _build_document(skill, missing)  # type: ignore[arg-type]

    # Metadata header is still present even without file content
    assert "Skill: docker-lifecycle" in doc
    assert "Category: docker" in doc


# ---------------------------------------------------------------------------
# _index_skills
# ---------------------------------------------------------------------------


def test_index_skills_populates_collection(
    populated_collection: chromadb.Collection,
) -> None:
    """After indexing, the collection count should equal the skill count."""
    assert populated_collection.count() == 3


def test_index_skills_empty_list(tmp_path: pytest.TempPathFactory) -> None:
    """_index_skills with an empty list should leave the collection unchanged."""
    client = chromadb.EphemeralClient()
    dummy_ef = _DummyEmbeddingFn()
    collection = client.create_collection(
        name="empty_test",
        embedding_function=dummy_ef,  # type: ignore[arg-type]
    )
    _index_skills(collection, [], str(tmp_path))
    assert collection.count() == 0


# ---------------------------------------------------------------------------
# search_skills_in_collection
# ---------------------------------------------------------------------------


def test_search_returns_results(populated_collection: chromadb.Collection) -> None:
    """search_skills_in_collection should return the requested number of results."""
    results = search_skills_in_collection(
        populated_collection, "smart contracts", n_results=2
    )
    assert len(results) == 2


def test_search_result_keys(populated_collection: chromadb.Collection) -> None:
    """Each search result should contain the required metadata keys."""
    results = search_skills_in_collection(
        populated_collection, "docker container", n_results=1
    )
    assert len(results) == 1
    result = results[0]
    assert "name" in result
    assert "category" in result
    assert "skill_name" in result
    assert "description" in result
    assert "distance" in result


def test_search_n_results_capped_at_collection_size(
    populated_collection: chromadb.Collection,
) -> None:
    """Requesting more results than indexed documents should not raise an error."""
    results = search_skills_in_collection(
        populated_collection, "anything", n_results=100
    )
    assert len(results) == 3  # Only 3 skills indexed


# ---------------------------------------------------------------------------
# get_or_create_collection
# ---------------------------------------------------------------------------


def test_get_or_create_collection_indexes_skills(
    skill_fixtures: tuple[list[dict[str, str]], str],
    tmp_path: pytest.TempPathFactory,
) -> None:
    """get_or_create_collection should build the index on first call."""
    _, res_dir = skill_fixtures
    chroma_dir = str(tmp_path / "chroma")
    dummy_ef = _DummyEmbeddingFn()

    collection = get_or_create_collection(
        chroma_path=chroma_dir,
        resources_dir=res_dir,
        embedding_fn=dummy_ef,
    )
    assert collection.count() == 3


def test_get_or_create_collection_reuses_index(
    skill_fixtures: tuple[list[dict[str, str]], str],
    tmp_path: pytest.TempPathFactory,
) -> None:
    """get_or_create_collection should reuse an up-to-date index without re-indexing."""
    _, res_dir = skill_fixtures
    chroma_dir = str(tmp_path / "chroma")
    dummy_ef = _DummyEmbeddingFn()

    # First call builds the index
    get_or_create_collection(
        chroma_path=chroma_dir, resources_dir=res_dir, embedding_fn=dummy_ef
    )

    # Second call should reuse it (no error, same count)
    collection2 = get_or_create_collection(
        chroma_path=chroma_dir, resources_dir=res_dir, embedding_fn=dummy_ef
    )
    assert collection2.count() == 3
