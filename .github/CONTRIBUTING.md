# Contributing to QScript

First off, thank you for your interest in contributing! We appreciate your time and effort.

## Table of Contents

1. [How to File an Issue](#how-to-file-an-issue)
2. [Development Setup](#development-setup)
3. [Code Style & Tests](#code-style--tests)
4. [Adding a New Adapter](#adding-a-new-adapter)
5. [Submitting a Pull Request](#submitting-a-pull-request)
6. [Code of Conduct](#code-of-conduct)

## How to File an Issue

1. Search existing issues to avoid duplicates.
2. Click **New Issue** and choose the appropriate template.
3. Provide a clear title and description:
   - What you expected to happen
   - What actually happened
   - Steps to reproduce
   - Versions of Python/Node, OS, and adapters

## Development Setup

1. **Fork** this repository.
2. **Clone** your fork and install dev dependencies:

   ```bash
   git clone https://github.com/edouardkombo/QScript.git
   cd QScript
   pip install -e .[dev]
   playwright install
   ```

3. **Install** the adapter you’re working on:

   - **Python:**

     ```bash
     pip install -e adapters/playwright-python
     ```

   - **JavaScript:**

     ```bash
     cd adapters/selenium-js && npm install
     ```

## Code Style & Tests

- **Formatting:**

  - Python: [Black](https://github.com/psf/black) (88-char line length)
  - JavaScript: [Prettier](https://prettier.io/) with project defaults

- **Linting:**

  - Python: `flake8`
  - JavaScript: `eslint` (via adapter’s `package.json`)

- **Tests:**

  - Place new `.qscript` tests in `tests/`.
  - Run:

    ```bash
    pytest tests/            # Python adapter
    npx qscript-selenium tests/*.qscript --base-url=https://example.com  # JS adapter
    ```

- **CI:**

  - All tests must pass on GitHub Actions before merging.

## Adding a New Adapter

1. **Create** a new folder under `adapters/`, e.g., `adapters/my-adapter`.
2. **Copy** structure from an existing adapter:
   - Packaging manifest (`pyproject.toml` or `package.json`)
   - `README.md` with CLI instructions
   - `src/` folder with `handler` implementation
3. **Implement** the QScript DSL handlers you need.
4. **Add** a `console_scripts` entry or `bin/` script for your CLI.
5. **Write** example `.qscript` files in `tests/` and ensure they pass.
6. **Update** `.github/workflows/ci.yml` to include your adapter in the matrix.

## Submitting a Pull Request

1. **Fork & branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Commit messages:**

   - Use [Conventional Commits](https://www.conventionalcommits.org/):
     - `feat(adapter): add X support`
     - `fix(playwright): handle timeout errors gracefully`

3. **Push** your branch and open a PR against `main`.

4. **Fill out** the PR template:
   - What problem does this solve?
   - How did you test it?
   - Any breaking changes?

5. **Respond** to review comments promptly.

## Code of Conduct

Please note we have a [Code of Conduct](../CODE_OF_CONDUCT.md). By participating, you agree to abide by its terms.

---

Thank you for helping make QScript better! 🚀
