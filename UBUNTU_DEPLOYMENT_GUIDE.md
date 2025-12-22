# Ubuntu Deployment Guide for Memora Core

This guide is specifically optimized for Ubuntu servers and provides the fastest deployment path.

## 🚀 Quick Ubuntu Deployment (3 minutes)

### Prerequisites
- Ubuntu 20.04 LTS or 22.04 LTS (recommended)
- User with sudo privileges
- SSH access to your server

### Step 1: Prepare Local Files (Windows)

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

1. **Connect to your Ubuntu server:**
   - Host: `185.231.59.157`
   - Username: Your Ubuntu username
   - Password: Your password
   - Port: `22` (SSH)

2. **Navigate to your home directory:**
   - Usually `/home/your-username/`

3. **Create project folder:**
   - Create folder: `memora_core`

4. **Upload ALL files:**
   - Select all files from your local project
   - Drag to the `memora_core` folder on server
   - Ensure these files are included:
     - `Dockerfile`
     - `docker-compose.yml`
     - `requirements.txt`
     - `requirements_production.txt`
     - `.env` (your production environment file)
     - `docker/` folder
     - `deploy-ubuntu.sh` (Ubuntu-specific script)
     - All Django application files

### Step 3: Deploy on Ubuntu Server

1. **SSH into your Ubuntu server:**
   ```bash
   ssh username@185.231.59.157
   ```

2. **Navigate to project directory:**
   ```bash
   cd memora_core
   ```

3. **Make the Ubuntu deployment script executable:**
   ```bash
   chmod +x deploy-ubuntu.sh
   ```

4. **Run the Ubuntu deployment script:**
   ```bash
   ./deploy-ubuntu.sh
   ```

The script will automatically:
- ✅ Update Ubuntu system
- ✅ Install Docker and Docker Compose
- ✅ Configure UFW firewall
- ✅ Build and start all containers
- ✅ Run database migrations
- ✅ Create admin user
- ✅ Configure security settings

### Step 4: Access Your Application

After successful deployment:
- **Main Application:** http://185.231.59.157
- **Admin Panel:** http://185.231.59.157/admin
- **Default Admin:** admin/admin123

## 🔧 Ubuntu-Specific Optimizations

### 1. System Updates
The script automatically updates Ubuntu:
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Docker Installation
Uses official Docker repository for Ubuntu:
```bash
# Official Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 3. UFW Firewall Configuration
Ubuntu's default firewall is automatically configured:
```bash
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable
```

## 📊 Ubuntu Monitoring Commands

### System Monitoring
```bash
# Check system resources
htop
free -h
df -h

# Check Docker status
docker stats
docker system df

# Check application logs
docker-compose logs -f
```

### Service Management
```bash
# Check Docker service
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check UFW status
sudo ufw status
```

## 🔒 Ubuntu Security Features

### 1. Automatic Security Updates
Enable automatic security updates:
```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. Fail2ban Installation (Optional)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. SSL Certificate with Certbot
```bash
# Install Certbot
sudo apt install certbot

# Get SSL certificate
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

## 🛠️ Ubuntu Troubleshooting

### Common Ubuntu Issues:

1. **Permission denied on Docker:**
   ```bash
   # Add user to docker group
   sudo usermod -aG docker $USER
   # Log out and back in, or run:
   newgrp docker
   ```

2. **Port 80 already in use:**
   ```bash
   # Check what's using port 80
   sudo netstat -tulpn | grep :80
   
   # Stop Apache if running
   sudo systemctl stop apache2
   sudo systemctl disable apache2
   ```

3. **Docker service not starting:**
   ```bash
   # Check Docker service
   sudo systemctl status docker
   
   # Restart Docker
   sudo systemctl restart docker
   ```

4. **UFW blocking connections:**
   ```bash
   # Check UFW status
   sudo ufw status
   
   # Allow specific ports
   sudo ufw allow 8000
   ```

### Performance Optimization:

1. **Enable Docker BuildKit:**
   ```bash
   export DOCKER_BUILDKIT=1
   ```

2. **Optimize Docker storage:**
   ```bash
   # Check Docker storage
   docker system df
   
   # Clean up unused resources
   docker system prune -a
   ```

3. **Monitor system resources:**
   ```bash
   # Install htop for better monitoring
   sudo apt install htop
   htop
   ```

## 🔄 Ubuntu Updates

### Update Application:
```bash
cd memora_core
git pull  # if using git
./deploy-ubuntu.sh
```

### Update Ubuntu System:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### Update Docker:
```bash
# Update Docker packages
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io
```

## 📈 Ubuntu Performance Tips

1. **Use SSD storage** for better I/O performance
2. **Allocate sufficient RAM** (minimum 2GB, recommended 4GB+)
3. **Enable swap** if needed:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **Optimize PostgreSQL for Ubuntu:**
   ```bash
   # The Docker setup already includes optimized PostgreSQL settings
   ```

## 🎯 Ubuntu Advantages

Your Ubuntu deployment includes:
- ✅ **Official Docker support** with latest versions
- ✅ **UFW firewall** pre-configured
- ✅ **Automatic security updates** capability
- ✅ **Optimized package management** with apt
- ✅ **Long-term support** (LTS versions)
- ✅ **Excellent documentation** and community support
- ✅ **Built-in monitoring tools**
- ✅ **Easy backup solutions**

## 🚀 Next Steps

After deployment:
1. **Change admin password**
2. **Configure SSL certificates**
3. **Set up automated backups**
4. **Monitor system resources**
5. **Configure log rotation**

---

**Your Memora Core application is now running on Ubuntu!** 🐧✨
