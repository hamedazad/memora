# PostgreSQL Admin Access Guide

## 🗄️ **PostgreSQL Administration Options**

### **Option 1: pgAdmin (Web Interface - Recommended)**

**pgAdmin** is the most popular PostgreSQL administration tool with a user-friendly web interface.

#### **How to Access:**
1. **Launch pgAdmin:**
   - Search "pgAdmin" in Windows Start menu
   - Or run: `"C:\Program Files\PostgreSQL\15\bin\pgAdmin4.exe"`

2. **pgAdmin opens in browser** (usually `http://127.0.0.1:54321`)

3. **Add your database server:**
   - Right-click "Servers" → "Register" → "Server"
   - **General tab:**
     - Name: `Memora Database`
   - **Connection tab:**
     - Host: `localhost`
     - Port: `5432`
     - Database: `memora_db`
     - Username: `memora_user`
     - Password: `memora_password_2024`

#### **pgAdmin Features:**
- 📊 **Database Browser**: Navigate tables, views, functions
- 🔍 **Query Tool**: Run SQL queries with syntax highlighting
- 📈 **Statistics**: View database performance metrics
- 🔧 **Schema Management**: Create/modify tables, indexes
- 📋 **Data Viewer**: Browse and edit table data
- 🛡️ **Security**: Manage users and permissions

### **Option 2: Command Line (psql)**

**psql** is the PostgreSQL interactive terminal.

#### **How to Access:**
```bash
# Navigate to PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\15\bin"

# Connect to database
psql -U memora_user -d memora_db -h localhost -p 5432
# Enter password when prompted: memora_password_2024
```

#### **Useful psql Commands:**
```sql
-- List all tables
\dt

-- Describe table structure
\d table_name

-- List databases
\l

-- Switch database
\c database_name

-- List users
\du

-- Show current database
SELECT current_database();

-- Show table data
SELECT * FROM memory_assistant_memory LIMIT 10;

-- Exit psql
\q
```

### **Option 3: Django Admin (Web Interface)**

**Django Admin** provides a web interface for your application data.

#### **How to Access:**
1. **Start your Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Visit Django Admin:**
   - URL: `http://localhost:8000/admin/`
   - Login with your superuser credentials

#### **Django Admin Features:**
- 👥 **User Management**: Create/edit users
- 📝 **Memory Management**: View/edit memories
- 🔍 **Search**: Search through your data
- 📊 **Statistics**: View data counts

### **Option 4: Third-Party Tools**

#### **DBeaver (Free, Cross-platform)**
- Download from: https://dbeaver.io/
- Supports PostgreSQL and many other databases
- Rich features for database management

#### **DataGrip (JetBrains - Paid)**
- Professional database IDE
- Advanced SQL editor and debugging

## 🔧 **Quick Database Commands**

### **Check Database Status:**
```bash
# Check if PostgreSQL is running
sc query postgresql-x64-15

# Start PostgreSQL service
net start postgresql-x64-15

# Stop PostgreSQL service
net stop postgresql-x64-15
```

### **Backup Database:**
```bash
# Create backup
pg_dump -U memora_user -d memora_db -h localhost > backup.sql

# Restore backup
psql -U memora_user -d memora_db -h localhost < backup.sql
```

### **Check Database Size:**
```sql
-- In psql or pgAdmin query tool
SELECT 
    pg_size_pretty(pg_database_size('memora_db')) as database_size;
```

## 🎯 **Recommended Workflow**

1. **For daily development**: Use **Django Admin** (`http://localhost:8000/admin/`)
2. **For database administration**: Use **pgAdmin**
3. **For quick queries**: Use **psql** command line
4. **For complex operations**: Use **DBeaver** or **DataGrip**

## 🔐 **Security Notes**

- Keep your database passwords secure
- Don't share admin credentials
- Regularly backup your database
- Use strong passwords for production environments

## 📞 **Need Help?**

- **pgAdmin Documentation**: https://www.pgadmin.org/docs/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/
- **Django Admin Documentation**: https://docs.djangoproject.com/en/stable/ref/contrib/admin/ 