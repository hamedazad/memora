# PostgreSQL Migration Guide

This guide will help you migrate your Memora Memory Assistant from SQLite to PostgreSQL.

## 🎯 Why PostgreSQL?

- **Better Performance**: Handles concurrent users more efficiently
- **Advanced Features**: Full-text search, JSON operations, complex queries
- **Production Ready**: Industry standard for production deployments
- **Scalability**: Better for growing applications
- **Data Integrity**: ACID compliance and advanced constraints

## 📋 Prerequisites

### 1. Install PostgreSQL

#### Windows
1. Download from [PostgreSQL Official Site](https://www.postgresql.org/download/windows/)
2. Run the installer
3. Remember the password you set for the `postgres` user
4. Add PostgreSQL to your PATH

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Install Python Dependencies
```bash
pip install psycopg2-binary
```

## 🚀 Migration Steps

### Step 1: Setup PostgreSQL Database

Run the PostgreSQL setup script:
```bash
python setup_postgresql.py
```

This script will:
- Check if PostgreSQL is installed
- Create a `.env` file with database configuration
- Create database and user
- Test the connection

### Step 2: Configure Environment Variables

Update your `.env` file with your actual PostgreSQL credentials:
```env
# Database Configuration
DB_NAME=memora_db
DB_USER=memora_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Django Secret Key
DJANGO_SECRET_KEY=your_secret_key_here
```

### Step 3: Migrate Data (Optional)

If you have existing data in SQLite that you want to preserve:

```bash
python migrate_to_postgresql.py
```

This script will:
- Backup your SQLite data to JSON files
- Switch Django to use PostgreSQL
- Restore all data to PostgreSQL
- Verify the migration

### Step 4: Run Django Migrations

```bash
python manage.py migrate
```

### Step 5: Create Superuser

```bash
python manage.py createsuperuser
```

### Step 6: Test the Application

```bash
python manage.py runserver
```

## 🔧 Manual Database Setup

If you prefer to set up the database manually:

### 1. Connect to PostgreSQL
```bash
psql -U postgres
```

### 2. Create Database and User
```sql
CREATE USER memora_user WITH PASSWORD 'your_secure_password';
CREATE DATABASE memora_db OWNER memora_user;
GRANT ALL PRIVILEGES ON DATABASE memora_db TO memora_user;
\q
```

### 3. Test Connection
```bash
psql -U memora_user -d memora_db -h localhost
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Refused
```
Error: could not connect to server: Connection refused
```
**Solution**: Make sure PostgreSQL is running
```bash
# Windows
net start postgresql

# macOS
brew services start postgresql

# Ubuntu
sudo systemctl start postgresql
```

#### 2. Authentication Failed
```
Error: FATAL: password authentication failed
```
**Solution**: Check your `.env` file and ensure the password is correct

#### 3. Database Does Not Exist
```
Error: database "memora_db" does not exist
```
**Solution**: Create the database manually or run the setup script

#### 4. Permission Denied
```
Error: permission denied for database
```
**Solution**: Grant proper permissions to your user

### Performance Optimization

#### 1. Connection Pooling
Add to your `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'memora_db'),
        'USER': os.getenv('DB_USER', 'memora_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'memora_password'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'charset': 'utf8',
        },
        'CONN_MAX_AGE': 60,  # Connection pooling
    }
}
```

#### 2. Index Optimization
PostgreSQL will automatically create indexes, but you can optimize further:
```sql
-- Create indexes for better search performance
CREATE INDEX idx_memory_content ON memory_assistant_memory USING gin(to_tsvector('english', content));
CREATE INDEX idx_memory_tags ON memory_assistant_memory USING gin(tags);
CREATE INDEX idx_memory_created_at ON memory_assistant_memory(created_at);
```

## 📊 Monitoring

### Check Database Size
```sql
SELECT pg_size_pretty(pg_database_size('memora_db'));
```

### Check Table Sizes
```sql
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### Monitor Connections
```sql
SELECT count(*) FROM pg_stat_activity WHERE datname = 'memora_db';
```

## 🔒 Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords for database users
2. **Limit Network Access**: Configure PostgreSQL to only accept connections from your application
3. **Regular Backups**: Set up automated backups
4. **Update Regularly**: Keep PostgreSQL updated with security patches
5. **Use SSL**: Enable SSL connections in production

## 📈 Production Deployment

For production deployment, consider:

1. **Connection Pooling**: Use `django-db-connection-pool` or `pgBouncer`
2. **Read Replicas**: Set up read replicas for better performance
3. **Backup Strategy**: Implement automated backups
4. **Monitoring**: Use tools like `pgAdmin` or `pg_stat_statements`
5. **Load Balancing**: Consider using multiple database servers

## 🎉 Migration Complete!

After completing the migration:

1. ✅ Test all functionality
2. ✅ Verify data integrity
3. ✅ Update your deployment scripts
4. ✅ Remove old SQLite files (optional)
5. ✅ Update documentation

Your Memora Memory Assistant is now running on PostgreSQL! 🚀 