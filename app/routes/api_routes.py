from flask import jsonify, request, session
from app.models.cases_management import Complaint, CaseReport
from app.extensions import db
from functools import wraps
from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

# =====================
# Auth Decorator: login_required
# =====================
def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({"error": "Unauthorized. Please log in."}), 401
            if role and session.get('user_role') != role:
                return jsonify({"error": "Forbidden. Admin access required."}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator
