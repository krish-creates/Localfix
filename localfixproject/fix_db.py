import sqlite3

conn = sqlite3.connect('localfix.db')
cursor = conn.cursor()

try:
    # This command adds the missing column to your existing table
    cursor.execute("ALTER TABLE reviews ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
    conn.commit()
    print("Column added successfully!")
except sqlite3.OperationalError:
    print("Column already exists or table doesn't exist.")

conn.close()