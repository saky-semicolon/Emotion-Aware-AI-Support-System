from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app.models.users import User, StudentProfile, Department
from app.models.detection import DetectionResults
from app.models.cases_management import Complaint, Notification
from app.extensions import db
from functools import wraps
from flask import render_template
from flask import Blueprint


# Add the following routes to your main_routes.py
import os
import openai
from flask import jsonify, request, render_template
from app.models.users import User
from app.utils.openai_helper import get_new_response

main = Blueprint('main', __name__, template_folder='../templates')

# =====================
# Home Page
# =====================
@main.route('/')
def home():
    return render_template('index.html')

# =====================
# Login Required Decorator
# =====================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for('main.login'))
            if role and session.get('user_role') != role:
                flash("Unauthorized access.", "danger")
                return redirect(url_for('main.login'))
            return f(*args, **kwargs)
        return wrapper
    return decorator

# =====================
# Login Route
# =====================

@main.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            session['user_role'] = user.role
            flash("Logged in successfully.", "success")

            if user.role == 'admin':
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('main.user_dashboard'))

        error = True  # Set error flag if credentials are invalid
    return render_template('login.html', error=error)

# Previous login route commented out for reference
# @main.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']

#         user = User.query.filter_by(email=email).first()
#         if user and check_password_hash(user.password_hash, password):
#             session['user_id'] = user.user_id
#             session['user_role'] = user.role
#             flash("Logged in successfully.", "success")

#             if user.role == 'admin':
#                 return redirect(url_for('main.admin_dashboard'))
#             return redirect(url_for('main.user_dashboard'))

#         flash("Invalid credentials", "danger")
#     return render_template('login.html')

# =====================
# Registration Route
# =====================
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['fullName']
        student_id = request.form['studentId']
        email = request.form['email']
        school = request.form['school']
        year = request.form['year']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        profile_picture = request.files.get('profilePicture')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('main.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))

        department = Department.query.filter_by(dept_name=school).first()
        if not department:
            department = Department(dept_name=school)
            db.session.add(department)
            db.session.commit()

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role='student'
        )
        db.session.add(user)
        db.session.flush()

        profile = StudentProfile(
            user_id=user.user_id,
            full_name=full_name,
            id_number=student_id,
            academic_year=year,
            dept_id=department.dept_id
        )
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('user/register.html')

# =====================
# Logout Route
# =====================
@main.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('main.login'))

# =====================
# Student Dashboard
# =====================
@main.route('/dashboard')
@login_required(role='student')
def user_dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    emos = DetectionResults.query.filter_by(user_id=user_id).all()

    # Count emotions (Remove Raw Counts once Model Is Integrated)
    # This is a placeholder for the actual emotion detection logic.
    # In a real application, you would replace this with the actual emotion detection logic.
    # Example raw counts (replace with actual detection logic)
    raw_counts = {"happy": 0.5, "surprise": 0.15, "sad": 0, "angry": 0, "fear": 0, "neutral": 0}
    for emo in emos:
        key = emo.primary_emo.lower()
        if key in raw_counts:
            raw_counts[key] += 1

    # Normalize to 0-1 scale
    total = sum(raw_counts.values()) or 1
    normalized = {k: round(v / total, 2) for k, v in raw_counts.items()}

    return render_template("user/dashboard.html",
                           user_name=user.profile.full_name,
                           emotions=normalized)

# =====================
# Student Profile
# =====================
# @main.route('/profile')
# @login_required(role='student')
# def profile():
#     user_id = session.get('user_id')
#     user = User.query.get(user_id)
#     return render_template("user/profile.html", user=user.profile)

@main.route('/profile')
@login_required(role='student')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Session expired. Please log in again.", "warning")
        return redirect(url_for('main.login'))

    user = User.query.get(user_id)
    if not user or user.role != 'student':
        flash("Unauthorized access.", "danger")
        return redirect(url_for('main.login'))

    student_profile = user.profile
    return render_template('user/profile.html', profile=student_profile)


    # Convert binary image to base64 string
    profile_image_data = base64.b64encode(profile.profile_image).decode('utf-8') if profile.profile_image else None
    return render_template("user/profile.html", profile=profile, profile_image_data=profile_image_data)


# =====================
# Chatbot Page
# =====================
# @main.route('/chatbot')
# @login_required(role='student')
# def chatbot():
#     return render_template("user/chatbot.html")



# =====================
# Chatbot Page Route
# =====================
@main.route('/chatbot')
@login_required(role='student')
def chatbot():
    return render_template("user/chatbot.html")

# =====================
# Set up OpenAI API Key securely
# =====================
openai.api_key = os.getenv("OPENAI_API_KEY")  # Store your key in .env

# =====================
# Chatbot Text Message Route (OpenAI)
# =====================
@main.route('/chatbot/text', methods=['POST'])
@login_required(role='student')
def chatbot_text():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        reply = get_new_response(user_message)  # Call the new function here
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# =====================
# Complaint Status
# =====================
@main.route('/complaintstatus')
@login_required(role='student')
def complaint_status():
    user_id = session.get('user_id')
    complaints = Complaint.query.filter_by(user_id=user_id).all()

    # Transform objects to dictionaries for JSON compatibility
    complaint_list = [{
        "id": c.complaint_id,
        "title": c.title,
        "date": c.created_at.strftime("%Y-%m-%d"),
        "status": c.complaint_status.lower()  # e.g., "open", "in progress", "resolved"
    } for c in complaints]

    return render_template("user/complaintstatus.html", complaints=complaint_list)


# =====================
# Alerts
# =====================
@main.route('/alerts')
@login_required(role='student')
def alerts():
    user_id = session.get('user_id')
    alerts = Alert.query.filter_by(user_id=user_id).all()

    alert_data = [{
        "id": a.id,
        "title": a.title,
        "message": a.message,
        "priority": a.priority,  # "high", "medium", "low"
        "time": a.timestamp.strftime("%Y-%m-%d %H:%M"),
        "read": a.read
    } for a in alerts]

    return render_template('user/alerts.html', alerts=alert_data)

# =====================
# Admin Login Page
# =====================
@main.route('/admin')
def admin_login():
    return render_template("admin/login_admin.html")

# =====================
# Admin Dashboard
# =====================
@main.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    total = Complaint.query.count()
    pending = Complaint.query.filter_by(complaint_status='open').count()
    resolved = Complaint.query.filter_by(complaint_status='resolved').count()

    emotions = db.session.query(DetectionResults.primary_emo, db.func.count(DetectionResults.primary_emo))\
        .group_by(DetectionResults.primary_emo).all()
    total_detected = sum(count for _, count in emotions)
    emotion_data = [
        {"name": emo, "count": count, "percentage": round(count / total_detected * 100, 2)}
        for emo, count in emotions
    ]

    return render_template("admin/dashboard_admin.html", total_complaints=total,
                           pending_complaints=pending, resolved_complaints=resolved,
                           emotions=emotion_data)

# =====================
# Admin Complaints Page
# =====================
@main.route('/admin/complaints')
@login_required(role='admin')
def admin_complaints():
    complaints = Complaint.query.all()
    return render_template("admin/complaint.html", complaints=complaints)

# =====================
# Admin Alerts Page
# =====================
@main.route('/admin/alerts')
@login_required(role='admin')
def admin_alerts():
    notifications = Notification.query.order_by(Notification.sent_at.desc()).all()
    return render_template("admin/alert_admin.html", notifications=notifications)
