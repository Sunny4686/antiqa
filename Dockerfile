FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project

COPY src ./src
COPY data/kommuner.csv ./kommuner.csv
RUN uv sync --locked --no-dev

RUN useradd --create-home app && mkdir -p /app/data && chown -R app /app/data
USER app

EXPOSE 8000
HEALTHCHECK --interval=60s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["uv", "run", "--no-sync", "fyndjakt", "serve", "--host", "0.0.0.0", "--port", "8000"]
