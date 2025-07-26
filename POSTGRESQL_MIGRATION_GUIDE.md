# PostgreSQL Migration Guide for MindCare

## 🎯 Overview

This guide will help you migrate from SQLite to PostgreSQL safely and successfully.

## 📋 Prerequisites

### 1. Install PostgreSQL

- **Windows**: Download from [PostgreSQL Official Site](https://www.postgresql.org/download/windows/)
- **macOS**: `brew install postgresql`
- **Linux**: `sudo apt-get install postgresql postgresql-contrib`

### 2. Install pgAdmin (Optional but Recommended)

- Download from [pgAdmin Official Site](https://www.pgadmin.org/download/)
- Provides web-based interface for database management

## 🚀 Step-by-Step Migration Process

### Phase 1: PostgreSQL Setup

1. **Install PostgreSQL**

   ```bash
   # Follow installation wizard
   # Remember the password you set for 'postgres' user
   ```

2. **Create Database**

   ```sql
   -- Connect to PostgreSQL as postgres user
   psql -U postgres

   -- Create database
   CREATE DATABASE mindcare_db;

   -- Exit
   \q
   ```

3. **Test Connection**
   ```bash
   psql -U postgres -d mindcare_db -h localhost
   ```

### Phase 2: Update Environment Variables

1. **Edit .env file**

   ```bash
   # Update these values in your .env file:
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=mindcare_db
   DB_USER=postgres
   DB_PASSWORD=your_actual_password_here
   DB_HOST=localhost
   DB_PORT=5432
   ```

2. **Verify .env file**
   ```bash
   cat .env
   ```

### Phase 3: Run Migration

1. **Test current setup**

   ```bash
   python manage.py check
   ```

2. **Run migration script**

   ```bash
   python migrate_to_postgresql.py
   ```

3. **Or run manually**

   ```bash
   # Test connection
   python manage.py dbshell

   # Run migrations
   python manage.py migrate

   # Load backup data
   python manage.py loaddata backup_sqlite.json

   # Create superuser if needed
   python manage.py createsuperuser
   ```

### Phase 4: Verification

1. **Test Django**

   ```bash
   python manage.py runserver
   ```

2. **Check database**

   ```bash
   python manage.py dbshell
   ```

3. **Verify data**
   ```bash
   python manage.py shell
   ```
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   print(f"Users: {User.objects.count()}")
   ```

## 🔧 pgAdmin Setup

### 1. Install pgAdmin

- Download and install pgAdmin 4
- Launch pgAdmin

### 2. Connect to Database

1. Right-click "Servers" → "Register" → "Server"
2. **General Tab**:
   - Name: `MindCare Local`
3. **Connection Tab**:
   - Host: `localhost`
   - Port: `5432`
   - Database: `mindcare_db`
   - Username: `postgres`
   - Password: `your_password`

### 3. Test Connection

- Expand your server
- Expand "Databases"
- You should see `mindcare_db`

## 🛡️ Safety Measures

### Backup Strategy

```bash
# Before migration
cp db.sqlite3 db.sqlite3.backup

# After successful migration
# Keep SQLite backup for 1 week
```

### Rollback Plan

If something goes wrong:

1. Stop Django server
2. Update .env: `DB_ENGINE=django.db.backends.sqlite3`
3. Restart Django server
4. System will use SQLite again

## 🧪 Testing Checklist

- [ ] User registration works
- [ ] User login works
- [ ] All models save correctly
- [ ] Admin interface works
- [ ] All views load properly
- [ ] File uploads work
- [ ] Search functionality works
- [ ] Pagination works

## 🚨 Troubleshooting

### Common Issues

1. **Connection Refused**

   - Check if PostgreSQL is running
   - Verify port 5432 is open
   - Check firewall settings

2. **Authentication Failed**

   - Verify username/password in .env
   - Check pg_hba.conf file
   - Try connecting with psql first

3. **Database Does Not Exist**

   - Create database manually
   - Check database name in .env

4. **Migration Errors**
   - Check for conflicting migrations
   - Run `python manage.py showmigrations`
   - Reset migrations if needed

### Useful Commands

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# Check Django database connection
python manage.py dbshell

# Reset migrations (if needed)
python manage.py migrate --fake-initial

# Check installed apps
python manage.py check --deploy
```

## 📊 Performance Optimization

### PostgreSQL Settings

```sql
-- In postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

### Django Settings

```python
# Add to settings.py
DATABASES = {
    'default': {
        # ... existing config ...
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'charset': 'utf8',
        },
    }
}
```

## 🎉 Success Criteria

Migration is successful when:

- [ ] All data is preserved
- [ ] All functionality works
- [ ] Performance is acceptable
- [ ] Backup is verified
- [ ] Team is trained on pgAdmin

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Review PostgreSQL logs
3. Check Django logs
4. Verify environment variables
5. Test with a simple Django app first

---

**Remember**: Take your time, test thoroughly, and always have a backup plan!
