"""Neo4j citation-network demo: driver and six query helpers for MCP tools."""

import os
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError

_NEO4J_DRIVER: list[Driver | None] = [None]

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password123")


def get_driver() -> Driver | None:
    """Return a Neo4j driver if configured; otherwise None."""
    if not NEO4J_URI or not NEO4J_URI.strip():
        return None
    if _NEO4J_DRIVER[0] is None:
        try:
            d = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
            )
            _NEO4J_DRIVER[0] = d
        except (Neo4jError, DriverError, OSError):
            return None
    return _NEO4J_DRIVER[0]


def _run_query(driver: Driver, cypher: str, **params: Any) -> list[dict[str, Any]]:
    with driver.session() as session:
        result = session.run(cypher, params)
        return [dict(r) for r in result]


def query_most_cited(driver: Driver) -> str:
    """Find most influential papers."""
    try:
        rows = _run_query(
            driver,
            """
            MATCH (p:Paper)
            RETURN p.title as title, p.year as year, p.citations as citations
            ORDER BY p.citations DESC
            LIMIT 5
            """,
        )
    except (Neo4jError, DriverError, OSError) as e:
        return f"Neo4j error: {e}. Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
    out = ["MOST CITED PAPERS:", "-" * 50]
    for r in rows:
        out.append(f"  [{r['citations']} cites] {r['title']} ({r['year']})")
    return "\n".join(out)


def query_citation_chain(driver: Driver) -> str:
    """Follow citation chains (papers citing papers citing papers)."""
    try:
        rows = _run_query(
            driver,
            """
            MATCH path = (p1:Paper)-[:CITES*1..3]->(p2:Paper)
            WHERE p1.year > p2.year
            RETURN p1.title as citing,
                   [n in nodes(path) | n.title] as chain,
                   length(path) as depth
            ORDER BY depth DESC
            LIMIT 5
            """,
        )
    except (Neo4jError, DriverError, OSError) as e:
        return f"Neo4j error: {e}. Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
    out = ["CITATION CHAINS (papers citing papers citing papers):", "-" * 50]
    for r in rows:
        chain = " → ".join(r["chain"])
        out.append(f"  Depth {r['depth']}: {chain}")
    return "\n".join(out)


def query_coauthorship(driver: Driver) -> str:
    """Find collaboration networks (co-authorship)."""
    try:
        rows = _run_query(
            driver,
            """
            MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
            WHERE a1.name < a2.name
            RETURN a1.name as author1, a2.name as author2,
                   collect(p.title) as papers
            """,
        )
    except (Neo4jError, DriverError, OSError) as e:
        return f"Neo4j error: {e}. Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
    out = ["CO-AUTHORSHIP NETWORK:", "-" * 50]
    for r in rows:
        out.append(f"  {r['author1']} ↔ {r['author2']}")
        for paper in r["papers"]:
            out.append(f"      └─ {paper}")
    return "\n".join(out)


def query_research_influence(driver: Driver) -> str:
    """Who influenced whom across topics (Author → Paper → Citations → Topics)."""
    try:
        rows = _run_query(
            driver,
            """
            MATCH (a:Author)-[:AUTHORED]->(p:Paper)<-[:CITES]-(citing:Paper)-[:ABOUT]->(t:Topic)
            RETURN a.name as author,
                   count(DISTINCT citing) as influenced_papers,
                   collect(DISTINCT t.name) as topics_influenced
            ORDER BY influenced_papers DESC
            """,
        )
    except (Neo4jError, DriverError, OSError) as e:
        return f"Neo4j error: {e}. Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
    out = ["RESEARCH INFLUENCE (Author → Paper → Citations → Topics):", "-" * 50]
    for r in rows:
        topics = ", ".join(r["topics_influenced"])
        out.append(f"  {r['author']}: influenced {r['influenced_papers']} papers")
        out.append(f"      Topics: {topics}")
    return "\n".join(out)


def query_shortest_path(driver: Driver) -> str:
    """How are two papers connected? Shortest path between papers."""
    try:
        rows = _run_query(
            driver,
            """
            MATCH path = shortestPath(
                (p1:Paper {title: 'Citation Analysis with ML'})
                -[*]-(p2:Paper {title: 'PageRank: The Original Algorithm'})
            )
            RETURN [n in nodes(path) |
                CASE WHEN n:Paper THEN n.title
                     WHEN n:Author THEN n.name
                     WHEN n:Topic THEN n.name
                END] as path
            """,
        )
    except (Neo4jError, DriverError, OSError) as e:
        return f"Neo4j error: {e}. Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
    out = ["SHORTEST PATH BETWEEN PAPERS:", "-" * 50]
    for r in rows:
        out.append(f"  {' → '.join(r['path'])}")
    return "\n".join(out)


def query_topic_clusters(driver: Driver) -> str:
    """Which topics are researched together? Topic co-occurrence."""
    try:
        rows = _run_query(
            driver,
            """
            MATCH (t1:Topic)<-[:ABOUT]-(p:Paper)-[:ABOUT]->(t2:Topic)
            WHERE t1.name < t2.name
            RETURN t1.name as topic1, t2.name as topic2,
                   count(p) as shared_papers
            ORDER BY shared_papers DESC
            """,
        )
    except (Neo4jError, DriverError, OSError) as e:
        return f"Neo4j error: {e}. Run the citation demo seed script first: scripts/neo4j_citation_demo.py"
    out = ["TOPIC CO-OCCURRENCE:", "-" * 50]
    for r in rows:
        out.append(f"  {r['topic1']} ∩ {r['topic2']}: {r['shared_papers']} papers")
    return "\n".join(out)
