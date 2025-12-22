#!/bin/bash

# Fix Audio Build Issues Script for Ubuntu Server
# This script fixes the pyaudio build issues by using production requirements

echo "🔧 Fixing audio package build issues..."

# Stop any running containers
docker-compose down 2>/dev/null || true

# Remove old images to force rebuild
docker system prune -f

# Clean Docker build cache
docker builder prune -f

# Make sure we're using the production requirements
if [ -f requirements.production.txt ]; then
    echo "✅ Using production requirements (no audio packages)"
else
    echo "❌ Production requirements file not found!"
    exit 1
fi

echo "✅ Audio build issues fixed!"
echo "The Dockerfile now uses requirements.production.txt (no problematic audio packages)"
echo "Now run: ./quick-deploy-ubuntu.sh"
