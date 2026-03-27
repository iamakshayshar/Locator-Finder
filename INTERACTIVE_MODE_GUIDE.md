# Interactive Mode Guide

## Overview

Interactive Mode is a game-changing feature that removes the need for pre-configuring authentication and login sequences. Instead, you manually navigate the website in an open browser while the tool automatically captures locators for each page state.

## The Problem It Solves

Previously, you had to:
- Configure login credentials upfront
- Specify exact CSS selectors for form fields
- Predict all pages you'd visit
- Run crawls non-interactively

Now with Interactive Mode, you:
- Open a real browser
- Navigate naturally through the application
- The tool captures locators on-the-fly
- No configuration needed!

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────┐
│           User Opens Browser (Interactive)           │
│                                                       │
│  ┌─────────────────────────────────────────────┐   │
│  │         Browser Window (Visible)             │   │
│  │  • User clicks links, fills forms, etc.      │   │
│  │  • Full control over navigation              │   │
│  └─────────────────────────────────────────────┘   │
│                      ▲                               │
│                      │ User Actions                  │
│                      │                               │
└──────────────────────┼───────────────────────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   DOM Change Detector         │
       │ (Runs in background)          │
       │ • Compares page hash          │
       │ • Detects new page loads      │
       │ • Detects DOM mutations       │
       └───────────────────────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   Page Snapshot Capture       │
       │ When page changes:            │
       │ • Generate page name          │
       │ • Extract all elements        │
       │ • Store in memory             │
       │ • Auto-name as page_1, etc.   │
       └───────────────────────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   Data Collected Per Page:    │
       │ • Page URL                    │
       │ • Page Title                  │
       │ • All interactive elements    │
       │ • Element attributes          │
       │ • Generated locators          │
       └───────────────────────────────┘
                       │
                       ▼
       ┌───────────────────────────────┐
       │   Export on Finish            │
       │ Browser closed = done         │
       │ • CSV per page                │
       │ • Combined JSON               │
       │ • Excel with sheets           │
       │ • Python code                 │
       │ • Simple text format          │
       └───────────────────────────────┘
```

## Step-by-Step Example: Testing a Login Workflow

### 1. Start Interactive Mode
```bash
python -m src.cli \
  --url "https://demo.example.com/login" \
  --interactive \
  --no-headless \
  --export locators json csv
```

### 2. Browser Opens
- Website loads at the provided URL (login page)
- Tool displays:
```
================================================================================
INTERACTIVE MODE STARTED
================================================================================
Initial URL: https://demo.example.com/login

Instructions:
1. Interact with the website normally (click links, fill forms, etc.)
2. Each page navigation automatically captures locators
3. Close the browser window to finish and export locators
4. Or press Ctrl+C to stop monitoring
================================================================================
```

### 3. Tool Detects Initial Page
```
✓ Captured: login_page (15 elements)
```
The login page is automatically captured with all its elements:
- Username input field
- Password input field
- Login button
- "Remember Me" checkbox
- "Forgot Password" link
- etc.

### 4. You Manually Log In
1. Click on username field
2. Type your credentials
3. Click login button
4. Page navigates to dashboard

### 5. Tool Detects Page Change
```
✓ Captured: dashboard_page (42 elements)
```
A new page state detected! All elements on the dashboard are captured:
- Navigation menu
- Welcome message
- Data tables
- Action buttons
- Filter controls
- etc.

### 6. You Click Around
You decide to test the filtering feature:
1. Click "Apply Filters" button
2. New filter panel appears
3. Tool detects the change:
```
✓ Captured: filter_results_page (38 elements)
```

### 7. Close Browser When Done
1. Simply close the browser window
2. Tool automatically stops monitoring
3. Generates output files:
```
================================================================================
INTERACTIVE MODE COMPLETED
Total pages captured: 3
================================================================================

Pages captured:
  1. login_page: 15 elements
  2. dashboard_page: 42 elements
  3. filter_results_page: 38 elements

Exporting captured pages...

Exported Files:
  ✓ LOCATORS: output/interactive_pages_20260327_132630.txt
  ✓ JSON: output/interactive_pages_20260327_132630.json
  ✓ CSV: output/interactive_pages_20260327_132630.csv
```

## Page Naming Behavior

The tool automatically generates page names based on:

### Priority Order
1. **Page Title** (highest priority)
   - Browser title → `login_page`, `dashboard_page`
   - Spaces replaced with underscores
   - Converted to lowercase
   - Suffix `_page` added

2. **URL Path** (fallback)
   - URL `/profile` → `profile_page`
   - URL `/api/users/list` → `list_page`
   - Takes the last segment of path

3. **Default** (last resort)
   - If no title/URL: `home_page` or `page`

### Name Collision Handling
If you visit the same page twice, the tool adds a counter:
- First visit: `login_page`
- Second visit: `login_page_1`
- Third visit: `login_page_2`

This helps track page states at different points in your workflow.

## DOM Change Detection

The tool monitors for DOM changes using:

### 1. **Page Hash Comparison**
- Generated from page HTML using MD5
- Compares current hash with previous
- Different hash = page changed

### 2. **Polling Interval**
- Checks every 2 seconds (configurable)
- Lightweight operation
- Doesn't interfere with your interaction

### 3. **Triggers*
Change detection occurs on:
- ✅ Full page navigation
- ✅ JavaScript-based page transitions
- ✅ Dynamic content loading
- ✅ DOM mutations from interactions
- ✅ AJAX-based page updates

## Export Formats

### 1. Simple Text Format (.txt)
```
================================================================================
PAGE: Login
================================================================================
URL: https://demo.example.com/login

username_input = //input[@name='username']
password_input = //input[@name='password']
login_btn = //button[@type='submit']
forgot_link = //a[contains(text(), 'Forgot')]

================================================================================
PAGE: Dashboard
================================================================================
URL: https://demo.example.com/dashboard

nav_menu = //nav[@class='sidebar']
user_welcome = //h1[contains(text(), 'Welcome')]
logout_btn = //a[contains(text(), 'Logout')]
```

### 2. JSON Format (.json)
```json
{
  "login_page": {
    "url": "https://demo.example.com/login",
    "title": "Login",
    "element_count": 15,
    "elements": [...]
  },
  "dashboard_page": {
    "url": "https://demo.example.com/dashboard",
    "title": "Dashboard",
    "element_count": 42,
    "elements": [...]
  }
}
```

### 3. CSV Format (.csv)
One CSV file per page with columns:
- Tag, Text, Type, ID, Name, Data-TestID, XPath, CSS Selector, URL

### 4. Excel Format (.xlsx)
- One sheet per page
- Formatted headers
- Auto-sized columns
- Professional appearance

### 5. Python Format (.py)
```python
# Page: Login
login_page = {
    'username_input': '//input[@name="username"]',
    'password_input': '//input[@name="password"]',
    'login_btn': '//button[@type="submit"]',
}

# Page: Dashboard
dashboard_page = {
    'nav_menu': '//nav[@class="sidebar"]',
    'user_welcome': '//h1[contains(text(), "Welcome")]',
    'logout_btn': '//a[contains(text(), "Logout")]',
}
```

## Advanced Usage

### Combining with Standard Mode

Standard mode still supports automation:
```bash
# Standard: Automated crawling with depth
python -m src.cli --url "https://example.com" --depth 3 --export csv

# Interactive: Manual navigation
python -m src.cli --url "https://example.com" --interactive --export json
```

### Performance Metrics

- Polling interval: 2 seconds (adjustable)
- DOM hash calculation: Negligible overhead
- Memory: Stores one snapshot per page
- Browser overhead: Minimal (just monitoring)

### Best Practices

1. **Start at a natural entry point**
   ```bash
   python -m src.cli --url "https://app.com/login" --interactive
   ```

2. **Test complete workflows**
   - Login → Dashboard → Create Item → Edit → Delete
   - Hover effects → Tooltips → Expanded menus

3. **Use descriptive page titles**
   - Sites with clear `<title>` tags get better page names

4. **Export in multiple formats**
   ```bash
   --export locators json csv excel python
   ```

5. **Stay patient during polling**
   - Wait ~2 seconds for changes to register
   - Close browser cleanly (not force-quit)

## Troubleshooting

### Issue: Page not being captured
**Solution:** 
- Wait 2 seconds after action (polling interval)
- Check if page title changed (determines new page)
- Try performing a more distinct navigation

### Issue: Browser hangs
**Solution:**
- Use Ctrl+C to exit gracefully
- Close browser window instead of force-quit
- Check logs in `logs/crawler.log`

### Issue: Duplicate page captures
**Solution:**
- Normal behavior - different page states
- This is a feature, not a bug!
- Helps identify dynamic content changes

### Issue: Elements not captured correctly
**Solution:**
- Some elements might be hidden with CSS
- Verify elements exist using browser DevTools
- Check element visibility settings

## Differences: Interactive Mode vs Standard Mode

| Feature | Interactive | Standard |
|---------|-----------|----------|
| **Browser Control** | You drive it | Automatic crawl |
| **Login Required** | Manual (run login yourself) | Automated with credentials |
| **Pages Captured** | Only visited pages | All reachable pages |
| **Per-Page Tracking** | ✅ Yes | ✅ Can tag by URL |
| **Dynamic Content** | ✅ Captured in real-time | Depends on config |
| **User Interaction** | Required | Not needed |
| **Typical Use Case** | Quick locator testing | Comprehensive crawls |

## When to Use Interactive Mode

✅ **Use Interactive Mode When:**
- You're building new tests and need quick locators
- You want to verify locators work as you navigate
- Testing dynamic/JavaScript-heavy sites
- Need to capture page states at specific points
- Don't want to configure login automation
- Testing multi-step user workflows
- Exploring a new application

❌ **Use Standard Mode When:**
- Need complete site coverage
- Pages are statically linked
- Want fully automated process
- Have stable page structure
- Need recursive crawling
- Testing on CI/CD pipelines

## Examples

See [README.md](README.md) for complete examples including:
- Testing login flows
- Testing dynamic interactions  
- Multi-step workflow testing
- Comparing with standard mode

## Questions?

Refer to [README.md](README.md) for full documentation and [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) for standard mode authentication.
