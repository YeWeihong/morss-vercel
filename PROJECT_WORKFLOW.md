# Morss Project Workflow Documentation

> **Related Documentation**: To learn how to use custom XPath rules to create feeds from any webpage, see **[XPATH_CUSTOM_FEEDS.md](XPATH_CUSTOM_FEEDS.md)**

## Project Overview

Morss is a tool for obtaining full-text RSS feeds. Its main function is to extract links from simplified RSS feeds on the web, visit those links to fetch complete article content, and put the full content back into the RSS feed.

## Core Workflow

### 1. Data Flow Process

```
User Request → FeedFetch (Fetch Feed) → FeedGather (Fill Content) → FeedFormat (Format Output) → Return Complete Feed
```

#### 1.1 FeedFetch Stage (Feed Acquisition)
- **Input**: RSS feed URL
- **Processing**:
  - Downloads RSS feed using `crawler.adv_get()`
  - Supports multiple feed formats: RSS 2.0, Atom, RDF
  - Can generate feeds from HTML/JSON pages based on custom rules (`feedify.ini` config)
  - Supports caching mechanism to avoid redundant downloads
- **Output**: Parsed feed object (containing title, description, article list, etc.)

#### 1.2 FeedGather Stage (Content Filling)
- **Input**: Feed object
- **Processing**:
  - Iterates through each article entry in the feed
  - Uses `crawler.adv_get()` to visit each article's link
  - Uses `readabilite` module to extract main article content (based on content analysis algorithm)
  - Supports concurrent fetching with time and quantity limits (to prevent overload)
  - Caches processed article content
- **Output**: Feed object filled with complete content

#### 1.3 FeedFormat Stage (Format Output)
- **Input**: Complete feed object
- **Processing**: Converts based on user-selected format
- **Output Format Support**:
  - RSS/Atom XML
  - JSON
  - CSV
  - HTML

### 2. Code Architecture

```
morss/
├── __main__.py       # Entry point: Detects run mode (CLI/Web server/CGI)
├── morss.py          # Core logic: FeedFetch, FeedGather, FeedFormat
├── crawler.py        # HTTP request handling: Downloads web content, handles redirects, caching, etc.
├── feeds.py          # Feed parsing: Supports parsing and generation of multiple formats
├── readabilite.py    # Content extraction: Extracts main article content from HTML pages
├── caching.py        # Cache system: Supports memory, Redis, disk cache
├── cli.py            # Command-line interface
├── wsgi.py           # Web server interface
└── feedify.ini       # Custom rule configuration: Defines scraping rules for specific websites
```

### 3. Data Transmission Details

#### 3.1 HTTP Request Handling (crawler.py)
- Uses Python standard library `urllib` for HTTP requests
- Supports the following features:
  - Automatic gzip compression handling
  - Follows HTTP redirects (301/302)
  - Handles various character encodings (auto-detection using `chardet`)
  - Random User-Agent (to avoid blocking)
  - Cookie support
  - HTTP caching (ETag, Last-Modified)

#### 3.2 Content Extraction (readabilite.py)
- Uses heuristic algorithm to identify article body:
  - Scores based on HTML tag weights
  - Excludes ads, sidebars, comments, and other irrelevant content
  - Preserves meaningful tags (paragraphs, headings, images, etc.)
  - Calculates content density to determine main content area

#### 3.3 Caching Mechanism (caching.py)
- Three cache backends:
  1. **Memory cache** (default): In-process dictionary, lost after restart
  2. **Redis cache**: Requires external Redis service
  3. **Disk cache**: Uses `diskcache` library, persisted to local disk
- Cached content includes:
  - HTTP responses (avoid redundant downloads)
  - Extracted article content
  - Feed parsing results

## External Dependency Analysis

### 1. Required Python Dependencies (Locally Installed)
These dependencies are downloaded locally during Docker build or pip install, **do not depend on external services**:

```python
# Extracted from setup.py
install_requires = [
    'lxml',              # XML/HTML parsing
    'bs4',               # BeautifulSoup, HTML parsing helper
    'python-dateutil',   # Date-time parsing
    'chardet'            # Character encoding detection
]

extras_require = {
    'full': [
        'redis',         # Redis cache client (optional)
        'diskcache',     # Disk cache (optional)
        'gunicorn',      # High-performance HTTP server (optional)
        'setproctitle'   # Process title setting (optional)
    ]
}
```

### 2. Runtime Network Dependencies

#### 2.1 Required External Resources
When Morss runs, it needs to access:
- **Target RSS feeds**: The RSS/Atom feed URLs you want to process
- **Article source websites**: Websites that article links in the feed point to

**These dependencies are functional and unavoidable** because Morss's core functionality is to fetch content from these websites.

#### 2.2 No Dependency on External Services
Morss **does not depend** on any of the following external services:
- ✅ No need to access morss.it official server
- ✅ No need to access any API services
- ✅ No need for third-party content extraction services
- ✅ No need for cloud services or CDN
- ✅ Does not use external databases

### 3. Docker Deployment Analysis

Looking at the Dockerfile:
```dockerfile
FROM alpine:edge                    # Base image (one-time download)

ADD . /app                          # Copy source code to container

RUN set -ex; \
    apk add --no-cache --virtual .run-deps python3 py3-lxml py3-setproctitle py3-setuptools; \
    apk add --no-cache --virtual .build-deps py3-pip py3-wheel; \
    pip3 install --no-cache-dir /app[full]; \
    apk del .build-deps                # Install dependencies from package manager during build

USER 1000:1000
ENTRYPOINT ["/bin/sh", "/app/morss-helper"]
CMD ["run"]
```

**Docker Deployment Dependencies**:
- Base image and dependency packages are downloaded from Alpine repository and PyPI during **build time**
- After build completion, the container runs **completely self-contained**, no need to download again
- All dependencies are packaged in the image

## Local Deployment Autonomy

### ✅ Scenarios Where It Can Run Completely Autonomously

1. **All dependencies are in the container/environment**
   - Docker image includes all runtime dependencies after build
   - No need to connect to external services to run core functionality

2. **Cache mechanism guarantee**
   - Using disk cache can persist fetched content
   - Cache remains valid after restart
   - Can use cached content in offline mode (`--cache` parameter)

3. **Localized core algorithms**
   - Content extraction algorithm (readabilite) runs completely locally
   - RSS parsing is done locally
   - Does not depend on cloud APIs or third-party services

### ⚠️ Scenarios Still Requiring Network Access

1. **Fetching new content**
   - Must access target RSS feeds
   - Must access article source websites
   - This is a functional requirement and unavoidable

2. **Potential risks**
   - If target website shuts down, that feed cannot be updated (but cached content remains available)
   - If website changes HTML structure, readabilite may need rule adjustments
   - If website blocks your IP, proxy configuration may be needed

### 🔧 Recommendations to Enhance Autonomy

1. **Use disk cache**
   ```bash
   docker run -p 8000:8000 -e CACHE=diskcache -v /home/user/morss-cache:/cache morss
   ```

2. **Adjust cache strategy**
   ```bash
   # Increase cache size and retention time
   -e CACHE_SIZE=10737418240  # 10GB
   -e LIM_ITEM=-1              # No limit on cached articles
   ```

3. **Use cached content in offline mode**
   ```bash
   morss --cache http://example.com/feed.xml
   ```

4. **Regularly backup cache data**
   - Cache directory contains all extracted article content
   - Can be backed up regularly to prevent data loss

## Summary

### Project Flow Diagram

```
                           ┌─────────────────┐
                           │  User Request   │
                           │   (RSS URL)     │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │   FeedFetch     │
                           │  (Fetch Feed)   │
                           │  - Download RSS │
                           │  - Parse format │
                           │  - Check cache  │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │   FeedGather    │
                           │ (Fill Content)  │
                           │  - Visit links  │
                           │  - Extract text │
                           │  - Cache content│
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │   FeedFormat    │
                           │ (Format Output) │
                           │  - RSS/JSON     │
                           │  - CSV/HTML     │
                           └────────┬────────┘
                                    │
                           ┌────────▼────────┐
                           │  Return Result  │
                           └─────────────────┘
```

### Key Points

1. **High Autonomy**: Core functionality is completely localized, does not depend on third-party APIs
2. **Network Required**: Must access target RSS sources and article websites (functional requirement)
3. **Persistable**: Can save fetched content through disk cache
4. **Strong Fault Tolerance**: Supports offline mode using cache
5. **Open Source Freedom**: AGPLv3 license, free to modify and deploy

### Dependency Risk Assessment

| Dependency Type | Risk Level | Description |
|----------------|-----------|-------------|
| Python dependency packages | Low | Packaged in container, unless PyPI completely disappears (unlikely) |
| Target RSS sources | Medium | If source website closes, that source is unavailable, but doesn't affect other sources |
| Article source websites | Medium | Cannot fetch new content after website closure, but cached content remains available |
| Morss official service | None | Local deployment does not depend on official servers |
| Third-party APIs | None | Does not use any third-party API services |

### Worst Case Scenario Analysis

**If the original author stops maintaining and all related websites close**:
- ✅ Your local deployment can still run
- ✅ Cached article content remains accessible
- ✅ Can continue processing any accessible RSS feeds
- ✅ Code is open source, can maintain and modify yourself
- ❌ Cannot fetch new feed content (unless target websites are still online)
- ❌ If target websites undergo major redesigns, extraction rules may need adjustment

**Conclusion**: Locally deployed Morss instances are **highly autonomous** and will not fail due to the original project stopping maintenance.
