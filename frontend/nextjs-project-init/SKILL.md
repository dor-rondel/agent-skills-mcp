---
name: nextjs-project-init
description: Use this skill when initializing a brand new Next.js web application from scratch. Covers pnpm setup, boilerplate structure configuration, quality tool validation, and writing the wildcard PR validation GitHub Actions workflow.
---

# Next.js Project Initialization & CI Setup

This skill provides an automated scaffolding script to initialize a Next.js web application using your preferred local ecosystem (`pnpm`, TypeScript, Tailwind CSS) alongside a rigorous PR validation GitHub Action pipeline.

## 🏃‍♂️ Step-by-Step Initialization Workflow

### 1. Scaffold Next.js Boilerplate

Run the native initializer utilizing `pnpm`. Configure the project prompt choices with TypeScript, ESLint, Tailwind CSS, `src/` directory, and App Router as needed:

```bash
pnpm create next-app@latest my-web-app
cd my-web-app
```

### 2. Configure Quality Automation Scripts

Ensure your local `package.json` contains matching scripts for your validation pipeline (Lint, Typecheck, Unit Tests, and Prettier checks):

```bash
pnpm add --save-dev prettier eslint-config-prettier
```

- Ensure the following block exists or is updated inside your `package.json` scripts block:
  ```json
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "typecheck": "tsc --noEmit",
    "test:unit": "vitest run",
    "format:check": "prettier --check ."
  }
  ```

### 3. Establish GitHub Actions PR Validation Workflow

Create the workflow directory structure and inject the wildcard branch validation workflow. This pipeline ensures every inbound PR passes formatting, typing, testing, and production compilation limits before landing:

```bash
mkdir -p .github/workflows
```

then in .github/workflows/ci.yml add the following YAML:

```
name: Assert New PR Is Valid Action

    on:
      pull_request:
        branches:
          - '*'

    jobs:
      validate:
        name: Validate Project
        runs-on: ubuntu-latest

        steps:
          - name: Checkout repository
            uses: actions/checkout@v6

          - name: Setup pnpm
            uses: pnpm/action-setup@v4
            with:
              version: 10

          - name: Setup Node.js
            uses: actions/setup-node@v4
            with:
              node-version: '20.x'
              cache: 'pnpm'

          - name: Install dependencies
            run: pnpm install --frozen-lockfile

          - name: Lint
            run: pnpm lint

          - name: Typecheck
            run: pnpm typecheck

          - name: Unit tests
            run: pnpm test:unit

          - name: Prettier check
            run: pnpm format:check

          - name: Build
            run: pnpm build
```

---

## 🛠️ Baseline Verification Run

Before pushing the new initialization branch upstream, run your entire local quality pipeline sequence using the frozen lockfile context to confirm full compliance:

```bash
pnpm install
pnpm format:check && pnpm lint && pnpm typecheck && pnpm build
```
