# mcpkit

MCP toolkit for OpenWebUI, FastMCP, and deployment.

A ready-to-run stack that pairs OpenWebUI with a FastMCP server: all tools query a Neo4j citation graph (papers, authors, topics). You can connect via direct MCP or through the mcpo proxy (REST/OpenAPI), and deploy to EC2 with the included Docker Compose and Caddy setup.

## Features

- **OpenWebUI Ready**: Pre-configured OpenWebUI setup ready for document assistance and chat
- **FastMCP Server Integration**: Demonstrates how to integrate a FastMCP server alongside OpenWebUI
- **Knowledge Graph Integration**: All MCP tools are Neo4j-backed and query the citation graph.
- **MCP-to-OpenAPI Proxy**: Shows how to expose MCP tools as REST APIs using mcpo
- **Production Deployment**: Includes Docker Compose setup with Caddy reverse proxy for EC2 deployment

## Quick Start

1. **Clone and configure**

   From the repo root:
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

2. **Start services**
   ```bash
   make dev
   ```

3. **Seed the graph**

   Run `make seed-db` once to seed the Neo4j citation graph (papers, authors, topics). The MCP tools query this graph. See [docs/NEO4J_DEMO.md](docs/NEO4J_DEMO.md) for tool list and system prompt.

4. **Access OpenWebUI**

   Open http://localhost:3000 in your browser

5. **Configure LLM (OpenRouter)**

   - Go to **Admin Settings** → **Connections**
   - Click **Manage OpenAI Connections** → **Add Connection**
   - Set:
     - **URL**: `https://openrouter.ai/api/v1`
     - **API Key**: Your OpenRouter API key (get one at [openrouter.ai](https://openrouter.ai))
   - Save

6. **Setup Tool Integration**
   
   **Option A: Direct MCP Server**
   
   - Go to **Admin Settings** → **External Tools**
   - Under **Manage Tool Servers**, click **Add Connection**
   - Set:
     - **URL**: `http://host.docker.internal:8090/mcp` (use `host.docker.internal` for local dev)
     - **Auth**: `None` (no authentication required for direct MCP)
   - Save
   - In a chat, click the **Integrations** icon (below the text input area)
   - Find your tools and turn them on
   - Tools are now available in chat

   **Option B: Via mcpo Proxy (REST API)**
   
   - Go to **Admin Settings** → **External Tools**
   - Under **Manage Tool Servers**, click **Add Connection**
   - Set:
     - **URL**: `http://host.docker.internal:8000` (use `host.docker.internal` for local dev)
     - **Auth**: `Bearer`
     - **Bearer Token**: Your `MCPO_API_KEY` from `.env` (defaults to `dev-api-key` for local dev)
   - Save
   - In a chat, click the **Integrations** icon (below the text input area)
   - Find your tools and turn them on
   - Tools are now available in chat
   - Note: This uses the REST/OpenAPI proxy, not direct MCP protocol
   - Access Swagger docs at `http://localhost:8000/docs`

   For production deployment, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

7. **Start Querying**

   - In a chat, click the **Integrations** icon (below the text input area), find your tools and turn them on
   - Start a new chat, select a model, and ask questions about the citation graph (e.g. “Show most cited papers”, “Show co-authorship network”)

## Available Commands

```bash
make dev          # Start local development (http://localhost:3000)
make dev-down     # Stop local development

make seed-db      # Seed Neo4j citation graph (run after make dev; required for tools)

make prod         # Start production (with Caddy reverse proxy)
make prod-down    # Stop production

make deploy                # Deploy main branch to EC2
make deploy BRANCH=feature # Deploy specific branch

make clean        # Clean up Docker images and containers
```

## Project Structure

```
mcpkit/
├── docker-compose.yaml         # Base configuration
├── docker-compose.override.yaml # Local dev overrides
├── docker-compose.prod.yaml    # Production with Caddy
├── mcp-server/                 # MCP server for extensible tools
│   ├── server.py              # FastMCP server implementation
│   ├── neo4j_demo.py          # Neo4j citation-network query helpers
│   ├── Dockerfile             # MCP server container
│   └── README.md              # MCP server documentation
├── scripts/                    # Deployment and seed scripts
│   ├── deploy.sh              # Git-based deploy to EC2
│   ├── setup-ec2-docker.sh
│   └── neo4j_citation_demo.py # Seed script for Neo4j citation graph
├── webserver/                  # Caddy reverse proxy
│   ├── Caddyfile              # Production config
│   └── Caddy.Dockerfile
└── docs/
    ├── DEPLOYMENT.md          # Production deployment guide
    └── NEO4J_DEMO.md          # Neo4j citation demo setup and usage
```

## Production Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for full production deployment instructions.

## MCP Server Integration

This project demonstrates how to integrate a FastMCP server with OpenWebUI and expose it as a REST API using mcpo (MCP-to-OpenAPI proxy).

- **FastMCP Server** (`mcp-server`): Implements MCP tools using FastMCP 3.0 on port 8090; all tools query the Neo4j citation graph (six tools: most cited, citation chain, co-authorship, research influence, shortest path, topic clusters)
- **mcpo Proxy** (`mcpo`): Exposes MCP tools as REST/OpenAPI endpoints on port 8000

**Access:**
- **MCP endpoint**: `http://localhost:8090/mcp` (direct MCP protocol)
- **OpenAPI proxy**: `http://localhost:8000` (REST API with Swagger docs at `/docs`)
- **Neo4j Browser** (local): `http://localhost:7474` to inspect the citation graph (after `make seed-db`)

See [mcp-server/README.md](mcp-server/README.md) for extending the MCP server; see [docs/NEO4J_DEMO.md](docs/NEO4J_DEMO.md) for the Neo4j demo setup and tool list.
