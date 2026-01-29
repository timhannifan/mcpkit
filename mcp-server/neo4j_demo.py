"""Neo4j citation-network demo: driver and execute_cypher_query for MCP tools."""

import logging
import os
import re
from typing import Any

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import DriverError, Neo4jError

logger = logging.getLogger(__name__)

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
    """Execute a Cypher query and return results as a list of dictionaries."""
    with driver.session() as session:
        result = session.run(cypher, params)
        # Consume the result while session is still open
        records = list(result)
        return [dict(record) for record in records]


def _validate_cypher_query(query: str) -> tuple[bool, str]:
    """
    Validate a Cypher query for safety.

    Returns:
        (is_valid, error_message) - If is_valid is False, error_message explains why.
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"

    # Normalize query for checking (uppercase, remove comments)
    normalized = re.sub(r"//.*?$", "", query, flags=re.MULTILINE)  # Remove single-line comments
    normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL)  # Remove multi-line comments
    normalized = normalized.upper()

    # Dangerous keywords that should be blocked
    dangerous_keywords = [
        "DELETE",
        "DROP",
        "DETACH",
        "REMOVE",
    ]

    # Check for dangerous keywords
    for keyword in dangerous_keywords:
        # Use word boundaries to avoid false positives
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, normalized):
            return (
                False,
                f"Query contains dangerous operation: {keyword}. Only read-only queries are allowed.",
            )

    # Block CREATE/MERGE/SET operations
    write_keywords = ["CREATE", "MERGE", "SET"]
    for keyword in write_keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, normalized):
            return (
                False,
                f"Query contains write operation: {keyword}. Only read-only queries (MATCH, RETURN, etc.) are allowed.",
            )

    # Ensure query contains at least one safe read operation
    safe_keywords = ["MATCH", "RETURN", "WITH", "UNWIND", "CALL"]
    has_safe_operation = any(
        re.search(r"\b" + re.escape(kw) + r"\b", normalized) for kw in safe_keywords
    )

    if not has_safe_operation:
        return False, "Query must contain at least one read operation (MATCH, RETURN, WITH, etc.)"

    return True, ""


_MAX_VALUE_DISPLAY_LEN = 30


def _format_query_results(rows: list[dict[str, Any]]) -> str:
    """Format query rows as a table-like string."""
    all_keys = sorted(set().union(*(row.keys() for row in rows)))
    out = ["QUERY RESULTS:", "-" * 50]
    header = " | ".join(f"{k:20}" for k in all_keys)
    out.extend([header, "-" * len(header)])
    for row in rows:
        values = []
        for k in all_keys:
            val = row.get(k)
            if val is None:
                val_str = "null"
            elif isinstance(val, (list, tuple)):
                val_str = f"[{', '.join(str(v) for v in val)}]"
            elif isinstance(val, dict):
                val_str = str(val)
            else:
                val_str = str(val)
            if len(val_str) > _MAX_VALUE_DISPLAY_LEN:
                val_str = val_str[: _MAX_VALUE_DISPLAY_LEN - 3] + "..."
            values.append(f"{val_str:20}")
        out.append(" | ".join(values))
    out.append(f"\nTotal rows: {len(rows)}")
    return "\n".join(out)


def execute_cypher_query(driver: Driver, query: str, params: dict[str, Any] | None = None) -> str:
    """
    Execute a Cypher query with validation.

    Args:
        driver: Neo4j driver instance
        query: Cypher query string
        params: Optional query parameters dictionary

    Returns:
        Formatted result string or error message
    """
    is_valid, error_msg = _validate_cypher_query(query)
    if not is_valid:
        logger.warning("Cypher validation failed: %s", error_msg)
        return f"Query validation failed: {error_msg}"

    try:
        rows = _run_query(driver, query, **params) if params else _run_query(driver, query)
    except Exception as e:
        logger.error("Cypher execution failed: %s", e, exc_info=True)
        return f"Error executing query: {type(e).__name__}: {e}"

    if not rows:
        return "Query executed successfully but returned no results."
    return _format_query_results(rows)
