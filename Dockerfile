FROM python:3.9-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Install common scientific packages
RUN pip install numpy scipy pandas matplotlib seaborn scikit-learn

# Copy source code with the correct directory structure
COPY src/ ./src/
COPY web/ ./web/
COPY tests/ ./tests/
COPY tools/ ./tools/
COPY run_api_direct.py .
COPY run_frontend_direct.py .
COPY setup.py .
COPY pyproject.toml .
COPY README.md .

# Install additional dependencies
RUN pip install uvicorn fastapi pydantic requests chardet

# Install the package in development mode
RUN pip install -e .

# Expose ports for API and frontend
EXPOSE 8000 8080

# Create a startup script
RUN echo '#!/bin/bash\npython run_api_direct.py & python run_frontend_direct.py & wait' > /app/start.sh
RUN chmod +x /app/start.sh

# Default command to run both services
CMD ["/app/start.sh"] 