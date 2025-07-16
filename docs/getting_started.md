# Getting Started

A step-by-step guide to clone this repository, install dependencies, write your first QScript, and run it with any adapter.

## 1. Clone the Repository

```bash
git clone https://github.com/edouardkombo/QScript.git
cd qscript-adapters
```

## 2. Install Shared Development Tools

From the root of the repo:

```bash
pip install -e .[dev]
playwright install
```

- Installs shared dev dependencies: `pytest`, `black`, `flake8`, `mkdocs`, etc.
- Installs Playwright browser binaries (required by the Python adapter).

## 3. Install an Adapter

### Playwright (Python)

```bash
pip install -e adapters/playwright-python
```

### Selenium (JavaScript)

```bash
cd adapters/selenium-js
npm install
```

Each adapter will expose its own CLI:

- `qscript-playwright`
- `qscript-selenium`

## 4. Write Your First QScript

Create `tests/hello.qscript` with:

```qscript
Test: Hello world [LOW]
Tags: example

# Navigate to the site
Goto "<BASE_URL>"

# Verify HTTP 200
Assert page.status is 200

# Check for an <h1>
Assert element "h1" exists

End
```

> **Note**: QScript files must end in `.qscript` and can use variables like `<BASE_URL>`.

## 5. Run Your QScript

Supply `BASE_URL` and use the adapter’s CLI.

### Playwright-Python

```bash
qscript-playwright tests/hello.qscript \
  -v BASE_URL=https://github.com
```

### Selenium-JS

```bash
npx qscript-selenium tests/hello.qscript \
  --base-url=https://github.com
```

Both commands will print a JSON array summarizing each step’s status.

## 6. Run the Shared Test Suite

Validate every adapter against the canonical tests:

```bash
# Python adapter
pytest tests/

# JavaScript adapter
npx qscript-selenium tests/*.qscript \
  --base-url=https://github.com
```

## 7. Add or Extend an Adapter

1. Copy an existing adapter folder under `adapters/`.
2. Update its manifest (`pyproject.toml` or `package.json`) and CLI entry point.
3. Implement `handler.*` to support the QScript DSL.
4. Add a CI job in `.github/workflows/ci.yml` to run your new CLI against `tests/`.

You're all set—write more `.qscript` files in `tests/` and have each adapter execute them consistently!
