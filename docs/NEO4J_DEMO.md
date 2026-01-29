# Neo4j Knowledge Graph Demo via MCP

Demonstrates knowledge-graph integration via MCP: the MCP server talks to Neo4j and exposes a single tool so OpenWebUI chat can query the graph. A standalone script seeds the DB; the server exposes `neo4j_execute_cypher` for dynamic Cypher queries.

## Why knowledge graphs?

- **Model relationships naturally** — Entities and links map directly to nodes and edges; no heavy normalization or junction tables.
- **Traverse efficiently** — Follow connections in one hop; path and neighborhood queries stay simple.
- **Discover patterns** — Structure and connectivity (clusters, centrality, paths) are first-class.
- **Query relationships directly** — No JOINs; add relationship types without schema churn.

This demo uses a **citation network**: nodes = Papers, Authors, Topics; edges = CITES, AUTHORED, ABOUT. Node properties include title/year/citation_count on papers, name/affiliation on authors.

## Prerequisites

- Docker Compose (`make dev` or `make prod`).

## Quick start

1. **Start the stack**  
   `make dev` or `make prod`.

2. **Seed the citation graph (once)**  
   ```bash
   make seed-db
   ```
   Runs the seed script inside the mcp-server container. Run anytime to reset and re-seed.

3. **Connect the MCP server in OpenWebUI**  
   Admin Settings → External Tools → Add Connection → URL. In a chat, enable tools via Integrations.

4. **Edit the chat system prompt**  
   Use the controls in the upper right of the chat to open the system prompt / custom instructions. Paste the [System prompt](#system-prompt) block below.

5. **Use the Neo4j tool in chat**  
   Enable the MCP tool in Integrations and ask the model about the citation graph (e.g. "Find papers by Alice Chen" or "Which papers cite both Modern Graph Neural Networks and PageRank: The Original Algorithm?").

## System prompt

Paste into the chat system prompt (upper-right controls):

```
You have access to a Neo4j citation-network demo. When the user asks about the citation graph, papers, authors, or research, use the neo4j_execute_cypher tool.

IMPORTANT: When calling neo4j_execute_cypher, you MUST pass the query as a parameter named "query". The tool requires a "query" parameter with the Cypher query string. You can optionally pass a "params" parameter for query parameters.

Example correct usage:
- User asks: "Find all papers by Alice Chen"
- You call: neo4j_execute_cypher(query="MATCH (a:Author {name: 'Alice Chen'})-[:AUTHORED]->(p:Paper) RETURN p.title, p.year")

The query must be read-only (MATCH, RETURN, etc.) - write operations are blocked for safety.

Graph schema:
- Nodes: Paper (properties: title, year, citations), Author (properties: name, affiliation), Topic (properties: name)
- Relationships: CITES (Paper -> Paper), AUTHORED (Author -> Paper), ABOUT (Paper -> Topic)
```

## Tool

| Tool | Description |
|------|-------------|
| `neo4j_execute_cypher` | Execute custom Cypher queries (read-only, validated for safety) |

The `neo4j_execute_cypher` tool allows the LLM to generate and execute custom Cypher queries based on user requests.

**Usage:**
- The LLM generates a Cypher query from the user's natural language request
- The tool validates the query for safety (blocks DELETE, DROP, CREATE, MERGE, SET operations)
- Only read-only queries are allowed (MATCH, RETURN, WITH, WHERE, ORDER BY, LIMIT, etc.)
- Results are returned in a formatted table

**Example:**
- User: "Find all papers written by Alice Chen"
- LLM generates: `MATCH (a:Author {name: 'Alice Chen'})-[:AUTHORED]->(p:Paper) RETURN p.title, p.year`
- Tool executes and returns formatted results

**Safety:**
- All queries are validated before execution
- Dangerous operations (DELETE, DROP, CREATE, MERGE, SET, REMOVE) are blocked
- Only read-only operations are permitted

## Neo4j Browser (local only)

Inspect the graph at `http://localhost:7474`. Sign in with user `neo4j` and `NEO4J_PASSWORD` (default `password123`).

**Environment:** Neo4j connection uses `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD`. See [env.example](../env.example); defaults are fine for local dev. For production, set `NEO4J_PASSWORD` (and optionally the others) in `.env`.
