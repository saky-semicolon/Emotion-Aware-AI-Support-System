from datetime import datetime
from werkzeug.security import generate_password_hash
import json
from app import create_app
from app.extensions import db
from app.models.users import Department, User, StudentProfile, AuthSession # adjust import path if needed
from app.models.preprocessing import AudioRec, PreprocessingResults, FeatureVectors
from app.models.feedback import UserFeedback, ChatResponse  
from app.models.detection import MLModel, DetectionResults
from app.models.cases_management import Complaint, CaseReport, CaseHistory, PriorityAlert, Notification


# Sample data entries for all tables in your schema

def seed_all_data(db, Department, User, StudentProfile, AuthSession, AudioRec, PreprocessingResults,
                  FeatureVectors, MLModel, DetectionResults, Complaint, UserFeedback, ChatResponse,
                  CaseReport, CaseHistory, PriorityAlert, Notification):
    # Clear all tables first (only for test purposes)
    db.drop_all()
    db.create_all()

    # Departments
    cs = Department(dept_name="Computer Science")
    bss = Department(dept_name="Business and Social Studies")
    ehr = Department(dept_name="Education and Human Resources")
    db.session.add_all([cs, bss,ehr])
    db.session.commit()

    # Users
    user1 = User(email="alice@example.com", password_hash=generate_password_hash("password123"), role="student")
    user2 = User(email="bob@example.com", password_hash=generate_password_hash("securepass"), role="student")
    db.session.add_all([user1, user2])
    db.session.commit()

    # Student Profiles
    profile1 = StudentProfile(user_id=user1.user_id, full_name="Alice Smith", gender="Female",
                              academic_year="Year 2", dept_id=cs.dept_id, phone="1234567890")
    profile2 = StudentProfile(user_id=user2.user_id, full_name="Bob Johnson", gender="Male",
                              academic_year="Year 3", dept_id=bss.dept_id, phone="0987654321")
    db.session.add_all([profile1, profile2])
    db.session.commit()

    # Auth Sessions
    session1 = AuthSession(user_id=user1.user_id, token_hash="token123", ip_add="192.168.1.1", user_agent="Chrome")
    db.session.add(session1)
    db.session.commit()

    # Audio Recordings
    rec1 = AudioRec(user_id=user1.user_id, processing_status="completed", transcription_status="completed")
    db.session.add(rec1)
    db.session.commit()

    # Preprocessing Results
    prepro1 = PreprocessingResults(rec_id=rec1.rec_id, noise_red=True, sampling_rate=44100, features_extracted=True, prepro_time=2.5)
    db.session.add(prepro1)

    # Feature Vectors
    features1 = FeatureVectors(rec_id=rec1.rec_id, mfcc=json.dumps([1.2, 0.9, 1.5]), rmse=0.23, zcr=0.05)
    db.session.add(features1)

    # ML Models
    model1 = MLModel(model_name="EmotionNet", model_type="LSTM", version="1.0", accuracy=0.89)
    db.session.add(model1)
    db.session.commit()

    # Detection Results
    detect1 = DetectionResults(rec_id=rec1.rec_id, user_id=user1.user_id, primary_emo="sad",
                                detected_emos=json.dumps(["sad", "neutral"]), severity_level="high", model_id=model1.model_id)
    db.session.add(detect1)
    db.session.commit()

    # Complaints
    complaint1 = Complaint(detect_id=detect1.detect_id, user_id=user1.user_id, priority_level="high", complaint_status="open")
    db.session.add(complaint1)
    db.session.commit()

    # Feedback
    feedback1 = UserFeedback(rec_id=rec1.rec_id, user_id=user1.user_id, complaint_id=complaint1.complaint_id,
                             rating=4, comments="Need more support")
    db.session.add(feedback1)

    # Chat Response
    chat1 = ChatResponse(rec_id=rec1.rec_id, user_id=user1.user_id, resp_type="info", resp_text="We received your complaint.", follow_up_req=False)
    db.session.add(chat1)

    # Case Report
    report1 = CaseReport(complaint_id=complaint1.complaint_id, content="Initial investigation", recommendations="Schedule counseling")
    db.session.add(report1)

    # Case History
    history1 = CaseHistory(complaint_id=complaint1.complaint_id, changed_by=user2.user_id, field_changed="status", old_value="open", new_value="in_progress")
    db.session.add(history1)

    # Priority Alert
    alert1 = PriorityAlert(detect_id=detect1.detect_id, alert_status="active")
    db.session.add(alert1)

    # Notification
    notif1 = Notification(user_id=user1.user_id, complaint_id=complaint1.complaint_id, message="Your case has been updated")
    db.session.add(notif1)

    db.session.commit()

    return "All sample data inserted successfully."

app = create_app()
with app.app_context():
    seed_all_data(db, Department, User, StudentProfile, AuthSession, AudioRec, PreprocessingResults,
                  FeatureVectors, MLModel, DetectionResults, Complaint, UserFeedback, ChatResponse,
                  CaseReport, CaseHistory, PriorityAlert, Notification)
    print("✅ Data inserted successfully!")