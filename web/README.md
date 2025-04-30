# Web Components for Dirac Hashes

This directory contains the web-related components for the Dirac Hashes project:

## Contents

- `frontend/`: Frontend HTML, CSS, and JavaScript files for the demo UI
- `api/`: FastAPI backend API implementation
- `serve_frontend.py`: Simple script to serve the frontend locally
- `run_api.py`: Script to run the API server locally
- `render.yaml`: Configuration for deployment on Render
- `vercel.json`: Configuration for deployment on Vercel

## Running Locally

### Frontend

```bash
python serve_frontend.py
```

This will start a local web server on port 8000.

### API

```bash
python run_api.py
```

This will start the API server on port 8080.

## Deployment

The project can be deployed on Render or Vercel using the provided configuration files.

### Requirements

The web components require the following Python packages:

```
fastapi>=0.70.0
uvicorn>=0.15.0
python-multipart>=0.0.5
```

Plus all the dependencies of the main `dirac-hashes` package. 