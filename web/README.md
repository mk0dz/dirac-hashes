# Web Components for Dirac Hashes

This directory contains the web-related components for the Dirac Hashes project:

## Contents

- `frontend/`: Frontend HTML, CSS, and JavaScript files for the demo UI
- `api/`: FastAPI backend API implementation
- `render.yaml`: Configuration for deployment on Render
- `vercel.json`: Configuration for deployment on Vercel

## Frontend Documentation

The frontend interface provides a user-friendly way to interact with the Dirac Hashes project. It includes several key pages:

- **Home**: Introduction to the project with key features
- **Hash Testing**: Generate and compare different hash algorithms
- **Signature Testing**: Test quantum-resistant signature schemes
- **KEM Testing**: Test Key Encapsulation Mechanism algorithms

### Key Files and Structure

- `frontend/index.html`: Main entry point and landing page
- `frontend/hash-test.html`: Hash generation and testing interface
- `frontend/test-compare.html`: Compare different hash algorithms
- `frontend/js/app.js`: Main JavaScript with API integration
- `frontend/css/`: Styling for the application

### API Integration

The frontend connects to the API using the URL specified in `js/app.js`. For local development, it uses `http://localhost:8000`. For production, it uses `https://dirac-hashes.onrender.com`.

To change the API endpoint:
1. Edit `frontend/js/app.js`
2. Update the `API_URL` constant with your deployment URL

### Performance and Security Visualizations

The application includes interactive charts that visualize:

1. Performance metrics comparing different hash algorithms
2. Security level comparisons between algorithms
3. Quantum resistance ratings

These visualizations can be found in:
- Hash comparison page
- Test-compare results section
- Security analysis page

## Running Locally

### Frontend

```bash
cd frontend
python -m http.server 8080
```

This will start a local web server on port 8080.

### API

```bash
cd api
uvicorn run_api:app --reload --port 8000
```

This will start the API server on port 8000.

## Hash Algorithm Q&A

### What makes Dirac Hashes quantum-resistant?

Dirac Hashes use post-quantum cryptographic principles and specialized hash functions designed to withstand attacks from quantum computers. The algorithms specifically resist Grover's and Shor's algorithms, which could potentially break traditional hash functions.

### How do the different algorithms compare?

- **Improved**: Our fastest algorithm with excellent quantum resistance
- **Grover**: Algorithm designed specifically to resist Grover's quantum attack
- **Shor**: Algorithm designed specifically to resist Shor's quantum factoring algorithm

### What are the security levels?

1. **Standard** (128-bit): Suitable for regular applications
2. **High** (192-bit): Recommended for sensitive information
3. **Very High** (256-bit): Highest security for critical applications

### How can I interpret the performance graphs?

The performance visualization shows:
- Execution time (lower is better)
- Memory usage (lower is better)
- Input/output size ratios
- Avalanche effect metrics

These metrics help you choose the right algorithm for your specific use case balancing security and performance needs.

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