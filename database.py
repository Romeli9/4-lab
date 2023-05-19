from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Students(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Student {self.full_name}>'

def initialize_database(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
