# Memora Core - Docker Deployment Guide

This guide explains how to deploy the Memora Core application to your server at `185.231.59.157` using Docker and FileZilla.

## Prerequisites

### Server Requirements
- Ubuntu 20.04+ or CentOS 8+ (recommended)
- Docker and Docker Compose installed
- At least 2GB RAM
- At least 10GB free disk space
- Ports 80, 443, 8000, 5432, 6379 available

### Local Requirements
- FileZilla or similar FTP client
- Git (optional, for version control)

## Step 1: Prepare Your Local Environment

1. **Create production environment file:**
   ```bash
   cp env.production.example .env
   ```

2. **Edit the `.env` file with your production values:**
   ```bash
   # Generate a secure secret key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   
   # Update .env with your values
   SECRET_KEY=your-generated-secret-key
   OPENAI_API_KEY=your-openai-api-key
   ALLOWED_HOSTS=185.231.59.157,localhost,127.0.0.1
   ```

## Step 2: Upload Files to Server

### Using FileZilla:

1. **Connect to your server:**
   - Host: `185.231.59.157`
   - Username: Your server username
   - Password: Your server password
   - Port: 22 (SSH) or 21 (FTP)

2. **Create project directory on server:**
   - Navigate to `/home/your-username/` or `/var/www/`
   - Create folder: `memora_core`

3. **Upload all project files:**
   - Upload the entire project folder to the server
   - Make sure to include all Docker files:
     - `Dockerfile`
     - `docker-compose.yml`
     - `requirements.txt`
     - `requirements_production.txt`
     - `.env` (your production environment file)
     - `docker/` folder
     - All Django application files

## Step 3: Server Setup

### SSH into your server:
```bash
ssh username@185.231.59.157
```

### Install Docker (if not already installed):
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Navigate to project directory:
```bash
cd /path/to/memora_core
```

## Step 4: SSL Certificate Setup (Optional but Recommended)

### For Let's Encrypt SSL:
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to Docker SSL directory
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
sudo chmod 644 docker/nginx/ssl/cert.pem
sudo chmod 600 docker/nginx/ssl/key.pem
```

### For self-signed certificate (development only):
```bash
# Generate self-signed certificate
sudo mkdir -p docker/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=185.231.59.157"
```

## Step 5: Deploy the Application

### Build and start containers:
```bash
# Build the Docker images
docker-compose build

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### Monitor logs:
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx
```

## Step 6: Database Setup

### Run migrations:
```bash
# Run Django migrations
docker-compose exec web python manage.py migrate

# Create superuser (optional)
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput
```

## Step 7: Verify Deployment

### Check application health:
```bash
# Test health endpoint
curl http://185.231.59.157/health/

# Test main application
curl http://185.231.59.157/
```

### Check container status:
```bash
docker-compose ps
docker-compose logs --tail=50
```

## Step 8: Firewall Configuration

### Configure UFW firewall:
```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

## Step 9: Maintenance Commands

### Update application:
```bash
# Pull latest changes (if using Git)
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Backup database:
```bash
# Create backup
docker-compose exec db pg_dump -U memora_user memora_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U memora_user memora_db < backup_file.sql
```

### View logs:
```bash
# Application logs
docker-compose logs -f web

# Database logs
docker-compose logs -f db

# Nginx logs
docker-compose logs -f nginx
```

### Restart services:
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart web
```

## Troubleshooting

### Common Issues:

1. **Port already in use:**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :80
   
   # Stop conflicting service
   sudo systemctl stop apache2  # or nginx
   ```

2. **Database connection issues:**
   ```bash
   # Check database container
   docker-compose logs db
   
   # Test database connection
   docker-compose exec web python manage.py dbshell
   ```

3. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   chmod +x docker/entrypoint.sh
   ```

4. **SSL certificate issues:**
   ```bash
   # Check certificate validity
   openssl x509 -in docker/nginx/ssl/cert.pem -text -noout
   
   # Renew Let's Encrypt certificate
   sudo certbot renew
   ```

### Performance Optimization:

1. **Increase Docker resources** in Docker Desktop settings
2. **Add Redis caching** (already included in docker-compose.yml)
3. **Configure database connection pooling**
4. **Enable Gzip compression** (already configured in nginx)

## Security Considerations

1. **Change default passwords** in `.env` file
2. **Use strong secret keys**
3. **Enable HTTPS** with proper SSL certificates
4. **Configure firewall** to only allow necessary ports
5. **Regular security updates**
6. **Database backups**
7. **Monitor logs** for suspicious activity

## Monitoring

### Basic monitoring setup:
```bash
# Check resource usage
docker stats

# Monitor disk space
df -h

# Check memory usage
free -h

# Monitor application logs
docker-compose logs -f --tail=100
```

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all required ports are open
4. Check server resources (CPU, memory, disk)

For additional help, refer to the Docker and Django documentation. 