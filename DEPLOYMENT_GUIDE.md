# Memora Core Deployment Guide

This guide provides step-by-step instructions for running your Django app both locally and on your server (185.231.59.157).

## 📋 Prerequisites

### Local Development
- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for version control)

### Server Deployment
- Ubuntu/Debian server with SSH access
- Root or sudo privileges
- Domain name (optional, for SSL)

## 🏠 Local Development Setup

### Option 1: Automated Setup (Recommended)
```bash
# Run the automated setup script
python setup_local.py
```

### Option 2: Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file from template
cp env.example .env
# Edit .env with your settings

# 5. Run database migrations
python manage.py migrate

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Create superuser
python manage.py createsuperuser

# 8. Run development server
python manage.py runserver
```

### Local Development Commands
```bash
# Start development server
python manage.py runserver

# Run with specific port
python manage.py runserver 8080

# Run with external access
python manage.py runserver 0.0.0.0:8000

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Shell access
python manage.py shell
```

## 🖥️ Server Deployment

### Step 1: Initial Server Setup

SSH into your server and run the setup script:
```bash
# Connect to your server
ssh root@185.231.59.157

# Download and run the setup script
wget https://your-repo-url/server_setup.sh
chmod +x server_setup.sh
./server_setup.sh
```

### Step 2: Copy Project Files

Transfer your project files to the server:
```bash
# From your local machine, copy files to server
scp -r /path/to/your/project/* root@185.231.59.157:/opt/memora_core/

# Or use rsync for better performance
rsync -avz --exclude 'venv' --exclude '__pycache__' --exclude '.git' /path/to/your/project/ root@185.231.59.157:/opt/memora_core/
```

### Step 3: Configure Environment

Edit the production environment file:
```bash
# SSH into server
ssh root@185.231.59.157

# Navigate to project directory
cd /opt/memora_core

# Edit .env file
nano .env
```

Update the `.env` file with your actual values:
```env
# Production Environment Configuration
DEBUG=False
SECRET_KEY=your-actual-secret-key-here
ALLOWED_HOSTS=185.231.59.157,localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password_2024
DB_HOST=localhost
DB_PORT=5432

# OpenAI Configuration
OPENAI_API_KEY=your-actual-openai-api-key

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# App Configuration
APP_NAME=Memora
APP_VERSION=1.0.0
APP_ENVIRONMENT=production
```

### Step 4: Deploy Application

Run the deployment script:
```bash
# Make script executable
chmod +x deploy_server.sh

# Run deployment
./deploy_server.sh
```

## 🐳 Docker Deployment (Alternative)

If you prefer Docker deployment:

```bash
# 1. Copy project files to server
scp -r /path/to/your/project/* root@185.231.59.157:/opt/memora_core/

# 2. SSH into server
ssh root@185.231.59.157

# 3. Navigate to project directory
cd /opt/memora_core

# 4. Edit .env file
nano .env

# 5. Run Docker deployment
chmod +x deploy.sh
./deploy.sh
```

## 🔧 Server Management Commands

### Service Management
```bash
# Check service status
sudo systemctl status memora_core

# Start service
sudo systemctl start memora_core

# Stop service
sudo systemctl stop memora_core

# Restart service
sudo systemctl restart memora_core

# Enable auto-start
sudo systemctl enable memora_core

# View logs
sudo journalctl -u memora_core -f
```

### Database Management
```bash
# Access PostgreSQL
sudo -u postgres psql

# Create database backup
sudo -u postgres pg_dump memora_db > backup.sql

# Restore database
sudo -u postgres psql memora_db < backup.sql
```

### Nginx Management
```bash
# Check Nginx status
sudo systemctl status nginx

# Reload Nginx configuration
sudo systemctl reload nginx

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Test Nginx configuration
sudo nginx -t
```

### Redis Management
```bash
# Check Redis status
sudo systemctl status redis-server

# Access Redis CLI
redis-cli

# Test Redis connection
redis-cli ping
```

## 🔒 Security Considerations

### 1. Change Default Passwords
```bash
# Change admin password
python manage.py changepassword admin

# Change database password
sudo -u postgres psql -c "ALTER USER memora_user PASSWORD 'new_secure_password';"
```

### 2. Configure SSL/HTTPS
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 3. Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 📊 Monitoring and Maintenance

### 1. Log Monitoring
```bash
# Application logs
sudo journalctl -u memora_core -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log

# System logs
sudo tail -f /var/log/syslog
```

### 2. Performance Monitoring
```bash
# Check system resources
htop
df -h
free -h

# Check service status
sudo systemctl status memora_core postgresql redis-server nginx
```

### 3. Backup Strategy
```bash
# Create backup script
cat > /opt/backup_memora.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

mkdir -p $BACKUP_DIR

# Database backup
sudo -u postgres pg_dump memora_db > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/memora_core/media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/backup_memora.sh

# Add to crontab for daily backups
echo "0 2 * * * /opt/backup_memora.sh" | sudo crontab -
```

## 🚨 Troubleshooting

### Common Issues

1. **Service won't start**
   ```bash
   # Check logs
   sudo journalctl -u memora_core --no-pager -l
   
   # Check configuration
   python manage.py check
   ```

2. **Database connection issues**
   ```bash
   # Test database connection
   python manage.py dbshell
   
   # Check PostgreSQL status
   sudo systemctl status postgresql
   ```

3. **Static files not loading**
   ```bash
   # Recollect static files
   python manage.py collectstatic --noinput
   
   # Check Nginx configuration
   sudo nginx -t
   ```

4. **Permission issues**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER /opt/memora_core/
   
   # Fix permissions
   chmod -R 755 /opt/memora_core/
   ```

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u memora_core -f`
2. Verify configuration: `python manage.py check`
3. Test database: `python manage.py dbshell`
4. Check service status: `sudo systemctl status memora_core`

## 🔄 Updates and Maintenance

### Updating the Application
```bash
# 1. Backup current version
sudo systemctl stop memora_core
cp -r /opt/memora_core /opt/memora_core_backup

# 2. Update code
cd /opt/memora_core
git pull  # or copy new files

# 3. Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Collect static files
python manage.py collectstatic --noinput

# 6. Restart service
sudo systemctl restart memora_core
```

This guide should help you successfully deploy and maintain your Memora Core application both locally and on your server!
