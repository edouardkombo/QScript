# QScript Playwright Adapter

A Python-based QScript adapter that drives Playwright to execute `.qscript` test files and emits structured JSON results on stdout.

## 📦 Installation

From the **root** of your cloned repository:

1. Install the adapter in editable mode:

   ```bash
   pip install -e adapters/playwright-python
   ```

2. Install Playwright browsers (one-time step):

   ```bash
   playwright install
   ```

This makes the `qscript-playwright` CLI available on your `PATH`.

## 🚀 CLI Usage

```bash
qscript-playwright <path/to/file.qscript> [OPTIONS]
```

- `<path/to/file.qscript>`: Path to your QScript file (must end in `.qscript`).

### Common Options

| Flag       | Description                                          | Default   |
|------------|------------------------------------------------------|-----------|
| `--devices`| Comma-separated device profiles (desktop, mobile, bot)| `desktop` |
| `--browser`| Playwright engine (chromium, firefox, webkit)        | `chromium`|
| `--debug`  | Write detailed debug logs to stderr                  | `off`     |
| `--snap`   | On assertion failure, capture HTML + PNG snapshots in CWD | `off` |
| `-v KEY=VAL`| Define a KEY=VAL substitution in the script          | `none`    |

Example:

```bash
qscript-playwright tests/login.qscript \
  --devices desktop,bot \
  --browser firefox \
  --debug \
  --snap \
  -v USER=alice \
  -v PASS=Secret123
```

## 🔤 QScript DSL Commands

Your `.qscript` files may contain any of the following commands:

1. **Navigation / Interaction**

   ```qscript
   Goto "https://example.com"
   Click "button#login"
   Fill "input[name='user']" with "alice"
   FillAuto "input[name='search']" with "playwright"
   ScrollTo "footer"
   WaitFor "div#results"
   ```

2. **Assertions**

   ```qscript
   Assert page.status is 200
   Assert page.url is "https://example.com/dashboard"
   Assert element "h1" exists
   Assert element "h1" visible
   Assert CLS < 0.1
   Assert element "header" similar to "Welcome" < 0.8
   Assert children of "ul.menu" count >= 3
   ```

3. **Session & Context**

   ```qscript
   SaveSession "session1"
   RestoreSession "session1"
   AssertCookie "sessionid" is "abcdef123456"
   Viewport 1024x768
   ```

4. **Control Flow**

   ```qscript
   Retry 3 times on failure
   SetVar "TOKEN" = "computed_value"
   WaitForPopup
   SwitchToPopup
   ClosePopup
   SwitchToIFrame "iframe#chat"
   ReturnFromIFrame
   ```

## 📋 Example `.qscript` File

```qscript
Test: Login flow [HIGH]
Tags: auth smoke

# Navigate to login page
Goto "https://example.com/login"

# Fill form and submit
Fill "input#user" with "<USER>"
Fill "input#pass" with "<PASS>"
Click "button#submit"

# Verify dashboard
WaitFor "div#welcome"
Assert page.status is 200
Assert element "div#welcome" similar to "Welcome, Alice" < 0.9
End
```

Run it with:

```bash
qscript-playwright examples/login_flow.qscript \
  --devices desktop \
  --browser chromium \
  --debug \
  -v USER=alice \
  -v PASS=Secret123
```

## 🛠️ Development & Testing

1. Run tests (pytest):

   ```bash
   pytest adapters/playwright-python/tests
   ```

2. Lint & format:

   ```bash
   black adapters/playwright-python
   flake8 adapters/playwright-python
   ```

3. Re-build docs (if any):

   ```bash
   mkdocs build
   ```

## 📝 License

This adapter is MIT-licensed. See the root [LICENSE](../LICENSE) for full terms.
