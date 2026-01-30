import pymysql

try:
    conn = pymysql.connect(host='localhost', user='root', password='root')
    cursor = conn.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS neighbourhood')
    conn.commit()
    cursor.close()
    conn.close()
    print('✓ Database neighbourhood created successfully!')
except Exception as e:
    print(f'✗ Error: {e}')
