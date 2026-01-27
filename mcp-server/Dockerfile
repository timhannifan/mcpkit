FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Create working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml .
COPY uv.lock* .

# Resolve and install Python packages from pyproject/uv.lock
RUN /usr/local/bin/uv venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN uv sync

# Copy application code
COPY server.py neo4j_demo.py ./

# Expose MCP server port
EXPOSE 8090

# Run the MCP server
CMD ["python", "-u", "server.py"]
