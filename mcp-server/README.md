# MCP Server for OpenWebUI

MCP server demonstrating knowledge-graph integration via Neo4j. Exposes six tools that query a citation-network demo graph (papers, authors, topics, citations).

## Features

Neo4j citation-demo tools:

- **neo4j_most_cited** — Most cited papers
- **neo4j_citation_chain** — Citation chains (papers citing papers)
- **neo4j_coauthorship** — Co-authorship / collaboration network
- **neo4j_research_influence** — Who influenced whom across topics
- **neo4j_shortest_path** — Shortest path between two papers
- **neo4j_topic_clusters** — Topic co-occurrence

The graph is seeded by running `make seed-db` from the repo root. See [Neo4j Citation Demo](../docs/NEO4J_DEMO.md) for setup and usage.

## Running

The MCP server is part of the docker-compose stack:

```bash
make dev    # Local development
make prod   # Production
```

Endpoint: `http://localhost:8090/mcp` (from host) or `http://mcp-server:8090/mcp` (from containers).

## Extending

Add tools by defining a Pydantic input model and decorating a function with `@mcp.tool()`:

```python
class MyToolInput(BaseModel):
    param: str = Field(description="Parameter description")

@mcp.tool()
async def my_tool(data: MyToolInput) -> str:
    """Tool description."""
    return f"Result: {data.param}"
```

See `server.py` and `neo4j_demo.py` for the Neo4j tools.
