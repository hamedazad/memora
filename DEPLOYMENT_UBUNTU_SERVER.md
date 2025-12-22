# Memora Core Deployment Guide for Ubuntu Server (185.231.59.15)

## 🚀 Quick Start Instructions

### Step 1: Prepare Your Local Environment
1. **Create production environment file:**
   ```bash
   cp env.production .env
   ```

2. **Edit the .env file with your actual values:**
   - Change `SECRET_KEY` to a long, random string
   - Add your `OPENAI_API_KEY`
   - Update database password if needed
   - Add email credentials if you want email functionality

### Step 2: Transfer Files to Server
1. **Create a compressed archive:**
   ```bash
   tar -czf memora_core.tar.gz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' .
   ```

2. **Transfer to server:**
   ```bash
   scp memora_core.tar.gz user@185.231.59.15:/home/user/
   ```

3. **SSH into your server:**
   ```bash
   ssh user@185.231.59.15
   ```

### Step 3: Server Setup
1. **Extract files:**
   ```bash
   cd /home/user
   tar -xzf memora_core.tar.gz
   cd memora_core
   ```

2. **Create .env file on server:**
   ```bash
   cp env.production .env
   # Edit with your actual values
   nano .env
   ```

3. **Make deployment script executable:**
   ```bash
   chmod +x deploy-ubuntu.sh
   ```

4. **Run deployment:**
   ```bash
   ./deploy-ubuntu.sh
   ```

## 📋 Detailed Configuration

### Environment Variables (.env file)
```bash
# Required - Change these values
SECRET_KEY=your-long-random-secret-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Database - Change password for security
DB_PASSWORD=your-secure-database-password

# Optional - Email configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Server Requirements
- Ubuntu 20.04 or higher
- At least 2GB RAM
- 10GB free disk space
- Docker and Docker Compose will be installed automatically

### Ports Used
- **80**: HTTP (Nginx)
- **443**: HTTPS (Nginx) - disabled for now
- **8000**: Django (internal)
- **5432**: PostgreSQL (internal)
- **6379**: Redis (internal)

## 🔧 Post-Deployment Steps

### 1. Change Default Admin Password
```bash
docker-compose exec web python manage.py changepassword admin
```

### 2. Create Additional Users
```bash
docker-compose exec web python manage.py createsuperuser
```

### 3. Check Application Status
```bash
# View running containers
docker-compose ps

# Check logs
docker-compose logs -f

# Test application
curl http://185.231.59.15/health/
```

### 4. Configure SSL (Optional)
1. **Generate SSL certificates:**
   ```bash
   mkdir -p docker/nginx/ssl
   # Add your SSL certificates here
   ```

2. **Enable HTTPS in nginx.conf:**
   - Uncomment the HTTPS server block
   - Update SSL certificate paths

3. **Update .env file:**
   ```bash
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   ```

4. **Restart services:**
   ```bash
   docker-compose restart nginx web
   ```

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart web
```

### Update Application
```bash
# Stop services
docker-compose down

# Pull latest code and rebuild
git pull origin main
docker-compose build --no-cache
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate
```

### Backup Database
```bash
# Create backup
docker-compose exec db pg_dump -U memora_user memora_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker-compose exec -T db psql -U memora_user memora_db < backup_file.sql
```

## 🔒 Security Considerations

### 1. Firewall Configuration
The deployment script configures UFW firewall:
- SSH (port 22)
- HTTP (port 80)
- HTTPS (port 443)

### 2. Database Security
- Change default database password
- Consider using external database for production

### 3. Application Security
- Use strong SECRET_KEY
- Enable HTTPS in production
- Regular security updates

### 4. Monitoring
```bash
# Check system resources
htop

# Check disk usage
df -h

# Check Docker resources
docker system df
```

## 🚨 Troubleshooting

### Common Issues

1. **Port 80 already in use:**
   ```bash
   sudo lsof -i :80
   sudo systemctl stop apache2  # if Apache is running
   ```

2. **Docker permission issues:**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. **Database connection issues:**
   ```bash
   docker-compose logs db
   docker-compose restart db
   ```

4. **Static files not loading:**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   docker-compose restart nginx
   ```

### Health Checks
```bash
# Application health
curl http://185.231.59.15/health/

# Database health
docker-compose exec db pg_isready -U memora_user

# Redis health
docker-compose exec redis redis-cli ping
```

## 📞 Support

If you encounter issues:
1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all required ports are open
4. Check server resources (CPU, RAM, disk)

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks
1. **Update system packages:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Clean up Docker:**
   ```bash
   docker system prune -f
   ```

3. **Backup database regularly:**
   ```bash
   # Add to crontab for daily backups
   0 2 * * * docker-compose exec db pg_dump -U memora_user memora_db > /backups/backup_$(date +\%Y\%m\%d).sql
   ```

### Application Updates
1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Rebuild and restart:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   docker-compose exec web python manage.py migrate
   ```

---

**Server IP:** 185.231.59.15  
**Application URL:** http://185.231.59.15  
**Admin URL:** http://185.231.59.15/admin  
**Default Admin:** admin/admin123 (change immediately!)
