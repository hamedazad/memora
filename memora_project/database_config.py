"""
Smart Database Configuration
Automatically selects database based on environment
"""

import os
from pathlib import Path


def get_database_config(base_dir):
    """
    Get database configuration based on environment
    
    Environment Priority:
    1. ENVIRONMENT variable (production, staging, development, testing)
    2. DB_ENGINE variable (explicit database type)
    3. Default: SQLite for development
    
    Returns:
        dict: Database configuration
    """
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    db_engine = os.getenv('DB_ENGINE', os.getenv('DATABASE_ENGINE'))
    
    # Production: Always use PostgreSQL
    if environment == 'production':
        if not os.getenv('DB_PASSWORD'):
            raise ValueError('DB_PASSWORD environment variable is required in production')
        
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', os.getenv('DATABASE_NAME', 'memora_db')),
                'USER': os.getenv('DB_USER', os.getenv('DATABASE_USER', 'memora_user')),
                'PASSWORD': os.getenv('DB_PASSWORD', os.getenv('DATABASE_PASSWORD')),
                'HOST': os.getenv('DB_HOST', os.getenv('DATABASE_HOST', 'localhost')),
                'PORT': os.getenv('DB_PORT', os.getenv('DATABASE_PORT', '5432')),
                'CONN_MAX_AGE': 600,  # Connection pooling
                'OPTIONS': {
                    'connect_timeout': 10,
                    'options': '-c statement_timeout=30000'  # 30 second query timeout
                }
            }
        }
    
    # Staging: Use PostgreSQL
    elif environment == 'staging':
        return {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.getenv('DB_NAME', os.getenv('DATABASE_NAME', 'memora_staging_db')),
                'USER': os.getenv('DB_USER', os.getenv('DATABASE_USER', 'memora_staging_user')),
                'PASSWORD': os.getenv('DB_PASSWORD', os.getenv('DATABASE_PASSWORD', 'staging_password')),
                'HOST': os.getenv('DB_HOST', os.getenv('DATABASE_HOST', 'localhost')),
                'PORT': os.getenv('DB_PORT', os.getenv('DATABASE_PORT', '5432')),
                'CONN_MAX_AGE': 300,
            }
        }
    
    # Testing: Use SQLite in memory for speed
    elif environment == 'testing':
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',  # In-memory for speed
            }
        }
    
    # Development: Default to SQLite, allow PostgreSQL override
    else:
        # Explicit PostgreSQL request
        if db_engine and 'postgresql' in db_engine:
            return {
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': os.getenv('DB_NAME', os.getenv('DATABASE_NAME', 'memora_dev_db')),
                    'USER': os.getenv('DB_USER', os.getenv('DATABASE_USER', 'memora_dev_user')),
                    'PASSWORD': os.getenv('DB_PASSWORD', os.getenv('DATABASE_PASSWORD', 'dev_password')),
                    'HOST': os.getenv('DB_HOST', os.getenv('DATABASE_HOST', 'localhost')),
                    'PORT': os.getenv('DB_PORT', os.getenv('DATABASE_PORT', '5432')),
                }
            }
        
        # Default: SQLite for development (best for most developers)
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': base_dir / 'db.sqlite3',
                'OPTIONS': {
                    'timeout': 20,
                }
            }
        }


def get_database_info():
    """
    Get human-readable database information for logging/debugging
    
    Returns:
        dict: Database information
    """
    environment = os.getenv('ENVIRONMENT', 'development').lower()
    db_engine = os.getenv('DB_ENGINE', os.getenv('DATABASE_ENGINE', ''))
    
    if environment == 'production':
        return {
            'environment': 'Production',
            'database_type': 'PostgreSQL',
            'host': os.getenv('DB_HOST', 'localhost'),
            'name': os.getenv('DB_NAME', 'memora_db'),
            'recommended': True,
            'description': 'Production database with connection pooling'
        }
    elif environment == 'staging':
        return {
            'environment': 'Staging',
            'database_type': 'PostgreSQL',
            'host': os.getenv('DB_HOST', 'localhost'),
            'name': os.getenv('DB_NAME', 'memora_staging_db'),
            'recommended': True,
            'description': 'Staging environment for testing'
        }
    elif environment == 'testing':
        return {
            'environment': 'Testing',
            'database_type': 'SQLite',
            'file': ':memory:',
            'recommended': True,
            'description': 'In-memory database for fast testing'
        }
    else:
        if db_engine and 'postgresql' in db_engine:
            return {
                'environment': 'Development',
                'database_type': 'PostgreSQL',
                'host': os.getenv('DB_HOST', 'localhost'),
                'name': os.getenv('DB_NAME', 'memora_dev_db'),
                'recommended': False,
                'description': 'Optional PostgreSQL for development',
                'note': 'SQLite is recommended for easier development'
            }
        else:
            return {
                'environment': 'Development',
                'database_type': 'SQLite',
                'file': 'db.sqlite3',
                'recommended': True,
                'description': 'Fast and easy development database'
            }


def print_database_info():
    """Print current database configuration (for debugging)"""
    info = get_database_info()
    
    print("=" * 60)
    print("Database Configuration")
    print("=" * 60)
    print(f"Environment: {info['environment']}")
    print(f"Database: {info['database_type']}")
    
    if 'host' in info:
        print(f"Host: {info['host']}")
        print(f"Name: {info['name']}")
    elif 'file' in info:
        print(f"File: {info['file']}")
    
    print(f"Recommended: {'✅ Yes' if info['recommended'] else '⚠️  No'}")
    print(f"Description: {info['description']}")
    
    if 'note' in info:
        print(f"Note: {info['note']}")
    
    print("=" * 60)




























