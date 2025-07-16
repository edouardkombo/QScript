# Architecture Overview

This repository hosts multiple **QScript adapters**, each translating the same DSL into a different automation engine. A single set of `.qscript` files under `tests/` serves both as canonical test suites and as runnable examples.

## Repository Structure

```
<your-repo>/
├── adapters/
│   ├── playwright-python/
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── src/qscript_playwright/handler.py
│   └── selenium-js/
│       ├── package.json
│       ├── README.md
│       └── src/qscript_selenium/handler.js (Coming)
├── tests/
│   ├── homepage.qscript
│   ├── seo_meta.qscript
│   └── link_crawl.qscript
├── docs/
│   ├── architecture.md
│   └── getting_started.md
├── .github/workflows/ci.yml
├── scripts/format.sh
├── LICENSE
├── README.md
├── pyproject.toml
└── .gitignore
```

## Key Components

1. **Adapters** (`adapters/`)

   - **playwright-python/**

     - Python package using Playwright.
     - Contains its own `pyproject.toml`, `README.md`, and source under `src/qscript_playwright/handler.py`.

   - **selenium-js/**

     - JavaScript package using Selenium.
     - Contains its own `package.json`, `README.md`, and source under `src/qscript_selenium/handler.js` (in development).

     Each adapter is independently versioned and installed, exposing its own CLI entry point.

2. **Shared Tests & Examples** (`tests/`)

   - All `.qscript` files here (e.g., `homepage.qscript`, `seo_meta.qscript`, `link_crawl.qscript`) serve both as the official test suite and as usage examples.
   - CI workflows run every adapter’s CLI against all files in `tests/` to ensure consistency.

3. **Documentation** (`docs/`)

   - **architecture.md** — This overview.
   - **getting_started.md** — Step-by-step quickstart guide.

4. **CI Workflows** (`.github/workflows/ci.yml`)

   - Defines a matrix that installs each adapter and runs its CLI against the shared `tests/` folder.

5. **Meta-package & Dev Tooling** (`pyproject.toml` at repo root)

   - Declares shared development dependencies (pytest, black, flake8, mkdocs, etc.).
   - Configures formatting, linting, and test discovery for the entire repo.

## Design Principles

This structure ensures a **single source of truth** for QScript files, simplifies maintenance, and makes it easy to add new adapters without duplication.
