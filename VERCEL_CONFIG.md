# Vercel Deployment Configuration

This project is configured to deploy on Vercel using the following files:

## Configuration Files

### 1. `vercel.json`
The main Vercel configuration file that defines:
- **Build**: Uses `@vercel/python` to build the `api/index.py` serverless function
- **Routes**: Routes all requests to the Python serverless function
- **Environment Variables**: Sets default performance limits for Vercel's 10-second timeout

### 2. `runtime.txt`
Specifies Python 3.9 as the runtime version. This ensures compatibility with all dependencies.

### 3. `requirements.txt`
Lists Python dependencies with version constraints:
- `lxml>=4.6.0,<7.0.0` - XML processing
- `beautifulsoup4>=4.9.0` - HTML parsing
- `python-dateutil>=2.8.0` - Date handling
- `chardet>=4.0.0` - Character encoding detection

### 4. `.vercelignore`
Excludes unnecessary files from deployment:
- Tests, Docker files, documentation (except essential docs)
- Build artifacts, cache files
- Development tools and CI/CD configs for other platforms

### 5. `api/index.py`
The serverless function entry point that:
- Imports the WSGI application from `morss.wsgi`
- Exposes it as both `app` and `handler` for Vercel compatibility
- Handles all HTTP requests (both RSS feeds and static files)

## How It Works

1. **Request Flow**: All requests → Vercel → `api/index.py` → WSGI application
2. **Static Files**: The WSGI middleware (`cgi_file_handler`) serves files from the `www/` directory
3. **RSS Processing**: The main application processes RSS feed URLs and returns full-text feeds
4. **Environment**: Serverless function runs with Python 3.9 and limited memory/time

## Environment Variables

The following environment variables are configured in `vercel.json`:

- `MAX_ITEM=30` - Maximum number of articles to fetch
- `MAX_TIME=20` - Maximum time (seconds) for fetching articles
- `TIMEOUT=8` - HTTP request timeout (seconds)
- `LIM_TIME=25` - Total processing time limit (seconds)
- `LIM_ITEM=50` - Maximum total items to process

These values are optimized for Vercel's Hobby plan (10-second timeout).

## Deployment

### Quick Deploy
Click the button in README.md or use:
```bash
vercel
```

### Production Deploy
```bash
vercel --prod
```

## Vercel Limitations

- **Execution Time**: 10 seconds for Hobby plan (configurable values prevent timeout)
- **Memory**: 1024 MB (sufficient for typical RSS feeds)
- **Stateless**: Each request runs in a fresh container (caching requires external Redis)

## Troubleshooting

### Build Fails
- Check that `lxml` builds successfully (may take time)
- Ensure Python version is 3.9 or compatible

### Function Timeout
- Reduce `MAX_ITEM` and `MAX_TIME` in Vercel dashboard
- Consider upgrading to Pro plan for 60-second timeout

### Static Files Not Loading
- All static files are served by the WSGI application
- Files must exist in the `www/` directory
- Check `cgi_file_handler` middleware in `morss/wsgi.py`

## Testing Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the WSGI application
python main.py

# Test in browser
open http://localhost:8000
```

## Further Reading

- [VERCEL_DEPLOYMENT_CN.md](VERCEL_DEPLOYMENT_CN.md) - Detailed deployment guide (Chinese)
- [README.md](README.md) - Project overview
- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
