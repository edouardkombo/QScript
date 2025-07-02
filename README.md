
# QScript: Human-Centric QA Scripting Language

QScript is a human-readable, flow-based scripting language for defining automated quality assurance checks. Inspired by Gherkin but designed for **clarity**, **speed**, and **machine efficiency**, QScript allows developers, product owners, and testers to write readable and executable QA specifications in `.qscript` files.

---

## ✅ What Makes QScript Unique?

- **Readable**: Looks like pseudocode but executes like code
- **Composable**: Define reusable `Flows` and nestable `Scenarios`
- **Extensible**: Covers SEO, UX, Functional, Performance, and Security
- **Intuitive**: Syntax rules designed to avoid confusion or ambiguity
- **Modular**: Tests can be grouped by product, category, or priority

---

## 📦 File Format

QScript scripts are written in `.qscript` files, structured with:

- `Test`: assertion-driven check with priority
- `Flow`: reusable step chain (no assertion needed)
- `Scenario`: high-level sequence of `Flows` and `Assertions`

---

## 📐 Syntax Overview

```
Test: Check home title [HIGH]
  Tags: [SEO]
  Goto "/"
  Assert "title" matches /.+/
End

Flow: Login Flow
  Goto "/login"
  Fill "#email" with "admin@example.com"
  Fill "#password" with "secret"
  Click "#submit"
  WaitFor ".dashboard"
End

Scenario: Full Deposit
  Steps:
    Use "Login Flow"
    Use "Deposit Flow"
    Assert "#thankyou" is visible
  End
End
```

---

## 🔠 Priorities

Use either the short form `[P0–P3]` or human-readable form:

| Label     | Equivalent | Description        |
|-----------|------------|--------------------|
| CRITICAL  | P0         | Blocker/Fail Fast  |
| HIGH      | P1         | Must pass in prod  |
| MEDIUM    | P2         | Desirable to test  |
| LOW       | P3         | Optional cosmetic  |

---

## 🧠 Structure Definitions

### `Test`
- Must contain one or more `Assert`
- Appears in test reports

### `Flow`
- Reusable action logic (e.g., Login, Signup)
- No assertions required

### `Scenario`
- High-level sequence of `Flow`, `Use`, and `Assert`
- Optional `Tags`, `Steps`, and conditions

---

## 🌀 Control Blocks

### `ForEachURL`
```
Test: Footer exists [LOW]
  ForEachURL:
    "/"
    "/contact"
  Do:
    Assert "footer" is visible
  End
End
```

### `ForEachData`
```
Test: Login Variants [CRITICAL]
  ForEachData:
    Table:
      | email            | password |
      | user@site.com    | pass123  |
  Do:
    Use "Login Flow"
  End
End
```

---

## 🧩 Action Commands

```
Goto "/path"
Click "#button"
Fill "#email" with "test@example.com"
FillAuto "#amount" as "random_2digit"
WaitFor ".success"
ScrollTo "#footer"
Viewport 1440 900
```

---

## 🧪 Assertions

```
Assert "#el" is visible
Assert "page.status" is 200
Assert "#title" text matches /Welcome/
AssertCookie "auth" exists
Assert "$token" == "$userToken"
```

---

## 🧠 Meta Features

```
Retry 2 times
WaitFor "#el" timeout 3000ms
SetVar "token" from JS "window.token"
SaveSession as "session1"
RestoreSession "session1"
SkipIfEnv: "STAGING"
```

---

## 🌍 Context Management

- `WaitForPopup`, `SwitchToPopup`, `ClosePopup`
- `SwitchToIFrame`, `ReturnFromIFrame`
- `ClearCookies`, `SaveSession`, `RestoreSession`

---

## 🧠 Reserved Words

- `page.status`, `page.url`, `page.redirected_from`
- `page.loadtime`, `viewport.width`, `$<variable>`

---

## 📁 Test Organization

Structure your repo like:
```
/tests
  ├── seo.qscript
  ├── ux.qscript
  ├── deposit.qscript
  ├── regressions.qscript
```

---

## 🔌 Import Support

To reuse flows across files:
```
Import "../flows/common-flows.qscript"
Use "Login Flow"
```

---

## 🚦 Reporting Engine

Each `Test` emits:
- Pass/fail status
- Step-by-step execution logs
- Screenshot (optional)
- Step duration and error detail

---

## 📚 Example Scenario

```
Flow: Signup Flow
  Goto "/signup"
  FillAuto "#email" as "random_email"
  FillAuto "#pass" as "random_password"
  Click "#register"
  WaitFor ".welcome"
End

Scenario: Signup + Deposit
  Steps:
    Use "Signup Flow"
    Use "Deposit Flow"
    Assert "#thanks" is visible
  End
End
```

---

## 💡 Philosophy

> “Write like a human. Test like a machine.”

QScript empowers your team to scale testing without bottlenecks.

- Fast onboarding
- IDE-friendly
- AI-generatable
- Git-diffable
- Future-proof

---

## 🧪 Coming Soon
- Live test runner UI
- GitHub Action integration
- Auto generate `.qscript` from URL or video
- Visual test flow map
- Native VS Code extension

---

## ✨ Start Testing Now

Just drop your first `.qscript` file in your test repo and let the runner do the rest.

Want help writing your first test? Use:
```
npx qscript-gen --input "verify title on homepage" --file seo.qscript
```

Or try it live with:
```
python qa_runner.py --file tests/home.qscript --mode desktop
```

Enjoy QA like never before. 🎯
