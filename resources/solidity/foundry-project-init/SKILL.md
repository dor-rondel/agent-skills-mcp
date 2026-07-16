---
name: foundry-project-init
description: Use this skill when initializing a brand new EVM Solidity smart contract project using Foundry from scratch. Covers forge setup, structure scaffolding, and configuring the exact path-filtered GitHub Actions CI workflow.
---

# Foundry Smart Contract Project Initialization & CI Setup

This skill provides the end-to-end setup script to bootstrap a clean, secure Solidity development workspace utilizing Foundry (`forge`) along with an automated GitHub Actions CI pipeline.

## 🏃‍♂️ Step-by-Step Initialization Workflow

### 1. Initialize the Foundry Template

Create your root repository folder and initialize the default Foundry workspace structure natively:

```bash
mkdir smart-contract && cd smart-contract
```

```bash
forge init --vscode
```

### 2. Scaffold Hidden & Automation Paths

Ensure all required configuration and CI directories exist before writing template files:

```bash
mkdir -p .github/workflows
```

### 3. Establish GitHub Actions CI Workflow

Inject your strict, path-filtered continuous integration pipeline. This workflow optimizes runner performance by only executing on actual configuration or contract source code alterations in .github/workflows/ci.yml

```
name: CI

    permissions: {}

    on:
      push:
        paths:
          - 'contracts/**'
          - 'script/**'
          - 'foundry.toml'
      pull_request:
        paths:
          - 'contracts/**'
          - 'script/**'
          - 'foundry.toml'
      workflow_dispatch:

    jobs:
      check:
        name: Foundry project
        runs-on: ubuntu-latest
        permissions:
          contents: read
        steps:
          - uses: actions/checkout@v6
            with:
              persist-credentials: false
              submodules: recursive

          - name: Install Foundry
            uses: foundry-rs/foundry-toolchain@v1

          - name: Show Forge version
            run: forge --version

          - name: Run Forge fmt
            run: forge fmt --check

          - name: Run Forge build
            run: forge build --sizes

          - name: Run Forge tests
            run: forge test -vvv
```

---

## 🛠️ Baseline Verification & Sanity Run

Always execute the verification pipeline locally directly after bootstrapping to ensure your compiler settings (`foundry.toml`), mappings, and initial test files compile flawlessly before publishing upstream:

1. **Format Check:** Validate that style layouts are structurally compliant:

```bash
forge fmt --check
```

2. **Build Verification:** Compile contracts and ensure sizes don't breach the EIP-170 limit:

```bash
forge build --sizes
```

3. **Test Execution:** Run the baseline suite with verbose execution logging:

```bash
forge test -vvv
```
