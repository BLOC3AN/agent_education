#!/bin/bash
# AWS Free Tier Deployment Script
# This script helps deploy the Agent Education app to AWS EC2 Free Tier

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="agent-education"
DOCKER_COMPOSE_FILE="aws/docker-compose.yml"
ENV_FILE="aws/.env.aws"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  AWS Free Tier Deployment${NC}"
    echo -e "${BLUE}  Agent Education Platform${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    print_step "Checking prerequisites..."

    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi

    # Check if .env.aws file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_error "Environment file $ENV_FILE not found. Please copy and configure it."
        exit 1
    fi

    echo -e "${GREEN}✅ All prerequisites met${NC}"
}

setup_environment() {
    print_step "Setting up environment..."

    # Create data directory if it doesn't exist
    mkdir -p data/agent_data

    # Set proper permissions
    chmod -R 755 data/

    echo -e "${GREEN}✅ Environment setup complete${NC}"
}

build_and_deploy() {
    print_step "Building and deploying application..."

    # Stop existing containers
    print_step "Stopping existing containers..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down || true

    # Build new image
    print_step "Building Docker image..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache

    # Start services
    print_step "Starting services..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

    echo -e "${GREEN}✅ Deployment complete${NC}"
}

check_health() {
    print_step "Checking application health..."

    # Wait for application to start
    sleep 30

    # Check if container is running
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
        echo -e "${GREEN}✅ Application is running${NC}"

        # Try to access health endpoint
        if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Application health check passed${NC}"
            echo -e "${GREEN}🎉 Application is accessible at: http://localhost:8501${NC}"
        else
            print_warning "Application is running but health check failed. It might still be starting up."
        fi
    else
        print_error "Application failed to start. Check logs with: docker-compose -f $DOCKER_COMPOSE_FILE logs"
        exit 1
    fi
}

show_logs() {
    print_step "Showing application logs..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" logs --tail=50
}

show_status() {
    print_step "Application status:"
    docker-compose -f "$DOCKER_COMPOSE_FILE" ps

    print_step "Resource usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

cleanup() {
    print_step "Cleaning up..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" down
    docker system prune -f
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Main script
main() {
    print_header

    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            setup_environment
            build_and_deploy
            check_health
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "stop")
            docker-compose -f "$DOCKER_COMPOSE_FILE" down
            echo -e "${GREEN}✅ Application stopped${NC}"
            ;;
        "restart")
            docker-compose -f "$DOCKER_COMPOSE_FILE" restart
            echo -e "${GREEN}✅ Application restarted${NC}"
            ;;
        "cleanup")
            cleanup
            ;;
        "help")
            echo "Usage: $0 [command]"
            echo "Commands:"
            echo "  deploy   - Deploy the application (default)"
            echo "  logs     - Show application logs"
            echo "  status   - Show application status and resource usage"
            echo "  stop     - Stop the application"
            echo "  restart  - Restart the application"
            echo "  cleanup  - Stop and clean up all resources"
            echo "  help     - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
