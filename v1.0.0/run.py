from flask import render_template
from app import create_app, db
from app.models.users import User
from werkzeug.security import generate_password_hash
from datetime import datetime

# Create the Flask app by calling the factory function
app = create_app()

def create_admin():
    admin_email = 'admin@gmail.com'
    admin_password = 'Fyp//&em7861'

    existing_admin = User.query.filter_by(email=admin_email, role='admin').first()
    if not existing_admin:
        admin = User(
            email=admin_email,
            password_hash=generate_password_hash(admin_password),
            role='admin',
            reg_date=datetime.utcnow(),
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created.')
    else:
        print('ℹ️ Admin user already exists.')

if __name__ == '__main__':
    with app.app_context():  # Make sure to use the app's context
        db.create_all()  # Create tables
        create_admin()  # Create the admin account if not exists
    app.run(debug=True)  # Run the app
