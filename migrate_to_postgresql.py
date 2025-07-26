#!/usr/bin/env python
"""
Migration script to help migrate from SQLite to PostgreSQL
Run this script after setting up PostgreSQL and updating your .env file
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

def main():
    # Setup Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindcare.settings')
    django.setup()
    
    print("🚀 Starting PostgreSQL Migration Process...")
    print("=" * 50)
    
    # Step 1: Test database connection
    print("1. Testing PostgreSQL connection...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL connected successfully!")
            print(f"   Version: {version[0]}")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("   Please check your .env file and PostgreSQL installation")
        return False
    
    # Step 2: Run migrations
    print("\n2. Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Step 3: Load data from backup
    print("\n3. Loading data from backup...")
    if os.path.exists('backup_sqlite.json'):
        try:
            execute_from_command_line(['manage.py', 'loaddata', 'backup_sqlite.json'])
            print("✅ Data loaded successfully!")
        except Exception as e:
            print(f"❌ Data loading failed: {e}")
            print("   You may need to manually load the data")
    else:
        print("⚠️  No backup file found. Skipping data loading.")
    
    # Step 4: Create superuser if needed
    print("\n4. Checking for superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            print("   No superuser found. Creating one...")
            execute_from_command_line(['manage.py', 'createsuperuser'])
        else:
            print("✅ Superuser already exists!")
    except Exception as e:
        print(f"❌ Superuser creation failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Migration completed successfully!")
    print("   Your Django app is now using PostgreSQL!")
    print("\nNext steps:")
    print("1. Test your application thoroughly")
    print("2. Update your .env file with production settings")
    print("3. Consider setting up pgAdmin for database management")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 