# Authentication Guide - Website Crawler

This guide shows how to configure the Web Crawler for different authentication scenarios commonly found in real-world applications.

## Table of Contents

- [Common Authentication Patterns](#common-authentication-patterns)
- [Step-by-Step Guides](#step-by-step-guides)
- [Troubleshooting](#troubleshooting)
- [API Usage](#api-usage)

## Common Authentication Patterns

### Pattern 1: Simple Form-Based Login
**Example: Basic login page with username and password fields**

```bash
python -m src.cli \
  --url "https://myapp.com/protected" \
  --login-url "https://myapp.com/login" \
  --username "test@example.com" \
  --password "mypassword" \
  --username-field "input[name='username']" \
  --password-field "input[name='password']" \
  --login-button "button[type='submit']" \
  --wait-for "body.authenticated"
```

### Pattern 2: Email/Username with Custom IDs
**Example: When fields have specific id attributes**

```bash
python -m src.cli \
  --url "https://app.example.com/dashboard" \
  --login-url "https://app.example.com/login" \
  --username "user@example.com" \
  --password "securepass123" \
  --username-field "input#email-address" \
  --password-field "input#login-password" \
  --login-button "button#submit-btn" \
  --wait-for ".main-dashboard"
```

### Pattern 3: Form with Class-Based Selectors
**Example: Bootstrap or Tailwind UI with class selectors**

```bash
python -m src.cli \
  --url "https://saas.app.io/workspace" \
  --login-url "https://saas.app.io/auth/login" \
  --username "admin@company.com" \
  --password "strongpassword" \
  --username-field "input.form-control[type='email']" \
  --password-field "input.form-control[type='password']" \
  --login-button "button.btn-primary" \
  --wait-for ".workspace-content"
```

### Pattern 4: Multi-Step Login
**For applications with multi-step auth, run crawler after first login:**

```bash
# Step 1: Login manually or with initial auth
python -m src.cli \
  --url "https://secure.bank.com" \
  --login-url "https://secure.bank.com/login" \
  --username "john_doe" \
  --password "pass123" \
  --wait-for ".dashboard" \
  --save-cookies bank_cookies.json

# Step 2: Use saved cookies for crawling protected pages
python -m src.cli \
  --url "https://secure.bank.com/accounts" \
  --cookies bank_cookies.json \
  --depth 2 \
  --export locators
```

## Step-by-Step Guides

### Guide 1: Crawling a Staging Application

**Scenario:** Your company has a staging environment at `https://staging.internal.company.com` that requires login.

**Step 1: Identify form selectors**

Open the login page in a browser with GUI (non-headless):
```bash
python -m src.cli \
  --url "https://staging.internal.company.com/login" \
  --no-headless \
  --verbose
```

Right-click on each field:
- Username field → Inspect → Note the selector (e.g., `input[name='user']`)
- Password field → Inspect → Note the selector (e.g., `input[name='pwd']`)
- Login button → Inspect → Note the selector (e.g., `button.login`)
- Post-login page element → Inspect → Note the selector (e.g., `.content`)

**Step 2: Test login with verbose output**

```bash
python -m src.cli \
  --url "https://staging.internal.company.com/dashboard" \
  --login-url "https://staging.internal.company.com/login" \
  --username "testuser" \
  --password "testpass" \
  --username-field "input[name='user']" \
  --password-field "input[name='pwd']" \
  --login-button "button.login" \
  --wait-for ".content" \
  --no-headless \
  --verbose
```

**Step 3: Save cookies for reuse**

```bash
python -m src.cli \
  --url "https://staging.internal.company.com/dashboard" \
  --login-url "https://staging.internal.company.com/login" \
  --username "testuser" \
  --password "testpass" \
  --username-field "input[name='user']" \
  --password-field "input[name='pwd']" \
  --login-button "button.login" \
  --wait-for ".content" \
  --save-cookies staging_cookies.json \
  --verbose
```

**Step 4: Crawl all pages with saved cookies**

```bash
python -m src.cli \
  --url "https://staging.internal.company.com/dashboard" \
  --cookies staging_cookies.json \
  --depth 3 \
  --max-pages 100 \
  --export csv json locators
```

### Guide 2: Crawling SaaS Applications

**Scenario:** Crawling your SaaS app (e.g., Jira, Confluence, Slack workspace, GitHub repo)

#### GitHub Repository (Private)
```bash
# First time: Login and save cookies
python -m src.cli \
  --url "https://github.com/myorg/myrepo" \
  --login-url "https://github.com/login" \
  --username "myusername" \
  --password "mytoken" \
  --username-field "input#login_field" \
  --password-field "input#password" \
  --login-button "input[type='submit']" \
  --wait-for ".Header--link" \
  --save-cookies github_cookies.json

# Subsequent crawls: Reuse cookies
python -m src.cli \
  --url "https://github.com/myorg/myrepo" \
  --cookies github_cookies.json \
  --depth 2 \
  --export locators
```

#### Jira Cloud
```bash
python -m src.cli \
  --url "https://yourcompany.atlassian.net/browse/PROJECT" \
  --login-url "https://id.atlassian.com/login" \
  --username "user@company.com" \
  --password "apitoken" \
  --username-field "input[name='username']" \
  --password-field "input[name='password']" \
  --login-button "button[type='submit']" \
  --wait-for ".navigation-sidebar" \
  --save-cookies jira_cookies.json \
  --export locators
```

### Guide 3: Using Environment Variables for Security

**Scenario:** You don't want to hardcode passwords in scripts or bash history.

**Step 1: Create a `.env` file (in .gitignore!)**
```
export APP_LOGIN_URL="https://app.company.com/login"
export APP_URL="https://app.company.com/protected"
export APP_USERNAME="automation@company.com"
export APP_PASSWORD="secretpassword123"
export APP_WAIT_FOR=".page-loaded"
```

**Step 2: Source the env vars and run**
```bash
source .env

python -m src.cli \
  --url "$APP_URL" \
  --login-url "$APP_LOGIN_URL" \
  --username "$APP_USERNAME" \
  --password "$APP_PASSWORD" \
  --wait-for "$APP_WAIT_FOR" \
  --save-cookies cookies.json \
  --export locators
```

**Step 3: Add to .gitignore**
```
.env
cookies.json
```

## Troubleshooting

### Issue 1: Login Button Not Found

**Symptoms:** Error "Could not find element: button[type='submit']"

**Solutions:**
1. Check if the button has a different selector
   ```bash
   # Try class-based selector
   --login-button "button.login-button"
   
   # Try id-based selector
   --login-button "button#login-btn"
   
   # Try span text inside button
   --login-button "button:contains('Sign In')"
   
   # Try link instead of button
   --login-button "a.login-link"
   ```

2. Check if form submission is different
   ```bash
   # Maybe the form submits on Enter key
   # Add --wait-for to confirm page loads
   --wait-for ".authenticated"
   ```

### Issue 2: Login Succeeds But Elements Not Found

**Symptoms:** Login works but crawling returns 0 elements

**Solutions:**
1. Increase wait time - page might load slowly
   ```bash
   --implicit-wait 10
   ```

2. Verify the --wait-for selector matches post-login page
   ```bash
   python -m src.cli \
     --url "yourapp.com/dashboard" \
     --cookies cookies.json \
     --no-headless \
     --verbose
   ```
   Wait for page to load, then manually verify elements exist

3. Check if session expired
   - Cookies might be expired
   - Re-login and save fresh cookies

### Issue 3: Credentials Rejected

**Symptoms:** Login fails or password error

**Solutions:**
1. Verify credentials are correct
2. Check if account is activated/not locked
3. Some sites may have rate limiting - wait before retry
4. Check if two-factor auth is enabled - might need different approach

### Issue 4: Selector Changes Between Page Loads

**Symptoms:** Login works once but fails on subsequent runs

**Solutions:**
1. Save and reuse cookies instead of re-logging in
2. Check if session expires quickly - increase max-pages
3. Site might block repeated logins from same IP - use proxy

## API Usage

### Python Code Example: Authenticated Crawling

```python
from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter

# Initialize crawler
crawler = WebCrawler(headless=True)

# Login with credentials
login_success = crawler.login_with_credentials(
    login_url="https://app.example.com/login",
    username="user@example.com",
    password="mypassword",
    username_field_selector="input[name='username']",
    password_field_selector="input[type='password']",
    login_button_selector="button.login-btn",
    wait_for_selector=".dashboard",
    wait_timeout=10
)

if not login_success:
    print("Login failed!")
    crawler.close()
    exit(1)

# Save session cookies for future reuse
crawler.save_cookies_to_file("cookies.json")

# Crawl authenticated pages
results = crawler.crawl_recursive(
    start_url="https://app.example.com/dashboard",
    max_depth=2,
    max_pages=50
)

# Generate locators
generator = LocatorGenerator(crawler.driver)
locators_data = []

for result in results:
    if result.get("status") == "success":
        for element in result.get("elements", []):
            locators = generator.generate_locators(element)
            locators_data.append(locators)

# Export
exporter = Exporter(output_dir="output")
exporter.export_to_locators_txt(locators_data, "authenticated_locators.txt")
exporter.export_to_json(locators_data, "authenticated_locators.json")

crawler.close()
print(f"Found and exported {len(locators_data)} locators")
```

### Python Code Example: Cookie Reuse

```python
from src.crawler import WebCrawler
from src.locator_generator import LocatorGenerator
from src.exporter import Exporter

crawler = WebCrawler(headless=True)

# Load previously saved cookies (from a successful login)
cookies_loaded = crawler.load_cookies_from_file("cookies.json")

if not cookies_loaded:
    print("Cookies file not found or invalid")
    exit(1)

# Crawl with existing session
results = crawler.crawl_recursive(
    start_url="https://app.example.com/dashboard",
    max_depth=3,
    max_pages=100
)

# Process and export...
generator = LocatorGenerator(crawler.driver)
exporter = Exporter()

locators_data = []
for result in results:
    if result.get("status") == "success":
        for element in result.get("elements", []):
            locators = generator.generate_locators(element)
            locators_data.append(locators)

exporter.export_to_locators_txt(locators_data)
exporter.export_to_excel(locators_data)

crawler.close()
```

## Best Practices

1. **Always save cookies after successful login**
   ```bash
   --save-cookies session.json
   ```

2. **Use environment variables for credentials**
   - Never commit passwords to git
   - Use `.env` file in `.gitignore`

3. **Test login flow first without headless mode**
   ```bash
   --no-headless --verbose
   ```

4. **Use specific, unique selectors**
   - ID selectors are best: `input#email`
   - Avoid generic selectors: `input`, `button`

5. **Set appropriate wait times**
   - For slow pages: `--implicit-wait 10`
   - For ajax: `--wait-for ".loaded-indicator"`

6. **Handle session expiry**
   - Refresh cookies periodically
   - Check if cookies are valid before crawling
   - Add retry logic for failed requests

7. **Log activities for debugging**
   ```bash
   --verbose
   ```

## Need Help?

- Check the main [README.md](README.md) for general usage
- Review [config/config.yaml](config/config.yaml) for configuration options
- Run with `--verbose` flag to see detailed logs
- Check logs in `logs/crawler.log` for troubleshooting
