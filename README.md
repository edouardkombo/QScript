QScript Adapters
A unified framework for writing, testing, and sharing QScript—a concise, human-readable DSL for end-to-end web automation—across multiple automation engines.
🚀 Project Overview

Purpose: Define a single, consistent test format (QScript) that can be executed by any adapter (Playwright-Python, Selenium-JS, etc.).
Structure:

<your-repo>/
├── adapters/
│   ├── playwright-python/   # Python + Playwright adapter
│   └── selenium-js/         # JavaScript + Selenium adapter
├── tests/                   # Shared QScript files (tests & examples)
├── docs/                    # Architecture & getting started guides
├── .github/                 # CI configs
├── LICENSE                  # MIT license
├── README.md                # This overview
└── pyproject.toml           # Meta-package & dev dependencies

📦 Installation

Clone:
git clone https://github.com/edouardkombo/qscript-adapters.git
cd qscript-adapters


Shared tools & browsers:
pip install -e .[dev]
playwright install


Install an adapter:

Playwright (Python):
pip install -e adapters/playwright-python


Selenium (JavaScript):
cd adapters/selenium-js && npm install





Each adapter’s README has its own CLI instructions and examples:

Playwright-Python Adapter
Selenium-JS Adapter

🔤 QScript DSL Manifesto
QScript is designed to be:

Linear: One command per line, executed in order.
Declarative: Focus on what to do, not how internally.
Self-documenting: Tests read like plain English.
Engine-agnostic: Any adapter can implement the same commands.

Core Commands

Navigation & Interaction

Goto "<URL>"
Click "<selector>"
Fill "<selector>" with "<text>"
FillAuto "<selector>" with "<text>"
ScrollTo "<selector>"
WaitFor "<selector>"


Assertions

Assert page.status is <code>
Assert page.url is "<URL>"
Assert element "<selector>" exists
Assert element "<selector>" visible
Assert CLS < <threshold>
Assert element "<selector>" similar to "<text>" < <threshold>
Assert children of "<selector>" count <op> <number>
Assert attribute <selector>@<attr> matches /<regex>/
Assert each attribute <attr> in elements "<selector>" matches /<regex>/


Session & Context

SaveSession "<name>"
RestoreSession "<name>"
AssertCookie "<name>" is "<value>"
Viewport <width>x<height>


Control Flow

Retry <n> times on failure
SetVar "<VAR>" = <JS expression>
WaitForPopup / SwitchToPopup / ClosePopup
SwitchToIFrame "<selector>" / ReturnFromIFrame



File Format

Files must end in .qscript.
Lines beginning with # are comments.
Special headers:
Test: <Name> [<LEVEL>] — Begins a test case.
Tags: <tag1> <tag2> ... — Optional metadata.
End — Marks end of a test case.



Variables & Substitution

Use <VAR> placeholders in the script.
Pass -v VAR=value on the CLI.
Adapters replace <VAR> before execution.

🔗 Links & Further Reading

Architecture
Quickstart
Playwright-Python Adapter
Selenium-JS Adapter

🤝 Contributing
We welcome contributions of all kinds—new adapters, bug fixes, feature ideas, or improved DSL commands.

Fork the repo and create your branch:
git checkout -b feature/my-new-adapter


Implement your changes:

For new adapters: Follow the pattern in adapters/, include README.md, tests, and CI entry.
For core features: Ensure existing adapters continue to pass all tests/*.qscript.


Write Tests in tests/ to cover your changes.

Open a Pull Request against main with a clear title and description.

Engage in the review—address feedback, add docs, and iterate.


See Contributing Guidelines for detailed guidelines.

Manifesto in brief:QScript is the one true DSL for web automation—simple, declarative, and adapter-agnostic—designed so that AI, humans, and CI systems all read the same language and get identical results.
