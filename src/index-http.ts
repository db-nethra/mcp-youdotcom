#!/usr/bin/env node
import "dotenv/config";
import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import { z } from "zod";
import { YouApiClient } from "./services/youApiClient.js";

// Get API key from environment variable
const API_KEY = process.env.YOU_API_KEY as string;
if (!API_KEY) {
  console.error("ERROR: YOU_API_KEY environment variable must be set");
  process.exit(1);
}

// Get port from environment variable or default to 3000
const PORT = process.env.PORT || 3000;

// Initialize API client
const youClient = new YouApiClient(API_KEY);

// Create Express app
const app = express();
app.use(express.json());

// Create MCP server
const server = new McpServer({
  name: "You.com MCP Server",
  version: "1.0.0"
});

// Web Search Tool
server.tool(
  "web_search",
  {
    query: z.string().describe("The search query to send to You.com")
  },
  async ({ query }: { query: string }) => {
    try {
      const results = await youClient.search(query);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(results, null, 2)
        }]
      };
    } catch (error) {
      console.error("Search error:", error);
      return {
        content: [{
          type: "text",
          text: `Error performing search: ${error instanceof Error ? error.message : String(error)}`
        }],
        isError: true
      };
    }
  }
);

// Smart AI Tool
server.tool(
  "smart_search",
  {
    query: z.string().describe("The query to send to You.com's Smart API"),
    instructions: z.string().optional().describe("Custom instructions for tailoring the response (optional)"),
    conversationId: z.string().optional().describe("A hex UUID to maintain conversation continuity (optional)")
  },
  async ({ query, instructions, conversationId }: { query: string; instructions?: string; conversationId?: string }) => {
    try {
      const result = await youClient.smartSearch(query, instructions, conversationId);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error("Smart search error:", error);
      return {
        content: [{
          type: "text",
          text: `Error performing smart search: ${error instanceof Error ? error.message : String(error)}`
        }],
        isError: true
      };
    }
  }
);

// Research Tool
server.tool(
  "research",
  {
    query: z.string().describe("The research query to send to You.com's Research API"),
    instructions: z.string().optional().describe("Custom instructions for tailoring the response (optional)")
  },
  async ({ query, instructions }: { query: string; instructions?: string }) => {
    try {
      const result = await youClient.research(query, instructions);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(result, null, 2)
        }]
      };
    } catch (error) {
      console.error("Research error:", error);
      return {
        content: [{
          type: "text",
          text: `Error performing research: ${error instanceof Error ? error.message : String(error)}`
        }],
        isError: true
      };
    }
  }
);

// News Tool
server.tool(
  "news_search",
  {
    query: z.string().describe("The news query to send to You.com's News API")
  },
  async ({ query }: { query: string }) => {
    try {
      const results = await youClient.getNews(query);
      return {
        content: [{
          type: "text",
          text: JSON.stringify(results, null, 2)
        }]
      };
    } catch (error) {
      console.error("News search error:", error);
      return {
        content: [{
          type: "text",
          text: `Error performing news search: ${error instanceof Error ? error.message : String(error)}`
        }],
        isError: true
      };
    }
  }
);

// Root endpoint
app.get("/", (req, res) => {
  res.json({
    service: "You.com MCP Server",
    version: "1.0.0",
    endpoints: {
      health: "/health",
      sse: "/sse",
      message: "/message"
    }
  });
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok", service: "You.com MCP Server" });
});

// SSE endpoint for MCP communication
app.get("/sse", async (req, res) => {
  console.error("Client connected via SSE");
  const transport = new SSEServerTransport("/message", res);
  await server.connect(transport);
});

// MCP endpoint (Databricks standard)
app.get("/mcp", async (req, res) => {
  console.error("Client connected via MCP endpoint");
  const transport = new SSEServerTransport("/mcp/message", res);
  await server.connect(transport);
});

// Message endpoint for client requests
app.post("/message", async (req, res) => {
  // This will be handled by the SSE transport
  res.status(200).end();
});

// MCP message endpoint
app.post("/mcp/message", async (req, res) => {
  // This will be handled by the SSE transport
  res.status(200).end();
});

// Start the server
app.listen(PORT, () => {
  console.error(`You.com MCP server running on http://localhost:${PORT}`);
  console.error(`SSE endpoint: http://localhost:${PORT}/sse`);
  console.error(`Health check: http://localhost:${PORT}/health`);
});