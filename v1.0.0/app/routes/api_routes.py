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

# =====================
# Route: Update Complaint Status
# ===================== 
@api.route('/api/update_status', methods=['POST'])
@login_required(role='admin')
def update_status():
    data = request.get_json()
    
    if not data or not all(k in data for k in ('id', 'status')):
        return jsonify({"error": "Missing 'id' or 'status' in request body."}), 400

    complaint = Complaint.query.get(data['id'])
    if not complaint:
        return jsonify({"error": "Complaint not found."}), 404

    complaint.complaint_status = data['status']
    db.session.commit()
    return jsonify({"message": "Complaint status updated successfully."}), 200

# =====================
# Route: Get Complaint Report
# =====================
@api.route('/api/complaint_report/<int:complaint_id>')
@login_required(role='admin')
def get_report(complaint_id):
    report = CaseReport.query.filter_by(complaint_id=complaint_id).first()
    if not report:
        return jsonify({"error": "Report not found."}), 404

    return jsonify({
        "content": report.content,
        "recommendations": report.recommendations,
        "generated_at": report.generated_at.strftime("%Y-%m-%d %H:%M")
    }), 200
