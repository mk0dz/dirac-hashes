# Deployment Files for Dirac Hashes

This directory contains files for deploying the Dirac Hashes package and associated services using Docker.

## Contents

- `Dockerfile`: Configuration for building a Docker image of the application
- `docker-compose.yml`: Docker Compose configuration for running the full stack
- `.dockerignore`: List of files to exclude from the Docker build context

## Usage

### Building the Docker Image

```bash
cd /path/to/dirac-hashes
docker build -t dirac-hashes -f deployment/Dockerfile .
```

### Running with Docker Compose

```bash
cd /path/to/dirac-hashes
docker-compose -f deployment/docker-compose.yml up
```

This will start both the API and frontend services as defined in the docker-compose.yml file.

## Customization

You can modify the Dockerfile and docker-compose.yml to suit your specific deployment needs. Environment variables and other configuration options can be adjusted in these files. 