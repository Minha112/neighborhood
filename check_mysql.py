import pymysql
from django.db import connections
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'neighborhood_project.settings')
django.setup()

print("=" * 50)
print("MySQL Connection Verification")
print("=" * 50)

# Test 1: Direct PyMySQL connection
try:
    conn = pymysql.connect(host='localhost', user='root', password='root', database='neighbourhood')
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"✓ Direct connection: MySQL {version[0]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Direct connection failed: {e}")

# Test 2: Django connection
try:
    db = connections['default']
    db.ensure_connection()
    print(f"✓ Django connection: Connected to '{db.settings_dict['NAME']}'")
except Exception as e:
    print(f"✗ Django connection failed: {e}")

# Test 3: Check tables
try:
    cursor = connections['default'].cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"✓ Database tables: {len(tables)} tables found")
    cursor.close()
except Exception as e:
    print(f"✗ Cannot retrieve tables: {e}")

print("=" * 50)
