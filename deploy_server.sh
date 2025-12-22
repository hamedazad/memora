#!/bin/bash

# Server Deployment Script for Memora Core (Traditional Deployment)
# Run this on your server after copying project files

set -e

echo "🚀 Deploying Memora Core on Server"
echo "=================================="

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please create it first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f manage.py ]; then
    print_error "manage.py not found. Please run this script from the project root."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_step "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_step "Installing Python dependencies..."
pip install -r requirements.txt

# Install Gunicorn for production
print_step "Installing Gunicorn..."
pip install gunicorn

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p staticfiles
mkdir -p media
mkdir -p logs

# Run database migrations
print_step "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
print_step "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
print_step "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Create systemd service file
print_step "Creating systemd service..."
sudo tee /etc/systemd/system/memora_core.service > /dev/null <<EOF
[Unit]
Description=Memora Core Django Application
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=/opt/memora_core
Environment=PATH=/opt/memora_core/venv/bin
ExecStart=/opt/memora_core/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 120 memora_project.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
print_step "Enabling and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable memora_core
sudo systemctl start memora_core

# Check service status
print_step "Checking service status..."
sleep 5
if sudo systemctl is-active --quiet memora_core; then
    print_status "✅ Memora Core service is running"
else
    print_error "❌ Service failed to start. Checking logs..."
    sudo journalctl -u memora_core --no-pager -l
    exit 1
fi

# Reload Nginx
print_step "Reloading Nginx..."
sudo systemctl reload nginx

# Test the application
print_step "Testing application..."
sleep 10
if curl -f http://185.231.59.157/ >/dev/null 2>&1; then
    print_status "✅ Application is accessible!"
else
    print_warning "⚠️  Application might not be accessible yet. Checking logs..."
    sudo journalctl -u memora_core --no-pager -l --lines=20
fi

print_status "🎉 Deployment completed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "  - Application URL: http://185.231.59.157"
echo "  - Admin URL: http://185.231.59.157/admin"
echo "  - Default admin credentials: admin/admin123"
echo "  - Service: memora_core (systemd)"
echo "  - Database: PostgreSQL"
echo "  - Cache: Redis"
echo "  - Reverse Proxy: Nginx"
echo ""
echo "🔧 Useful Commands:"
echo "  - View logs: sudo journalctl -u memora_core -f"
echo "  - Restart: sudo systemctl restart memora_core"
echo "  - Stop: sudo systemctl stop memora_core"
echo "  - Status: sudo systemctl status memora_core"
echo "  - Nginx logs: sudo tail -f /var/log/nginx/access.log"
echo ""
print_warning "⚠️  Don't forget to:"
echo "  - Change default admin password"
echo "  - Configure SSL certificates"
echo "  - Set up regular backups"
echo "  - Monitor logs for errors"
