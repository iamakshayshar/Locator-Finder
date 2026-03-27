# Interactive Mode - Quick Reference

## 30-Second Summary

**Interactive Mode = Open browser + Manually navigate + Tool captures locators automatically**

Start interactive mode:
```bash
python -m src.cli --url "https://example.com" --interactive --export locators
```

Then:
1. Navigate your site manually in the browser that opens
2. Tool automatically detects page changes
3. Each unique page is captured with all its locators
4. Close the browser when done
5. All pages exported to files

## Common Commands

### Basic Interactive Mode
```bash
python -m src.cli --url "https://example.com" --interactive
```

### With GUI (Non-Headless)
```bash
python -m src.cli --url "https://example.com" --interactive --no-headless
```

### Export As Text (Simple Format)
```bash
python -m src.cli --url "https://example.com" --interactive --export locators
```

### Export Multiple Formats
```bash
python -m src.cli \
  --url "https://example.com" \
  --interactive \
  --export locators json csv excel python
```

### With Verbose Logging
```bash
python -m src.cli --url "https://example.com" --interactive --verbose
```

### Custom Output Directory
```bash
python -m src.cli \
  --url "https://example.com" \
  --interactive \
  --output my_locators/results.csv \
  --export json
```

## What Gets Captured

For each page, the tool captures:
- ✅ Page URL
- ✅ Page title
- ✅ All interactive elements (buttons, inputs, links, etc.)
- ✅ Element IDs, classes, names, attributes
- ✅ Generated XPath and CSS selectors
- ✅ Timestamp of capture

## Output Files

Example with `--export locators json csv`:

```
output/
├── login_page_locators_20260327_120000.txt
├── dashboard_page_locators_20260327_120005.txt
├── interactive_pages_20260327_120010.json
└── interactive_pages_20260327_120010.csv
```

## Page Names Auto-Generated From

1. Browser `<title>` tag (e.g., "Login Page" → `login_page`)
2. URL path (e.g., `/dashboard` → `dashboard_page`)  
3. Default: `home_page`

Duplicates auto-numbered: `page`, `page_1`, `page_2`

## Real-World Example

### Test a checkout flow:
```bash
python -m src.cli \
  --url "https://store.example.com/products" \
  --interactive \
  --export json csv
```

Page sequence captured:
```
✓ Captured: products_page (28 elements)
✓ Captured: product_details_page (15 elements)  
✓ Captured: cart_page (12 elements)
✓ Captured: checkout_page (20 elements)
✓ Captured: billing_page (18 elements)
✓ Captured: order_confirmation_page (8 elements)
```

All pages automatically exported with locators!

## Key Differences from Standard Mode

| Aspect | Interactive | Standard |
|--------|:-----------:|:--------:|
| Manual navigation | ✅ | ❌ |
| Automated login | ❌ | ✅ |
| Real browser display | ✅ | ❌ |
| Recursive crawl | ❌ | ✅ |
| Per-page organization | ✅ | Partial |
| Requires user input | ✅ | ❌ |

## Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Stop interactive mode | `Ctrl+C` |
| Close browser | Just close the window |

## Tips & Tricks

1. **Wait 2 seconds** between actions so DOM change detector registers
2. **Use `--verbose`** to see detailed logging while navigating
3. **Export to Python** for direct use in test automation:
   ```bash
   --export python
   ```
   Creates file with variables:
   ```python
   login_page = { 'username': '//input[@name="username"]', ... }
   ```

4. **Start from entry point** (login page, home, etc.)

5. **Test natural workflows** - mimic real user behavior

## Troubleshooting Quick Fixes

| Problem | Fix |
|---------|-----|
| Page not captured | Wait 2 sec, then interact again |
| Browser won't open | Remove `--headless` or try `--no-headless` |
| Stuck / frozen | Press `Ctrl+C` to exit |
| Missing elements | Some elements may be hidden; check DOM |
| Odd page naming | Pages named from `<title>` tag; check source |

## Integration with Test Automation

Once you export to Python:

```bash
python -m src.cli --url "https://myapp.com" --interactive --export python
```

Use in your test:
```python
from output.interactive_pages_20260327_120000 import login_page, dashboard_page

# In your Selenium test
driver.find_element_by_xpath(login_page['username']).send_keys("test@example.com")
driver.find_element_by_xpath(login_page['password']).send_keys("password")
driver.find_element_by_xpath(login_page['login_btn']).click()
```

Perfect for rapid test development!

## For More Info

- Full guide: [INTERACTIVE_MODE_GUIDE.md](INTERACTIVE_MODE_GUIDE.md)
- Standard mode: [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)
- General docs: [README.md](README.md)
