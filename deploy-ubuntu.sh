#!/bin/bash

# Memora Core Ubuntu Deployment Script
# Optimized for Ubuntu servers

set -e

echo "🚀 Starting Memora Core Deployment on Ubuntu..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root. Use a regular user with sudo privileges."
    exit 1
fi

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

# Update system
print_step "Updating Ubuntu system..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_step "Installing required packages..."
sudo apt install -y curl wget git software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Install Docker
print_step "Installing Docker..."
if ! command -v docker &> /dev/null; then
    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    print_status "Docker installed. You may need to log out and back in for group changes to take effect."
else
    print_status "Docker is already installed."
fi

# Install Docker Compose (standalone)
print_step "Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed."
else
    print_status "Docker Compose is already installed."
fi

# Start Docker service
print_step "Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p docker/nginx/ssl
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

# Make entrypoint script executable
chmod +x docker/entrypoint.sh

# Stop existing containers if running
print_step "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build Docker images
print_step "Building Docker images..."
docker-compose build --no-cache

# Start services
print_step "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_step "Waiting for services to be ready..."
sleep 30

# Check if services are running
print_step "Checking service status..."
docker-compose ps

# Run database migrations
print_step "Running database migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collect static files
print_step "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_step "Checking for superuser..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Check application health
print_step "Checking application health..."
sleep 10

if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
    print_status "✅ Application is healthy!"
else
    print_warning "⚠️  Health check failed. Checking logs..."
    docker-compose logs --tail=20
fi

# Configure firewall
print_step "Configuring UFW firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Final status
print_status "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "  - Application URL: http://185.231.59.157"
echo "  - Admin URL: http://185.231.59.157/admin"
echo "  - Default admin credentials: admin/admin123"
echo "  - Database: PostgreSQL (containerized)"
echo "  - Cache: Redis (containerized)"
echo "  - Reverse Proxy: Nginx (containerized)"
echo "  - Firewall: UFW configured"
echo ""
echo "🔧 Useful Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Restart: docker-compose restart"
echo "  - Stop: docker-compose down"
echo "  - Update: ./deploy-ubuntu.sh"
echo "  - Check status: docker-compose ps"
echo ""
print_warning "⚠️  Important Security Steps:"
echo "  1. Change default admin password: docker-compose exec web python manage.py changepassword admin"
echo "  2. Configure SSL certificates for HTTPS"
echo "  3. Set up regular backups"
echo "  4. Monitor system resources"
echo ""
print_status "📖 For more information, see DEPLOYMENT.md"
print_status "🔒 Firewall is enabled and configured for SSH, HTTP, and HTTPS"
