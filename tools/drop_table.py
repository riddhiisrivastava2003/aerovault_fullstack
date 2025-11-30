"""Drop a table using Django DB connection.

Usage:
  python tools/drop_table.py django_admin_log

This script loads your Django settings and executes `DROP TABLE IF EXISTS <table>`
using the same DB credentials Django uses.
"""
import os
import sys

# Ensure project root is in path
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aerovault.settings')

import django
from django.db import connection

try:
    django.setup()
except Exception as e:
    print('Error setting up Django:', e)
    sys.exit(1)

if len(sys.argv) < 2:
    print('Usage: python tools/drop_table.py <table_name>')
    sys.exit(1)

table = sys.argv[1]

with connection.cursor() as cursor:
    try:
        sql = f"DROP TABLE IF EXISTS `{table}`;"
        cursor.execute(sql)
        print('Dropped table (if existed):', table)
    except Exception as e:
        print('Error executing DROP TABLE:', e)
        sys.exit(2)

print('Done')
