import sqlite3
import os

print("Applying DB patch...")
conn = sqlite3.connect('d:/Depart/database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        email TEXT,
        phone TEXT,
        profile_photo TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
''')

cursor.execute("SELECT id FROM users WHERE role='admin'")
admins = cursor.fetchall()
for admin in admins:
    cursor.execute("INSERT OR IGNORE INTO admins (user_id, name) VALUES (?, ?)", (admin[0], 'Administrator'))

conn.commit()
conn.close()
print("Patch applied successfully.")
