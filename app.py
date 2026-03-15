import os
import json
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from config import Config
from init_db import init_db

app = Flask(__name__)
app.config.from_object(Config)
app.permanent_session_lifetime = timedelta(days=7)

# Auto-initialize database
init_db()

# Configure Uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect(app.config['SQLITE_DB'])
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if user:
            g.user = dict(user)
        conn.close()

# Context processors
@app.context_processor
def inject_globals():
    conn = get_db_connection()
    c_name = conn.execute("SELECT description FROM site_content WHERE page='site_name'").fetchone()
    c_icon = conn.execute("SELECT description FROM site_content WHERE page='site_icon'").fetchone()
    
    c_ig = conn.execute("SELECT description FROM site_content WHERE page='social_instagram'").fetchone()
    c_fb = conn.execute("SELECT description FROM site_content WHERE page='social_facebook'").fetchone()
    c_tw = conn.execute("SELECT description FROM site_content WHERE page='social_twitter'").fetchone()
    conn.close()
    
    site_name = c_name['description'] if c_name else "Department Portal"
    site_icon = c_icon['description'] if c_icon else ""
    return dict(
        current_user=g.user, 
        site_name=site_name, 
        site_icon=site_icon,
        social_instagram=c_ig['description'] if c_ig else "",
        social_facebook=c_fb['description'] if c_fb else "",
        social_twitter=c_tw['description'] if c_tw else ""
    )

# ========== PUBLIC ROUTES ========== #

@app.route('/')
def home():
    conn = get_db_connection()
    content_row = conn.execute("SELECT * FROM site_content WHERE page = 'home'").fetchone()
    conn.close()
    
    if content_row:
        content = dict(content_row)
    else:
        content = {
            "title": "Welcome to the Department",
            "description": "Excellence in technological education and innovation."
        }
    return render_template('home.html', content=content)

@app.route('/students')
def students():
    year_filter = request.args.get('year')
    roll_filter = request.args.get('roll_number')
    conn = get_db_connection()
    
    query = "SELECT * FROM students WHERE is_approved = 1"
    params = []
    
    if year_filter:
        query += " AND year = ?"
        params.append(year_filter)
        
    if roll_filter:
        query += " AND roll_number LIKE ?"
        params.append(f"%{roll_filter}%")
        
    query += " ORDER BY year ASC"
    
    students_list = conn.execute(query, params).fetchall()
        
    conn.close()
    return render_template('students.html', students=[dict(s) for s in students_list], year_filter=year_filter, roll_filter=roll_filter)

@app.route('/achievements')
def achievements_page():
    conn = get_db_connection()
    achievements_list = conn.execute("""
        SELECT a.*, s.name as student_name, s.year, s.profile_photo
        FROM achievements a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.is_approved = 1 
        ORDER BY a.id DESC
    """).fetchall()
    conn.close()
    return render_template('achievements.html', achievements=[dict(a) for a in achievements_list])

@app.route('/faculty_list')
def faculty_list():
    conn = get_db_connection()
    faculty_members = conn.execute("SELECT * FROM faculty").fetchall()
    conn.close()
    return render_template('faculty.html', faculty=[dict(f) for f in faculty_members])

@app.route('/labs')
def labs():
    conn = get_db_connection()
    c_labs = conn.execute("SELECT description FROM site_content WHERE page='labs'").fetchone()
    conn.close()
    
    if c_labs:
        try:
            content = json.loads(c_labs['description'])
        except Exception:
            content = {"title": "State of the Art Laboratories", "details": []}
    else:
        content = {
            "title": "State of the Art Laboratories",
            "details": [{"name": "Computer Networks Lab", "software": "Cisco Packet Tracer, Wireshark"}, {"name": "Database Lab", "software": "MySQL, Oracle, MongoDB"}]
        }
    return render_template('labs.html', content=content)

@app.route('/events')
def events():
    conn = get_db_connection()
    events_list = conn.execute("SELECT * FROM events ORDER BY date DESC").fetchall()
    conn.close()
    return render_template('events.html', events=[dict(e) for e in events_list])

@app.route('/news')
def news():
    conn = get_db_connection()
    news_list = conn.execute("SELECT * FROM news ORDER BY date DESC").fetchall()
    
    # parse date strings to real dates for the template
    parsed_news = []
    for item in news_list:
        d = dict(item)
        d_typed: dict = {k: v for k, v in d.items()}
        try:
            d_typed['date'] = datetime.strptime(str(d_typed['date']), '%Y-%m-%d %H:%M:%S.%f')
        except:
            d_typed['date'] = datetime.now() # fallback
        parsed_news.append(d_typed)
        
    conn.close()
    return render_template('news.html', news=parsed_news)

@app.route('/contact')
def contact():
    conn = get_db_connection()
    c_addr = conn.execute("SELECT description FROM site_content WHERE page='contact_address'").fetchone()
    c_email = conn.execute("SELECT description FROM site_content WHERE page='contact_email'").fetchone()
    c_phone = conn.execute("SELECT description FROM site_content WHERE page='contact_phone'").fetchone()
    c_yt = conn.execute("SELECT description FROM site_content WHERE page='social_youtube'").fetchone()
    c_ig = conn.execute("SELECT description FROM site_content WHERE page='social_instagram'").fetchone()
    conn.close()
    
    address = c_addr['description'] if c_addr else "PSR Engineering College, Sivakasi"
    email = c_email['description'] if c_email else "info@psr.edu.in"
    phone = c_phone['description'] if c_phone else "+91 12345 67890"
    youtube = c_yt['description'] if c_yt else "#"
    instagram = c_ig['description'] if c_ig else "#"
    
    return render_template('contact.html', address=address, email=email, phone=phone, youtube=youtube, instagram=instagram)


# ========== AUTHENTICATION ========== #

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            if user['role'] == 'student':
                student_check = conn.execute("SELECT is_approved FROM students WHERE user_id = ?", (user['id'],)).fetchone()
                if not student_check or not student_check['is_approved']:
                    flash('Your account is waiting for admin verification.', 'warning')
                    conn.close()
                    return render_template('login.html')
                    
            session['user_id'] = user['id']
            session['role'] = user['role']
            session.permanent = True
            flash('Login successful!', 'success')
            
            conn.close()
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user['role'] == 'faculty':
                return redirect(url_for('faculty_dashboard'))
            elif user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
        else:
            conn.close()
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        roll_number = request.form['roll_number']
        year = request.form['year']
        
        hashed_pw = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, 'student'))
            user_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO students (user_id, name, roll_number, year) VALUES (?, ?, ?, ?)", 
                (user_id, name, roll_number, year)
            )
            conn.commit()
            flash('Registration successful! Waiting for admin approval.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username or Roll Number already exists.", 'danger')
        except Exception as err:
            flash(f"Error: {err}", 'danger')
        finally:
            conn.close()
            
    return render_template('register.html')

# ========== STUDENT AREA ========== #

def handle_upload(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Using a timestamp to ensure uniqueness
        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename
    return None

@app.route('/student/dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if not g.user or g.user['role'] != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    student_data_row = conn.execute("SELECT * FROM students WHERE user_id = ?", (g.user['id'],)).fetchone()
    
    if not student_data_row:
        # Fallback if student profile is somehow missing
        flash('Student profile not found. Please contact admin.', 'danger')
        return redirect(url_for('login'))
        
    student_data = dict(student_data_row)
    
    if request.method == 'POST':
        action = request.form.get('req_action')
        
        if action == 'update_profile':
            email = request.form.get('email')
            phone = request.form.get('phone')
            name = request.form.get('name')
            roll_number = request.form.get('roll_number')
            
            # Photo upload
            photo_filename = student_data['profile_photo']
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file.filename != '':
                    new_filename = handle_upload(file)
                    if new_filename:
                        photo_filename = new_filename
            
            conn.execute("""
                UPDATE students SET name=?, roll_number=?, email=?, phone=?, profile_photo=? 
                WHERE user_id=?
            """, (name, roll_number, email, phone, photo_filename, g.user['id']))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('student_dashboard'))
            
        elif action == 'add_achievement':
            title = request.form.get('title')
            desc = request.form.get('description')
            ach_type = request.form.get('type') # event or achievement
            
            proof_filename = None
            if 'proof' in request.files:
                proof_filename = handle_upload(request.files['proof'])
                
            conn.execute("""
                INSERT INTO achievements (student_id, title, description, type, proof_url, date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_data['id'], title, desc, ach_type, proof_filename, str(datetime.now())))
            conn.commit()
            flash(f'{ach_type.capitalize()} added successfully!', 'success')
            
        elif action == 'lock_profile':
            conn.execute("UPDATE students SET profile_locked=1 WHERE user_id=?", (g.user['id'],))
            conn.commit()
            flash('Profile locked successfully!', 'success')
            return redirect(url_for('student_dashboard'))
            
        elif action == 'delete_self':
            # Completely clear student and user record
            conn.execute("DELETE FROM achievements WHERE student_id = ?", (student_data['id'],))
            conn.execute("DELETE FROM students WHERE id = ?", (student_data['id'],))
            conn.execute("DELETE FROM users WHERE id = ?", (g.user['id'],))
            conn.commit()
            session.clear()
            flash('Your account and all data have been permanently deleted.', 'info')
            return redirect(url_for('home'))
            
    student_data_row = conn.execute("SELECT * FROM students WHERE user_id = ?", (g.user['id'],)).fetchone()
    student_data = dict(student_data_row)
    
    achievements_list = conn.execute("SELECT * FROM achievements WHERE student_id = ?", (student_data['id'],)).fetchall()
    student_achievements = [dict(a) for a in achievements_list]
    
    conn.close()
    
    return render_template('student_dashboard.html', student=student_data, achievements=student_achievements)


# ========== FACULTY AREA ========== #

@app.route('/faculty/dashboard', methods=['GET', 'POST'])
def faculty_dashboard():
    if not g.user or g.user['role'] != 'faculty':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    faculty_data_row = conn.execute("SELECT * FROM faculty WHERE user_id = ?", (g.user['id'],)).fetchone()
    faculty_data = dict(faculty_data_row)
    
    if request.method == 'POST':
        action = request.form.get('req_action')
        
        if action == 'update_profile':
            email = request.form.get('email')
            phone = request.form.get('phone')
            photo_filename = faculty_data.get('profile_photo')
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file.filename != '':
                    new_filename = handle_upload(file)
                    if new_filename:
                        photo_filename = new_filename
            conn.execute("UPDATE faculty SET email=?, phone=?, profile_photo=? WHERE user_id=?", (email, phone, photo_filename, g.user['id']))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('faculty_dashboard'))
            
        elif action == 'add_news':
            conn.execute("""
                INSERT INTO news (title, content, uploaded_by, faculty_id, date)
                VALUES (?, ?, ?, ?, ?)
            """, (
                request.form.get('title'),
                request.form.get('content'),
                faculty_data['name'],
                faculty_data['id'],
                str(datetime.now())
            ))
            conn.commit()
            flash('News added successfully!', 'success')
            
        elif action == 'add_event':
            title = request.form.get('title')
            desc = request.form.get('description')
            date_str = request.form.get('date')
            
            image_filename = None
            if 'image' in request.files:
                image_filename = handle_upload(request.files['image'])
                
            conn.execute("""
                INSERT INTO events (title, description, date, uploaded_by, faculty_id, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (title, desc, date_str, faculty_data['name'], faculty_data['id'], image_filename))
            conn.commit()
            flash('Event added successfully!', 'success')
            
        elif action == 'upload_notes':
            doc_file = request.files.get('document')
            if doc_file and doc_file.filename != '':
                doc_filename = handle_upload(doc_file)
                conn.execute("""
                    INSERT INTO notes (title, subject, year, uploaded_by, file_url, date)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    request.form.get('title'),
                    request.form.get('subject'),
                    request.form.get('year'),
                    faculty_data['name'],
                    doc_filename,
                    str(datetime.now())
                ))
                conn.commit()
                flash('Notes uploaded successfully!', 'success')
                
        elif action == 'delete_self':
            # Completely clear faculty and user record
            conn.execute("DELETE FROM news WHERE faculty_id = ?", (faculty_data['id'],))
            conn.execute("DELETE FROM events WHERE faculty_id = ?", (faculty_data['id'],))
            conn.execute("DELETE FROM faculty WHERE id = ?", (faculty_data['id'],))
            conn.execute("DELETE FROM users WHERE id = ?", (g.user['id'],))
            conn.commit()
            session.clear()
            flash('Your faculty account and all your contributions have been permanently deleted.', 'info')
            return redirect(url_for('home'))
    
    news_rows = conn.execute("SELECT * FROM news WHERE faculty_id = ?", (faculty_data['id'],)).fetchall()
    faculty_news = [dict(n) for n in news_rows]
    conn.close()
    return render_template('faculty_dashboard.html', faculty=faculty_data, news=faculty_news)

@app.route('/faculty/students')
def faculty_students():
    if not g.user or g.user['role'] != 'faculty':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    students_list = conn.execute("SELECT * FROM students WHERE is_approved = 1 ORDER BY year, roll_number").fetchall()
    conn.close()
    return render_template('faculty_students.html', students=[dict(s) for s in students_list])


# ========== ADMIN AREA ========== #

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if not g.user or g.user['role'] != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    admin_data_row = conn.execute("SELECT * FROM admins WHERE user_id = ?", (g.user['id'],)).fetchone()
    admin_data = dict(admin_data_row) if admin_data_row else {"name": "Administrator", "email": "", "phone": ""}
    
    if request.method == 'POST':
        action = request.form.get('req_action')
        
        if action == 'update_profile':
            email = request.form.get('email')
            phone = request.form.get('phone')
            name = request.form.get('name')
            photo_filename = admin_data.get('profile_photo')
            
            if 'profile_photo' in request.files:
                file = request.files['profile_photo']
                if file.filename != '':
                    new_filename = handle_upload(file)
                    if new_filename:
                        photo_filename = new_filename
                        
            conn.execute("UPDATE admins SET name=?, email=?, phone=?, profile_photo=? WHERE user_id=?", (name, email, phone, photo_filename, g.user['id']))
            conn.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
    
    pending_students = conn.execute("SELECT count(*) as count FROM students WHERE is_approved = 0").fetchone()['count']
    pending_achievements = conn.execute("SELECT count(*) as count FROM achievements WHERE is_approved = 0").fetchone()['count']
    
    # Reload admin data securely
    admin_data_row = conn.execute("SELECT * FROM admins WHERE user_id = ?", (g.user['id'],)).fetchone()
    admin_data = dict(admin_data_row) if admin_data_row else {"name": "Administrator", "email": "", "phone": ""}
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                           pending_students=pending_students, 
                           pending_achievements=pending_achievements,
                           admin=admin_data)

@app.route('/admin/achievements', methods=['GET', 'POST'])
def admin_achievements():
    if not g.user or g.user['role'] != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('req_action')
        ach_id = request.form.get('achievement_id')
        
        if action == 'approve':
            conn.execute("UPDATE achievements SET is_approved = 1 WHERE id = ?", (ach_id,))
            conn.commit()
            flash('Achievement approved and published.', 'success')
        elif action == 'delete':
            conn.execute("DELETE FROM achievements WHERE id = ?", (ach_id,))
            conn.commit()
            flash('Achievement request deleted.', 'info')
            
        return redirect(url_for('admin_achievements'))

    pending_achievements = conn.execute("""
        SELECT a.*, s.name as student_name, s.roll_number, s.year
        FROM achievements a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.is_approved = 0
    """).fetchall()
    
    approved_achievements = conn.execute("""
        SELECT a.*, s.name as student_name, s.roll_number, s.year
        FROM achievements a 
        JOIN students s ON a.student_id = s.id 
        WHERE a.is_approved = 1
    """).fetchall()
    
    conn.close()
    return render_template('admin_achievements.html', 
                           pending=[dict(p) for p in pending_achievements], 
                           approved=[dict(a) for a in approved_achievements])

@app.route('/admin/students', methods=['GET', 'POST'])
def admin_students():
    if not g.user or g.user['role'] != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('req_action')
        student_id = request.form.get('student_id')
        
        if action == 'approve':
            conn.execute("UPDATE students SET is_approved = 1 WHERE id = ?", (student_id,))
            conn.commit()
            flash('Student approved successfully.', 'success')
        elif action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            year = request.form.get('year')
            roll = request.form.get('roll_number')
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            hashed_pw = generate_password_hash(password)
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, 'student'))
                user_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO students (user_id, name, roll_number, year, email, phone, is_approved) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (user_id, name, roll, year, email, phone, 1)
                )
                conn.commit()
                flash('Student added successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Username or Roll Number already exists', 'danger')
            except Exception as err:
                flash(f'Error adding student: {err}', 'danger')
        elif action == 'delete':
            try:
                stu_row = conn.execute("SELECT user_id FROM students WHERE id = ?", (student_id,)).fetchone()
                if stu_row:
                    u_id = stu_row['user_id']
                    # Clear completely all related records to avoid errors
                    conn.execute("DELETE FROM achievements WHERE student_id = ?", (student_id,))
                    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
                    conn.execute("DELETE FROM users WHERE id = ?", (u_id,))
                    conn.commit()
                    flash('Student permanently deleted.', 'success')
                else:
                    flash('Student not found.', 'danger')
            except Exception as str_err:
                flash(f'Error deleting student: {str_err}', 'danger')
        elif action == 'edit':
            student_id = request.form.get('student_id')
            name = request.form.get('name')
            year = request.form.get('year')
            roll = request.form.get('roll_number')
            email = request.form.get('email')
            phone = request.form.get('phone')
            conn.execute("UPDATE students SET name=?, year=?, roll_number=?, email=?, phone=? WHERE id=?", (name, year, roll, email, phone, student_id))
            conn.commit()
            flash('Student updated successfully.', 'success')
            
    students_list = conn.execute("SELECT * FROM students ORDER BY is_approved ASC, year ASC").fetchall()
    conn.close()
    return render_template('admin_students.html', students=[dict(s) for s in students_list])

@app.route('/admin/faculty', methods=['GET', 'POST'])
def admin_faculty():
    if not g.user or g.user['role'] != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('req_action')
        
        if action == 'add':
            username = request.form.get('username')
            password = request.form.get('password')
            name = request.form.get('name')
            dept = request.form.get('department')
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            hashed_pw = generate_password_hash(password)
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, 'faculty'))
                user_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO faculty (user_id, name, department, email, phone) VALUES (?, ?, ?, ?, ?)",
                    (user_id, name, dept, email, phone)
                )
                conn.commit()
                flash('Faculty added successfully!', 'success')
            except sqlite3.IntegrityError:
                flash('Username already exists', 'danger')
            except Exception as err:
                flash(f'Error adding faculty: {err}', 'danger')
                
        elif action == 'delete':
            fac_id = request.form.get('faculty_id')
            u_id = conn.execute("SELECT user_id FROM faculty WHERE id = ?", (fac_id,)).fetchone()['user_id']
            conn.execute("DELETE FROM faculty WHERE id = ?", (fac_id,))
            conn.execute("DELETE FROM users WHERE id = ?", (u_id,))
            conn.commit()
            flash('Faculty deleted successfully!', 'success')
        elif action == 'edit':
            fac_id = request.form.get('faculty_id')
            name = request.form.get('name')
            dept = request.form.get('department')
            phone = request.form.get('phone')
            email = request.form.get('email')
            conn.execute("UPDATE faculty SET name=?, department=?, phone=?, email=? WHERE id=?", (name, dept, phone, email, fac_id))
            conn.commit()
            flash('Faculty updated successfully.', 'success')
            
    faculty_list = conn.execute("SELECT * FROM faculty").fetchall()
    conn.close()
    return render_template('admin_faculty.html', faculty=[dict(f) for f in faculty_list])

@app.route('/admin/content', methods=['GET', 'POST'])
def admin_content():
    if not g.user or g.user['role'] != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('req_action')
        if action == 'update_home':
            # Check if exists
            exists = conn.execute("SELECT * FROM site_content WHERE page='home'").fetchone()
            if exists:
                conn.execute("UPDATE site_content SET title=?, description=? WHERE page='home'", (request.form.get('home_title'), request.form.get('home_desc')))
            else:
                conn.execute("INSERT INTO site_content (page, title, description) VALUES ('home', ?, ?)", (request.form.get('home_title'), request.form.get('home_desc')))
            conn.commit()
            flash('Homepage content updated.', 'success')
            
        elif action == 'update_general':
            def upsert(page, val):
                if conn.execute("SELECT * FROM site_content WHERE page=?", (page,)).fetchone():
                    conn.execute("UPDATE site_content SET description=? WHERE page=?", (val, page))
                else:
                    conn.execute("INSERT INTO site_content (page, title, description) VALUES (?, '', ?)", (page, val))
            
            site_name = request.form.get('site_name')
            if site_name:
                upsert('site_name', site_name)
                
            if 'site_icon' in request.files:
                file = request.files['site_icon']
                if file.filename != '':
                    new_filename = handle_upload(file)
                    if new_filename:
                        upsert('site_icon', new_filename)
                        
            conn.commit()
            flash('General website settings updated.', 'success')
            
        elif action == 'update_contact':
            def upsert(page, val):
                if conn.execute("SELECT * FROM site_content WHERE page=?", (page,)).fetchone():
                    conn.execute("UPDATE site_content SET description=? WHERE page=?", (val, page))
                else:
                    conn.execute("INSERT INTO site_content (page, title, description) VALUES (?, '', ?)", (page, val))
            
            upsert('contact_address', request.form.get('address'))
            upsert('contact_email', request.form.get('email'))
            upsert('contact_phone', request.form.get('phone'))
            conn.commit()
            flash('Contact info updated.', 'success')
            
        elif action == 'update_social':
            def upsert(page, val):
                if conn.execute("SELECT * FROM site_content WHERE page=?", (page,)).fetchone():
                    conn.execute("UPDATE site_content SET description=? WHERE page=?", (val, page))
                else:
                    conn.execute("INSERT INTO site_content (page, title, description) VALUES (?, '', ?)", (page, val))
            
            upsert('social_youtube', request.form.get('youtube'))
            upsert('social_instagram', request.form.get('instagram'))
            upsert('social_facebook', request.form.get('facebook'))
            upsert('social_twitter', request.form.get('twitter'))
            conn.commit()
            flash('Social media links updated across the site.', 'success')
            
        elif action == 'update_labs':
            def upsert(page, val):
                if conn.execute("SELECT * FROM site_content WHERE page=?", (page,)).fetchone():
                    conn.execute("UPDATE site_content SET description=? WHERE page=?", (val, page))
                else:
                    conn.execute("INSERT INTO site_content (page, title, description) VALUES (?, '', ?)", (page, val))
            
            labs_title = request.form.get('labs_title')
            names = request.form.getlist('lab_name[]')
            softwares = request.form.getlist('lab_software[]')
            
            details = []
            for n, s in zip(names, softwares):
                if n.strip() or s.strip():
                    details.append({"name": n.strip(), "software": s.strip()})
                    
            content = {"title": labs_title, "details": details}
            upsert('labs', json.dumps(content))
            conn.commit()
            flash('Labs page updated.', 'success')
            
        elif action == 'delete_news':
            conn.execute("DELETE FROM news WHERE id=?", (request.form.get('news_id'),))
            conn.commit()
            flash('News deleted.', 'success')
            
        elif action == 'delete_event':
            conn.execute("DELETE FROM events WHERE id=?", (request.form.get('event_id'),))
            conn.commit()
            flash('Event deleted.', 'success')
        elif action == 'add_news':
            title = request.form.get('title')
            content = request.form.get('content')
            conn.execute("INSERT INTO news (title, content, uploaded_by, faculty_id, date) VALUES (?, ?, ?, ?, ?)", (title, content, 'Admin', 0, str(datetime.now())))
            conn.commit()
            flash('News added.', 'success')
        elif action == 'edit_news':
            conn.execute("UPDATE news SET title=?, content=? WHERE id=?", (request.form.get('title'), request.form.get('content'), request.form.get('news_id')))
            conn.commit()
            flash('News updated.', 'success')
        elif action == 'add_event':
            title = request.form.get('title')
            desc = request.form.get('description')
            date_str = request.form.get('date')
            image_filename = handle_upload(request.files['image']) if 'image' in request.files and request.files['image'].filename != '' else None
            conn.execute("INSERT INTO events (title, description, date, uploaded_by, faculty_id, image_url) VALUES (?, ?, ?, ?, ?, ?)", (title, desc, date_str, 'Admin', 0, image_filename))
            conn.commit()
            flash('Event added.', 'success')
        elif action == 'edit_event':
            title = request.form.get('title')
            desc = request.form.get('description')
            date_str = request.form.get('date')
            if 'image' in request.files and request.files['image'].filename != '':
                image_filename = handle_upload(request.files['image'])
                conn.execute("UPDATE events SET title=?, description=?, date=?, image_url=? WHERE id=?", (title, desc, date_str, image_filename, request.form.get('event_id')))
            else:
                conn.execute("UPDATE events SET title=?, description=?, date=? WHERE id=?", (title, desc, date_str, request.form.get('event_id')))
            conn.commit()
            flash('Event updated.', 'success')
            
    news_list = conn.execute("SELECT * FROM news ORDER BY date DESC").fetchall()
    events_list = conn.execute("SELECT * FROM events ORDER BY date DESC").fetchall()
    
    # parse date strings to real dates for the template
    parsed_news = []
    for item in news_list:
        d = dict(item)
        d_typed: dict = {k: v for k, v in d.items()}
        try:
            d_typed['date'] = datetime.strptime(str(d_typed['date']), '%Y-%m-%d %H:%M:%S.%f')
        except:
            d_typed['date'] = datetime.now() # fallback
        d_typed['_id'] = d_typed['id']
        parsed_news.append(d_typed)

    parsed_events = []
    for item in events_list:
        d = dict(item)
        d['_id'] = d['id']
        parsed_events.append(d)

    c_addr = conn.execute("SELECT description FROM site_content WHERE page='contact_address'").fetchone()
    c_email = conn.execute("SELECT description FROM site_content WHERE page='contact_email'").fetchone()
    c_phone = conn.execute("SELECT description FROM site_content WHERE page='contact_phone'").fetchone()
    c_yt = conn.execute("SELECT description FROM site_content WHERE page='social_youtube'").fetchone()
    c_ig = conn.execute("SELECT description FROM site_content WHERE page='social_instagram'").fetchone()
    c_fb = conn.execute("SELECT description FROM site_content WHERE page='social_facebook'").fetchone()
    c_tw = conn.execute("SELECT description FROM site_content WHERE page='social_twitter'").fetchone()
    
    c_name = conn.execute("SELECT description FROM site_content WHERE page='site_name'").fetchone()
    c_icon = conn.execute("SELECT description FROM site_content WHERE page='site_icon'").fetchone()
    
    contact_data = {
        'address': c_addr['description'] if c_addr else "123 College Avenue\nDepartment of Computer Science\nTech City, TC 12345",
        'email': c_email['description'] if c_email else "info@dept.edu",
        'phone': c_phone['description'] if c_phone else "+1 (555) 123-4567",
        'youtube': c_yt['description'] if c_yt else "",
        'instagram': c_ig['description'] if c_ig else "",
        'facebook': c_fb['description'] if c_fb else "",
        'twitter': c_tw['description'] if c_tw else ""
    }
    
    general_data = {
        'site_name': c_name['description'] if c_name else "Department Portal",
        'site_icon': c_icon['description'] if c_icon else ""
    }
    
    c_home = conn.execute("SELECT title, description FROM site_content WHERE page='home'").fetchone()
    home_data = {
        'title': c_home['title'] if c_home else "",
        'description': c_home['description'] if c_home else ""
    }
    
    c_labs = conn.execute("SELECT description FROM site_content WHERE page='labs'").fetchone()
    if c_labs:
        try:
            labs_data = json.loads(c_labs['description'])
        except Exception:
            labs_data = {"title": "State of the Art Laboratories", "details": []}
    else:
        labs_data = {
            "title": "State of the Art Laboratories",
            "details": [{"name": "Computer Networks Lab", "software": "Cisco Packet Tracer, Wireshark"}, {"name": "Database Lab", "software": "MySQL, Oracle, MongoDB"}]
        }
    
    conn.close()
    return render_template('admin_content.html', news=parsed_news, events=parsed_events, contact_data=contact_data, general_data=general_data, home_data=home_data, labs_data=labs_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
