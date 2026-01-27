#!/usr/bin/env python3
"""Citation Network Knowledge Graph Demo. Seed the citation graph for MCP tools; run anytime to reset."""

import logging
import os
import sys

from neo4j import GraphDatabase, NotificationMinimumSeverity

logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
USER = os.environ.get("NEO4J_USER", "neo4j")
PASSWORD = os.environ.get("NEO4J_PASSWORD", "password123")


class CitationGraph:
    def __init__(self, uri: str = URI, auth: tuple[str, str] = (USER, PASSWORD)):
        self.driver = GraphDatabase.driver(
            uri,
            auth=auth,
            warn_notification_severity=NotificationMinimumSeverity.OFF,
        )

    def close(self) -> None:
        self.driver.close()

    def clear_database(self) -> None:
        """Start fresh."""
        with self.driver.session() as s:
            s.run("MATCH (n) DETACH DELETE n")
        logger.info("Database cleared")

    def create_schema(self) -> None:
        """Create indexes for performance."""
        with self.driver.session() as s:
            s.run("CREATE INDEX IF NOT EXISTS FOR (p:Paper) ON (p.id)")
            s.run("CREATE INDEX IF NOT EXISTS FOR (a:Author) ON (a.name)")
            s.run("CREATE INDEX IF NOT EXISTS FOR (t:Topic) ON (t.name)")
        logger.info("Schema created")

    def populate_sample_data(self) -> None:
        """
        Create a realistic citation network.

        Graph Structure:
        (Author)-[:AUTHORED]->(Paper)-[:CITES]->(Paper)
                                    `-[:ABOUT]->(Topic)
        """
        with self.driver.session() as s:
            # Create foundational papers (highly cited)
            s.run("""
                CREATE (p1:Paper {id: 'p1', title: 'PageRank: The Original Algorithm', year: 1998, citations: 0})
                CREATE (p2:Paper {id: 'p2', title: 'MapReduce: Simplified Data Processing', year: 2004, citations: 0})
                CREATE (p3:Paper {id: 'p3', title: 'The Graph Database Manifesto', year: 2010, citations: 0})

                CREATE (a1:Author {name: 'Alice Chen', affiliation: 'Stanford'})
                CREATE (a2:Author {name: 'Bob Smith', affiliation: 'Google'})
                CREATE (a3:Author {name: 'Carol Wu', affiliation: 'MIT'})

                CREATE (t1:Topic {name: 'Graph Algorithms'})
                CREATE (t2:Topic {name: 'Distributed Systems'})
                CREATE (t3:Topic {name: 'Databases'})

                CREATE (a1)-[:AUTHORED {role: 'primary'}]->(p1)
                CREATE (a2)-[:AUTHORED {role: 'primary'}]->(p2)
                CREATE (a3)-[:AUTHORED {role: 'primary'}]->(p3)

                CREATE (p1)-[:ABOUT]->(t1)
                CREATE (p2)-[:ABOUT]->(t2)
                CREATE (p3)-[:ABOUT]->(t3)
                CREATE (p3)-[:ABOUT]->(t1)
            """)

            # Create newer papers that cite the foundational ones
            s.run("""
                CREATE (p4:Paper {id: 'p4', title: 'Modern Graph Neural Networks', year: 2020, citations: 0})
                CREATE (p5:Paper {id: 'p5', title: 'Scalable Knowledge Graphs', year: 2022, citations: 0})
                CREATE (p6:Paper {id: 'p6', title: 'Citation Analysis with ML', year: 2023, citations: 0})

                CREATE (a4:Author {name: 'David Lee', affiliation: 'Berkeley'})
                CREATE (a5:Author {name: 'Eva Martinez', affiliation: 'CMU'})

                WITH p4, p5, p6, a4, a5
                MATCH (p1:Paper {id: 'p1'}), (p2:Paper {id: 'p2'}), (p3:Paper {id: 'p3'})
                MATCH (t1:Topic {name: 'Graph Algorithms'}), (t3:Topic {name: 'Databases'})
                MATCH (a1:Author {name: 'Alice Chen'})

                CREATE (a4)-[:AUTHORED]->(p4)
                CREATE (a5)-[:AUTHORED]->(p5)
                CREATE (a4)-[:AUTHORED]->(p6)
                CREATE (a1)-[:AUTHORED]->(p6)

                CREATE (p4)-[:CITES]->(p1)
                CREATE (p4)-[:CITES]->(p3)
                CREATE (p5)-[:CITES]->(p2)
                CREATE (p5)-[:CITES]->(p3)
                CREATE (p6)-[:CITES]->(p1)
                CREATE (p6)-[:CITES]->(p4)
                CREATE (p6)-[:CITES]->(p5)

                CREATE (p4)-[:ABOUT]->(t1)
                CREATE (p5)-[:ABOUT]->(t3)
                CREATE (p6)-[:ABOUT]->(t1)
                CREATE (p6)-[:ABOUT]->(t3)
            """)

            # Update citation counts
            s.run("""
                MATCH (p:Paper)<-[c:CITES]-()
                WITH p, count(c) as cnt
                SET p.citations = cnt
            """)

        logger.info("Sample data created (6 papers, 5 authors, 3 topics)")

    def query_most_cited(self) -> None:
        """Simple: Find most influential papers."""
        logger.info("\nMOST CITED PAPERS:")
        logger.info("-" * 50)
        with self.driver.session() as s:
            result = s.run("""
                MATCH (p:Paper)
                RETURN p.title as title, p.year as year, p.citations as citations
                ORDER BY p.citations DESC
                LIMIT 5
            """)
            for r in result:
                logger.info("  [%s cites] %s (%s)", r["citations"], r["title"], r["year"])

    def query_citation_chain(self) -> None:
        """
        Graph Power: Follow citation chains
        This is where graphs shine - no JOINs needed!
        """
        logger.info("\nCITATION CHAINS (papers citing papers citing papers):")
        logger.info("-" * 50)
        with self.driver.session() as s:
            result = s.run("""
                MATCH path = (p1:Paper)-[:CITES*1..3]->(p2:Paper)
                WHERE p1.year > p2.year
                RETURN p1.title as citing,
                       [n in nodes(path) | n.title] as chain,
                       length(path) as depth
                ORDER BY depth DESC
                LIMIT 5
            """)
            for r in result:
                chain = " → ".join(r["chain"])
                logger.info("  Depth %s: %s", r["depth"], chain)

    def query_coauthorship(self) -> None:
        """Relationship Discovery: Find collaboration networks."""
        logger.info("\nCO-AUTHORSHIP NETWORK:")
        logger.info("-" * 50)
        with self.driver.session() as s:
            result = s.run("""
                MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
                WHERE a1.name < a2.name
                RETURN a1.name as author1, a2.name as author2,
                       collect(p.title) as papers
            """)
            for r in result:
                logger.info("  %s & %s", r["author1"], r["author2"])
                for paper in r["papers"]:
                    logger.info("      - %s", paper)

    def query_research_influence(self) -> None:
        """Complex Traversal: Who influenced whom across topics?"""
        logger.info("\nRESEARCH INFLUENCE (Author → Paper → Citations → Topics):")
        logger.info("-" * 50)
        with self.driver.session() as s:
            result = s.run("""
                MATCH (a:Author)-[:AUTHORED]->(p:Paper)<-[:CITES]-(citing:Paper)-[:ABOUT]->(t:Topic)
                RETURN a.name as author,
                       count(DISTINCT citing) as influenced_papers,
                       collect(DISTINCT t.name) as topics_influenced
                ORDER BY influenced_papers DESC
            """)
            for r in result:
                topics = ", ".join(r["topics_influenced"])
                logger.info("  %s: influenced %s papers", r["author"], r["influenced_papers"])
                logger.info("      Topics: %s", topics)

    def query_shortest_path(self) -> None:
        """Path Finding: How are two papers connected?"""
        logger.info("\nSHORTEST PATH BETWEEN PAPERS:")
        logger.info("-" * 50)
        with self.driver.session() as s:
            result = s.run("""
                MATCH path = shortestPath(
                    (p1:Paper {title: 'Citation Analysis with ML'})
                    -[*]-(p2:Paper {title: 'PageRank: The Original Algorithm'})
                )
                RETURN [n in nodes(path) |
                    CASE WHEN n:Paper THEN n.title
                         WHEN n:Author THEN n.name
                         WHEN n:Topic THEN n.name
                    END] as path
            """)
            for r in result:
                logger.info("  %s", " → ".join(r["path"]))

    def query_topic_clusters(self) -> None:
        """Pattern Discovery: Which topics are researched together?"""
        logger.info("\nTOPIC CO-OCCURRENCE:")
        logger.info("-" * 50)
        with self.driver.session() as s:
            result = s.run("""
                MATCH (t1:Topic)<-[:ABOUT]-(p:Paper)-[:ABOUT]->(t2:Topic)
                WHERE t1.name < t2.name
                RETURN t1.name as topic1, t2.name as topic2,
                       count(p) as shared_papers
                ORDER BY shared_papers DESC
            """)
            for r in result:
                logger.info("  %s ∩ %s: %s papers", r["topic1"], r["topic2"], r["shared_papers"])


def main() -> int:
    logger.info("=" * 60)
    logger.info("CITATION NETWORK KNOWLEDGE GRAPH DEMO")
    logger.info("=" * 60)
    logger.info("Connecting to %s as %s", URI, USER)

    graph = CitationGraph()

    try:
        # Setup
        graph.clear_database()
        graph.create_schema()
        graph.populate_sample_data()

        # Run demonstration queries
        graph.query_most_cited()
        graph.query_citation_chain()
        graph.query_coauthorship()
        graph.query_research_influence()
        graph.query_shortest_path()
        graph.query_topic_clusters()
    except Exception:
        logger.exception("Error")
        return 1
    else:
        return 0
    finally:
        graph.close()


if __name__ == "__main__":
    sys.exit(main())
