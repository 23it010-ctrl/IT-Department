import os
import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

def init_db():
    db_path = Config.SQLITE_DB
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('student', 'faculty', 'admin'))
        )
    ''')
    
    # Create students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            roll_number TEXT UNIQUE,
            year TEXT CHECK(year IN ('1st', '2nd', '3rd', '4th')),
            email TEXT,
            phone TEXT,
            profile_photo TEXT,
            is_approved INTEGER DEFAULT 0,
            profile_locked INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create faculty table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            department TEXT,
            email TEXT,
            phone TEXT,
            profile_photo TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            date TEXT,
            uploaded_by TEXT,
            faculty_id INTEGER,
            image_url TEXT
        )
    ''')

    # Create news table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            uploaded_by TEXT,
            faculty_id INTEGER,
            date TEXT
        )
    ''')

    # Create notes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            subject TEXT,
            year TEXT,
            uploaded_by TEXT,
            file_url TEXT,
            date TEXT
        )
    ''')

    # Create achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            title TEXT,
            description TEXT,
            type TEXT,
            proof_url TEXT,
            date TEXT,
            is_approved INTEGER DEFAULT 0
        )
    ''')

    # Create site_content table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS site_content (
            page TEXT PRIMARY KEY,
            title TEXT,
            description TEXT
        )
    ''')
    
    # Create admins table
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

    # --- MIGRATIONS (Add missing columns to existing tables) ---
    def add_column_if_not_exists(table, column, definition):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if column not in columns:
            print(f"🔧 Migrating: Adding column '{column}' to table '{table}'...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    # Students table migrations
    add_column_if_not_exists('students', 'is_approved', 'INTEGER DEFAULT 0')
    add_column_if_not_exists('students', 'profile_locked', 'INTEGER DEFAULT 0')
    add_column_if_not_exists('students', 'email', 'TEXT')
    add_column_if_not_exists('students', 'phone', 'TEXT')
    add_column_if_not_exists('students', 'profile_photo', 'TEXT')

    # Faculty table migrations
    add_column_if_not_exists('faculty', 'profile_photo', 'TEXT')
    add_column_if_not_exists('faculty', 'email', 'TEXT')
    add_column_if_not_exists('faculty', 'phone', 'TEXT')

    # Achievements table migrations
    add_column_if_not_exists('achievements', 'is_approved', 'INTEGER DEFAULT 0')

    # Admins table migrations
    add_column_if_not_exists('admins', 'profile_photo', 'TEXT')
    add_column_if_not_exists('admins', 'email', 'TEXT')
    add_column_if_not_exists('admins', 'phone', 'TEXT')
    
    # Handle Default Admin and Linked Data
    cursor.execute("SELECT id FROM users WHERE role='admin'")
    admin_users = cursor.fetchall()
    if not admin_users:
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', hashed_pw, 'admin'))
        admin_id = cursor.lastrowid
        print("Default admin user created (Username: admin, Password: admin123)")
    else:
        admin_id = admin_users[0][0]

    cursor.execute("INSERT OR IGNORE INTO admins (user_id, name) VALUES (?, ?)", (admin_id, 'Administrator'))
    
    conn.commit()
    
    # Data Permanence Verification
    print("--- 📊 Data Permanence Summary ---")
    users_count = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    students_count = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    faculty_count = cursor.execute("SELECT COUNT(*) FROM faculty").fetchone()[0]
    print(f"✅ Users Stored: {users_count}")
    print(f"✅ Students Registered: {students_count}")
    print(f"✅ Faculty Members: {faculty_count}")
    print("----------------------------------")
    
    conn.close()
    print("SQLite database initialized successfully!")

if __name__ == '__main__':
    init_db()
