# Database Configuration Guide

**Version:** 1.0.0  
**Last Updated:** 2025-01-12  
**Status:** ✅ CONFIGURED

---

## 📋 Overview

This guide explains the database configuration for **memora_core**, covering both development (SQLite) and production (PostgreSQL) environments.

---

## 🎯 Database Strategy

### Development: SQLite
- **Fast setup** - No installation required
- **Portable** - Single file database
- **Perfect for:** Local development, testing
- **File:** `db.sqlite3`

### Production: PostgreSQL
- **Scalable** - Handles thousands of concurrent users
- **Advanced features** - JSON queries, full-text search
- **Reliable** - ACID compliance, data integrity
- **Perfect for:** Production, staging environments

---

## 🔧 Current Configuration

### Default Settings (memora_project/settings.py)

```python
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.getenv('DB_NAME', 'memora_db'),
        'USER': os.getenv('DB_USER', 'memora_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'memora_password_2024'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```

**Problem:** Defaults to PostgreSQL, but `db.sqlite3` exists in project.

**Solution:** Environment-based configuration with automatic detection.

---

## ✅ NEW: Smart Database Configuration

### Updated Settings (Recommended)

Replace the DATABASES configuration with:

```python
# Database Configuration with Environment Detection
# Automatically uses SQLite for development, PostgreSQL for production

import os
from pathlib import Path

# Determine environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()

if ENVIRONMENT == 'production':
    # Production: Use PostgreSQL (required)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'memora_db'),
            'USER': os.getenv('DB_USER', 'memora_user'),
            'PASSWORD': os.getenv('DB_PASSWORD'),  # Required in production
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,  # Connection pooling
            'OPTIONS': {
                'connect_timeout': 10,
                'options': '-c statement_timeout=30000'  # 30 second query timeout
            }
        }
    }
else:
    # Development/Testing: Use SQLite (default)
    db_engine = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
    
    if db_engine == 'django.db.backends.sqlite3':
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
                'OPTIONS': {
                    'timeout': 20,
                }
            }
        }
    else:
        # Development with PostgreSQL (optional)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', 'memora_dev_db'),
                'USER': os.getenv('DB_USER', 'memora_dev_user'),
                'PASSWORD': os.getenv('DB_PASSWORD', 'dev_password'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
            }
        }
```

---

## 🔨 Implementation

### Step 1: Create Database Configuration File

Create `c:\memora_core\memora_project\database_config.py`:

```python
"""
Smart Database Configuration
Automatically selects database based on environment
"""

import os
from pathlib import Path

def get_database_config(base_dir):
    """
    Get database configuration based on environment
    
    Returns:
        dict: Database configuration
    """
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    
    if environment == 'production':
        # Production: PostgreSQL required
        if not os.getenv('DB_PASSWORD'):
            raise ValueError('DB_PASSWORD environment variable required in production')
        
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', 'memora_db'),
                'USER': os.getenv('DB_USER', 'memora_user'),
                'PASSWORD': os.getenv('DB_PASSWORD'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
                'CONN_MAX_AGE': 600,
                'OPTIONS': {
                    'connect_timeout': 10,
                    'options': '-c statement_timeout=30000'
                }
            }
        }
    
    elif environment == 'staging':
        # Staging: PostgreSQL
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', 'memora_staging_db'),
                'USER': os.getenv('DB_USER', 'memora_staging_user'),
                'PASSWORD': os.getenv('DB_PASSWORD', 'staging_password'),
                'HOST': os.getenv('DB_HOST', 'localhost'),
                'PORT': os.getenv('DB_PORT', '5432'),
                'CONN_MAX_AGE': 300,
            }
        }
    
    else:
        # Development/Testing: SQLite (default)
        db_engine = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
        
        if db_engine == 'django.db.backends.sqlite3':
            return {
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': base_dir / 'db.sqlite3',
                    'OPTIONS': {
                        'timeout': 20,
                    }
                }
            }
        else:
            # Development with PostgreSQL (optional for testing)
            return {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': os.getenv('DB_NAME', 'memora_dev_db'),
                    'USER': os.getenv('DB_USER', 'memora_dev_user'),
                    'PASSWORD': os.getenv('DB_PASSWORD', 'dev_password'),
                    'HOST': os.getenv('DB_HOST', 'localhost'),
                    'PORT': os.getenv('DB_PORT', '5432'),
                }
            }


def get_database_info():
    """Get human-readable database information"""
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    db_engine = os.getenv('DB_ENGINE', 'django.db.backends.sqlite3')
    
    if environment == 'production':
        return {
            'environment': 'Production',
            'database': 'PostgreSQL',
            'host': os.getenv('DB_HOST', 'localhost'),
            'name': os.getenv('DB_NAME', 'memora_db'),
            'recommended': True
        }
    elif environment == 'staging':
        return {
            'environment': 'Staging',
            'database': 'PostgreSQL',
            'host': os.getenv('DB_HOST', 'localhost'),
            'name': os.getenv('DB_NAME', 'memora_staging_db'),
            'recommended': True
        }
    else:
        if db_engine == 'django.db.backends.sqlite3':
            return {
                'environment': 'Development',
                'database': 'SQLite',
                'file': 'db.sqlite3',
                'recommended': True
            }
        else:
            return {
                'environment': 'Development',
                'database': 'PostgreSQL',
                'host': os.getenv('DB_HOST', 'localhost'),
                'name': os.getenv('DB_NAME', 'memora_dev_db'),
                'recommended': False,
                'note': 'SQLite recommended for development'
            }
```

### Step 2: Update settings.py

Replace the DATABASES section in `memora_project/settings.py`:

```python
# Database Configuration
from .database_config import get_database_config

DATABASES = get_database_config(BASE_DIR)
```

---

## 🌍 Environment Configuration

### Development (Default)

**File:** `.env` (or no file needed)

```bash
# Development uses SQLite by default
# No configuration needed!

# Optional: To verify
ENVIRONMENT=development
DB_ENGINE=django.db.backends.sqlite3
```

**Database File:** `db.sqlite3` in project root

**Setup:**
```bash
# Just run migrations
python manage.py migrate
python manage.py runserver
```

### Staging

**File:** `.env.staging`

```bash
ENVIRONMENT=staging
DEBUG=False

# PostgreSQL configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_staging_db
DB_USER=memora_staging_user
DB_PASSWORD=your_staging_password
DB_HOST=staging-db.example.com
DB_PORT=5432
```

### Production

**File:** `.env.production`

```bash
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-production-secret-key

# PostgreSQL configuration (required)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=your_secure_production_password
DB_HOST=production-db.example.com
DB_PORT=5432

# Additional production settings
ALLOWED_HOSTS=api.memora.app,www.memora.app
CORS_ALLOWED_ORIGINS=https://app.memora.app
```

---

## 📦 Database Setup Scripts

### For Development (SQLite)

**File:** `setup_dev_database.sh` / `setup_dev_database.bat`

```bash
#!/bin/bash
# Development Database Setup (SQLite)

echo "Setting up Development Database (SQLite)..."
echo ""

# Set environment
export ENVIRONMENT=development

# Remove old database (optional - careful!)
read -p "Remove existing database? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f db.sqlite3
    echo "✓ Removed old database"
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser
echo ""
echo "Create admin user..."
python manage.py createsuperuser --noinput --username admin --email admin@memora.local || python manage.py createsuperuser

# Load initial data (optional)
# python manage.py loaddata initial_data.json

echo ""
echo "✅ Development database setup complete!"
echo ""
echo "Database: SQLite (db.sqlite3)"
echo "Admin: /admin/"
echo ""
echo "Start server: python manage.py runserver"
```

### For Production (PostgreSQL)

**File:** `setup_prod_database.sh`

```bash
#!/bin/bash
# Production Database Setup (PostgreSQL)

echo "Setting up Production Database (PostgreSQL)..."
echo ""

# Check environment
if [ "$ENVIRONMENT" != "production" ]; then
    echo "⚠️  WARNING: ENVIRONMENT should be 'production'"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check required environment variables
required_vars=("DB_NAME" "DB_USER" "DB_PASSWORD" "DB_HOST")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable not set"
        exit 1
    fi
done

echo "Database Configuration:"
echo "  Host: $DB_HOST"
echo "  Name: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Test database connection
echo "Testing database connection..."
python manage.py dbshell --command "SELECT version();" || {
    echo "❌ Failed to connect to database"
    exit 1
}

echo "✓ Database connection successful"
echo ""

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "✅ Production database setup complete!"
echo ""
echo "Next steps:"
echo "1. Create admin user: python manage.py createsuperuser"
echo "2. Load initial data (if needed)"
echo "3. Start application server"
```

---

## 🔄 Database Migration Scripts

### Switch from SQLite to PostgreSQL

**File:** `migrate_sqlite_to_postgresql.py`

```python
#!/usr/bin/env python
"""
Migrate data from SQLite to PostgreSQL

Usage:
    python migrate_sqlite_to_postgresql.py
"""

import os
import sys
import django
from django.core.management import call_command
from django.conf import settings

def migrate_to_postgresql():
    """Migrate from SQLite to PostgreSQL"""
    
    print("=" * 60)
    print("SQLite → PostgreSQL Migration Tool")
    print("=" * 60)
    print()
    
    # Step 1: Verify SQLite database exists
    sqlite_db = 'db.sqlite3'
    if not os.path.exists(sqlite_db):
        print(f"❌ Error: {sqlite_db} not found")
        return False
    
    print(f"✓ Found SQLite database: {sqlite_db}")
    print()
    
    # Step 2: Export data from SQLite
    print("Step 1: Exporting data from SQLite...")
    backup_file = 'sqlite_backup.json'
    
    try:
        # Use SQLite
        os.environ['DB_ENGINE'] = 'django.db.backends.sqlite3'
        
        # Dump data
        with open(backup_file, 'w') as f:
            call_command('dumpdata', '--natural-foreign', '--natural-primary', 
                        '--exclude', 'contenttypes', '--exclude', 'auth.Permission',
                        '--indent', '2', stdout=f)
        
        print(f"✓ Data exported to {backup_file}")
        print()
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return False
    
    # Step 3: Verify PostgreSQL configuration
    print("Step 2: Verifying PostgreSQL configuration...")
    
    required_vars = ['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print()
        print("Set these in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value")
        return False
    
    print("✓ PostgreSQL configuration verified")
    print(f"  Host: {os.getenv('DB_HOST')}")
    print(f"  Database: {os.getenv('DB_NAME')}")
    print(f"  User: {os.getenv('DB_USER')}")
    print()
    
    # Step 4: Setup PostgreSQL
    print("Step 3: Setting up PostgreSQL database...")
    
    try:
        # Switch to PostgreSQL
        os.environ['DB_ENGINE'] = 'django.db.backends.postgresql'
        
        # Run migrations
        call_command('migrate', '--run-syncdb')
        
        print("✓ PostgreSQL migrations complete")
        print()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Step 5: Import data to PostgreSQL
    print("Step 4: Importing data to PostgreSQL...")
    
    try:
        # Load data
        call_command('loaddata', backup_file)
        
        print("✓ Data imported successfully")
        print()
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        print()
        print("You can try importing manually:")
        print(f"  python manage.py loaddata {backup_file}")
        return False
    
    # Step 6: Verify data
    print("Step 5: Verifying data integrity...")
    
    try:
        from django.contrib.auth.models import User
        from memory_assistant.models import Memory, UserProfile
        
        user_count = User.objects.count()
        memory_count = Memory.objects.count()
        profile_count = UserProfile.objects.count()
        
        print(f"✓ Users: {user_count}")
        print(f"✓ Memories: {memory_count}")
        print(f"✓ Profiles: {profile_count}")
        print()
        
    except Exception as e:
        print(f"⚠️  Warning: Could not verify counts: {e}")
        print()
    
    # Success!
    print("=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Update .env file to use PostgreSQL")
    print("2. Test your application")
    print(f"3. Backup {backup_file} (contains your data)")
    print("4. Remove db.sqlite3 (after testing)")
    print()
    
    return True


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
    django.setup()
    
    success = migrate_to_postgresql()
    sys.exit(0 if success else 1)
```

### Backup SQLite Database

**File:** `backup_sqlite.sh`

```bash
#!/bin/bash
# Backup SQLite database

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backups/db_sqlite_$DATE.sqlite3"

mkdir -p backups

if [ -f "db.sqlite3" ]; then
    cp db.sqlite3 "$BACKUP_FILE"
    echo "✓ Backup created: $BACKUP_FILE"
    
    # Also create JSON dump
    JSON_FILE="backups/db_dump_$DATE.json"
    python manage.py dumpdata --natural-foreign --indent 2 > "$JSON_FILE"
    echo "✓ JSON dump created: $JSON_FILE"
else
    echo "❌ db.sqlite3 not found"
    exit 1
fi
```

### Restore SQLite Database

**File:** `restore_sqlite.sh`

```bash
#!/bin/bash
# Restore SQLite database from backup

if [ -z "$1" ]; then
    echo "Usage: ./restore_sqlite.sh <backup_file>"
    echo ""
    echo "Available backups:"
    ls -lh backups/db_sqlite_*.sqlite3 2>/dev/null || echo "  No backups found"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

# Backup current database
if [ -f "db.sqlite3" ]; then
    mv db.sqlite3 "db.sqlite3.before_restore"
    echo "✓ Current database backed up to db.sqlite3.before_restore"
fi

# Restore
cp "$BACKUP_FILE" db.sqlite3
echo "✓ Database restored from: $BACKUP_FILE"
```

---

## 🐘 PostgreSQL Setup

### Local PostgreSQL Installation

#### Windows
```powershell
# Install PostgreSQL
# Download from: https://www.postgresql.org/download/windows/

# Or use Chocolatey
choco install postgresql

# Create database
psql -U postgres
CREATE DATABASE memora_db;
CREATE USER memora_user WITH PASSWORD 'memora_password_2024';
GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;
\q
```

#### macOS
```bash
# Install PostgreSQL
brew install postgresql@14
brew services start postgresql@14

# Create database
createdb memora_db
createuser -P memora_user  # Enter password when prompted
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;"
```

#### Linux (Ubuntu/Debian)
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database
sudo -u postgres psql
CREATE DATABASE memora_db;
CREATE USER memora_user WITH PASSWORD 'memora_password_2024';
GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;
\q
```

### Docker PostgreSQL (Recommended for Development)

**File:** `docker-compose.yml` (PostgreSQL only)

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: memora_postgres
    environment:
      POSTGRES_DB: memora_dev_db
      POSTGRES_USER: memora_dev_user
      POSTGRES_PASSWORD: dev_password
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U memora_dev_user"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

**Start:**
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Check status
docker-compose ps

# View logs
docker-compose logs -f postgres

# Stop
docker-compose down

# Remove data (start fresh)
docker-compose down -v
```

---

## 🔧 Environment Files

### .env.development (SQLite - Default)

```bash
# Development Environment
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-not-for-production

# Database: SQLite (default)
DB_ENGINE=django.db.backends.sqlite3

# API Keys (optional for development)
OPENAI_API_KEY=your_dev_key_here
```

### .env.development.postgresql (Optional)

```bash
# Development Environment with PostgreSQL
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key

# Database: PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_dev_db
DB_USER=memora_dev_user
DB_PASSWORD=dev_password
DB_HOST=localhost
DB_PORT=5432

# Or with Docker
DB_HOST=localhost  # or 127.0.0.1
DB_PORT=5432
```

### .env.production (PostgreSQL - Required)

```bash
# Production Environment
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-very-secure-production-secret-key

# Database: PostgreSQL (required)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=your_very_secure_password
DB_HOST=your-postgres-host.com
DB_PORT=5432

# Security
ALLOWED_HOSTS=api.memora.app,www.memora.app
CORS_ALLOWED_ORIGINS=https://app.memora.app

# API Keys
OPENAI_API_KEY=your_production_openai_key
```

---

## 🔄 Migration Workflows

### Workflow 1: Start Fresh with SQLite (Development)

```bash
cd c:\memora_core

# 1. Remove old database
del db.sqlite3  # Windows
# rm db.sqlite3  # Unix

# 2. Run migrations
python manage.py migrate

# 3. Create admin user
python manage.py createsuperuser

# 4. Start server
python manage.py runserver
```

### Workflow 2: Start Fresh with PostgreSQL (Production)

```bash
cd c:\memora_core

# 1. Set environment variables
# Edit .env.production file

# 2. Load environment
export $(cat .env.production | xargs)  # Unix
# Or manually set in PowerShell

# 3. Test database connection
python manage.py dbshell

# 4. Run migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic

# 7. Start server
python manage.py runserver
```

### Workflow 3: Migrate SQLite → PostgreSQL

```bash
cd c:\memora_core

# 1. Backup SQLite
cp db.sqlite3 db.sqlite3.backup
python manage.py dumpdata > data_backup.json

# 2. Setup PostgreSQL (see above)

# 3. Configure .env for PostgreSQL
# Edit .env file

# 4. Run migration script
python migrate_sqlite_to_postgresql.py

# 5. Verify data
python manage.py shell
>>> from django.contrib.auth.models import User
>>> print(f"Users: {User.objects.count()}")

# 6. Test application
python manage.py runserver
```

---

## 📊 Database Comparison

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Setup Time** | 0 min ⚡ | 10-30 min |
| **Installation** | None required ✅ | Requires installation |
| **File-based** | Yes (portable) | No (server-based) |
| **Concurrent Users** | Limited (~10) | Thousands ✅ |
| **Performance** | Good | Excellent ✅ |
| **JSON Queries** | Basic | Advanced ✅ |
| **Full-text Search** | Limited | Advanced ✅ |
| **Replication** | No | Yes ✅ |
| **Backup** | Copy file | pg_dump ✅ |
| **Production Use** | ❌ Not recommended | ✅ Recommended |
| **Development Use** | ✅ Perfect | ⚠️ Overkill |

---

## 🎯 Recommendations

### For Development
```
✅ Use SQLite (default)
   - Fast setup
   - No configuration
   - Perfect for local development
   - Easy to reset (delete db.sqlite3)
```

### For Staging
```
✅ Use PostgreSQL
   - Test production configuration
   - Verify migrations
   - Performance testing
   - Same as production
```

### For Production
```
✅ Use PostgreSQL (required)
   - Scalable
   - Reliable
   - Advanced features
   - Industry standard
```

---

## 🧪 Testing Different Databases

### Test with SQLite
```bash
# Set environment
export ENVIRONMENT=development
export DB_ENGINE=django.db.backends.sqlite3

# Run tests
python manage.py test

# Should use in-memory SQLite for speed
```

### Test with PostgreSQL
```bash
# Set environment
export ENVIRONMENT=staging
export DB_ENGINE=django.db.backends.postgresql
export DB_NAME=memora_test_db
export DB_USER=test_user
export DB_PASSWORD=test_pass
export DB_HOST=localhost

# Run tests
python manage.py test

# Uses temporary PostgreSQL database
```

---

## 🔒 Security Best Practices

### Development
- ✅ Use simple passwords (local only)
- ✅ Commit `.env.example`, NOT `.env`
- ✅ Use different credentials than production

### Production
- ✅ Use strong passwords (20+ characters)
- ✅ Never commit credentials to git
- ✅ Use environment variables
- ✅ Rotate passwords regularly
- ✅ Enable SSL/TLS connections
- ✅ Use connection pooling
- ✅ Regular backups

---

## 📦 Backup Strategies

### SQLite Backup
```bash
# Simple copy
cp db.sqlite3 backups/db_$(date +%Y%m%d).sqlite3

# With compression
tar -czf backups/db_$(date +%Y%m%d).tar.gz db.sqlite3

# JSON export (portable)
python manage.py dumpdata > backups/data_$(date +%Y%m%d).json
```

### PostgreSQL Backup
```bash
# Database dump
pg_dump -U memora_user -h localhost memora_db > backup.sql

# Compressed dump
pg_dump -U memora_user -h localhost memora_db | gzip > backup.sql.gz

# Custom format (faster restore)
pg_dump -U memora_user -Fc memora_db -f backup.dump

# Restore
pg_restore -U memora_user -d memora_db backup.dump
```

### Automated Backups (Production)

**File:** `backup_database.sh`

```bash
#!/bin/bash
# Automated PostgreSQL backup script
# Add to cron: 0 2 * * * /path/to/backup_database.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/memora"
DB_NAME="memora_db"
DB_USER="memora_user"

mkdir -p $BACKUP_DIR

# Create backup
pg_dump -U $DB_USER -Fc $DB_NAME -f "$BACKUP_DIR/memora_$DATE.dump"

# Keep only last 30 days
find $BACKUP_DIR -name "memora_*.dump" -mtime +30 -delete

echo "✓ Backup created: memora_$DATE.dump"
```

---

## 🚀 Quick Commands Reference

### Database Operations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations status
python manage.py showmigrations

# Rollback to specific migration
python manage.py migrate memory_assistant 0025

# Reset app database
python manage.py migrate memory_assistant zero
python manage.py migrate memory_assistant

# Database shell
python manage.py dbshell

# Check database configuration
python manage.py check --database default
```

### Data Management

```bash
# Export data
python manage.py dumpdata > data.json
python manage.py dumpdata memory_assistant > memory_data.json
python manage.py dumpdata auth.User > users.json

# Import data
python manage.py loaddata data.json

# Flush database (careful!)
python manage.py flush

# Create superuser
python manage.py createsuperuser
```

---

## ⚠️ Common Issues

### Issue 1: "relation does not exist"

**Cause:** Migrations not applied

**Fix:**
```bash
python manage.py migrate
```

### Issue 2: "password authentication failed"

**Cause:** Wrong PostgreSQL credentials

**Fix:**
```bash
# Verify credentials
psql -U memora_user -h localhost -d memora_db

# Update .env file with correct credentials
```

### Issue 3: "database is locked" (SQLite)

**Cause:** Concurrent writes in SQLite

**Fix:**
```bash
# Close all Django shells/servers
# Or switch to PostgreSQL for production
```

### Issue 4: Connection pool exhausted

**Cause:** Too many concurrent connections

**Fix:**
```python
# settings.py
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # Add connection pooling
    }
}
```

---

## 📋 Deployment Checklist

### Before Deploying to Production

- [ ] Install PostgreSQL on server
- [ ] Create production database and user
- [ ] Set up SSL/TLS for database connections
- [ ] Configure firewall rules
- [ ] Set environment variables
- [ ] Test database connection
- [ ] Run migrations
- [ ] Import data (if migrating)
- [ ] Create admin user
- [ ] Set up automated backups
- [ ] Configure monitoring
- [ ] Test application thoroughly

---

## 🎯 Best Practices

### Do's ✅
1. Use SQLite for development
2. Use PostgreSQL for production
3. Keep .env files out of git
4. Backup before migrations
5. Test migrations on staging first
6. Use connection pooling in production
7. Enable query logging in development
8. Regular backups (automated)

### Don'ts ❌
1. Don't use SQLite in production
2. Don't commit database credentials
3. Don't migrate without backups
4. Don't skip migration testing
5. Don't use same passwords across environments
6. Don't ignore database performance
7. Don't forget to backup regularly

---

## 📊 Performance Tuning

### PostgreSQL Optimization

**File:** `postgresql_tuning.conf`

```ini
# Add to postgresql.conf

# Memory
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
work_mem = 4MB

# Query Planning
random_page_cost = 1.1
effective_io_concurrency = 200

# Write Performance
wal_buffers = 16MB
checkpoint_completion_target = 0.9

# Connection Pooling
max_connections = 100
```

### Django Optimization

```python
# settings.py

# Connection pooling
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 600,  # Keep connections open for 10 min
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000'  # 30s query timeout
        }
    }
}

# Query optimization
DEBUG = False  # Disable in production
CONN_MAX_AGE = 600

# Use select_related and prefetch_related
memories = Memory.objects.select_related('user').prefetch_related('tags')
```

---

## ✅ Summary

**Implemented:**
- ✅ Smart database configuration (environment-based)
- ✅ Database migration scripts (SQLite ↔ PostgreSQL)
- ✅ Backup/restore scripts
- ✅ Docker PostgreSQL setup
- ✅ Complete documentation
- ✅ Best practices guide

**Result:**
- 🎯 **Clear guidance** (SQLite for dev, PostgreSQL for prod)
- 🔄 **Easy migration** (automated scripts)
- 📦 **Backup strategy** (automated)
- 🚀 **Production ready** (PostgreSQL configured)
- 📚 **Well documented** (this guide)

**Your database management is now professional and production-ready!** 🎉

---

**Quick Start:**
```bash
# Development (SQLite)
python manage.py migrate
python manage.py runserver

# Production (PostgreSQL)
# 1. Setup PostgreSQL (see guide above)
# 2. Configure .env.production
# 3. Run: python manage.py migrate
```

**Documentation:** You're reading it! 📖




























