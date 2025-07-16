# QScript: Self-Executable Acceptance Criteria DSL

> **Transform your acceptance criteria into living tests across any framework**

QScript makes your acceptance criteria the **single source of truth**—a human-readable `.qscript` file that _is_ the test. Write your feature steps once, embed them in your issue tracker, and run instantly on Playwright, Selenium, or Cypress—no glue code, BDD layers, or manual test plans.

---

## 🔥 Why QScript?

- **Living ACs**: Your `.qscript` file _is_ your acceptance criteria and your test. Edit one place, and the change runs everywhere.
- **Framework‑Agnostic**: The same DSL works on **Playwright**, **Selenium**, or **Cypress** via `--adapter`—zero rewrites when you switch tools.
- **Built‑in Device Matrix**: Run desktop, mobile, and bot contexts **in parallel** by default (`--device desktop,mobile,bot`).
- **80%+ Time Savings**: Replace 3–5 artifacts (~30–40 LOC) with a 5‑line script—author in minutes, maintain in seconds.
- **Democratized QA**: Product, SEO, Marketing—or anyone—can read, review, and execute tests without coding.
- **Open Source**: MIT‑licensed. Star, fork, and help shape the universal test language.

---

## 🚀 Project Overview

- **Purpose:** Define a single, consistent test format (QScript) that can be executed by any adapter (Playwright-Python, Selenium-JS, etc.).
- **Structure:**

```
QScript/
├── adapters/
│   ├── playwright-python/   # Python + Playwright adapter
│   └── selenium-js/         # JavaScript + Selenium adapter
├── tests/                   # Shared QScript files (tests & examples)
├── docs/                    # Architecture & getting started guides
├── .github/                 # CI configs
├── LICENSE                  # MIT license
├── README.md                # This overview
└── pyproject.toml           # Meta-package & dev dependencies
```

## 📦 Installation

1. **Clone:**

   ```bash
   git clone https://github.com/edouardkombo/QScript.git
   cd QScript
   ```

2. **Shared tools & browsers:**

   ```bash
   pip install -e .[dev]
   playwright install
   ```

3. **Install an adapter:**

   - **Playwright (Python):**

     ```bash
     pip install -e adapters/playwright-python
     ```

   - **Selenium (JavaScript):**

     ```bash
     cd adapters/selenium-js && npm install
     ```

Each adapter’s README has its own CLI instructions and examples:

- [Playwright-Python Adapter](adapters/playwright-python/README.md)
- [Selenium-JS Adapter](adapters/selenium-js/README.md)

## 🔤 QScript DSL Manifesto

QScript is designed to be:

- **Linear:** One command per line, executed in order.
- **Declarative:** Focus on *what* to do, not *how* internally.
- **Self-documenting:** Tests read like plain English.
- **Engine-agnostic:** Any adapter can implement the same commands.

### Core Commands

1. **Navigation & Interaction**

   - `Goto "<URL>"`
   - `Click "<selector>"`
   - `Fill "<selector>" with "<text>"`
   - `FillAuto "<selector>" with "<text>"`
   - `ScrollTo "<selector>"`
   - `WaitFor "<selector>"`

2. **Assertions**

   - `Assert page.status is <code>`
   - `Assert page.url is "<URL>"`
   - `Assert element "<selector>" exists`
   - `Assert element "<selector>" visible`
   - `Assert CLS < <threshold>`
   - `Assert element "<selector>" similar to "<text>" < <threshold>`
   - `Assert children of "<selector>" count <op> <number>`
   - `Assert attribute <selector>@<attr> matches /<regex>/`
   - `Assert each attribute <attr> in elements "<selector>" matches /<regex>/`

3. **Session & Context**

   - `SaveSession "<name>"`
   - `RestoreSession "<name>"`
   - `AssertCookie "<name>" is "<value>"`
   - `Viewport <width>x<height>`

4. **Control Flow**

   - `Retry <n> times on failure`
   - `SetVar "<VAR>" = <JS expression>`
   - `WaitForPopup` / `SwitchToPopup` / `ClosePopup`
   - `SwitchToIFrame "<selector>"` / `ReturnFromIFrame`

### File Format

- Files **must** end in `.qscript`.
- Lines beginning with `#` are comments.
- Special headers:
  - `Test: <Name> [<LEVEL>]` — Begins a test case.
  - `Tags: <tag1> <tag2> ...` — Optional metadata.
  - `End` — Marks end of a test case.

### Variables & Substitution

- Use `<VAR>` placeholders in the script.
- Pass `-v VAR=value` on the CLI.
- Adapters replace `<VAR>` before execution.

## 🔗 Links & Further Reading

- [Architecture](docs/architecture.md)
- [Quickstart](docs/getting_started.md)
- [Playwright-Python Adapter](adapters/playwright-python/README.md)
- [Selenium-JS Adapter](adapters/selenium-js/README.md)

## 🤝 Contributing

We welcome contributions of all kinds—new adapters, bug fixes, feature ideas, or improved DSL commands.

1. **Fork** the repo and create your branch:

   ```bash
   git checkout -b feature/my-new-adapter
   ```

2. **Implement** your changes:

   - For new adapters (Puppeteer, TestCafe, etc.): Follow the pattern in `adapters/`, include `README.md`, tests, and CI entry.
   - For core features: Ensure existing adapters continue to pass all `tests/*.qscript`.
   - DSL enhancements
   - Bug Fixes & docs improvements

3. **Write Tests** in `tests/` to cover your changes.

4. **Open a Pull Request** against `main` with a clear title and description.

5. **Engage** in the review—address feedback, add docs, and iterate.

See [Contributing Guidelines](.github/CONTRIBUTING.md) for detailed guidelines.

> **Manifesto in brief:**
> QScript is the *one true DSL* for web automation—simple, declarative, and adapter-agnostic—designed so that AI, humans, and CI systems all read the same language and get identical results.
