# Dirac Hashes Deployment

This directory contains the files needed to deploy the Dirac Hashes application using Docker.

## Quick Start

To build and run the Docker container:

```bash
# Navigate to the project root directory
cd /path/to/dirac-hashes

# Build and start the container
docker-compose -f deployment/docker-compose.yml up -d

# To view logs
docker-compose -f deployment/docker-compose.yml logs -f

# To stop the container
docker-compose -f deployment/docker-compose.yml down
```

## Accessing the Application

Once the container is running, you can access:

- **Frontend UI**: http://localhost:8080
- **API Endpoint**: http://localhost:8000

## Environment Variables

You can customize the deployment with these environment variables:

- `PYTHONPATH`: Path to the Python modules
- `PYTHONUNBUFFERED`: Ensures Python output is sent straight to the terminal

## Development Mode

The container mounts source directories as volumes, allowing you to make changes to the code and see them reflected immediately without rebuilding the container.

## Troubleshooting

If you encounter any issues:

1. Check the logs: `docker-compose -f deployment/docker-compose.yml logs`
2. Ensure ports 8000 and 8080 are available on your host machine
3. Verify that all dependencies are correctly installed
4. Check the healthcheck status with `docker ps`

## Production Deployment

For production deployment, consider:

1. Using a production-grade WSGI server
2. Setting up proper SSL/TLS certificates
3. Configuring a reverse proxy (Nginx or Apache)
4. Setting up proper authentication and authorization 