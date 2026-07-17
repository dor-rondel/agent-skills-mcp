"""ChromaDB indexer for agent skills semantic search.

Manages a persistent ChromaDB vector store used to support natural-language
similarity search over the agent skill library. Skills are embedded using the
``all-MiniLM-L6-v2`` sentence-transformer model, which runs entirely locally
and requires no API keys.

The collection is built lazily on first use and automatically re-indexed
whenever the number of discovered skills differs from the stored count.
"""

import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from agent_skills_server.skills import discover_skills, get_resources_dir

logger = logging.getLogger(__name__)

COLLECTION_NAME = "agent_skills"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_chroma_db_path() -> Path:
    """Return the absolute path to the persistent ChromaDB storage directory.

    Returns:
        The resolved absolute path to the ``.chroma/`` directory at the
        repository root.
    """
    return Path(__file__).resolve().parent.parent.parent / ".chroma"


def _build_document(skill: dict[str, str], skill_file: Path) -> str:
    """Build a rich text document for embedding from a skill's metadata and content.

    Prepends the skill's name, category, and description as prose so they
    contribute meaningfully to the semantic embedding alongside the full
    SKILL.md body text.

    Args:
        skill: Skill metadata dictionary from ``discover_skills``.
        skill_file: Path to the corresponding SKILL.md file.

    Returns:
        A single string combining the metadata header and file content.
    """
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        logger.warning("Could not read skill file: %s", skill_file)
        content = ""

    return (
        f"Skill: {skill['name']}\n"
        f"Category: {skill['category']}\n"
        f"Description: {skill['description']}\n\n"
        f"{content}"
    )


def _index_skills(
    collection: chromadb.Collection,
    skills: list[dict[str, str]],
    resources_dir: str,
) -> None:
    """Upsert all discovered skill documents into a ChromaDB collection.

    Each document is identified by the canonical ``{category}/{skill_name}``
    string and includes the full SKILL.md content alongside frontmatter
    metadata for post-query filtering.

    Args:
        collection: The ChromaDB collection to upsert documents into.
        skills: Skill metadata list returned by ``discover_skills``.
        resources_dir: Root path of the resources directory used to resolve
            each SKILL.md file.
    """
    if not skills:
        logger.warning("No skills found to index.")
        return

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict[str, str]] = []

    res_path = Path(resources_dir)
    for skill in skills:
        skill_file = res_path / skill["category"] / skill["skill_name"] / "SKILL.md"
        doc_id = f"{skill['category']}/{skill['skill_name']}"
        ids.append(doc_id)
        documents.append(_build_document(skill, skill_file))
        metadatas.append(
            {
                "name": skill["name"],
                "category": skill["category"],
                "skill_name": skill["skill_name"],
                "description": skill["description"],
            }
        )

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)  # type: ignore[arg-type]
    logger.info("Indexed %d skills into ChromaDB collection.", len(ids))


def get_or_create_collection(
    chroma_path: str | None = None,
    resources_dir: str | None = None,
    embedding_fn: Any = None,
) -> chromadb.Collection:
    """Get or create a persistent ChromaDB collection indexed with all skills.

    On first call this function builds the vector index from all discovered
    ``SKILL.md`` files. On subsequent calls the existing collection is reused
    unless the skill count has changed, in which case the collection is fully
    re-indexed via upsert.

    Args:
        chroma_path: Override path for the ChromaDB storage directory.
            Defaults to ``.chroma/`` at the repository root.
        resources_dir: Override path for the resources directory.
            Defaults to ``resources/`` at the repository root.
        embedding_fn: Override the embedding function. Useful for injecting a
            lightweight mock in tests. Defaults to
            ``SentenceTransformerEmbeddingFunction(all-MiniLM-L6-v2, cpu)``.

    Returns:
        A ChromaDB ``Collection`` ready for querying.
    """
    db_path = chroma_path or str(get_chroma_db_path())
    res_dir = resources_dir or str(get_resources_dir())
    skills = discover_skills(res_dir)

    client = chromadb.PersistentClient(path=db_path)

    if embedding_fn is None:
        embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            device="cpu",
        )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,  # type: ignore[arg-type]
        metadata={"hnsw:space": "cosine"},
    )

    existing_count = collection.count()
    if existing_count != len(skills):
        logger.info(
            "Re-indexing: %d skills discovered, %d in index.",
            len(skills),
            existing_count,
        )
        _index_skills(collection, skills, res_dir)
    else:
        logger.debug("Index is up to date with %d skills.", existing_count)

    return collection


def search_skills_in_collection(
    collection: chromadb.Collection,
    query: str,
    n_results: int = 3,
) -> list[dict[str, str]]:
    """Query the ChromaDB collection for skills semantically matching a query.

    Args:
        collection: The ChromaDB collection to query.
        query: A natural-language description of the desired skill.
        n_results: Maximum number of ranked results to return. Capped at the
            total number of indexed documents.

    Returns:
        A ranked list of result dictionaries sorted by relevance. Each entry
        contains:

            - ``name``: Human-readable skill name.
            - ``category``: Skill category (e.g., ``solidity``, ``langgraph``).
            - ``skill_name``: Skill directory identifier.
            - ``description``: Short description of the skill.
            - ``distance``: Cosine distance score (lower = more similar).
    """
    capped = min(n_results, max(collection.count(), 1))
    results = collection.query(
        query_texts=[query],
        n_results=capped,
        include=["metadatas", "distances"],
    )

    output: list[dict[str, str]] = []
    raw_metas = results.get("metadatas") or [[]]
    raw_dists = results.get("distances") or [[]]

    for meta, dist in zip(raw_metas[0], raw_dists[0]):
        if meta is not None:
            output.append(
                {
                    "name": str(meta.get("name", "")),
                    "category": str(meta.get("category", "")),
                    "skill_name": str(meta.get("skill_name", "")),
                    "description": str(meta.get("description", "")),
                    "distance": str(round(float(dist), 4)),
                }
            )
    return output
