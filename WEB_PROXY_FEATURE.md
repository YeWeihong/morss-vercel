# Web Proxy Prefix Feature

## Overview

The Web Proxy Prefix feature allows you to use web proxy wrappers (like `https://sitedl.westpan.me/123/https/target.com/`) to access blocked sites while correctly resolving relative URLs extracted from the page.

## Problem Statement

When using web proxy wrappers to access blocked sites:
- The scraper extracts relative links from HTML using XPath (e.g., `/article/123.html`)
- Standard URL resolution with `urljoin()` can break when using a web proxy
- It might resolve to `https://sitedl.westpan.me/article/123.html` instead of `https://sitedl.westpan.me/123/https/target.com/article/123.html`

## Solution

The `web_proxy` parameter allows you to specify a web proxy prefix that will be concatenated with relative links instead of using standard URL resolution.

## Usage

### API Parameter

Add the `web_proxy` parameter to your morss request URL:

```
https://your-morss-instance.vercel.app/:web_proxy=https://proxy.com/view/http://target.com/https://target.com/feed.xml
```

### Example Scenarios

#### Scenario 1: Basic Web Proxy Usage

**Input:**
- `web_proxy`: `https://proxy.com/view/http://target.com`
- Extracted link: `/foo/bar.html`

**Result:**
```
https://proxy.com/view/http://target.com/foo/bar.html
```

#### Scenario 2: Complex Proxy with Path

**Input:**
- `web_proxy`: `https://sitedl.westpan.me/123/https/t66y.com`
- Extracted link: `/article/123.html`

**Result:**
```
https://sitedl.westpan.me/123/https/t66y.com/article/123.html
```

#### Scenario 3: Absolute URLs with Web Proxy

**Input:**
- `web_proxy`: `https://proxy.com/view/http://target.com`
- Extracted link: `http://example.com/article/123.html` (absolute URL)

**Result:**
```
http://example.com/article/123.html
```
*Note: Absolute URLs are preserved unchanged to avoid breaking external links*

#### Scenario 4: Without Web Proxy (Standard Behavior)

**Input:**
- No `web_proxy` parameter
- Feed URL: `http://target.com/feed`
- Extracted link: `/article/123.html`

**Result:**
```
http://target.com/article/123.html
```

## Implementation Details

### Code Location

The implementation is in `morss/morss.py`:

1. **Helper Function:** `web_proxy_join(web_proxy, relative_link)` (Public API)
   - Concatenates web proxy prefix with relative links
   - Handles double slashes properly
   - Ensures proper slash formatting
   - Can be imported and used directly: `from morss.morss import web_proxy_join`

2. **Modified Function:** `ItemFix(item, options, feedurl='/')`
   - Checks for `options.web_proxy`
   - Uses `urlparse()` to determine if link is relative (no scheme)
   - Applies `web_proxy_join()` only for relative URLs when web_proxy is provided
   - Preserves absolute URLs unchanged
   - Falls back to standard `urljoin()` when web_proxy is not provided

### Slash Handling

The `web_proxy_join()` function handles various slash scenarios:

- Trailing slash in proxy: `https://proxy.com/` → removes it
- Leading slash in link: ensures it's present
- Prevents double slashes in the concatenated result

## Testing

The feature includes comprehensive test coverage in `tests/test_web_proxy.py`:

- ✓ Basic concatenation
- ✓ Trailing slash handling
- ✓ Leading slash handling
- ✓ Double slash prevention
- ✓ Complex proxy URLs
- ✓ Integration with ItemFix function
- ✓ Standard behavior without web_proxy
- ✓ Absolute link handling

All 8 tests pass, and all 85 existing tests continue to pass.

## Technical Notes

### URL Parameter Encoding

When passing the `web_proxy` parameter in a URL, ensure proper encoding:

```bash
# Use URL encoding for special characters
web_proxy=https%3A%2F%2Fproxy.com%2Fview%2Fhttp%3A%2F%2Ftarget.com
```

Or use the pipe character (`|`) instead of forward slash (`/`) for backward compatibility:

```bash
# Using pipes (automatically converted by parse_options)
web_proxy=https:||proxy.com|view|http:||target.com
```

### Limitations

- The feature assumes relative links start with `/` or can be prefixed with `/`
- The web_proxy is only applied to relative URLs (URLs without a scheme like `http://`)
- Absolute URLs are preserved unchanged to avoid breaking external links
- Users should only use this feature when accessing sites through web proxies

## Examples

### CLI Usage

```bash
python -m morss :web_proxy=https://proxy.com/view/http://target.com https://target.com/feed.xml
```

### HTTP Request

```
GET /:web_proxy=https://proxy.com/view/http://target.com/https://target.com/feed.xml
```

### Multiple Parameters

```
GET /:web_proxy=https://proxy.com/view/http://target.com:md=True/https://target.com/feed.xml
```

## Backward Compatibility

The feature is fully backward compatible:
- When `web_proxy` is not provided, standard URL resolution is used
- All existing functionality remains unchanged
- No breaking changes to the API
