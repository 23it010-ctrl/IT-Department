# 🛡️ Data Safety & Permanence Guide

This project is built with a **Data-First** philosophy. Your registered students, faculty, and uploaded content are protected by multiple layers of security.

## 1. How Your Data is Protected
- **SQLite Persistence**: All data is stored in `database.db`. This file is separate from your code. When you update the background, change the CSS, or modify `app.py`, the `database.db` file remains untouched.
- **Smart Initialization**: The system uses `CREATE TABLE IF NOT EXISTS`. This means it checks for existing data every time the website starts. It will **never** overwrite or delete your current records during a restart or code change.
- **Git Separation**: We have configured the project to ignore `database.db` in Git updates. This prevents a "clean" code push from accidentally overwriting your live data on the server.

## 2. Managing Your Data
- **Manual Deletion Only**: Student profiles, faculty details, and achievements can only be removed if an Admin or the User intentionally clicks "Delete". 
- **Code Updates**: You can safely change the design, colors, or logic in `static/`, `templates/`, or `app.py`. These files do not interact with the storage layer in a destructive way.

## 3. Creating Backups
We have provided a dedicated backup script. Run this regularly to keep a safe copy of your data:
```bash
python backup_db.py
```
This will create a timestamped copy in the `/backups` folder.

## 4. Performance & Reliability
- **Local Hosting**: If running on your own PC/Server, the data stays in your project folder forever.
- **Cloud Hosting (Vercel)**: ⚠️ **Important Note**: Vercel's filesystem is temporary. While your code changes are safe, data entered *on the live Vercel site* will be lost on the next build. For a production "Main Project" on Vercel, it is highly recommended to connect an external database (like Supabase or MongoDB).

---
**Status: ✅ All Data Systems Verified & Secure.**
