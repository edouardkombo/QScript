
# QScript Adapters

A unified framework for writing, testing, and sharing **QScript**â€”a concise, human-readable DSL for end-to-end web automationâ€”across multiple automation engines.

## ðŸš€ Project Overview

-   **Purpose:** Define a single, consistent test format (QScript) that can be executed by any adapter (Playwright-Python, Selenium-JS, etc.).
-   **Structure:**

```
your-repo/
â”œâ”€â”€ adapters/
â”‚   â”œâ”€â”€ playwright-python/   â† Python + Playwright adapter
â”‚   â””â”€â”€ selenium-js/         â† JavaScript + Selenium adapter
â”œâ”€â”€ tests/                   â† Shared QScript files (tests & examples)
â”œâ”€â”€ docs/                    â† Architecture & getting started guides
â”œâ”€â”€ .github/                 â† CI configs
â”œâ”€â”€ LICENSE                  â† MIT license
â”œâ”€â”€ README.md                â† This overview
â””â”€â”€ pyproject.toml           â† Meta-package & dev dependencies

```

## ðŸ“¦ Installation

1.  **Clone:**
    
    ```bash
    git clone https://github.com/your-org/qscript-adapters.git
    cd qscript-adapters
    
    ```
    
2.  **Shared tools & browsers:**
    
    ```bash
    pip install -e .[dev]
    playwright install
    
    ```
    
3.  **Install an adapter:**
    
    -   **Playwright (Python):**
        
        ```bash
        pip install -e adapters/playwright-python
        
        ```
        
    -   **Selenium (JavaScript):**
        
        ```bash
        cd adapters/selenium-js && npm install
        
        ```
        

Each adapterâ€™s README has its own CLI instructions and examples:

-   [adapters/playwright-python/README.md](https://github.com/edouardkombo/QScript/adapters/playwright-python/README.md)
-   [adapters/selenium-js/README.md](https://github.com/edouardkombo/QScript/adapters/selenium-js/README.md)

## ðŸ”¤ QScript DSL Manifesto

QScript is designed to be:

-   **Linear:** one command per line, executed in order.
-   **Declarative:** focus on _what_ to do, not _how_ internally.
-   **Self-documenting:** tests read like plain English.
-   **Engine-agnostic:** any adapter can implement the same commands.

### Core Commands

1.  **Navigation & Interaction**
    
    -   `Goto "<URL>"`
    -   `Click "<selector>"`
    -   `Fill "<selector>" with "<text>"`
    -   `FillAuto "<selector>" with "<text>"`
    -   `ScrollTo "<selector>"`
    -   `WaitFor "<selector>"`
2.  **Assertions**
    
    -   `Assert page.status is <code>`
    -   `Assert page.url is "<URL>"`
    -   `Assert element "<selector>" exists`
    -   `Assert element "<selector>" visible`
    -   `Assert CLS < <threshold>`
    -   `Assert element "<selector>" similar to "<text>" < <threshold>`
    -   `Assert children of "<selector>" count <op> <number>`
    -   `Assert attribute <selector>@<attr> matches /<regex>/`
    -   `Assert each attribute <attr> in elements "<selector>" matches /<regex>/`
3.  **Session & Context**
    
    -   `SaveSession "<name>"`
    -   `RestoreSession "<name>"`
    -   `AssertCookie "<name>" is "<value>"`
    -   `Viewport <width>x<height>`
4.  **Control Flow**
    
    -   `Retry <n> times on failure`
    -   `SetVar "<VAR>" = <JS expression>`
    -   `WaitForPopup` / `SwitchToPopup` / `ClosePopup`
    -   `SwitchToIFrame "<selector>"` / `ReturnFromIFrame`

### File Format

-   Files **must** end in `.qscript`.
-   Lines beginning with `#` are comments.
-   Special headers:
    -   `Test: <Name> [<LEVEL>]` â€” begins a test case.
    -   `Tags: <tag1> <tag2> â€¦` â€” optional metadata.
    -   `End` â€” marks end of a test case.

### Variables & Substitution

-   Use `<VAR>` placeholders in the script.
-   Pass `-v VAR=value` on the CLI.
-   Adapters replace `<VAR>` before execution.

## ðŸ”— Links & Further Reading

-   **Architecture:** [docs/architecture.md](https://github.com/edouardkombo/QScript/docs/architecture.md)
-   **Quickstart:** [docs/getting_started.md](https://github.com/edouardkombo/QScript/docs/getting_started.md)
-   **Playwright-Python Adapter:** [adapters/playwright-python/README.md](https://github.com/edouardkombo/QScript/adapters/playwright-python/README.md)
-   **Selenium-JS Adapter:** [adapters/selenium-js/README.md](https://github.com/edouardkombo/QScript/adapters/selenium-js/README.md)

## ðŸ¤ Contributing

We welcome contributions of all kindsâ€”new adapters, bug fixes, feature ideas, or improved DSL commands.

1.  **Fork** the repo and create your branch:
    
    ```bash
    git checkout -b feature/my-new-adapter
    
    ```
    
2.  **Implement** your changes:
    
    -   For new adapters: follow the pattern in `adapters/`, include `README.md`, tests, and CI entry.
    -   For core features: ensure existing adapters continue to pass all `tests/*.qscript`.
3.  **Write Tests** in `tests/` to cover your changes.
    
4.  **Open a Pull Request** against `main` with a clear title and description.
    
5.  **Engage** in the reviewâ€”address feedback, add docs, and iterate.
    

See [CONTRIBUTING.md](https://github.com/edouardkombo/QScript/.github/CONTRIBUTING.md) for detailed guidelines.

> **Manifesto in brief:**  
> QScript is the _one true DSL_ for web automationâ€”simple, declarative, and adapter-agnosticâ€”designed so that AI, humans, and CI systems all read the same language and get identical results.
