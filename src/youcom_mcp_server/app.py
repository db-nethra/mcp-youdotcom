import os
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import httpx

# Get API key from environment variable
API_KEY = os.getenv("YOU_API_KEY")
if not API_KEY:
    raise ValueError("YOU_API_KEY environment variable must be set")

# Create MCP server
mcp = FastMCP("You.com MCP Server")

# You.com API base URL
YOU_API_BASE = "https://api.ydc-index.io"


@mcp.tool()
async def web_search(query: str) -> Dict[str, Any]:
    """
    Search the web using You.com's search API.

    Args:
        query: The search query to send to You.com

    Returns:
        Search results from You.com
    """
    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": API_KEY}
        params = {"query": query}

        response = await client.get(
            f"{YOU_API_BASE}/v1/search",
            headers=headers,
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


# Note: The following tools require premium API access
# Commenting out for basic plan


# @mcp.tool()
async def smart_search_premium(
    query: str,
    instructions: str | None = None,
    conversation_id: str | None = None
) -> Dict[str, Any]:
    """
    Perform a smart AI-powered search using You.com's Smart API.

    Args:
        query: The query to send to You.com's Smart API
        instructions: Custom instructions for tailoring the response (optional)
        conversation_id: A hex UUID to maintain conversation continuity (optional)

    Returns:
        AI-generated response with citations from You.com
    """
    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

        payload = {"query": query}
        if instructions:
            payload["instructions"] = instructions
        if conversation_id:
            payload["conversation_id"] = conversation_id

        response = await client.post(
            f"{YOU_API_BASE}/smart",
            headers=headers,
            json=payload,
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()


# @mcp.tool()
async def research_premium(query: str, instructions: str | None = None) -> Dict[str, Any]:
    """
    Conduct comprehensive research using You.com's Research API.

    Args:
        query: The research query to send to You.com's Research API
        instructions: Custom instructions for tailoring the response (optional)

    Returns:
        Detailed research findings from You.com
    """
    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

        payload = {"query": query}
        if instructions:
            payload["instructions"] = instructions

        response = await client.post(
            f"{YOU_API_BASE}/research",
            headers=headers,
            json=payload,
            timeout=120.0
        )
        response.raise_for_status()
        return response.json()


# @mcp.tool()
async def news_search_premium(query: str) -> Dict[str, Any]:
    """
    Search for recent news articles using You.com's News API.

    Args:
        query: The news query to send to You.com's News API

    Returns:
        Recent news articles from You.com
    """
    async with httpx.AsyncClient() as client:
        headers = {"X-API-Key": API_KEY}
        params = {"query": query}

        response = await client.get(
            f"{YOU_API_BASE}/news",
            headers=headers,
            params=params,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()


# Create MCP streamable HTTP app
mcp_app = mcp.streamable_http_app()

# Create FastAPI app with MCP lifespan
app = FastAPI(
    lifespan=lambda _: mcp.session_manager.run(),
)

# Mount MCP app to FastAPI
app.mount("/", mcp_app)