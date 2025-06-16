from app.extensions import db
from datetime import datetime
from sqlalchemy import Enum


class Department(db.Model):
    __tablename__ = 'department'
    dept_id = db.Column(db.Integer, primary_key=True)
    dept_name = db.Column(db.String(100), nullable=False)
    students = db.relationship('StudentProfile', backref='department', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False , index=True)
    role = db.Column(db.String(50), nullable=False)  # student/admin
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, index=True)
    is_active = db.Column(db.Boolean, default=True)
    # Relationships
    recordings = db.relationship('AudioRec', backref='user')
    sessions = db.relationship('AuthSession', backref='user')
    profile = db.relationship('StudentProfile', backref='user', uselist=False)

class StudentProfile(db.Model):
    __tablename__ = 'student_profile'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'dept_id', name='uq_user_department'),
    )
    profile_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    id_number = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(Enum('Male', 'Female', 'Other', name='gender_enum'), nullable=True)
    academic_year = db.Column(db.String(50))
    dept_id = db.Column(db.Integer, db.ForeignKey('department.dept_id'), nullable=False)
    phone = db.Column(db.String(20))
    


class AuthSession(db.Model):
    __tablename__ = 'auth_sessions'
    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    token_hash = db.Column(db.String(256), nullable=False)
    ip_add = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expired_at = db.Column(db.DateTime)
    is_revoked = db.Column(db.Boolean, default=False)
    user_agent = db.Column(db.String(255))

    