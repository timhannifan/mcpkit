# MCP Server for OpenWebUI

MCP server demonstrating knowledge-graph integration via Neo4j. Exposes a single tool, `neo4j_execute_cypher`, that runs dynamic Cypher queries against a citation-network demo graph (papers, authors, topics, citations).

## Features

- **neo4j_execute_cypher** — Execute custom Cypher queries (read-only, validated for safety)

The graph is seeded by running `make seed-db` from the repo root. See [Neo4j Citation Demo](../docs/NEO4J_DEMO.md) for setup and usage.

## Running

The MCP server is part of the docker-compose stack:

```bash
make dev    # Local development
make prod   # Production
```

Endpoint: `http://localhost:8090/mcp` (from host) or `http://mcp-server:8090/mcp` (from containers).
