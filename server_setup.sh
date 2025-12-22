#!/bin/bash

# Server Setup Script for Memora Core
# Run this on your server (185.231.59.157)

set -e

echo "🚀 Setting up Memora Core on Server"
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

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_warning "Running as root. This is fine for initial setup."
fi

# Update system packages
print_step "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages
print_step "Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl wget unzip

# Install Docker and Docker Compose
print_step "Installing Docker and Docker Compose..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
print_step "Creating application directory..."
sudo mkdir -p /opt/memora_core
sudo chown $USER:$USER /opt/memora_core

# Configure PostgreSQL
print_step "Configuring PostgreSQL..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE memora_db;"
sudo -u postgres psql -c "CREATE USER memora_user WITH PASSWORD 'memora_password_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;"
sudo -u postgres psql -c "ALTER USER memora_user CREATEDB;"

# Configure Redis
print_step "Configuring Redis..."
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Configure Nginx
print_step "Configuring Nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/memora_core > /dev/null <<EOF
server {
    listen 80;
    server_name 185.231.59.157;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /opt/memora_core/staticfiles/;
    }

    location /media/ {
        alias /opt/memora_core/media/;
    }
}
EOF

# Enable the site
sudo ln -sf /etc/nginx/sites-available/memora_core /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# Configure firewall
print_step "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# Create production environment file
print_step "Creating production environment file..."
cat > /opt/memora_core/.env <<EOF
# Production Environment Configuration
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=185.231.59.157,localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password_2024
DB_HOST=localhost
DB_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# App Configuration
APP_NAME=Memora
APP_VERSION=1.0.0
APP_ENVIRONMENT=production
EOF

print_status "✅ Server setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your project files to /opt/memora_core/"
echo "2. Edit /opt/memora_core/.env with your actual API keys"
echo "3. Run the deployment script: ./deploy.sh"
echo ""
echo "🔧 Useful commands:"
echo "  - Check services: sudo systemctl status postgresql redis-server nginx"
echo "  - View logs: sudo journalctl -u nginx -f"
echo "  - Restart services: sudo systemctl restart postgresql redis-server nginx"
echo ""
print_warning "⚠️  Don't forget to:"
echo "  - Change the SECRET_KEY in .env file"
echo "  - Add your OpenAI API key"
echo "  - Configure SSL certificates for HTTPS"
echo "  - Set up regular backups"
