#!/bin/bash

# Memora Core Server Deployment Script
# Server: 185.231.59.157
# Username: root
# Password: Azad@12862525

set -e

echo "🚀 Deploying Memora Core to Server 185.231.59.157"
echo "================================================="

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

# Server configuration
SERVER_IP="185.231.59.157"
SERVER_USER="root"
SERVER_PASSWORD="Azad@12862525"
APP_DIR="/opt/memora_core"

# Function to run commands on server via SSH
run_on_server() {
    sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
}

# Function to copy files to server
copy_to_server() {
    sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no -r "$1" "$SERVER_USER@$SERVER_IP:$2"
}

# Check if sshpass is installed
if ! command -v sshpass &> /dev/null; then
    print_error "sshpass is required but not installed."
    echo "Install it with:"
    echo "  Ubuntu/Debian: sudo apt install sshpass"
    echo "  macOS: brew install sshpass"
    echo "  Windows: Use WSL or install via package manager"
    exit 1
fi

# Test server connection
print_step "Testing server connection..."
if run_on_server "echo 'Connection successful'"; then
    print_status "✅ Server connection established"
else
    print_error "❌ Failed to connect to server"
    exit 1
fi

# Create application directory on server
print_step "Creating application directory on server..."
run_on_server "mkdir -p $APP_DIR"
run_on_server "mkdir -p $APP_DIR/logs"
run_on_server "mkdir -p $APP_DIR/media"
run_on_server "mkdir -p $APP_DIR/staticfiles"

# Copy project files to server
print_step "Copying project files to server..."
print_status "This may take a few minutes depending on your internet connection..."

# Create a temporary archive to speed up transfer
print_status "Creating temporary archive..."
tar -czf memora_core_deploy.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.log' \
    --exclude='venv' \
    --exclude='env' \
    --exclude='.env' \
    --exclude='media/*' \
    --exclude='staticfiles/*' \
    --exclude='*.tar.gz' \
    --exclude='*.zip' \
    .

# Copy archive to server
copy_to_server "memora_core_deploy.tar.gz" "$APP_DIR/"

# Extract archive on server
print_step "Extracting files on server..."
run_on_server "cd $APP_DIR && tar -xzf memora_core_deploy.tar.gz && rm memora_core_deploy.tar.gz"

# Clean up local archive
rm -f memora_core_deploy.tar.gz

# Make scripts executable
run_on_server "chmod +x $APP_DIR/*.sh"
run_on_server "chmod +x $APP_DIR/docker/entrypoint.sh"

# Copy production environment file
print_step "Setting up production environment..."
run_on_server "cp $APP_DIR/env.production.example $APP_DIR/.env"

# Update environment file with server-specific settings
run_on_server "sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=185.231.59.157,localhost,127.0.0.1/' $APP_DIR/.env"
run_on_server "sed -i 's/your-super-secret-key-change-this-in-production/$(openssl rand -base64 32)/' $APP_DIR/.env"

# Run server setup script
print_step "Running server setup script..."
run_on_server "cd $APP_DIR && bash server_setup.sh"

# Wait for services to be ready
print_step "Waiting for services to be ready..."
sleep 30

# Run deployment script
print_step "Running deployment script..."
run_on_server "cd $APP_DIR && bash deploy-ubuntu.sh"

# Check if application is running
print_step "Checking application status..."
sleep 10

if run_on_server "curl -f http://localhost:80/ >/dev/null 2>&1"; then
    print_status "✅ Application is running successfully!"
else
    print_warning "⚠️  Application might not be fully ready yet. Checking logs..."
    run_on_server "cd $APP_DIR && docker-compose logs --tail=20"
fi

# Final status
print_status "🎉 Deployment completed!"
echo ""
echo "📋 Deployment Summary:"
echo "  🌐 Application URL: http://185.231.59.157"
echo "  🔧 Admin Panel: http://185.231.59.157/admin"
echo "  👤 Default Admin: admin / admin123"
echo "  📁 App Directory: $APP_DIR"
echo ""
echo "🔧 Useful Commands (run on server):"
echo "  - Check status: docker-compose ps"
echo "  - View logs: docker-compose logs -f"
echo "  - Restart app: docker-compose restart"
echo "  - Stop app: docker-compose down"
echo "  - Update app: ./deploy-ubuntu.sh"
echo ""
echo "🔒 Security Reminders:"
echo "  1. Change admin password: docker-compose exec web python manage.py changepassword admin"
echo "  2. Add your OpenAI API key to .env file"
echo "  3. Set up SSL certificates for HTTPS"
echo "  4. Configure regular backups"
echo ""
print_status "📖 Access your application at: http://185.231.59.157"





















