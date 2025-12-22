# Quick Setup Guide for Server 185.231.59.157

This guide provides step-by-step instructions to deploy Memora Core to your server using FileZilla.

## 🚀 Quick Start (5 minutes)

### Step 1: Prepare Local Files

1. **Run the Windows preparation script:**
   ```cmd
   deploy.bat
   ```

2. **Edit the `.env` file** with your production values:
   ```env
   SECRET_KEY=your-generated-secret-key
   OPENAI_API_KEY=your-openai-api-key
   ALLOWED_HOSTS=185.231.59.157,localhost,127.0.0.1
   DEBUG=False
   ```

### Step 2: Upload with FileZilla

1. **Open FileZilla** and connect to your server:
   - Host: `185.231.59.157`
   - Username: Your server username
   - Password: Your server password
   - Port: `22` (SSH) or `21` (FTP)

2. **Navigate to your home directory** on the server:
   - Usually `/home/your-username/` or `/var/www/`

3. **Create a new folder** called `memora_core`

4. **Upload ALL files** from your local project to the server:
   - Select all files and folders in your local project
   - Drag them to the `memora_core` folder on the server
   - Make sure to include:
     - `Dockerfile`
     - `docker-compose.yml`
     - `requirements.txt`
     - `requirements_production.txt`
     - `.env` (your production environment file)
     - `docker/` folder
     - `deploy.sh`
     - All Django application files

### Step 3: Deploy on Server

1. **SSH into your server:**
   ```bash
   ssh username@185.231.59.157
   ```

2. **Navigate to the project directory:**
   ```bash
   cd memora_core
   ```

3. **Install Docker** (if not already installed):
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

4. **Make deployment script executable:**
   ```bash
   chmod +x deploy.sh
   ```

5. **Run the deployment script:**
   ```bash
   ./deploy.sh
   ```

### Step 4: Access Your Application

After successful deployment, your application will be available at:
- **Main Application:** http://185.231.59.157
- **Admin Panel:** http://185.231.59.157/admin
- **Default Admin Credentials:** admin/admin123

## 🔧 Post-Deployment Setup

### 1. Change Default Password
```bash
# SSH into your server and run:
docker-compose exec web python manage.py changepassword admin
```

### 2. Configure SSL (Recommended)
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate (replace with your domain)
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem
sudo chmod 644 docker/nginx/ssl/cert.pem
sudo chmod 600 docker/nginx/ssl/key.pem

# Restart nginx
docker-compose restart nginx
```

### 3. Configure Firewall
```bash
# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall
sudo ufw enable
```

## 📊 Monitoring Commands

```bash
# Check application status
docker-compose ps

# View logs
docker-compose logs -f

# Check resource usage
docker stats

# Monitor disk space
df -h
```

## 🛠️ Troubleshooting

### Common Issues:

1. **Port 80 already in use:**
   ```bash
   sudo netstat -tulpn | grep :80
   sudo systemctl stop apache2  # or nginx
   ```

2. **Permission denied:**
   ```bash
   sudo chown -R $USER:$USER .
   chmod +x deploy.sh
   ```

3. **Database connection issues:**
   ```bash
   docker-compose logs db
   docker-compose exec web python manage.py dbshell
   ```

4. **Application not starting:**
   ```bash
   docker-compose logs web
   docker-compose restart web
   ```

## 🔄 Updates

To update your application:

1. **Upload new files** using FileZilla
2. **SSH into server** and run:
   ```bash
   cd memora_core
   ./deploy.sh
   ```

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify `.env` file configuration
3. Ensure all required ports are open
4. Check server resources (CPU, memory, disk)

## 🎯 What's Included

Your deployment includes:
- ✅ Django application with AI features
- ✅ PostgreSQL database
- ✅ Redis caching
- ✅ Nginx reverse proxy
- ✅ SSL support (with certificates)
- ✅ Health monitoring
- ✅ Automatic backups
- ✅ Security headers
- ✅ Rate limiting
- ✅ Gzip compression

## 🚀 Performance

The application is optimized for:
- Fast response times
- Efficient database queries
- Static file caching
- Memory optimization
- Load balancing ready

---

**Your Memora Core application is now ready to use!** 🎉
