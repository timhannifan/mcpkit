"""MCP server for OpenWebUI with Neo4j knowledge-graph demo tools."""

import logging
import os
import sys
from typing import Literal

import uvicorn
from fastmcp import FastMCP
from neo4j_demo import (
    get_driver,
    query_citation_chain,
    query_coauthorship,
    query_most_cited,
    query_research_influence,
    query_shortest_path,
    query_topic_clusters,
)
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# Create FastMCP instance
mcp = FastMCP("openwebui-tools")


# Tool input models
class Neo4jQueryInput(BaseModel):
    """Run the predefined citation-demo query. No parameters required."""

    run: Literal["query"] = Field(
        default="query",
        description="Only valid field. Do not add topic, filter, or any other parameters — this tool has no such inputs. Omit or leave default.",
    )


def _neo4j_result(fn):
    """Run a Neo4j query helper; return result string or error message."""
    driver = get_driver()
    if driver is None:
        return (
            "Neo4j not configured. Set NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD. "
            "Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
        )
    return fn(driver)


# Register tools
@mcp.tool()
async def neo4j_most_cited(_data: Neo4jQueryInput) -> str:
    """Use when the user asks about most cited papers, top papers by citations, influential papers, or citation rankings. Returns the top 5 most-cited papers from the citation demo graph. No parameters (topic, filter, etc.); call with {} or default only."""
    return _neo4j_result(query_most_cited)


@mcp.tool()
async def neo4j_citation_chain(_data: Neo4jQueryInput) -> str:
    """Use when the user asks about citation chains, papers that cite other papers, or how citations flow (e.g. "show citation chains" or "papers citing papers"). Returns citation chains up to depth 3 from the demo graph. No parameters; call with {} or default only."""
    return _neo4j_result(query_citation_chain)


@mcp.tool()
async def neo4j_coauthorship(_data: Neo4jQueryInput) -> str:
    """Use when the user asks about co-authors, collaboration networks, who wrote papers together, or author collaborations. Returns co-authorship pairs and the papers they collaborated on from the demo graph. No parameters; call with {} or default only."""
    return _neo4j_result(query_coauthorship)


@mcp.tool()
async def neo4j_research_influence(_data: Neo4jQueryInput) -> str:
    """Use when the user asks about research influence, who influenced whom, which authors influenced other papers or topics, or impact across topics. Returns authors and how many papers (and which topics) they influenced in the demo graph. Accepts no parameters (no topic or filter); call with {} or default only."""
    return _neo4j_result(query_research_influence)


@mcp.tool()
async def neo4j_shortest_path(_data: Neo4jQueryInput) -> str:
    """Use when the user asks how two papers are connected, shortest path between papers, or how "Citation Analysis with ML" connects to "PageRank". Returns the shortest path between those two papers in the demo graph. No parameters; call with {} or default only."""
    return _neo4j_result(query_shortest_path)


@mcp.tool()
async def neo4j_topic_clusters(_data: Neo4jQueryInput) -> str:
    """Use when the user asks about topic co-occurrence, which topics appear together, topic clusters, or papers that span multiple topics. Returns topic pairs and how many papers cover both from the demo graph. No parameters; call with {} or default only."""
    return _neo4j_result(query_topic_clusters)


if __name__ == "__main__":
    host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("MCP_SERVER_PORT", "8090"))

    logger.info("Starting MCP server on %s:%s", host, port)
    logger.info(
        "Registered tools: neo4j_most_cited, neo4j_citation_chain, neo4j_coauthorship, "
        "neo4j_research_influence, neo4j_shortest_path, neo4j_topic_clusters"
    )

    app = mcp.http_app(path="/mcp")
    logger.info("MCP endpoint available at http://%s:%s/mcp", host, port)

    uvicorn.run(app, host=host, port=port, log_level="info")
