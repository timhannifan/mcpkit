"""MCP server for OpenWebUI with Neo4j knowledge-graph demo tools."""

import logging
import os
import sys
from typing import Annotated, Any

import uvicorn
from fastmcp import FastMCP
from neo4j_demo import execute_cypher_query, get_driver
from pydantic import Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
    force=True,  # Force reconfiguration if already configured
)
logger = logging.getLogger(__name__)
# Ensure logs are flushed immediately
sys.stderr.flush()

# Create FastMCP instance
mcp = FastMCP("openwebui-tools")


# Register tools
@mcp.tool()
async def neo4j_execute_cypher(
    query: Annotated[
        str,
        Field(
            description="The Cypher query to execute. Must be a read-only query (MATCH, RETURN, etc.). Dangerous operations (DELETE, DROP, CREATE, MERGE, SET) are blocked for safety."
        ),
    ],
    params: Annotated[
        dict[str, Any] | None,
        Field(
            default=None,
            description="Optional dictionary of query parameters. Keys should match parameter names in the query (e.g., {'name': 'Alice Chen'}).",
        ),
    ] = None,
) -> str:
    """Execute a custom Cypher query against the Neo4j citation demo graph. Use this when the user asks for custom queries, ad-hoc analysis, or queries that aren't covered by other tools. Generate the Cypher query based on the user's natural language request, then call this tool with the generated query. The query must be read-only (MATCH, RETURN, etc.) - write operations are blocked for safety. Returns formatted query results or an error message."""
    try:
        driver = get_driver()
        if driver is None:
            error_msg = (
                "Neo4j not configured. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD. "
                "Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
            )
            logger.error("Neo4j driver not available")
            return error_msg
        return execute_cypher_query(driver, query, params)
    except Exception as e:
        logger.exception("neo4j_execute_cypher failed")
        return f"Unexpected error in neo4j_execute_cypher: {e}"


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8090"))

    logger.info("Starting MCP server on %s:%s", host, port)
    logger.info("Registered tools: neo4j_execute_cypher")

    app = mcp.http_app(path="/mcp")
    logger.info("MCP endpoint available at http://%s:%s/mcp", host, port)

    uvicorn.run(app, host=host, port=port, log_level="info")
