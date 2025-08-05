# Deployment Guide

This guide will help you deploy Memora Memory Assistant to production.

## 🚀 Production Deployment

### Prerequisites

- Python 3.8+
- PostgreSQL (recommended) or MySQL
- Nginx or Apache
- SSL certificate (required for voice features)
- Domain name

### 1. Server Setup

#### Ubuntu/Debian
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Install additional dependencies for voice features
sudo apt install ffmpeg portaudio19-dev python3-pyaudio
```

#### CentOS/RHEL
```bash
# Update system
sudo yum update -y

# Install Python and dependencies
sudo yum install python3 python3-pip nginx postgresql postgresql-server

# Enable and start services
sudo systemctl enable nginx postgresql
sudo systemctl start nginx postgresql
```

### 2. Application Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/memora.git
cd memora

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install production dependencies
pip install gunicorn psycopg2-binary
```

### 3. Environment Configuration

Create a production `.env` file:

```env
# Django Settings
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_URL=postgresql://username:password@localhost/memora_db

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Security
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Static Files
STATIC_ROOT=/var/www/memora/static/
MEDIA_ROOT=/var/www/memora/media/
```

### 4. Database Setup

#### PostgreSQL
```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE memora_db;
CREATE USER memora_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;
\q

# Update settings.py to use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'memora_db',
        'USER': 'memora_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Django Configuration

Update `settings.py` for production:

```python
# Security settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Static files
STATIC_ROOT = '/var/www/memora/static/'
MEDIA_ROOT = '/var/www/memora/media/'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

### 6. Static Files

```bash
# Collect static files
python manage.py collectstatic

# Create media directory
sudo mkdir -p /var/www/memora/media/
sudo chown -R www-data:www-data /var/www/memora/
```

### 7. Gunicorn Configuration

Create `/etc/systemd/system/memora.service`:

```ini
[Unit]
Description=Memora Memory Assistant
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/memora
Environment="PATH=/path/to/memora/venv/bin"
ExecStart=/path/to/memora/venv/bin/gunicorn --workers 3 --bind unix:/run/memora.sock memora_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

### 8. Nginx Configuration

Create `/etc/nginx/sites-available/memora`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Static files
    location /static/ {
        alias /var/www/memora/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/memora/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy to Gunicorn
    location / {
        proxy_pass http://unix:/run/memora.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 9. Start Services

```bash
# Enable and start services
sudo systemctl enable memora
sudo systemctl start memora
sudo systemctl reload nginx

# Check status
sudo systemctl status memora
sudo systemctl status nginx
```

### 10. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 11. Database Migrations

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 12. Monitoring and Logs

```bash
# View application logs
sudo journalctl -u memora -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check application status
sudo systemctl status memora
```

## 🔧 Maintenance

### Backup Database
```bash
# Create backup
pg_dump memora_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
psql memora_db < backup_file.sql
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Restart services
sudo systemctl restart memora
sudo systemctl reload nginx
```

### Version Management
```bash
# Show current version
python manage_version.py show

# Update version
python manage_version.py patch  # or minor, major
```

## 🛡️ Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] DEBUG=False in production
- [ ] Strong SECRET_KEY
- [ ] Database credentials secured
- [ ] API keys protected
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring and logging enabled

## 📊 Performance Optimization

- [ ] Database indexing
- [ ] Static file caching
- [ ] Gzip compression enabled
- [ ] CDN for static assets
- [ ] Database connection pooling
- [ ] Redis for caching (optional)

## 🆘 Troubleshooting

### Common Issues

1. **Voice features not working**: Ensure HTTPS is enabled
2. **Static files not loading**: Check STATIC_ROOT and permissions
3. **Database connection errors**: Verify database credentials and connectivity
4. **Permission denied**: Check file ownership and permissions

### Log Locations
- Application logs: `sudo journalctl -u memora`
- Nginx logs: `/var/log/nginx/`
- Django logs: Check your logging configuration

---

For additional support, check the main README.md or create an issue on GitHub. 