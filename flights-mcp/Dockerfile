# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS uv

# Install the project into /app
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
COPY pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD src /app/src
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --no-editable

FROM python:3.12-slim-bookworm

# Install socat
RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd --gid 1000 app && useradd --uid 1000 --gid app --shell /bin/bash --create-home app

WORKDIR /app

COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Define environment variable for Duffel API key
ENV DUFFEL_API_KEY_LIVE=your_duffel_live_api_key_here

# Expose port 6000
EXPOSE 6000

# Start the MCP server with socat to expose on port 6000
CMD ["socat", "TCP-LISTEN:6000,reuseaddr,fork", "EXEC:flights-mcp"]
