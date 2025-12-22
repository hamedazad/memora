#!/bin/bash
# Development Database Setup (SQLite)

echo "========================================"
echo "Development Database Setup (SQLite)"
echo "========================================"
echo ""

# Set environment
export ENVIRONMENT=development
export DB_ENGINE=django.db.backends.sqlite3

echo "Current configuration:"
echo "  Environment: $ENVIRONMENT"
echo "  Database: SQLite (db.sqlite3)"
echo ""

# Ask about resetting database
read -p "Reset database? This will DELETE all data! (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f db.sqlite3 ]; then
        rm db.sqlite3
        echo "  ✓ Removed old database"
    fi
fi

echo ""
echo "Running migrations..."
python manage.py migrate

echo ""
echo "========================================"
echo "✅ Database setup complete!"
echo "========================================"
echo ""
echo "Database file: db.sqlite3"
echo ""
echo "Next steps:"
echo "  1. Create admin user: python manage.py createsuperuser"
echo "  2. Start server: python manage.py runserver"
echo "  3. Access admin: http://localhost:8000/admin/"
echo ""




























