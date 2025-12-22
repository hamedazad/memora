# Memora Server & Mobile Setup Guide

This guide helps you set up Memora with a centralized PostgreSQL server that serves both web and mobile applications.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Mobile App     │    │   Memora Server  │    │   PostgreSQL    │
│  (C:\mobile)    │◄──►│  (C:\memora_core)│◄──►│   Database      │
│                 │    │                  │    │                 │
│ • React Native  │    │ • Django REST    │    │ • Centralized   │
│ • Offline Sync  │    │ • API Endpoints  │    │ • Shared Data   │
│ • Push Notif.   │    │ • Web Interface  │    │ • ACID Trans.   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Prerequisites

### Required Software
- **Python 3.11+** - For Django server
- **Node.js 18+** - For mobile development  
- **PostgreSQL 14+** - Database server
- **Git** - Version control

### Windows Installation
```bash
# Install Python
winget install Python.Python.3.11

# Install Node.js
winget install OpenJS.NodeJS

# Install PostgreSQL
winget install PostgreSQL.PostgreSQL

# Install Git
winget install Git.Git
```

## Quick Setup

### 1. Automated Setup (Recommended)

```bash
# Navigate to memora_core directory
cd C:\memora_core

# Run the automated deployment script
python deploy_server_mobile.py
```

This script will:
- ✅ Set up PostgreSQL database
- ✅ Configure Django server
- ✅ Create mobile app structure
- ✅ Generate configuration files
- ✅ Create start scripts

### 2. Manual Setup

#### Step 1: PostgreSQL Setup

```bash
# Run PostgreSQL setup script
python setup_postgresql_server.py
```

Or manually:
```sql
-- Connect to PostgreSQL as superuser
CREATE USER memora_user WITH PASSWORD 'memora_password_2024';
CREATE DATABASE memora_db OWNER memora_user;
GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;
```

#### Step 2: Django Server Configuration

```bash
# Install dependencies
pip install -r requirements.txt
pip install psycopg2-binary

# Copy environment configuration
cp env.server.example .env

# Edit .env file with your settings
# Update OPENAI_API_KEY, DB_PASSWORD, etc.

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

#### Step 3: Mobile App Setup

```bash
# Create mobile directory
mkdir C:\mobile
cd C:\mobile

# Create React Native app
npx react-native init MemoraApp --template react-native-template-typescript

# Copy configuration
cp C:\memora_core\mobile_config.json C:\mobile\config.json
```

## Configuration Files

### Server Environment (.env)
```env
# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=memora_password_2024
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,your-server-ip

# CORS for Mobile
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8081
CORS_ALLOW_CREDENTIALS=True

# API Keys
OPENAI_API_KEY=your-openai-api-key
```

### Mobile Configuration (mobile_config.json)
```json
{
  "server": {
    "development": {
      "baseUrl": "http://localhost:8000",
      "apiUrl": "http://localhost:8000/api/v1"
    }
  },
  "api": {
    "endpoints": {
      "auth": {
        "login": "/auth/login/",
        "register": "/auth/register/"
      },
      "memories": {
        "list": "/memories/",
        "create": "/memories/",
        "search": "/memories/search/"
      }
    }
  }
}
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/register/` - User registration
- `POST /api/v1/auth/token/refresh/` - Refresh token

### Memories
- `GET /api/v1/memories/` - List memories
- `POST /api/v1/memories/` - Create memory
- `GET /api/v1/memories/{id}/` - Get memory details
- `PUT /api/v1/memories/{id}/` - Update memory
- `DELETE /api/v1/memories/{id}/` - Delete memory
- `GET /api/v1/memories/search/?q=query` - Search memories

### AI Features
- `POST /api/v1/ai/enhance/` - Enhance memory with AI
- `POST /api/v1/ai/categorize/` - Auto-categorize memory
- `GET /api/v1/ai/suggestions/` - Get AI suggestions

### Voice Features
- `POST /api/v1/voice/transcribe/` - Transcribe audio to text
- `POST /api/v1/voice/enhance/` - Enhance voice recording

## Running the System

### Start Server
```bash
# Option 1: Manual start
cd C:\memora_core
python manage.py runserver 0.0.0.0:8000

# Option 2: Use start script
start_server.bat
```

### Start Mobile App
```bash
# Option 1: Manual start
cd C:\mobile\MemoraApp
npx react-native start

# Option 2: Use start script  
start_mobile.bat
```

## Data Migration

### From SQLite to PostgreSQL
If you have existing SQLite data:

```bash
# Run migration script
python migrate_to_postgresql.py
```

This will:
1. Backup SQLite data
2. Setup PostgreSQL
3. Migrate all data
4. Verify migration

## Mobile App Development

### API Service Integration
```typescript
// src/services/ApiService.ts
import config from '../config.json';

class ApiService {
  private baseUrl = config.server.development.apiUrl;
  
  async getMemories() {
    const response = await fetch(`${this.baseUrl}/memories/`);
    return response.json();
  }
  
  async createMemory(data: any) {
    const response = await fetch(`${this.baseUrl}/memories/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

### Offline Sync
```typescript
// Handle offline/online synchronization
class SyncService {
  async syncWhenOnline() {
    if (navigator.onLine) {
      // Upload pending changes
      await this.uploadPendingMemories();
      // Download server changes
      await this.downloadServerUpdates();
    }
  }
}
```

## Testing

### Server Testing
```bash
# Test API endpoints
curl http://localhost:8000/api/v1/health/

# Test authentication
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### Mobile Testing
```bash
# Test mobile app connection
cd C:\mobile\MemoraApp
npx react-native run-android  # or run-ios
```

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Failed**
   ```bash
   # Check PostgreSQL service
   net start postgresql-x64-14
   
   # Check connection
   psql -U memora_user -d memora_db -h localhost
   ```

2. **CORS Errors from Mobile**
   ```python
   # In settings.py, ensure:
   CORS_ALLOW_ALL_ORIGINS = True  # For development
   ```

3. **API Authentication Issues**
   ```bash
   # Check JWT token format
   # Ensure Authorization header: "Bearer <token>"
   ```

## Production Deployment

### Server (Ubuntu/CentOS)
```bash
# Install dependencies
sudo apt install postgresql nginx python3-pip

# Configure PostgreSQL
sudo -u postgres createuser memora_user
sudo -u postgres createdb memora_db -O memora_user

# Deploy with Gunicorn + Nginx
pip install gunicorn
gunicorn memora_project.wsgi:application --bind 0.0.0.0:8000
```

### Mobile (App Stores)
```bash
# Build for production
cd C:\mobile\MemoraApp
npx react-native run-android --variant=release
npx react-native run-ios --configuration Release
```

## Security Considerations

1. **Change default passwords** in production
2. **Use HTTPS** for production API
3. **Implement rate limiting** for API endpoints
4. **Enable database backups**
5. **Use environment variables** for secrets

## Support

For issues and questions:
- Check logs: `python manage.py runserver --verbosity=2`
- Database logs: Check PostgreSQL logs
- Mobile logs: Use React Native debugger

## Next Steps

1. ✅ Set up PostgreSQL database
2. ✅ Configure Django server  
3. ✅ Create mobile app structure
4. 🔄 Implement mobile-server synchronization
5. 🔄 Add push notifications
6. 🔄 Deploy to production


