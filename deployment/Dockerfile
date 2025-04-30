FROM python:3.9-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY api/ ./api/
COPY frontend/ ./frontend/
COPY run_api.py .
COPY serve_frontend.py .
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Expose ports for API and frontend
EXPOSE 8000 8080

# Default command to run the API server
CMD ["python", "run_api.py"] 