# NextFactory Database Setup Guide

This guide provides comprehensive instructions for setting up PostgreSQL database for the NextFactory ERP+MES Exhibition Demo.

## 🚀 Quick Start - Autonomous Setup (Recommended)

For the fastest setup experience, use our autonomous setup script:

```bash
python setup_postgres.py
```

This single command will:
- ✅ Check and install all dependencies
- ✅ Install and configure PostgreSQL 
- ✅ Create database, users, and roles
- ✅ Set up all Phase 3 modules and demo data
- ✅ Test the complete installation
- ✅ Provide ready-to-use exhibition demo

**Perfect for exhibitions, demos, and quick deployments!**

---

## Manual Setup (Alternative Method)

If you prefer manual setup or need custom configuration, follow the detailed instructions below.

## Overview

NextFactory uses PostgreSQL as its primary database system, providing robust data management for ERP and MES operations. The database setup includes user management, role-based access control, and comprehensive Phase 3 modules including:

### Phase 3 Optional Modules
- **ERP: Sales & CRM** – Customer orders, relationships, order history
- **ERP: Asset Management** – Track machines, tools, asset status
- **MES: Resource Allocation** – Assign/monitor resources, auto-allocation
- **MES: Product Tracking & Traceability** – Log genealogy, audit/export
- **MES: Maintenance Management** – Schedule/track maintenance, alerts
- **MES: Labor Management** – Worker schedules, shift templates, performance

## Prerequisites

### System Requirements
- **PostgreSQL**: Version 12 or higher (recommended: 14+)
- **Python**: Version 3.8 or higher (recommended: 3.10+)
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Memory**: Minimum 4GB RAM (recommended: 8GB+)
- **Storage**: Minimum 2GB free space for database and application

### Python Dependencies
All Python dependencies are listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

## PostgreSQL Installation

### Windows Installation

1. **Download PostgreSQL**:
   - Visit https://www.postgresql.org/download/windows/
   - Download the installer for your Windows version
   - Choose version 14 or higher for best compatibility

2. **Run Installation**:
   - Execute the installer as Administrator
   - Choose installation directory (default: `C:\Program Files\PostgreSQL\14`)
   - Set superuser password (remember this password!)
   - Use default port 5432
   - Choose default locale

3. **Verify Installation**:
   ```cmd
   psql --version
   ```

### macOS Installation

1. **Using Homebrew** (recommended):
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install PostgreSQL
   brew install postgresql@14
   brew services start postgresql@14
   ```

2. **Using PostgreSQL.app**:
   - Download from https://postgresapp.com/
   - Drag to Applications folder
   - Launch and initialize

3. **Verify Installation**:
   ```bash
   psql --version
   ```

### Linux Installation (Ubuntu/Debian)

1. **Update Package Index**:
   ```bash
   sudo apt update
   ```

2. **Install PostgreSQL**:
   ```bash
   sudo apt install postgresql postgresql-contrib
   ```

3. **Start PostgreSQL Service**:
   ```bash
   sudo systemctl start postgresql
   sudo systemctl enable postgresql
   ```

4. **Verify Installation**:
   ```bash
   psql --version
   ```

## Database Configuration

### Step 1: Create Database User

Connect to PostgreSQL as superuser and create NextFactory user:

```sql
-- Connect as postgres superuser
sudo -u postgres psql

-- Create NextFactory user
CREATE USER nextfactory WITH PASSWORD 'nextfactory123';

-- Grant necessary privileges
ALTER USER nextfactory CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE postgres TO nextfactory;

-- Exit PostgreSQL
\q
```

### Step 2: Create NextFactory Database

```sql
-- Connect as nextfactory user
psql -U nextfactory -h localhost

-- Create the database
CREATE DATABASE nextfactory;

-- Connect to the new database
\c nextfactory;

-- Verify connection
SELECT current_database(), current_user;

-- Exit
\q
```

### Step 3: Configure Environment Variables

Create a `.env` file in the NextFactory root directory:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=nextfactory
DB_USER=nextfactory
DB_PASSWORD=nextfactory123
DB_ECHO=false
```

**Note**: The application will use these default values if no `.env` file is present.

## Database Schema and Tables

NextFactory automatically creates the following database schema:

### Core Tables

#### 1. Roles Table
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    can_edit_users BOOLEAN DEFAULT FALSE,
    can_view_reports BOOLEAN DEFAULT TRUE,
    can_manage_inventory BOOLEAN DEFAULT FALSE,
    can_access_mes BOOLEAN DEFAULT FALSE,
    can_access_erp BOOLEAN DEFAULT FALSE,
    can_create_orders BOOLEAN DEFAULT FALSE,
    can_modify_schedule BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id INTEGER REFERENCES roles(id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Inventory Items Table
```sql
CREATE TABLE inventory_items (
    id SERIAL PRIMARY KEY,
    item_code VARCHAR(50) UNIQUE NOT NULL,
    item_name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    quantity DECIMAL(10,2) DEFAULT 0.00,
    unit_of_measure VARCHAR(20) NOT NULL,
    unit_cost DECIMAL(10,2) DEFAULT 0.00,
    reorder_point DECIMAL(10,2) DEFAULT 0.00,
    supplier VARCHAR(200),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Constraints

The system automatically creates appropriate indexes and constraints:

```sql
-- Unique constraints
ALTER TABLE roles ADD CONSTRAINT uq_role_name UNIQUE (name);
ALTER TABLE users ADD CONSTRAINT uq_user_username UNIQUE (username);
ALTER TABLE users ADD CONSTRAINT uq_user_email UNIQUE (email);
ALTER TABLE inventory_items ADD CONSTRAINT uq_inventory_item_code UNIQUE (item_code);

-- Indexes for performance
CREATE INDEX idx_users_role_id ON users(role_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_inventory_category ON inventory_items(category);
CREATE INDEX idx_inventory_status ON inventory_items(status);
```

## Automated Setup

NextFactory provides automated database setup tools:

### Option 1: Using Database Utility Script

```bash
# Navigate to NextFactory directory
cd /path/to/NextFactory

# Run database setup
python database.py
```

This script will:
- Test PostgreSQL connection
- Create the database if it doesn't exist
- Initialize all tables and schema
- Verify setup completion

### Option 2: Using Application Initialization

```bash
# The main application will automatically initialize the database
python main.py
```

The application checks database status on startup and guides you through any required setup.

## Data Seeding

After database setup, populate with demonstration data:

```bash
# Seed database with demo data
python seed_db.py

# Force re-creation of existing data (use with caution)
python seed_db.py --force
```

The seeding script creates:
- 5 system roles with appropriate permissions
- 5 demo users (one for each role)
- 12 sample inventory items across different categories
- Realistic data for demonstration purposes

## Database Maintenance

### Backup Database

```bash
# Create backup
pg_dump -U nextfactory -h localhost nextfactory > nextfactory_backup.sql

# Restore from backup
psql -U nextfactory -h localhost nextfactory < nextfactory_backup.sql
```

### Monitor Database Performance

```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('nextfactory'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::text)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::text) DESC;

-- Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'nextfactory';
```

### Reset Database

To completely reset the database:

```bash
# Stop the application first

# Connect to PostgreSQL
psql -U nextfactory -h localhost

# Drop and recreate database
DROP DATABASE IF EXISTS nextfactory;
CREATE DATABASE nextfactory;
\q

# Re-run setup and seeding
python database.py
python seed_db.py
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Connection Refused Error
```
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

**Solution**:
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Start PostgreSQL: `sudo systemctl start postgresql`
- Check port 5432 is available: `netstat -an | grep 5432`

#### 2. Authentication Failed
```
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL: password authentication failed
```

**Solutions**:
- Verify username and password in `.env` file
- Reset user password:
  ```sql
  sudo -u postgres psql
  ALTER USER nextfactory PASSWORD 'nextfactory123';
  ```

#### 3. Database Does Not Exist
```
psql: error: connection to server at "localhost" (127.0.0.1), port 5432 failed: FATAL: database "nextfactory" does not exist
```

**Solution**:
- Run database setup: `python database.py`
- Or manually create: `createdb -U nextfactory nextfactory`

#### 4. Permission Denied
```
ERROR: permission denied to create database
```

**Solution**:
- Grant database creation privileges:
  ```sql
  sudo -u postgres psql
  ALTER USER nextfactory CREATEDB;
  ```

#### 5. Port Already in Use
```
FATAL: lock file "postmaster.pid" already exists
```

**Solutions**:
- Check if PostgreSQL is already running
- Kill existing processes: `sudo pkill postgres`
- Restart PostgreSQL service

## Security Considerations

### Production Deployment

For production use, implement these security measures:

1. **Strong Passwords**:
   - Use complex passwords for database users
   - Implement password rotation policies

2. **Network Security**:
   - Configure `pg_hba.conf` for restricted access
   - Use SSL/TLS connections
   - Limit network access to database server

3. **User Privileges**:
   - Create separate users for different applications
   - Use principle of least privilege
   - Regular privilege audits

4. **Backup Security**:
   - Encrypt database backups
   - Store backups in secure locations
   - Test backup restoration procedures

### Exhibition Security

For exhibition use:
- Use demonstration credentials only
- Reset database after each demonstration
- Monitor for unauthorized access attempts
- Implement automatic session timeouts

## Performance Optimization

### Configuration Tuning

Edit PostgreSQL configuration for better performance:

```postgresql
# postgresql.conf adjustments for demonstration use
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Query Optimization

The application includes optimized queries:
- Proper indexing on frequently accessed columns
- Efficient joins between related tables
- Pagination for large result sets
- Connection pooling for better resource management

## Exhibition Checklist

Before each demonstration:

- [ ] PostgreSQL service is running
- [ ] Database connectivity test passes
- [ ] Demo data is properly seeded
- [ ] All user accounts are functional
- [ ] Backup of clean database state exists
- [ ] Application starts without errors
- [ ] All role-based features work correctly

## Support and Resources

### Documentation
- [PostgreSQL Official Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Python psycopg2 Documentation](https://www.psycopg.org/docs/)

### NextFactory Specific Help
- Check application logs for detailed error messages
- Use `python database.py` for database diagnostics
- Run `python seed_db.py` to reset demo data
- Contact NextFactory development team for technical support

---

**Note**: This guide is specifically designed for the NextFactory Exhibition Demo. For production deployment, additional security and performance considerations should be implemented.