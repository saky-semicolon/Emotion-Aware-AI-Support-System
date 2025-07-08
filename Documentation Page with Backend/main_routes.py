from flask import Blueprint, render_template, request, redirect, url_for
from app.models.feedback import Feedback
from app.extensions import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    feedbacks = Feedback.query.order_by(Feedback.timestamp.desc()).all()
    return render_template('index.html', feedbacks=feedbacks)

@main.route('/feedback', methods=['POST'])
def feedback():
    name = request.form.get('name')
    comment = request.form.get('comment')
    new_feedback = Feedback(name=name, comment=comment)
    db.session.add(new_feedback)
    db.session.commit()
    return redirect(url_for('main.index'))
