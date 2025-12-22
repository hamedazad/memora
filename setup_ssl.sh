#!/bin/bash

# SSL Setup Script for Memora Core
# Run this AFTER the main deployment is working
# This will set up Let's Encrypt SSL certificates

set -e

echo "🔒 Setting up SSL certificates for Memora Core"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
if [ "$EUID" -ne 0 ]; then
    print_error "Please run this script as root"
    exit 1
fi

# Install Certbot
print_step "Installing Certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# Stop containers temporarily
print_step "Stopping containers temporarily..."
cd /opt/memora_core
docker-compose down

# Get SSL certificate
print_step "Obtaining SSL certificate..."
certbot certonly --standalone -d 185.231.59.157 --email admin@185.231.59.157 --agree-tos --no-eff-email

# Copy certificates to Docker volume
print_step "Setting up certificates for Docker..."
mkdir -p /opt/memora_core/docker/nginx/ssl
cp /etc/letsencrypt/live/185.231.59.157/fullchain.pem /opt/memora_core/docker/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/185.231.59.157/privkey.pem /opt/memora_core/docker/nginx/ssl/key.pem
chmod 644 /opt/memora_core/docker/nginx/ssl/cert.pem
chmod 600 /opt/memora_core/docker/nginx/ssl/key.pem

# Update Nginx configuration to enable HTTPS
print_step "Updating Nginx configuration..."
sed -i 's/# server {/server {/' /opt/memora_core/docker/nginx/nginx.conf
sed -i 's/#     listen 443/    listen 443/' /opt/memora_core/docker/nginx/nginx.conf
sed -i 's/#     server_name/    server_name/' /opt/memora_core/docker/nginx/nginx.conf
sed -i 's/# ssl_/ssl_/g' /opt/memora_core/docker/nginx/nginx.conf
sed -i 's/# add_header/add_header/g' /opt/memora_core/docker/nginx/nginx.conf

# Add HTTP to HTTPS redirect
sed -i '/location \/ {/,/}/c\
        # Redirect HTTP to HTTPS\
        return 301 https://$server_name$request_uri;' /opt/memora_core/docker/nginx/nginx.conf

# Restart containers
print_step "Starting containers with SSL..."
docker-compose up -d

# Set up automatic renewal
print_step "Setting up automatic certificate renewal..."
echo "0 12 * * * /usr/bin/certbot renew --quiet --deploy-hook \"cd /opt/memora_core && docker-compose restart nginx\"" | crontab -

print_status "✅ SSL setup completed!"
echo ""
echo "🔒 Your site is now available at:"
echo "  - HTTPS: https://185.231.59.157"
echo "  - HTTP: http://185.231.59.157 (redirects to HTTPS)"
echo ""
echo "📋 SSL Certificate Details:"
echo "  - Certificate: /etc/letsencrypt/live/185.231.59.157/fullchain.pem"
echo "  - Private Key: /etc/letsencrypt/live/185.231.59.157/privkey.pem"
echo "  - Auto-renewal: Configured via cron"
echo ""
print_warning "⚠️  Certificate will auto-renew every 12 hours (if needed)"





















