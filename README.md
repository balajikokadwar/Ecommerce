# Selenium + Python + Behave BDD Framework (Page Object Model)

Automated UI test framework for the practice e-commerce site
[`rahulshettyacademy.com/client`](https://rahulshettyacademy.com/client/#/auth/login),
built with **Selenium WebDriver**, **Behave** (Gherkin/BDD) and the
**Page Object Model (POM)** design pattern.

Current flow automated: **log in → add "ZARA COAT 3" to the cart → open the
cart → verify the product is present**.

---

## 1. Project structure

```
Behave BDD POM/
├── config/
│   └── config.yaml            # Non-secret defaults (base_url, browser, timeouts...)
├── features/
│   ├── environment.py          # Behave hooks: driver lifecycle, screenshots on failure
│   ├── add_product_to_cart.feature
│   └── steps/
│       ├── login_steps.py      # Step definitions for the login page
│       ├── home_steps.py       # Step definitions for the home/product page
│       └── cart_steps.py       # Step definitions for the cart page
├── pages/                      # Page Object Model
│   ├── base_page.py            # Shared, wait-safe Selenium helpers
│   ├── login_page.py           # POM #1 – Login page
│   ├── home_page.py            # POM #2 – Home / product listing page
│   └── cart_page.py            # POM #3 – Cart page
├── utils/
│   ├── config_reader.py        # Merges config.yaml + .env + real env vars
│   ├── driver_factory.py       # Builds Chrome/Firefox/Edge WebDriver instances
│   └── logger.py               # Shared file + console logger
├── reports/
│   ├── junit/                  # JUnit XML results (consumed by CI test reporters)
│   ├── logs/                   # execution.log
│   └── screenshots/            # Auto-captured on step failure
├── behave.ini                  # Behave runtime configuration
├── requirements.txt
├── .env.example                # Template for local credentials
├── .env                        # Local-only credentials (git-ignored)
└── .gitignore
```

### Why this layout
- **`pages/`** contains only Selenium interaction logic (locators + actions).
  No assertions and no test data live here — that keeps page objects reusable
  across any number of feature files.
- **`features/steps/`** contains only Gherkin-to-Python glue. Each step
  delegates to a page object method and, where relevant, an assertion.
- **`utils/`** and **`config/`** are cross-cutting concerns (config, logging,
  driver creation) that every layer depends on, but that depend on nothing
  test-specific — this is what keeps the framework "layered" instead of a
  ball of mud.

---

## 2. Page Object Model

| Page object | File | Represents |
|---|---|---|
| `LoginPage` | `pages/login_page.py` | `/#/auth/login` |
| `HomePage` | `pages/home_page.py` | `/#/dashboard/dash` (product listing) |
| `CartPage` | `pages/cart_page.py` | `/#/dashboard/cart` |

All three inherit from `BasePage` (`pages/base_page.py`), which centralizes:
- Explicit `WebDriverWait`-based interactions (`click`, `type_text`,
  `get_text`, `wait_for_visible`, `wait_for_clickable`, `wait_for_invisible`, `is_visible`…).
  No implicit waits are used anywhere, to avoid the classic
  implicit+explicit wait mixing bugs.
- A resilient `click()` that retries a couple of times if a transient
  overlay (e.g. this site's `ngx-spinner-overlay` loading spinner) briefly
  intercepts the click — a real race condition this app exhibits after
  "Add To Cart".

Page objects are instantiated once per scenario in `features/environment.py`
(`before_scenario`) and attached to Behave's `context`, so any step can use
`context.login_page`, `context.home_page`, `context.cart_page`.

---

## 3. Configuration & secrets

Precedence (highest wins): **real environment variable → `.env` file →
`config/config.yaml`**.

- `config/config.yaml` — non-secret defaults: `base_url`, `browser`,
  `headless`, `explicit_wait`, `page_load_timeout`, `screenshot_on_failure`.
  Any key can be overridden by setting an environment variable with the
  same name in UPPERCASE (e.g. `HEADLESS=true`, `BROWSER=firefox`).
- `.env` (git-ignored) — local-only credentials, loaded via `python-dotenv`.
  Copy `.env.example` to `.env` and fill in `LOGIN_EMAIL` / `LOGIN_PASSWORD`.
- **In CI**, don't ship a `.env` file — set `LOGIN_EMAIL`, `LOGIN_PASSWORD`,
  `HEADLESS=true` (and `BROWSER` if needed) as repository/environment
  **secrets** and export them as env vars in the workflow step. The
  framework reads env vars first, so no code changes are needed.

Credentials are never hardcoded in page objects or step definitions —
`utils/config_reader.py:ConfigReader.login_email()/login_password()` is the
single place that resolves them, and it raises a clear error if they're
missing.

---

## 4. Running the tests locally

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up credentials
copy .env.example .env
# then edit .env with real LOGIN_EMAIL / LOGIN_PASSWORD

# 4. Run all tests (headed Chrome by default, per config/config.yaml)
behave

# Run only smoke tests
behave --tags=@smoke

# Run headless (what CI uses)
$env:HEADLESS = "true"; behave
```

No separate chromedriver/geckodriver download is required — Selenium 4's
built-in **Selenium Manager** resolves the correct driver for whichever
browser/version is installed, on Windows or in CI (Linux) alike.

### Outputs
- `reports/logs/execution.log` — full run log (also echoed to console).
- `reports/junit/*.xml` — JUnit XML per feature (generated because
  `junit = true` is set in `behave.ini`). CI systems (GitHub Actions'
  `dorny/test-reporter`, Jenkins, Azure DevOps, etc.) can consume this
  directly for a pass/fail test summary.
- `reports/screenshots/*.png` — automatically captured whenever a step
  fails (toggle via `screenshot_on_failure` in `config.yaml`).

---

## 5. CI/CD — GitHub Actions pipeline

`.github/workflows/bdd-tests.yml` runs the suite **module-wise, based on the
branch name**:

| Trigger | Branch/event | What runs |
|---|---|---|
| `push` to any branch | branch name contains `login` | `behave --tags=@login` |
| `push` to any branch | branch name contains `home` | `behave --tags=@home` |
| `push` to any branch | branch name contains `cart` | `behave --tags=@cart` |
| `push`/`pull_request` | no module keyword in the branch name | `behave --tags=@smoke` (fallback) |
| `schedule` (nightly, 01:30 UTC) | always the default branch | `behave --tags=@regression` (full suite) |
| `workflow_dispatch` (manual, "Run workflow" button) | — | uses the `tag` input you type in, if provided; otherwise falls back to the same branch-name detection |

How the branch → module mapping works (job step `Resolve which module/tag to
run` in the workflow): it lower-cases `github.head_ref` (for PRs) or
`github.ref_name` (for direct pushes) and checks whether it contains
`login`, `home`, or `cart` — first match wins. Add new keywords to the
`MODULES=(...)` array in that step as new page objects/features are added.

**Tagging convention this relies on**: every feature file must carry a
module tag matching one of those keywords (the current
`add_product_to_cart.feature` carries `@cart`), plus `@smoke`/`@regression`
on individual scenarios to control nightly vs. fast-path runs. Right now
there is a single feature covering the whole login→home→cart journey under
`@cart`; a branch named e.g. `feature/login-validation` will currently fall
back to `@smoke` (which still matches, since the one scenario carries that
tag too) rather than run an isolated login-only test — add a dedicated
`@login`-tagged feature once there's login-specific behaviour to test in
isolation.

Other things the pipeline does:
- Runs **headless** (`HEADLESS: "true"`) on `ubuntu-latest`, which ships
  with Chrome preinstalled — Selenium Manager resolves the matching driver
  automatically, no extra install step.
- Reads `LOGIN_EMAIL` / `LOGIN_PASSWORD` from **GitHub Actions secrets**
  (never from a committed `.env`) — see the setup steps below.
- Uploads `reports/` (logs, screenshots, JUnit XML) as a workflow artifact
  on every run, pass or fail (`if: always()`).
- Uses a `concurrency` group per branch/ref so pushing again to the same
  branch cancels the previous in-flight run instead of queueing.

### One-time setup required in the GitHub UI

1. **Push this project to a GitHub repository** (it isn't a git repo yet
   locally — `git init`, commit, add a remote, push).
2. **Add the two required secrets**: repo → **Settings → Secrets and
   variables → Actions → New repository secret**
   - `LOGIN_EMAIL`
   - `LOGIN_PASSWORD`

   (use the same values that are in your local `.env` — that file is
   git-ignored and must never be committed).
3. **Confirm Actions are enabled**: **Settings → Actions → General →
   Actions permissions** should allow running workflows (this is the
   default for new repos, but private/org repos sometimes have it
   restricted).
4. **Nightly schedule note**: GitHub only fires `schedule` triggers on the
   repository's **default branch**, and only once that workflow file
   exists on that branch — so the `bdd-tests.yml` file must be merged into
   `main` (or whichever branch is set as default) for the 01:30 UTC nightly
   run to start firing. Also note GitHub may auto-disable scheduled
   workflows after **60 days of repository inactivity**; a push or manual
   run re-enables them.
5. **Manual runs**: **Actions tab → "BDD Tests" workflow → "Run workflow"**
   button — you can optionally type a tag (e.g. `@login`) in the input box
   before running.
6. **(Optional) Branch protection**: if you want the pipeline to gate
   merges, go to **Settings → Branches → Add branch protection rule** for
   `main` and require the `Run BDD tests` status check to pass before
   merging.
7. **(Optional) Viewing results**: after a run, open it under the
   **Actions** tab → the run → the `bdd-test-reports-<id>` artifact at the
   bottom of the summary page contains the logs/screenshots/JUnit XML.

---

## 6. Extending the framework

- **New page**: add `pages/<name>_page.py` extending `BasePage`, wire it up
  in `features/environment.py:before_scenario` as `context.<name>_page`.
- **New scenario**: add a `.feature` file under `features/`; reuse existing
  step definitions where the wording matches, or add new ones under
  `features/steps/`.
- **New browser**: already supported — `utils/driver_factory.py` handles
  `chrome` / `firefox` / `edge`; set `BROWSER=firefox` (env var) or edit
  `config/config.yaml`.
- **Parallel execution / cross-browser matrix**: not wired up yet; the
  cleanest path is `behave-parallel` or splitting `behave` invocations per
  browser in the CI matrix — the framework's per-scenario driver creation
  already makes scenarios independent/thread-safe for this.

---

## 7. Design decisions worth knowing about

- **Selenium Manager over `webdriver-manager`**: fewer dependencies, and
  it's the officially supported mechanism in Selenium 4.6+.
- **Only explicit waits**: every interaction in `BasePage` goes through
  `WebDriverWait`; there is no `implicitly_wait()` anywhere, which avoids
  the well-known unpredictable-timeout bugs from mixing the two.
- **Resilient click with retry**: the target site shows a loading spinner
  (`.ngx-spinner-overlay`) right after "Add To Cart" that can intercept the
  next click for a few hundred milliseconds — `BasePage.click()` retries on
  `ElementClickInterceptedException`/`StaleElementReferenceException`
  instead of the test flaking.
