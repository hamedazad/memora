#!/bin/bash

# Memora Core Deployment Script
# This script automates the deployment process

set -e

echo "🚀 Starting Memora Core Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    if [ -f env.production.example ]; then
        cp env.production.example .env
        print_status "Created .env file from template. Please edit it with your production values."
        print_warning "You need to edit .env file before continuing!"
        exit 1
    else
        print_error "No .env template found. Please create .env file manually."
        exit 1
    fi
fi

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

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p docker/nginx/ssl
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Make entrypoint script executable
chmod +x docker/entrypoint.sh

# Stop existing containers if running
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build Docker images
print_status "Building Docker images..."
docker-compose build --no-cache

# Start services
print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_status "Checking service status..."
docker-compose ps

# Run database migrations
print_status "Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collect static files
print_status "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_status "Checking for superuser..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Check application health
print_status "Checking application health..."
sleep 10

if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
    print_status "✅ Application is healthy!"
else
    print_warning "⚠️  Health check failed. Checking logs..."
    docker-compose logs --tail=20
fi

# Final status
print_status "🎉 Deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "  - Application URL: http://185.231.59.157"
echo "  - Admin URL: http://185.231.59.157/admin"
echo "  - Default admin credentials: admin/admin123"
echo "  - Database: PostgreSQL (containerized)"
echo "  - Cache: Redis (containerized)"
echo "  - Reverse Proxy: Nginx (containerized)"
echo ""
echo "🔧 Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Restart: docker-compose restart"
echo "  - Stop: docker-compose down"
echo "  - Update: ./deploy.sh"
echo ""
print_warning "⚠️  Don't forget to:"
echo "  1. Change default admin password"
echo "  2. Configure SSL certificates"
echo "  3. Set up firewall rules"
echo "  4. Configure backups"
echo ""
print_status "📖 For more information, see DEPLOYMENT.md"
