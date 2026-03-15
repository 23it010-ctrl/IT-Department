import sqlite3
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='View SQLite Database Tables')
    parser.add_argument('table', nargs='?', default=None, help='Name of the table to view (e.g. users, students)')
    args = parser.parse_args()

    db_path = 'database.db'
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        # If no table specified, list all tables
        if not args.table:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            print("=== AVAILABLE TABLES ===")
            for t in tables:
                print(f" - {t['name']}")
                
            print("\nTo view a specific table, run: python view_db.py <table_name>")
            print("Example: python view_db.py students")
            return

        # View specific table
        table_name = args.table
        
        # A simple check to prevent SQL injection for basic use
        tables = [t['name'] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if table_name not in tables:
            print(f"Error: Table '{table_name}' does not exist.")
            print("Available tables are:", ", ".join(tables))
            return
            
        print(f"=== VIEWING TABLE: {table_name.upper()} ===")
        rows = conn.execute(f"SELECT * FROM {table_name} LIMIT 50").fetchall()
        
        if not rows:
            print(f"The table '{table_name}' is currently empty.")
            return
            
        # Get column names
        keys = rows[0].keys()
        
        # Calculate column widths
        widths = {k: len(str(k)) for k in keys}
        for row in rows:
            for k in keys:
                widths[k] = max(widths[k], len(str(row[k])))
                
        # Print header
        header = " | ".join(str(k).ljust(widths[k]) for k in keys)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in rows:
            print(" | ".join(str(row[k]).ljust(widths[k]) for k in keys))
            
        print(f"\nShowing {len(rows)} records.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()
