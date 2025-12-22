#!/bin/bash

# Transfer Memora Core to Ubuntu Server (185.231.59.15)
# This script prepares and transfers the application to your server

set -e

echo "🚀 Preparing Memora Core for transfer to Ubuntu server..."

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

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from production template..."
    if [ -f env.production ]; then
        cp env.production .env
        print_status "Created .env file from production template."
        print_warning "⚠️  IMPORTANT: Edit .env file with your actual values before transferring!"
        echo ""
        echo "Required changes in .env:"
        echo "  - SECRET_KEY: Generate a long random string"
        echo "  - OPENAI_API_KEY: Add your OpenAI API key"
        echo "  - DB_PASSWORD: Change to a secure password"
        echo "  - EMAIL_HOST_USER/EMAIL_HOST_PASSWORD: Add if using email"
        echo ""
        read -p "Press Enter after editing .env file..."
    else
        print_error "No .env template found. Please create .env file manually."
        exit 1
    fi
fi

# Get server details
print_step "Enter server connection details:"
read -p "Server username (default: root): " SERVER_USER
SERVER_USER=${SERVER_USER:-root}

read -p "Server IP (default: 185.231.59.15): " SERVER_IP
SERVER_IP=${SERVER_IP:-185.231.59.15}

read -p "Server directory (default: /home/$SERVER_USER): " SERVER_DIR
SERVER_DIR=${SERVER_DIR:-/home/$SERVER_USER}

# Create backup of current .env
print_step "Creating backup of .env file..."
cp .env .env.backup

# Create archive
print_step "Creating application archive..."
tar -czf memora_core.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env.backup' \
    --exclude='memora_core.tar.gz' \
    --exclude='staticfiles' \
    --exclude='media' \
    --exclude='logs' \
    .

print_status "Archive created: memora_core.tar.gz"

# Transfer to server
print_step "Transferring to server..."
scp memora_core.tar.gz $SERVER_USER@$SERVER_IP:$SERVER_DIR/

if [ $? -eq 0 ]; then
    print_status "✅ Transfer completed successfully!"
else
    print_error "❌ Transfer failed!"
    exit 1
fi

# Create server setup script
print_step "Creating server setup script..."
cat > server_setup.sh << 'EOF'
#!/bin/bash

# Server-side setup script for Memora Core

set -e

echo "🚀 Setting up Memora Core on Ubuntu server..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Extract files
print_step "Extracting application files..."
tar -xzf memora_core.tar.gz
cd memora_core

# Create .env file
print_step "Setting up environment file..."
if [ -f env.production ]; then
    cp env.production .env
    print_warning "⚠️  IMPORTANT: Edit .env file with your actual values!"
    echo "Required changes:"
    echo "  - SECRET_KEY: Generate a long random string"
    echo "  - OPENAI_API_KEY: Add your OpenAI API key"
    echo "  - DB_PASSWORD: Change to a secure password"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    print_warning "No env.production found. Please create .env file manually."
fi

# Make deployment script executable
chmod +x deploy-ubuntu.sh

# Run deployment
print_step "Starting deployment..."
./deploy-ubuntu.sh

print_status "🎉 Setup completed!"
echo ""
echo "📋 Next steps:"
echo "  1. Change admin password: docker-compose exec web python manage.py changepassword admin"
echo "  2. Test application: curl http://185.231.59.15/health/"
echo "  3. Access admin panel: http://185.231.59.15/admin"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Check status: docker-compose ps"
echo "  - Restart: docker-compose restart"
EOF

# Transfer setup script
scp server_setup.sh $SERVER_USER@$SERVER_IP:$SERVER_DIR/

print_status "✅ Server setup script transferred!"

# Final instructions
echo ""
echo "🎯 TRANSFER COMPLETED!"
echo ""
echo "📋 Next steps on your server:"
echo "  1. SSH into your server:"
echo "     ssh $SERVER_USER@$SERVER_IP"
echo ""
echo "  2. Navigate to the directory:"
echo "     cd $SERVER_DIR"
echo ""
echo "  3. Run the setup script:"
echo "     chmod +x server_setup.sh"
echo "     ./server_setup.sh"
echo ""
echo "  4. Follow the prompts to complete deployment"
echo ""
echo "🔗 Application will be available at:"
echo "   - Main app: http://$SERVER_IP"
echo "   - Admin panel: http://$SERVER_IP/admin"
echo "   - Default admin: admin/admin123 (change immediately!)"
echo ""
print_warning "⚠️  Remember to edit .env file with your actual values before running setup!"
