FROM python:3.12-slim

# Prevent Python from creating .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Show Python logs immediately.
ENV PYTHONUNBUFFERED=1

# Do not cache downloaded Python packages.
ENV PIP_NO_CACHE_DIR=1

# Streamlit configuration.
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Application directory inside the container.
WORKDIR /app

# Install curl for the container health check.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first to improve Docker caching.
COPY requirements.txt /app/requirements.txt

# Install Python dependencies.
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /app/requirements.txt

# Copy the complete project into the container.
COPY . /app

# Create runtime folders and a non-root user.
RUN mkdir -p /app/input /app/output /app/temp \
    && useradd --create-home --uid 10001 esaa \
    && chown -R esaa:esaa /app

# Run the application as a non-root user.
USER esaa

# Streamlit port.
EXPOSE 8501

# Check whether Streamlit is healthy.
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Start the Streamlit application.
CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true", "--browser.gatherUsageStats=false"]