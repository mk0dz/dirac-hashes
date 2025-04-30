#!/bin/bash
# Dirac Hashes deployment script

set -e  # Exit on error

# Display usage information
function show_usage {
  echo "Dirac Hashes Deployment Script"
  echo "------------------------------"
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  build    - Build the Docker image"
  echo "  run      - Run the container (will build first if needed)"
  echo "  stop     - Stop the running container"
  echo "  restart  - Restart the container"
  echo "  logs     - Show container logs"
  echo "  status   - Show container status"
  echo "  help     - Show this help message"
  echo ""
}

# Build the Docker image
function build_image {
  echo "Building Dirac Hashes Docker image..."
  docker build -t dirac-hashes -f Dockerfile .
  echo "Build completed successfully."
}

# Run the container
function run_container {
  echo "Starting Dirac Hashes container..."
  docker run -d --name dirac-hashes-app \
    -p 8000:8000 -p 8080:8080 \
    --restart unless-stopped \
    dirac-hashes
  echo "Container started. Frontend: http://localhost:8080, API: http://localhost:8000"
}

# Stop the container
function stop_container {
  echo "Stopping Dirac Hashes container..."
  docker stop dirac-hashes-app
  docker rm dirac-hashes-app
  echo "Container stopped and removed."
}

# Show container logs
function show_logs {
  echo "Showing logs for Dirac Hashes container..."
  docker logs -f dirac-hashes-app
}

# Show container status
function show_status {
  echo "Dirac Hashes container status:"
  docker ps -a | grep dirac-hashes-app || echo "No container found"
}

# Process commands
case "$1" in
  build)
    build_image
    ;;
  run)
    # Check if image exists, build if needed
    if [[ "$(docker images -q dirac-hashes 2> /dev/null)" == "" ]]; then
      build_image
    fi
    
    # Check if container is already running
    if docker ps -a | grep -q dirac-hashes-app; then
      echo "Container already exists. Stopping it first..."
      stop_container
    fi
    
    run_container
    ;;
  stop)
    stop_container
    ;;
  restart)
    if docker ps -a | grep -q dirac-hashes-app; then
      stop_container
    fi
    run_container
    ;;
  logs)
    show_logs
    ;;
  status)
    show_status
    ;;
  help|*)
    show_usage
    ;;
esac 