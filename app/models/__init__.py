from .users import User, StudentProfile, AuthSession, Department 
from .preprocessing import AudioRec, PreprocessingResults, FeatureVectors
from .feedback import UserFeedback, ChatResponse
from .detection import MLModel, DetectionResults
from .cases_management import Complaint, CaseReport, CaseHistory, PriorityAlert, Notification
from  app.extensions import db
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()