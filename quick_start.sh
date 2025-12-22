#!/bin/bash

# Quick Start Script for Memora Core
# This script provides options for both local and server deployment

set -e

echo "🚀 Memora Core Quick Start"
echo "=========================="

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

# Function to check if running on Windows
is_windows() {
    [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]
}

# Function for local setup
setup_local() {
    print_step "Setting up local development environment..."
    
    if is_windows; then
        print_status "Detected Windows environment"
        python setup_local.py
    else
        print_status "Detected Unix/Linux environment"
        python3 setup_local.py
    fi
}

# Function for server setup
setup_server() {
    print_step "Setting up server deployment..."
    
    if [ ! -f server_setup.sh ]; then
        print_error "server_setup.sh not found. Please ensure all deployment files are present."
        exit 1
    fi
    
    chmod +x server_setup.sh
    ./server_setup.sh
}

# Function to copy files to server
copy_to_server() {
    print_step "Copying files to server..."
    
    read -p "Enter server IP (default: 185.231.59.157): " SERVER_IP
    SERVER_IP=${SERVER_IP:-185.231.59.157}
    
    read -p "Enter server username (default: root): " SERVER_USER
    SERVER_USER=${SERVER_USER:-root}
    
    print_status "Copying files to $SERVER_USER@$SERVER_IP:/opt/memora_core/"
    
    # Create tar archive of project files
    tar --exclude='venv' --exclude='__pycache__' --exclude='.git' --exclude='*.pyc' -czf memora_core.tar.gz .
    
    # Copy to server
    scp memora_core.tar.gz $SERVER_USER@$SERVER_IP:/tmp/
    
    # Extract on server
    ssh $SERVER_USER@$SERVER_IP "mkdir -p /opt/memora_core && tar -xzf /tmp/memora_core.tar.gz -C /opt/memora_core && rm /tmp/memora_core.tar.gz"
    
    # Clean up local tar
    rm memora_core.tar.gz
    
    print_status "Files copied successfully!"
    print_status "SSH into server and run: cd /opt/memora_core && ./deploy_server.sh"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  local     - Set up local development environment"
    echo "  server    - Set up server deployment (run on server)"
    echo "  copy      - Copy project files to server"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local          # Set up local development"
    echo "  $0 server         # Set up server (run on server)"
    echo "  $0 copy           # Copy files to server"
    echo ""
    echo "For detailed instructions, see DEPLOYMENT_GUIDE.md"
}

# Main script logic
case "${1:-}" in
    "local")
        setup_local
        ;;
    "server")
        setup_server
        ;;
    "copy")
        copy_to_server
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    "")
        echo "Please choose an option:"
        echo ""
        echo "1. Local Development Setup"
        echo "2. Server Deployment Setup"
        echo "3. Copy Files to Server"
        echo "4. Show Help"
        echo ""
        read -p "Enter your choice (1-4): " choice
        
        case $choice in
            1)
                setup_local
                ;;
            2)
                setup_server
                ;;
            3)
                copy_to_server
                ;;
            4)
                show_help
                ;;
            *)
                print_error "Invalid choice. Please run '$0 help' for options."
                exit 1
                ;;
        esac
        ;;
    *)
        print_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

print_status "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "  - For local: Run 'python manage.py runserver'"
echo "  - For server: SSH into server and run deployment script"
echo "  - See DEPLOYMENT_GUIDE.md for detailed instructions"
