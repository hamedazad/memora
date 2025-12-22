# Memora Core Server Deployment Instructions

## Server Details
- **IP**: 185.231.59.157
- **Username**: root
- **Password**: Azad@12862525
- **OS**: Ubuntu

## Step 1: Connect to Your Server

### Option A: Using PuTTY (Windows)
1. Download and install PuTTY from https://putty.org/
2. Open PuTTY
3. Enter Host Name: `185.231.59.157`
4. Port: `22`
5. Connection type: `SSH`
6. Click "Open"
7. Login with username: `root` and password: `Azad@12862525`

### Option B: Using Windows Terminal/PowerShell
```powershell
ssh root@185.231.59.157
# Enter password: Azad@12862525
```

## Step 2: Prepare the Server

Once connected to your server, run these commands:

### Update System
```bash
apt update && apt upgrade -y
```

### Install Required Packages
```bash
apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl wget unzip software-properties-common apt-transport-https ca-certificates gnupg lsb-release
```

### Install Docker
```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
systemctl start docker
systemctl enable docker
```

### Install Docker Compose
```bash
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

### Create Application Directory
```bash
mkdir -p /opt/memora_core
cd /opt/memora_core
```

## Step 3: Transfer Project Files

### Option A: Using FileZilla (Recommended)
1. Open FileZilla
2. Connect to your server:
   - Host: `185.231.59.157`
   - Username: `root`
   - Password: `Azad@12862525`
   - Port: `22` (SFTP)
3. Navigate to `/opt/memora_core` on the server (right panel)
4. Upload all your project files from your local Windows machine to `/opt/memora_core/`

### Option B: Using SCP (if you have it on Windows)
```bash
scp -r C:\path\to\your\memora_core\* root@185.231.59.157:/opt/memora_core/
```

## Step 4: Configure the Application

Back in your SSH session on the server:

### Set Permissions
```bash
cd /opt/memora_core
chmod +x *.sh
chmod +x docker/entrypoint.sh
```

### Create Environment File
```bash
cp env.production.example .env
```

### Edit Environment File
```bash
nano .env
```

Update these values in the `.env` file:
```env
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-to-something-random
ALLOWED_HOSTS=185.231.59.157,localhost,127.0.0.1
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password_2024
DB_HOST=db
OPENAI_API_KEY=your-actual-openai-api-key-here
```

Save and exit (Ctrl+X, then Y, then Enter)

## Step 5: Deploy the Application

### Run the Deployment Script
```bash
cd /opt/memora_core
bash deploy-ubuntu.sh
```

This script will:
- Create necessary directories
- Build Docker images
- Start all services (PostgreSQL, Redis, Django, Nginx)
- Run database migrations
- Collect static files
- Create a default admin user

### Wait for Deployment
The deployment process takes 5-10 minutes. Wait for the success message.

## Step 6: Configure Firewall

```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw --force enable
```

## Step 7: Verify Deployment

### Check if services are running
```bash
cd /opt/memora_core
docker-compose ps
```

All services should show "Up" status.

### Test the application
```bash
curl http://localhost/
```

You should get HTML response.

### Check from your browser
Open your browser and go to: `http://185.231.59.157`

## Step 8: Access Admin Panel

1. Go to: `http://185.231.59.157/admin`
2. Default credentials:
   - Username: `admin`
   - Password: `admin123`

**⚠️ IMPORTANT**: Change the admin password immediately!

```bash
cd /opt/memora_core
docker-compose exec web python manage.py changepassword admin
```

## Useful Commands for Server Management

### Check Application Status
```bash
cd /opt/memora_core
docker-compose ps
```

### View Application Logs
```bash
docker-compose logs -f
```

### Restart Application
```bash
docker-compose restart
```

### Stop Application
```bash
docker-compose down
```

### Start Application
```bash
docker-compose up -d
```

### Update Application (after uploading new files)
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Troubleshooting

### If deployment fails:
1. Check logs: `docker-compose logs`
2. Restart services: `docker-compose restart`
3. Check disk space: `df -h`
4. Check memory: `free -h`

### If website is not accessible:
1. Check if services are running: `docker-compose ps`
2. Check firewall: `ufw status`
3. Check if port 80 is listening: `netstat -tlnp | grep :80`

### If you need to update your OpenAI API key:
```bash
nano /opt/memora_core/.env
# Edit the OPENAI_API_KEY line
docker-compose restart
```

## Security Recommendations

1. **Change default passwords** immediately
2. **Set up SSL certificates** for HTTPS
3. **Configure regular backups**
4. **Monitor system resources**
5. **Keep system updated**: `apt update && apt upgrade`

## Your Application URLs

- **Main Application**: http://185.231.59.157
- **Admin Panel**: http://185.231.59.157/admin
- **API Endpoints**: http://185.231.59.157/api/

---

## Quick Reference Commands

```bash
# Connect to server
ssh root@185.231.59.157

# Go to app directory
cd /opt/memora_core

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Restart app
docker-compose restart

# Update app (after file upload)
docker-compose down && docker-compose up -d --build
```

**Support**: If you encounter any issues, check the logs first with `docker-compose logs` and ensure all services are running with `docker-compose ps`.





















