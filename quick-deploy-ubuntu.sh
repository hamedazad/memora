#!/bin/bash

# Quick Ubuntu Deployment Script for Memora Core
# One-command deployment for Ubuntu servers

set -e

echo "🚀 Quick Ubuntu Deployment for Memora Core..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run as root. Use a regular user with sudo privileges."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f env.production.example ]; then
        cp env.production.example .env
        echo "✅ Created .env file. Please edit it with your production values before continuing."
        echo "📝 Edit .env file and run this script again."
        exit 1
    else
        echo "❌ No .env template found. Please create .env file manually."
        exit 1
    fi
fi

echo "📦 Installing Docker and dependencies..."
sudo apt update -qq
sudo apt install -y curl wget git software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update -qq
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
    sudo usermod -aG docker $USER
    echo "✅ Docker installed. You may need to log out and back in."
fi

# Install Docker Compose if not present
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

echo "🔧 Setting up application..."
mkdir -p docker/nginx/ssl logs media staticfiles
chmod +x docker/entrypoint.sh

echo "🏗️  Building and starting containers..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🗄️  Setting up database..."
docker-compose exec -T web python manage.py migrate --noinput
docker-compose exec -T web python manage.py collectstatic --noinput

echo "👤 Creating admin user..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Admin user created: admin/admin123')
else:
    print('ℹ️  Admin user already exists')
"

echo "🔒 Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ Deployment completed!"
echo ""
echo "🌐 Access your application:"
echo "   Main App: http://185.231.59.157"
echo "   Admin: http://185.231.59.157/admin"
echo "   Credentials: admin/admin123"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Restart: docker-compose restart"
echo "   Status: docker-compose ps"
echo ""
echo "🔒 Don't forget to change the admin password!"
