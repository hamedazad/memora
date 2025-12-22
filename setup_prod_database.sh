#!/bin/bash
# Production Database Setup (PostgreSQL)

echo "========================================"
echo "Production Database Setup (PostgreSQL)"
echo "========================================"
echo ""

# Check environment variables
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ] || [ -z "$DB_HOST" ]; then
    echo "❌ Error: Missing required environment variables"
    echo ""
    echo "Please set:"
    echo "  export DB_NAME=memora_db"
    echo "  export DB_USER=memora_user"
    echo "  export DB_PASSWORD=your_password"
    echo "  export DB_HOST=localhost"
    echo "  export DB_PORT=5432"
    echo ""
    echo "Or create .env file with these values"
    exit 1
fi

echo "Configuration:"
echo "  Host: $DB_HOST"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Set environment
export ENVIRONMENT=production
export DB_ENGINE=django.db.backends.postgresql

# Test database connection
echo "Testing database connection..."
python manage.py dbshell --command "SELECT version();" >/dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Error: Cannot connect to PostgreSQL"
    echo ""
    echo "Check:"
    echo "  1. PostgreSQL is running"
    echo "  2. Database exists: createdb $DB_NAME"
    echo "  3. User has permissions"
    exit 1
fi

echo "  ✓ Connection successful!"
echo ""

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================"
echo "✅ Production database setup complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Create admin: python manage.py createsuperuser"
echo "  2. Test application"
echo "  3. Configure production web server (gunicorn/nginx)"
echo ""




























