from flask import render_template, request, redirect, url_for, flash, session, Blueprint, jsonify , current_app ,send_file, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
from app.models.detection import DetectionResults 
from app.models.preprocessing import AudioRec
from datetime import datetime, timedelta
from sqlalchemy import func
from app.extensions import db
from flask_login import login_required
import os
from app.models.cases_management import  CaseHistory, Notification, PriorityAlert , Complaint, CaseReport
from app.ml_model.preprocess import generate_report
import logging  # <-- Added for error logging
from app.models.users import User, StudentProfile, Department
from flask import send_file, abort
from sqlalchemy.orm import joinedload
from app.ml_model.preprocess import generate_report  # update with your actual path
import glob
import re






# Initialize logging
logging.basicConfig(level=logging.INFO)


main = Blueprint('main', __name__)

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
# student complaint status
# =====================

@main.route('/complaintstatus')
@login_required(role='student')
def complaint_status():
    user_id = session.get('user_id')
    complaints = Complaint.query.filter_by(user_id=user_id).filter(Complaint.complaint_status != 'withdrawn').all()
    
    complaint_list = [{
        "id": c.complaint_id,
        "date": c.submit_date.strftime("%Y-%m-%d") if c.submit_date else "N/A",
        "status": c.complaint_status.lower(),
        "actions": c.actions or ""
    } for c in complaints]

    return render_template("user/complaintstatus.html", complaints=complaint_list)



# =====================
# Admin Login Page
# =====================
@main.route('/admin')
def admin_login():
    return render_template("admin/login_admin.html")



# =====================
# Login Route
# =====================
@main.route('/login', methods=['GET', 'POST'])
def login():
    error_message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id
            session['user_role'] = user.role
            flash("Logged in successfully.", "success")
            return redirect(url_for('main.admin_dashboard' if user.role == 'admin' else 'main.user_dashboard'))
        error_message = "Invalid email or password"
    return render_template('login.html', error_message=error_message)


# =====================
# registration Route
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
        gender = request.form['gender']
        phone = request.form.get('phone')

        # Check: Passwords must match
        if password != confirm_password:
            error_message = 'Passwords do not match.'
            return render_template('user/register.html', error_message=error_message)

        # Check: Email already registered
        if User.query.filter_by(email=email).first():
            error_message = 'This email is already registered.'
            return render_template('user/register.html', error_message=error_message)

        # Check: Student ID already used
        if StudentProfile.query.filter_by(id_number=student_id).first():
            error_message = 'This student ID is already used. Please use a different one.'
            return render_template('user/register.html', error_message=error_message)

        # Ensure department exists
        department = Department.query.filter_by(dept_name=school).first()
        if not department:
            department = Department(dept_name=school)
            db.session.add(department)
            db.session.commit()

        # Create User entry
        user = User(email=email, password_hash=generate_password_hash(password), role='student')
        db.session.add(user)
        db.session.flush()  # Get user_id without committing

        # Create Student Profile
        profile = StudentProfile(
            user_id=user.user_id,
            full_name=full_name,
            id_number=student_id,
            academic_year=year,
            dept_id=department.dept_id,
            gender=gender,
            phone=phone
        )
        db.session.add(profile)
        db.session.commit()

        flash('✅ Registration successful. You can now log in.', 'success')
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
# user Dashboard
# =====================
@main.route('/dashboard', endpoint='user_dashboard')
@login_required(role='student')
def user_dashboard():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    user_name = user.profile.full_name if user else "Unknown"

    # Filter detection results by user_id and exclude withdrawn complaints
    emotion_counts = db.session.query(
        DetectionResults.primary_emo,
        db.func.count(DetectionResults.primary_emo)
    ).join(Complaint, DetectionResults.detect_id == Complaint.detect_id) \
     .filter(
        DetectionResults.user_id == user_id,
        Complaint.complaint_status != 'withdrawn'
     ).group_by(DetectionResults.primary_emo).all()

    emotions = {
        'happy': 0,
        'sad': 0,
        'angry': 0,
        'fear': 0,
        'neutral': 0
    }

    total = sum(c for _, c in emotion_counts)
    for emo, count in emotion_counts:
        if emo in emotions and total > 0:
            emotions[emo] = count / total

    return render_template('user/dashboard.html', emotions=emotions, user_name=user_name)





# =====================
# Student Profile
# =====================
@main.route('/profile', methods=['GET', 'POST'])
@login_required(role='student')
def profile():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)

    profile = user.profile

    if request.method == 'POST':
        profile.full_name = request.form['full_name']
        profile.id_number = request.form['id_number']
        profile.academic_year = request.form['academic_year']
        school = request.form.get('school')
        profile.phone = request.form.get('phone')  
        profile.gender = request.form.get('gender') 

        department = Department.query.filter_by(dept_name=school).first()
        if not department:
            department = Department(dept_name=school)
            db.session.add(department)
            db.session.commit()
        profile.dept_id = department.dept_id

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('main.profile'))

    return render_template('user/profile.html', profile=profile)


# =====================
# Chatbot Page
# =====================
@main.route('/chatbot')
@login_required(role='student')
def chatbot():
    return render_template("user/chatbot.html")


# =====================
# Chatbot Message Handler (Updated)
# =====================
@main.route('/chatbot/message', methods=['POST'])
@login_required(role='student')
def chatbot_message():
    if not request.is_json:
        return jsonify({"error": "Invalid content type"}), 400

    data = request.get_json()
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # Common triggers
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'salam', 'hai' , 'good evening', 'assalamualaikum']
    submissions = ['i submitted', 'i recorded', 'i sent', 'i just recorded', 'i just submitted', 'done recording']
    status_inquiry = ['status', 'check my complaint', 'update', 'progress', 'complaint update', 'case status', 'resolved']
    help_requests = ['help', 'how', 'what to do', 'guide', 'instructions', 'steps', 'can you help', 'support', 'how to submit', 'how to record','step by step']
    gratitude = ['thank you', 'thanks', 'appreciate', 'grateful', 'thank u', 'many thanks']
    frustration = ['no reply', 'why late', 'waiting', 'ignored', 'not solved', 'not responded', 'no response', 'no action', 'too long', 'still waiting', 'no update', 'no action taken', 'no response yet']

    def matches_any(phrases):
        return any(phrase in user_message for phrase in phrases)

    # Rule-based responses
    if matches_any(greetings):
        reply = (
            "👋 **Hi there!** I'm here to support your emotional wellbeing and help you raise voice complaints to Student Affairs (SA).\n\n"
            "**Quick guide to start:**\n"
            "🎤 Tap the **microphone** to record your message (max 3 minutes).\n"
            "📤 It'll be automatically submitted once you stop recording.\n\n"
            "Need help? Just type *'how'* or *'guide'*."
        )

    elif matches_any(submissions):
        reply = (
            "✅ **Awesome! Your voice recording has been received.**\n\n"
            "📌 Our Student Affairs (SA) team will review it shortly.\n"
            "🕒 You can track the progress under the **Complaint Status** tab.\n\n"
            "Thanks for trusting us with your concern 💙"
        )

    elif matches_any(status_inquiry):
        reply = (
            "📍 **To check your complaint status:**\n"
            "1. Go to the **Complaint Status** tab on the sidebar.\n"
            "2. Find your complaint ID to see updates like *In Progress*, *Resolved*, or *Closed*.\n\n"
            "Let me know if you can't find it, I'm here to guide you!"
        )

    elif matches_any(help_requests):
        reply = (
            "🧭 **Need help? Here's how to submit a voice complaint:**\n\n"
            "🔴 Tap the **mic** button.\n"
            "🎙️ Record your voice clearly (max 3 minutes).\n"
            "📤 When you stop, it’s auto-submitted to SA.\n\n"
            "💬 You can also type here if you’d rather chat instead of speak."
        )

    elif matches_any(gratitude):
        reply = (
            "🤗 **You're most welcome!**\n\n"
            "I'm always here if you need help, want to talk, or have something to share.\n"
            "Wishing you peace and support ahead 💙"
        )

    elif matches_any(frustration):
        reply = (
            "😟 I'm really sorry you're feeling that way.\n\n"
            "Please know that your concern matters. The SA team reviews each complaint carefully.\n"
            "⏳ Sometimes there may be a short delay, but rest assured it is being looked into.\n"
            "You can check updates under the **Complaint Status** tab.\n\n"
            "If it’s urgent, please reach out to SA directly at +6011111111 .\n"
        )

    else:
        reply = (
            "🤖 I'm here to support you with submitting complaints and emotional wellbeing.\n\n"
            "Try saying:\n"
            "- *Hi* or *Hello*\n"
            "- *I submitted my voice complaint*\n"
            "- *How do I check my case status?*\n"
            "- *Help me record a message*\n\n"
            "Or just type what's on your mind — I'm listening."
        )

    return jsonify({"reply": reply})





# =====================
# admin dashboard
# =====================
@main.route('/admin/dashboard')
@login_required(role='admin')
def admin_dashboard():
    # Total complaints (excluding withdrawn and closed)
    total_complaints = db.session.query(func.count(Complaint.complaint_id))\
        .filter(Complaint.complaint_status.notin_(['withdrawn', 'closed'])).scalar()

    # Pending complaints (open or in_progress)
    pending_complaints = db.session.query(func.count(Complaint.complaint_id))\
        .filter(Complaint.complaint_status.in_(['open', 'in_progress'])).scalar()

    # Resolved complaints
    resolved_complaints = db.session.query(func.count(Complaint.complaint_id))\
        .filter(Complaint.complaint_status == 'resolved').scalar()

    # Emotion Distribution (exclude withdrawn complaints)
    emotion_counts = db.session.query(
        DetectionResults.primary_emo,
        func.count(DetectionResults.primary_emo)
    ).join(Complaint, Complaint.detect_id == DetectionResults.detect_id)\
     .filter(Complaint.complaint_status != 'withdrawn')\
     .group_by(DetectionResults.primary_emo).all()

    total_detects = sum([count for _, count in emotion_counts])

    emotions = [{
        'name': emo,
        'count': count,
        'percentage': round((count / total_detects) * 100, 2) if total_detects else 0
    } for emo, count in emotion_counts]

    return render_template('admin/dashboard_admin.html',
                           total_complaints=total_complaints,
                           pending_complaints=pending_complaints,
                           resolved_complaints=resolved_complaints,
                           emotions=emotions)


# =====================
# Admin Complaints
# =====================
@main.route('/admin/complaints')
@login_required(role='admin')
def admin_complaints():
    # Fetch only complaints that are NOT withdrawn
    complaints = db.session.query(Complaint).join(
        DetectionResults, Complaint.detect_id == DetectionResults.detect_id
    ).join(
        User, Complaint.user_id == User.user_id
    ).join(
        StudentProfile, StudentProfile.user_id == User.user_id
    ).filter(
        Complaint.complaint_status != 'withdrawn'
    ).add_columns(
        DetectionResults.primary_emo.label('emotion'),
        StudentProfile.full_name.label('user')
    ).all()

    # Build structured list with relevant fields
    complaint_list = []
    for c, emotion, user in complaints:
        complaint_list.append({
            "complaint_id": c.complaint_id,
            "complaint_status": c.complaint_status,
            "priority_level": c.priority_level,
            "submit_date": c.submit_date,
            "emotion": emotion,
            "user": user
        })

    # Sort: closed complaints last, then by submit_date descending
    sorted_complaints = sorted(
        complaint_list,
        key=lambda c: (c["complaint_status"] == "closed", -c["submit_date"].timestamp())
    )

    return render_template('admin/complaint.html', complaints=sorted_complaints)

# =====================
# Admin Alerts
# =====================
@main.route('/admin/alerts')
@login_required(role='admin')
def admin_alerts():
    # Define time threshold for 'read' alerts: 24 hours ago
    time_threshold = datetime.utcnow() - timedelta(hours=24)

    # Eager load detection and complaint, filter out old read alerts
    alerts = PriorityAlert.query.options(
        joinedload(PriorityAlert.detection).joinedload(DetectionResults.complaint)
    ).filter(
        ((PriorityAlert.alert_status == 'active') |
         ((PriorityAlert.alert_status == 'read') & (PriorityAlert.alert_timestamp >= time_threshold)))
    ).order_by(
        PriorityAlert.alert_status.desc(),  # 'read' after 'active'
        PriorityAlert.alert_timestamp.desc()
    ).all()

    # Prepare alert data, excluding withdrawn complaints
    alert_data = []
    for alert in alerts:
        detection = alert.detection
        complaint = detection.complaint if detection else None

        # Skip if complaint is withdrawn
        if complaint and complaint.complaint_status == 'withdrawn':
            continue

        alert_data.append({
            "alert": alert,
            "detection": detection,
            "complaint": complaint,
        })

    # Optional: sort to prioritize active alerts
    alert_data = sorted(alert_data, key=lambda x: x["alert"].alert_status != 'active')

    return render_template('admin/alert_admin.html', alert_data=alert_data)


# ===========================
# Admin update Alert status
# ===========================

@main.route('/update_alert_status/<int:alert_id>', methods=['POST'])
def update_alert_status(alert_id):
    alert = PriorityAlert.query.get_or_404(alert_id)

    # Only allow update if current status is 'active'
    if alert.alert_status != 'active':
        return jsonify({"success": False, "message": "Alert is already marked as read."}), 400

    new_status = request.json.get('status')

    if new_status == 'read':
        alert.alert_status = 'read'
        db.session.commit()
        return jsonify({"success": True, "message": "Alert status updated."})
    else:
        return jsonify({"success": False, "message": "Invalid status."}), 400



# ===========================
# admin send reply to student 
# ===========================
@main.route('/send_reply/<int:complaint_id>', methods=['POST'])
@login_required(role='admin')
def send_reply(complaint_id):
    data = request.get_json()
    reply_text = data.get('reply', '').strip()
    if not reply_text:
        return jsonify({'error': 'Reply text cannot be empty'}), 400

    complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    complaint.actions = reply_text
    db.session.commit()

    return jsonify({'message': 'Reply saved'})

# =============================
# admin update complaint status
# =============================

@main.route('/admin/update_status/<int:complaint_id>', methods=['POST'])
@login_required(role='admin')
def update_complaint_status(complaint_id):
    try:
        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'Missing status'}), 400

        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            return jsonify({'error': 'Complaint not found'}), 404

        # 🚫 Prevent update if status is already closed
        if complaint.complaint_status == 'closed':
            return jsonify({'error': 'Cannot update status of a closed complaint'}), 403

        old_status = complaint.complaint_status
        complaint.complaint_status = new_status
        complaint.resolved_at = datetime.utcnow() if new_status == 'resolved' else None

        user_id = session.get('user_id')

        history_entry = CaseHistory(
            complaint_id=complaint.complaint_id,
            changed_by=user_id,
            field_changed='complaint_status',
            old_value=old_status,
            new_value=new_status,
            change_timestamp=datetime.utcnow(),
            notes=data.get('notes', '')
        )
        db.session.add(history_entry)

        notification = Notification(
            user_id=complaint.user_id,
            complaint_id=complaint.complaint_id,
            message=f"Your complaint status has been updated to '{new_status}'.",
            sent_at=datetime.utcnow()
        )
        db.session.add(notification)

        db.session.commit()
        return jsonify({'message': 'Status updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating complaint status: {e}")
        return jsonify({'error': str(e)}), 500


# ==========================
# student withdraw complaint
# ==========================


@main.route('/withdraw_complaint/<int:complaint_id>', methods=['DELETE'])
@login_required(role='student')
def withdraw_complaint(complaint_id):
    try:
        # Get the logged-in student's ID
        user_id = session.get('user_id')

        # Find the complaint
        complaint = Complaint.query.filter_by(
            complaint_id=complaint_id,
            user_id=user_id
        ).first()

        if not complaint:
            return jsonify({'error': 'Complaint not found'}), 404

        # Prevent withdrawal if already resolved or withdrawn
        if complaint.complaint_status.lower() in ['resolved', 'withdrawn']:
            return jsonify({'error': 'Cannot withdraw a resolved or already withdrawn complaint'}), 400

        # Save the old status
        old_status = complaint.complaint_status

        # Soft delete: mark complaint as withdrawn
        complaint.complaint_status = 'withdrawn'

        # Log the change in case history
        history = CaseHistory(
            complaint_id=complaint.complaint_id,
            changed_by=user_id,
            field_changed='complaint_status',
            old_value=old_status,
            new_value='withdrawn',
            change_timestamp=datetime.now(),
            notes='Student withdrew the complaint.'
        )
        db.session.add(history)

        # Commit both updates
        db.session.commit()

        return jsonify({'message': 'Complaint withdrawn successfully'}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error withdrawing complaint: {e}")
        return jsonify({'error': 'An error occurred while withdrawing the complaint.'}), 500
    




# ==========================
# Download Report
# ==========================
@main.route('/admin/report/<int:complaint_id>')
def download_report(complaint_id):
    try:
        # Fetch complaint and related data
        complaint = Complaint.query.get(complaint_id)
        if not complaint:
            abort(404, description="Complaint not found")

        detection = DetectionResults.query.get(complaint.detect_id)
        student = StudentProfile.query.filter_by(user_id=complaint.user_id).first()
        if not student:
            abort(404, description="Student not found")

        # Report directory
        report_dir = os.path.join(os.getcwd(), "reports")
        os.makedirs(report_dir, exist_ok=True)

        # If report already exists in DB, return it
        existing_report = CaseReport.query.filter_by(complaint_id=complaint_id).first()
        if existing_report and existing_report.pdf_generated:
            for filename in os.listdir(report_dir):
                if filename.startswith(f"report_{complaint_id}_{complaint.user_id}_") and filename.endswith(".pdf"):
                    report_path = os.path.join(report_dir, filename)
                    # ✅ Allow viewing or downloading based on query param
                    as_attachment = request.args.get('download', 'true') == 'true'
                    return send_file(report_path, as_attachment=as_attachment, mimetype='application/pdf')

        # Find closest matching audio file
        upload_dir = os.path.join(os.getcwd(), "uploads")
        pattern = re.compile(rf"user_{complaint.user_id}_(\d{{8}}_\d{{6}})\.wav")
        best_match = None
        min_diff = float('inf')

        for fname in os.listdir(upload_dir):
            match = pattern.match(fname)
            if match:
                file_time = datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
                diff = abs((file_time - complaint.submit_date).total_seconds())
                if diff < min_diff:
                    min_diff = diff
                    best_match = fname

        if not best_match:
            abort(404, description="Matching audio file not found")

        audio_path = os.path.join(upload_dir, best_match)

        # Create a new filename with timestamp
        timestamp_str = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        report_filename = f"report_{complaint_id}_{complaint.user_id}_{timestamp_str}.pdf"
        report_path = os.path.join(report_dir, report_filename)

        # Generate the PDF report
        generate_report(audio_path, student, detection, complaint, report_path)

        # Save report info to database
        new_report = CaseReport(
            complaint_id=complaint_id,
            content=None,
            recommendations=None,
            generated_at=datetime.utcnow(),
            pdf_generated=True
        )
        db.session.add(new_report)
        db.session.commit()

        # ✅ Serve the generated file (download or view)
        as_attachment = request.args.get('download', 'true') == 'true'
        return send_file(report_path, as_attachment=as_attachment, mimetype='application/pdf')

    except Exception as e:
        current_app.logger.error(f"Report generation error: {e}", exc_info=True)
        abort(500, description="Failed to generate report")
