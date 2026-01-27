# Neo4j Knowledge Graph Demo via MCP

Demonstrates knowledge-graph integration via MCP: the MCP server talks to Neo4j and exposes tools so OpenWebUI chat can query the graph. A standalone script seeds the DB; the server exposes six demo-query tools.

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

5. **Use the Neo4j tools in chat**  
   Enable the MCP tools in Integrations and ask the model (e.g. “Show most cited papers”, “Show co-authorship network”).

## System prompt

Paste into the chat system prompt (upper-right controls):

```
You have access to a Neo4j citation-network demo. Use these tools when the user asks about the citation graph, papers, authors, or research:

- neo4j_most_cited — when they ask for most cited papers, top papers, influential papers, or citation rankings.
- neo4j_citation_chain — when they ask about citation chains, papers citing other papers, or how citations flow.
- neo4j_coauthorship — when they ask about co-authors, collaborators, who wrote papers together, or collaboration networks.
- neo4j_research_influence — when they ask who influenced whom, research impact, or influence across topics.
- neo4j_shortest_path — when they ask how two papers are connected or the path between "Citation Analysis with ML" and "PageRank".
- neo4j_topic_clusters — when they ask which topics appear together, topic co-occurrence, or papers spanning multiple topics.

Call the relevant tool instead of guessing; the demo has real data after the user runs "make seed-db".

Call each Neo4j tool with an empty object {} or omit parameters. Do not add topic, filter, or any other parameters — these tools accept no such inputs.
```

## Tool list

| Tool | Description |
|------|-------------|
| `neo4j_most_cited` | Most cited papers (by citation count) |
| `neo4j_citation_chain` | Citation chains (papers citing papers citing papers) |
| `neo4j_coauthorship` | Co-authorship / collaboration network |
| `neo4j_research_influence` | Who influenced whom across topics |
| `neo4j_shortest_path` | Shortest path between two papers |
| `neo4j_topic_clusters` | Topic co-occurrence (which topics appear together) |

## Neo4j Browser (local only)

Inspect the graph at `http://localhost:7474`. Sign in with user `neo4j` and `NEO4J_PASSWORD` (default `password123`).

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `bolt://neo4j:7687` | Bolt URI. MCP server and seed script (via `make seed-db`) use hostname `neo4j` inside the stack. |
| `NEO4J_USER` | `neo4j` | Neo4j user. |
| `NEO4J_PASSWORD` | `password123` | Neo4j password. Set in `.env` as `NEO4J_PASSWORD` for production. |

The MCP server and the seed run get these from docker-compose env. `make seed-db` passes `NEO4J_URI=bolt://neo4j:7687`, `NEO4J_USER`, and `NEO4J_PASSWORD` into the mcp-server container when it runs the seed script.
