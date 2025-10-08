# Building a Custom MCP Server on Databricks Apps: Learnings and Best Practices

## Overview
This document captures the complete journey of building a You.com MCP (Model Context Protocol) server and deploying it as a Databricks App. The project involved converting from Node.js to Python, debugging API authentication issues, and learning the nuances of the FastMCP framework.

## Starting Point
- **Initial Repository**: Cloned a Node.js-based You.com MCP server template
- **Goal**: Deploy as a Databricks App to integrate with AI Playground
- **Challenge**: The Node.js implementation wasn't compatible with Databricks Apps deployment pattern

## Major Framework Shift: Node.js → Python

### Why We Changed
The quicksizer-mcp example (a working Databricks App MCP server) was Python-based using FastMCP. After multiple deployment failures with Node.js, we decided to follow the proven pattern.

### Key Architectural Decisions

#### 1. Package Structure
```
youdotcom_MCP/
├── src/
│   └── youcom_mcp_server/
│       ├── __init__.py
│       ├── app.py          # MCP server and FastAPI integration
│       └── main.py         # Uvicorn entry point
├── pyproject.toml          # Package definition with entry points
├── app.yaml                # Databricks Apps configuration
└── requirements.txt        # Minimal (just uv)
```

**Why this structure?**
- Databricks Apps needs a clear entry point defined in `pyproject.toml`
- The `[project.scripts]` section allows `uv run youcom-mcp-server` to work
- FastAPI integration is required for HTTP transport in Databricks

#### 2. pyproject.toml Configuration
```toml
[project]
name = "youcom-mcp-server"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "mcp[cli]>=1.10.0",
    "uvicorn>=0.34.0",
    "httpx>=0.28.0",
]

[project.scripts]
youcom-mcp-server = "youcom_mcp_server.main:main"
```

**Critical Insight**: The entry point script name must match what's used in `app.yaml` command.

#### 3. FastMCP Integration Pattern
```python
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI

# Create MCP server
mcp = FastMCP("You.com MCP Server")

# Define tools
@mcp.tool()
async def web_search(query: str) -> Dict[str, Any]:
    # Tool implementation
    pass

# Create streamable HTTP app for MCP
mcp_app = mcp.streamable_http_app()

# Create FastAPI app with MCP lifespan
app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)

# Mount MCP app to FastAPI
app.mount("/", mcp_app)
```

**Key Points**:
- Use `streamable_http_app()` NOT `get_asgi_app()` (doesn't exist)
- FastAPI lifespan must call `mcp.session_manager.run()`
- Mount the MCP app at root path

#### 4. Main Entry Point
```python
import uvicorn

def main():
    uvicorn.run(
        "youcom_mcp_server.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```

**Why Uvicorn?**: Databricks Apps expects a long-running HTTP server, not a command-line tool.

## Issues Encountered and Solutions

### Issue 1: RuntimeWarning with python -m mcp.server.streamable_http
**Problem**: Initial attempt used `python -m mcp.server.streamable_http server:mcp` in app.yaml
**Error**: RuntimeWarning and deployment failures

**Solution**: Use uvicorn with proper entry point
- Changed app.yaml command to: `['uv', 'run', 'youcom-mcp-server']`
- Define entry point in pyproject.toml
- Let uvicorn handle the HTTP server lifecycle

### Issue 2: AttributeError - 'FastMCP' object has no attribute 'get_asgi_app'
**Problem**: Followed outdated documentation using `mcp.get_asgi_app()`
**Root Cause**: Old server.py file still existed after conversion

**Solution**:
- Use `mcp.streamable_http_app()` method instead
- Delete old files that don't match new package structure
- Sync to correct deployment path to ensure clean deployment

### Issue 3: Wrong Sync Path
**Problem**: Files synced to wrong location, old code still being deployed
**Expected Path**: `/Workspace/Users/[email]/.bundle/custom_mcp_search/dev/files/youdotcom_MCP`
**Actual Sync**: Was syncing to `bundle/custom_mcp_search` (incorrect)

**Solution**: Always sync to the full `.bundle` path where Databricks Apps actually deploys from

### Issue 4: API Key Format - 403 Forbidden Errors
**Problem**: API calls returned 403 Forbidden despite correct endpoint and authentication format
**Root Cause**: API key contained special characters `<__>` that were being replaced with plain `__`

**Details**:
- Correct format: `ydc-sk-...-7a7a3b29<__>1SCkS5ETU8N2v5f4TwEvbDf0`
- Incorrect format: `ydc-sk-...-7a7a3b29__1SCkS5ETU8N2v5f4TwEvbDf0`

**Why 403 not 401?**
- 401 = "I don't know who you are" (invalid/missing credentials)
- 403 = "I know who you are, but no permission" (valid format, wrong value)
- The malformed key had valid structure so passed authentication but failed authorization

**Testing Method**:
```bash
# Test with curl to verify API key format
curl --request GET \
  --url "https://api.ydc-index.io/v1/search?query=test" \
  --header "X-API-Key: [your-key-here]"
```

**Solution**: Preserve exact API key format including special characters

### Issue 5: API Endpoint Confusion
**Problem**: Multiple endpoints (/search, /v1/search, /v2/search) - which to use?
**Investigation**:
- Documentation showed both v1 and v2 endpoints
- v2 mentioned for "Bearer token authentication with Databricks Unity Catalog"
- Basic plan uses API key authentication

**Solution**: Use `/v1/search` with `X-API-Key` header for basic API plan

### Issue 6: Environment Variable Loading in Databricks
**Problem**: Need to pass API key securely to deployed app
**Options Considered**:
1. Databricks Secrets (most secure, requires scope creation)
2. Direct value in app.yaml (simpler for development)

**Solution Used**: Direct value in app.yaml for initial testing
```yaml
env:
  - name: 'YOU_API_KEY'
    value: 'ydc-sk-831714a5bdef1c90-...'
```

**Production Recommendation**: Use Databricks Secrets
```yaml
env:
  - name: 'YOU_API_KEY'
    valueFrom: 'scope_name/secret_key'
```

## Git Repository Management

### Setting Up Dual Remotes
```bash
git remote -v
# origin: Original template repo (read-only)
# myrepo: Your fork (push here)

# Push to your repo only
git push myrepo python-mcp-server
```

**Best Practice**: Keep original repo as reference, push changes to your fork

## Deployment Workflow

### Local Testing
```bash
# Set environment variable
export YOU_API_KEY='your-key-here'

# Run locally
uv run youcom-mcp-server

# Test endpoint
curl http://localhost:8000
```

### Sync to Databricks
```bash
databricks sync \
  /path/to/local/youdotcom_MCP \
  /Workspace/Users/[email]/.bundle/custom_mcp_search/dev/files/youdotcom_MCP \
  --profile [profile-name]
```

### Deploy App
```bash
databricks apps deploy mcp-youcom --profile [profile-name]
```

### Verify in AI Playground
1. Open Databricks AI Playground
2. Look for "You.com MCP Server" in MCP tools
3. Test `web_search` tool with a query

## Key Learnings for Future MCP Servers

### 1. Framework Selection
- **Use Python + FastMCP** for Databricks Apps
- Node.js MCP servers work locally but have deployment challenges
- Follow existing working examples (like quicksizer-mcp)

### 2. Project Structure Requirements
- Use `pyproject.toml` with proper entry points
- Separate package source in `src/` directory
- Define dependencies explicitly (don't rely on global installs)
- Minimal `requirements.txt` (just uv for Databricks Apps)

### 3. FastMCP Patterns
- Always use `streamable_http_app()` for HTTP transport
- Include FastAPI lifespan management with `mcp.session_manager.run()`
- Mount MCP app at root path in FastAPI
- Use async functions for all tools

### 4. Debugging Strategy
1. Test API calls with curl first (verify credentials and endpoints)
2. Test locally with `uv run` before deploying
3. Check exact sync path matches deployment location
4. Verify environment variables are loaded correctly
5. Look at Databricks app logs for runtime errors

### 5. API Key Management
- Preserve exact format including special characters
- Test with curl before embedding in code
- Use secrets for production, direct values for development
- Never commit API keys to git (use .gitignore for .env)

### 6. Common Pitfalls to Avoid
- ❌ Using `get_asgi_app()` (doesn't exist in FastMCP)
- ❌ Running MCP as CLI tool instead of HTTP server
- ❌ Syncing to wrong deployment path
- ❌ Modifying API key format (keep exact characters)
- ❌ Mixing Node.js and Python patterns
- ❌ Forgetting to clean up old files after refactoring

### 7. API Plan Considerations
- Free trial includes 1,000 calls/month
- Includes both web search AND news endpoints
- Use `/v1/search` for basic API key authentication
- `/v2/search` is for Bearer token auth (Unity Catalog integration)

## Quick Reference Commands

### Local Development
```bash
# Install dependencies
uv sync

# Run locally
uv run youcom-mcp-server

# Test API directly
curl -X GET "https://api.ydc-index.io/v1/search?query=test" \
  -H "X-API-Key: your-key"
```

### Databricks Deployment
```bash
# Sync files
databricks sync . /Workspace/Users/[email]/.bundle/.../files/[app] --profile [profile]

# Deploy app
databricks apps deploy [app-name] --profile [profile]

# Check app status
databricks apps get [app-name] --profile [profile]
```

### Git Operations
```bash
# Check remotes
git remote -v

# Push to your repo
git push myrepo [branch-name]

# Don't push to origin (original repo)
```

## Conclusion

Building a custom MCP server for Databricks Apps requires understanding the specific deployment patterns and framework requirements. The key success factors are:

1. Using Python + FastMCP (not Node.js)
2. Proper package structure with pyproject.toml
3. HTTP server deployment (uvicorn) not CLI
4. Exact API key format preservation
5. Correct sync paths to deployment location
6. Following working examples as templates

The conversion from Node.js to Python was necessary and ultimately led to a much cleaner, more maintainable implementation that follows Databricks Apps best practices.

## Resources

- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Databricks Apps Documentation](https://docs.databricks.com/en/dev-tools/databricks-apps/index.html)
- [You.com API Documentation](https://documentation.you.com/)
- [Quicksizer MCP Example](https://github.com/renardeinside/quicksizer-mcp)