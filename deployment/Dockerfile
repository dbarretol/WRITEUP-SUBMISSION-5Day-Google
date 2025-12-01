# Use Python 3.10 slim image for a small footprint
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Streamlit configuration
    STREAMLIT_SERVER_PORT=8080 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    # Vertex AI configuration defaults
    GOOGLE_GENAI_USE_VERTEXAI=true \
    # Add the virtual environment to the path (Automatic activation)
    PATH="/app/.venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# -------------------------------------------------------------------
# SECURITY BEST PRACTICE: Create a non-root user with home directory
# -------------------------------------------------------------------
RUN groupadd -r appuser && useradd -r -g appuser -m -d /home/appuser appuser

# Set Streamlit to use /tmp for its config (writable by appuser)
ENV STREAMLIT_CONFIG_DIR=/tmp/.streamlit \
    HOME=/home/appuser

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv (without the local package)
# We use --no-install-project to skip installing the local package as editable
RUN uv sync --frozen --no-dev --no-install-project

# Copy the rest of the application code
COPY . .

# Now install the local package in non-editable mode
RUN uv pip install --no-deps .

# -------------------------------------------------------------------
# SECURITY BEST PRACTICE: Change ownership and switch user
# -------------------------------------------------------------------
RUN chown -R appuser:appuser /app /home/appuser
USER appuser

# Expose the port Cloud Run expects
EXPOSE 8080

# Run the Streamlit application
CMD ["streamlit", "run", "app.py"]