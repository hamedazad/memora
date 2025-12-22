# 🚀 Memora Core Deployment Checklist for Ubuntu Server (185.231.59.15)

## ✅ Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Copy `env.production` to `.env`
- [ ] Generate a strong `SECRET_KEY` (use Django's `get_random_secret_key()`)
- [ ] Add your `OPENAI_API_KEY`
- [ ] Change `DB_PASSWORD` to a secure password
- [ ] Configure email settings (optional)
- [ ] Verify `ALLOWED_HOSTS` includes `185.231.59.15`

### 2. Server Requirements
- [ ] Ubuntu 20.04 or higher
- [ ] At least 2GB RAM available
- [ ] 10GB free disk space
- [ ] SSH access to server
- [ ] Port 80 available (not used by Apache/Nginx)

### 3. Network Configuration
- [ ] Server IP: `185.231.59.15`
- [ ] Port 80 open for HTTP
- [ ] Port 22 open for SSH
- [ ] Firewall configured (UFW will be set up automatically)

## 🚀 Deployment Steps

### Step 1: Local Preparation
```bash
# 1. Create production environment file
cp env.production .env

# 2. Edit .env with your actual values
# Use a text editor to modify .env

# 3. Run the transfer script (Windows)
transfer_to_server.bat

# OR manually create archive and transfer
powershell -Command "Compress-Archive -Path '.\*' -DestinationPath 'memora_core.zip' -Force"
scp memora_core.zip user@185.231.59.15:/home/user/
```

### Step 2: Server Setup
```bash
# 1. SSH into server
ssh user@185.231.59.15

# 2. Extract files
cd /home/user
unzip memora_core.zip
cd memora_core

# 3. Create .env file
cp env.production .env
nano .env  # Edit with your actual values

# 4. Make deployment script executable
chmod +x deploy-ubuntu.sh

# 5. Run deployment
./deploy-ubuntu.sh
```

## ✅ Post-Deployment Verification

### 1. Application Health
- [ ] Application accessible at `http://185.231.59.15`
- [ ] Health check passes: `curl http://185.231.59.15/health/`
- [ ] Admin panel accessible at `http://185.231.59.15/admin`
- [ ] Can log in with admin/admin123

### 2. Service Status
- [ ] All Docker containers running: `docker-compose ps`
- [ ] No error logs: `docker-compose logs --tail=20`
- [ ] Database connection working
- [ ] Redis connection working

### 3. Security Configuration
- [ ] Changed default admin password
- [ ] Strong SECRET_KEY in use
- [ ] Database password changed
- [ ] Firewall enabled (UFW)

## 🔧 Essential Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f nginx
docker-compose logs -f db
```

### Manage Services
```bash
# Check status
docker-compose ps

# Restart all services
docker-compose restart

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

### Database Operations
```bash
# Create backup
docker-compose exec db pg_dump -U memora_user memora_db > backup.sql

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Application Management
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Change admin password
docker-compose exec web python manage.py changepassword admin

# Shell access
docker-compose exec web python manage.py shell
```

## 🚨 Troubleshooting

### Common Issues

1. **Port 80 already in use**
   ```bash
   sudo lsof -i :80
   sudo systemctl stop apache2  # if Apache is running
   ```

2. **Docker permission issues**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

3. **Database connection failed**
   ```bash
   docker-compose logs db
   docker-compose restart db
   ```

4. **Static files not loading**
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   docker-compose restart nginx
   ```

### Health Checks
```bash
# Application
curl http://185.231.59.15/health/

# Database
docker-compose exec db pg_isready -U memora_user

# Redis
docker-compose exec redis redis-cli ping
```

## 📞 Support Information

### Application URLs
- **Main Application**: http://185.231.59.15
- **Admin Panel**: http://185.231.59.15/admin
- **Health Check**: http://185.231.59.15/health/

### Default Credentials
- **Username**: admin
- **Password**: admin123
- **⚠️ CHANGE IMMEDIATELY AFTER DEPLOYMENT**

### Server Information
- **IP Address**: 185.231.59.15
- **SSH Port**: 22
- **HTTP Port**: 80
- **HTTPS Port**: 443 (disabled for now)

## 🔄 Maintenance

### Regular Tasks
- [ ] Monitor system resources: `htop`
- [ ] Check disk usage: `df -h`
- [ ] Clean up Docker: `docker system prune -f`
- [ ] Backup database regularly
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`

### Updates
```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose exec web python manage.py migrate
```

---

**✅ Deployment Complete When All Items Are Checked**
