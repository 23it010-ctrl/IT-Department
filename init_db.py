import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

def init_db():
    print("Connecting to SQLite database...")
    print("🛡️  Data Safety Mode: Checking tables and preserving existing data...")
    conn = sqlite3.connect(Config.SQLITE_DB)
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
    
    # Insert default admin if not exists
    cursor.execute("SELECT id FROM users WHERE role='admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ('admin', hashed_pw, 'admin'))
        print("Default admin user created (Username: admin, Password: admin123)")
        
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
