# Dirac Hashes

Quantum-inspired cryptographic hash functions for future-proof security.

## Quick Start

See the full documentation in the [info/README.md](info/README.md) file.

### Main Features

- Quantum-inspired hash functions
- Post-quantum signature schemes
- Secure key generation and HMAC

### Project Structure

- **src/**: Source code for the core library
- **api/**: FastAPI implementation for the API
- **frontend/**: Web interface for demonstrations
- **tests/**: Organized test suite
  - **unit/**: Unit tests
  - **integration/**: Integration tests
  - **debug/**: Debug scripts
- **info/**: Documentation
- **benchmark.py**: Benchmarking with visualization
- **demo.py**: Interactive demonstrations

### Quick Usage

```bash
# Run the interactive demo
python demo.py

# Run benchmarks with visualization
python benchmark.py

# Run the API server
python run_api.py

# Run the frontend
python serve_frontend.py

# Run tests
pytest tests/
```

## Docker Deployment

This project can be easily deployed using Docker:

### Building and Running with Docker

```bash
# Build the image
docker build -t dirac-hashes .

# Run the API server
docker run -p 8000:8000 dirac-hashes

# Run the frontend (in a different terminal)
docker run -p 8080:8080 dirac-hashes python serve_frontend.py
```

### Using Docker Compose

For the easiest deployment, use Docker Compose to run both services:

```bash
# Start both API and frontend
docker-compose up

# Or run in detached mode
docker-compose up -d

# To stop all services
docker-compose down
```

The API will be available at http://localhost:8000 and the frontend at http://localhost:8080.

## Development

For development, it's recommended to use a virtual environment:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

Full documentation is available in the [info](./info/) directory. 