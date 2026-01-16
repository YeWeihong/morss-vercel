# Morss Custom XPath Rules Guide

## Overview

Morss supports creating RSS feeds from any webpage using custom XPath rules to extract content. This powerful feature allows you to create feeds for websites that don't offer RSS.

## What is XPath?

XPath (XML Path Language) is a language for finding information in XML/HTML documents. It uses path expressions to select nodes or node sets.

### Basic XPath Syntax

```xpath
/           # Select from root node
//          # Select nodes anywhere in the document
.           # Select current node
..          # Select parent of current node
@           # Select attributes

# Examples:
//div                    # Select all div elements
//div[@class="title"]    # Select all div elements with class="title"
//a/@href                # Select href attribute of all a elements
//div[@id="content"]//p  # Select all p elements inside div with id="content"
```

## Morss Custom Feed Parameters

### Required Parameter

#### `--items` (Required)
This is the **only required parameter** that activates the custom feed function. It defines how to find each "entry" (article/item) on the page.

**XPath rule**: XPath expression to match all RSS entries

**Examples**:
```bash
# Match all elements with class containing "title"
--items="//div[contains(@class, 'title')]"

# Match all divs with exactly class="post"
--items="//div[@class='post']"

# Match all article elements inside div with id="main"
--items="//div[@id='main']//article"
```

### Optional Parameters

#### `--item_link`
Defines how to extract the link from each entry.

**Default**: `(.|.//a|ancestor::a)/@href` (href of current node, or child a, or ancestor a)

**Examples**:
```bash
--item_link=".//a/@href"              # First link in entry
--item_link=".//@data-url"            # data-url attribute
--item_link=".//h2/a/@href"           # Link within h2 tag
```

#### `--item_title`
Defines how to extract the entry title.

**Default**: `.` (text content of current node)

**Examples**:
```bash
--item_title="./h2"                   # h2 tag text
--item_title=".//span[@class='name']" # span with class=name
--item_title="./a"                    # First link text
```

#### `--item_content`
Defines how to extract entry detailed content.

**Default**: None (if not specified, morss will try to extract full content from the link page)

**Examples**:
```bash
--item_content=".//div[@class='summary']"  # Summary div
--item_content="./p"                       # Paragraph
```

#### `--item_time`
Defines how to extract entry publication time.

**Default**: None

Morss supports various time formats and will auto-parse.

**Examples**:
```bash
--item_time=".//span[@class='date']"     # Date text
--item_time=".//@data-timestamp"          # Timestamp attribute
```

#### `--mode`
Specifies parser type.

**Options**: `xml`, `html`, `json`

**Default**: Auto-detect

- `html`: For regular HTML pages (most common)
- `xml`: For XML formatted data
- `json`: For JSON formatted data

#### Feed-level Parameters

These parameters define the entire feed's metadata:

- `--title`: Feed title (default: `//head/title`)
- `--desc`: Feed description (default: `//head/meta[@name="description"]/@content`)

## Web Server URL Format

When accessing morss via HTTP, parameters are passed through the URL in this format:

```
http://morss.example.com/:param1:param2=value/TARGET_URL
```

### URL Encoding Rules

1. **Slash Replacement**: In URLs, `/` must be replaced with `|` (pipe)
   - Reason: `/` has special meaning in URL paths
   - morss automatically converts `|` back to `/`

2. **URL Encoding**: Special characters need URL encoding
   - `[` → `%5B`
   - `]` → `%5D`
   - `=` → `%3D`
   - `"` → `%22`
   - space → `%20`

### Real Example Analysis

User-provided example:
```
https://morss.it/:items=%7C%7C*[class=title]/https://www.163.com/dy/media/T1486465837470.html
```

**Decoding process**:

1. **URL decode**: `%7C%7C*[class=title]` → `||*[class=title]`
2. **Pipe to slash**: `||*[class=title]` → `//*[class=title]`
3. **Final XPath**: `//*[class=title]`

**Meaning**:
- `//*`: Select any element in the document
- `[class=title]`: Elements with class attribute containing "title"

In HTML mode, morss automatically optimizes `[class=title]` to a more precise match:
```xpath
[@class and contains(concat(" ", normalize-space(@class), " "), " title ")]
```

This correctly matches cases like `class="post title"` or `class="title featured"`.

## Complete Examples

### Example 1: Simple Blog Feed

Given blog HTML structure:
```html
<div id="posts">
    <article class="post">
        <h2><a href="/post/1">Article Title 1</a></h2>
        <p class="summary">Article summary...</p>
        <span class="date">2024-01-01</span>
    </article>
    <article class="post">
        <h2><a href="/post/2">Article Title 2</a></h2>
        <p class="summary">Article summary...</p>
        <span class="date">2024-01-02</span>
    </article>
</div>
```

**CLI command**:
```bash
morss \
  --items="//article[@class='post']" \
  --item_title="./h2/a" \
  --item_link="./h2/a/@href" \
  --item_content="./p[@class='summary']" \
  --item_time="./span[@class='date']" \
  --mode=html \
  https://example.com/blog
```

**Web URL** (with URL encoding):
```
https://morss.it/:items=%7C%7Carticle%5B%40class%3D%27post%27%5D:item_title=.%7Ch2%7Ca:item_link=.%7Ch2%7Ca%7C%40href:item_content=.%7Cp%5B%40class%3D%27summary%27%5D:item_time=.%7Cspan%5B%40class%3D%27date%27%5D:mode=html/https://example.com/blog
```

### Example 2: List Page

Given news website structure:
```html
<div class="news-list">
    <div class="news-item">
        <a href="/news/1" class="title">News Title 1</a>
    </div>
    <div class="news-item">
        <a href="/news/2" class="title">News Title 2</a>
    </div>
</div>
```

**CLI command**:
```bash
morss \
  --items="//div[@class='news-item']" \
  --item_title=".//a[@class='title']" \
  --item_link=".//a[@class='title']/@href" \
  --mode=html \
  https://example.com/news
```

**Web URL**:
```
https://morss.it/:items=%7C%7Cdiv%5B%40class%3D%27news-item%27%5D:item_title=.%7C%7Ca%5B%40class%3D%27title%27%5D:item_link=.%7C%7Ca%5B%40class%3D%27title%27%5D%7C%40href:mode=html/https://example.com/news
```

### Example 3: Class Shorthand

Morss supports simplified class matching syntax (HTML mode only):

**Standard XPath**:
```xpath
//div[@class and contains(concat(" ", normalize-space(@class), " "), " post ")]
```

**Morss shorthand**:
```xpath
//div[class=post]
```

**User's example**:
```
:items=||*[class=title]
```
Equivalent to standard XPath:
```xpath
//*[@class and contains(concat(" ", normalize-space(@class), " "), " title ")]
```

## Debugging Tips

### 1. Use Browser DevTools

1. Open target webpage
2. Press F12 to open DevTools
3. Click element selector (or Ctrl+Shift+C)
4. Click content you want to extract
5. Right-click highlighted HTML element in DevTools
6. Select "Copy" → "Copy XPath" or "Copy full XPath"

**Note**: Browser-generated XPath is usually very long and needs simplification.

### 2. Test XPath Expressions

Test XPath in browser console:
```javascript
// Test if XPath matches elements
$x("//div[@class='post']")

// Check number of matched elements
$x("//div[@class='post']").length

// View first matched element
$x("//div[@class='post']")[0]
```

### 3. Use morss Debug Mode

```bash
# Set DEBUG environment variable
DEBUG=1 morss --items="//div[@class='post']" https://example.com

# Or via Web URL
https://morss.it/:debug:items=...
```

### 4. Incremental Rule Building

1. Set only `--items` first, ensure entries are matched
2. Add `--item_title`
3. Add `--item_link`
4. Finally add `--item_content` and `--item_time`

## Common XPath Patterns

### Selector Patterns

```xpath
# Select by ID
//div[@id='content']

# Select by class (exact match)
//div[@class='post']

# Select by class (contains)
//div[contains(@class, 'post')]

# Select by class (Morss HTML shorthand)
//div[class=post]

# Select by attribute
//div[@data-id='123']

# Select by text content
//div[contains(text(), 'keyword')]

# Select first child
//div[@class='list']/*[1]

# Select last child
//div[@class='list']/*[last()]

# Select first 3 elements
//div[@class='list']/*[position() <= 3]
```

### Combination Selectors

```xpath
# Parent-child (direct child)
//div[@class='parent']/div[@class='child']

# Descendant (any level)
//div[@class='parent']//div[@class='descendant']

# Sibling (following)
//div[@class='first']/following-sibling::div[1]

# Multiple conditions (AND)
//div[@class='post' and @data-status='published']

# Multiple conditions (OR)
//div[@class='post' or @class='article']
```

### Data Extraction

```xpath
# Extract text content
//div[@class='title']              # Returns element (morss extracts text)
//div[@class='title']/text()       # Directly returns text

# Extract attributes
//a/@href                          # Link URL
//img/@src                         # Image URL
//div/@data-id                     # Custom attribute

# Extract first match
(//div[@class='post'])[1]

# Extract from current node (relative path)
.//a/@href                         # Link under current node
./h2                               # Direct child h2
../div                             # Sibling div
```

## XPath Functions

Morss supports common XPath functions:

```xpath
# String functions
contains(@class, 'post')           # Contains check
starts-with(@class, 'post')        # Starts with check
normalize-space(text())            # Trim whitespace
concat('a', 'b')                   # String concatenation

# Position functions
position()                         # Current position
last()                             # Last position
count(//div)                       # Count

# Logic functions
not(@class)                        # Negation
```

## Advanced Techniques

### 1. Handle Dynamic Class Names

If class names contain dynamic parts (e.g., `post-123`):
```xpath
//div[starts-with(@class, 'post-')]
//div[contains(@class, 'post-')]
```

### 2. Exclude Elements

```xpath
# Exclude divs with class 'ad'
//div[@class='post' and not(contains(@class, 'ad'))]

# Exclude items containing specific child elements
//div[@class='post' and not(.//div[@class='sponsored'])]
```

### 3. Select Multiple Element Types

```xpath
# Select all h1, h2, h3
//*[self::h1 or self::h2 or self::h3]

# Select all article and div.post
//article | //div[@class='post']
```

### 4. Handle Namespaces

If HTML uses XML namespaces (uncommon), use prefixes:
```xpath
//atom:entry        # Atom format
//rdf:item          # RDF format
```

Morss has predefined common namespaces (see `NSMAP` in `feeds.py`).

## Troubleshooting

### Issue: XPath doesn't match any elements

**Solutions**:
1. Check HTML structure matches expectations (use browser DevTools)
2. Confirm correct `--mode` parameter (HTML pages should use `html` mode)
3. Try simpler XPath expressions for debugging
4. Check if content is JavaScript-loaded (morss only accesses initial HTML)

### Issue: URL-encoded XPath doesn't work

**Solutions**:
1. Ensure `/` is replaced with `|`
2. Use online URL encoding tool for special characters
3. Test with CLI command first to verify XPath correctness
4. Copy-paste complete URL in browser (don't type manually)

### Issue: Extracted content incomplete or contains extra content

**Solutions**:
1. Use more precise XPath (add more constraints)
2. Adjust relative paths (use `./` to limit to current node)
3. Use `text()` to extract only text content
4. Consider using `--item_content` to let morss extract full content from link page

### Issue: Time format not recognized

**Solutions**:
1. Morss supports many time formats, but special formats may fail
2. Ensure extracting time text, not elements with other content
3. Check if extracting correct attribute (e.g., `@datetime` vs `text()`)

## Predefined Rules

Morss has predefined rules for common websites in `feedify.ini`, including:

- Twitter
- Google Search
- DuckDuckGo Search
- Standard RSS/Atom formats

You can reference these rules to learn how to write custom rules:

```bash
# View predefined rules
cat /path/to/morss/morss/feedify.ini
```

## Further Learning

### XPath Tutorial Resources

- [W3Schools XPath Tutorial](https://www.w3schools.com/xml/xpath_intro.asp)
- [MDN XPath Documentation](https://developer.mozilla.org/en-US/docs/Web/XPath)
- [XPath Online Tester](https://www.freeformatter.com/xpath-tester.html)

### Practice Recommendations

1. Start with simple websites
2. Test XPath in browser console first
3. Debug with CLI mode, convert to Web URL after confirmation
4. Save successful rule configurations for future use

## Summary

XPath custom feeds is one of Morss's most powerful features, allowing you to:

✅ Create RSS feeds for any website
✅ Precisely control what content to extract
✅ Combine multiple data sources
✅ Filter and transform content

Key Points:
1. `--items` is the only required parameter
2. In Web URLs, `/` must be replaced with `|`
3. Special characters need URL encoding
4. HTML mode supports simplified class matching syntax
5. Use browser DevTools to help write XPath

By mastering XPath rules, you can create custom RSS feeds for almost any website!
