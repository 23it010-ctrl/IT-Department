import shutil
import os
from datetime import datetime

def backup_db():
    source = 'database.db'
    if not os.path.exists(source):
        print("Error: database.db not found. Nothing to backup.")
        return

    # Create backup directory if it doesn't exist
    backup_dir = 'backups'
    os.makedirs(backup_dir, exist_ok=True)

    # Create timestamped backup filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    destination = f'backups/database_backup_{timestamp}.db'

    try:
        shutil.copy2(source, destination)
        print(f"✅ Success! Database permanently backed up to: {destination}")
        print("You can run this script anytime to save a permanent copy of your data.")
    except Exception as e:
        print(f"❌ Backup failed: {e}")

if __name__ == '__main__':
    backup_db()
