# class Alert(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
#     title = db.Column(db.String(255))
#     message = db.Column(db.Text)
#     priority = db.Column(db.String(10))  # 'low', 'medium', 'high'
#     read = db.Column(db.Boolean, default=False)
#     timestamp = db.Column(db.DateTime, default=datetime.utcnow)
