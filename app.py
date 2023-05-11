from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, abort
from flask_restx import Api, Resource, fields
from database import db
import os

app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(120), nullable=False)
    semester_number = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.Integer, nullable=False)
    start_year = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_all_sorted(attribute):
        if attribute == 'name':
            return Student.query.order_by(Student.full_name).all()
        elif attribute == 'age':
            return Student.query.order_by(Student.age).all()
        elif attribute == 'gpa':
            return Student.query.order_by(Student.grade.desc()).all()
        elif attribute == 'subject':
            return Student.query.order_by(Student.subject).all()
        elif attribute == 'semester_number':
            return Student.query.order_by(Student.semester_number).all()
        elif attribute == 'start_year':
            return Student.query.order_by(Student.start_year).all()
        else:
            return Student.query.all()

    def __repr__(self):
        return f'<Student {self.id}>'





@app.route('/students',methods=['GET'])
def get_all_students():
    students = Student.query.all()
    return render_template('all_students.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        subject = request.form['subject']
        semester = request.form['semester']
        grade = request.form['grade']
        year = request.form['year']
        age = request.form['age']
        new_student = Student(full_name=name, subject=subject, semester_number=semester, grade=grade, start_year=year, age=age)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully')
        return redirect(url_for('get_all_students'))
    return render_template('add_student.html')

@app.route('/students/stats')
def get_student_stats():
    grades = [s.grade for s in Student.query.all()]
    average_grade = sum(grades) / len(grades)
    max_grade = max(grades)
    min_grade = min(grades)
    oldest_student = Student.query.order_by(Student.age.desc()).first()
    youngest_student = Student.query.order_by(Student.age.asc()).first()
    return render_template('stats.html', average_grade=average_grade, max_grade=max_grade, min_grade=min_grade, oldest_student=oldest_student, youngest_student=youngest_student)

@app.route('/sort', methods=['GET', 'POST'])
def sort_students():
    if request.method == 'POST':
        attribute = request.form.get('attribute')
        students = Student.get_all_sorted(attribute)
        return render_template('all_students.html', students=students)
    else:
        students = Student.query.all()
        return render_template('sort_students.html', students=students)

@app.route('/update_student', methods=['GET', 'POST'])
def update_student():
    if request.method == 'POST':
        old_full_name = request.form['old_full_name']
        new_full_name = request.form['new_full_name']
        student = Student.query.filter_by(full_name=old_full_name).first()
        if not student:
            flash(f'Student {old_full_name} not found')
            return redirect(url_for('update_student'))
        student.full_name = new_full_name
        student.age = request.form['age']
        student.grade = request.form['grade']
        db.session.commit()
        flash(f'Student {old_full_name} updated successfully')
        return redirect(url_for('get_all_students'))
    else:
        return render_template('update_student.html')


@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        full_name = request.form['full_name']
        student = Student.query.filter_by(full_name=full_name).first()
        if not student:
            flash(f'Student {full_name} not found')
            return redirect(url_for('delete_student'))
        db.session.delete(student)
        db.session.commit()
        flash(f'Student {full_name} deleted successfully')
        return redirect(url_for('get_all_students'))
    else:
         return render_template('delete_student.html')


# api = Api(app, version='1.0', title='Students API',
#    description='A simple API to manage students data')

# student_model = api.model('Student', {
#     'full_name': fields.String(required=True),
#     'subject': fields.String(required=True),
#     'semester_number': fields.Integer(required=True),
#     'grade': fields.Integer(required=True),
#     'start_year': fields.Integer(required=True),
#     'age': fields.Integer(required=True)
# })


# class StudentResource(Resource):
#     def get(self, id=None):
#         if id:
#             student = Student.query.filter_by(id=id).first()
#             if not student:
#                 abort(404, message=f"Student with id={id} not found")
#             return jsonify(student.serialize())
#         else:
#             students = Student.query.all()
#             return jsonify([s.serialize() for s in students])

#     def post(self):
#         data = request.json
#         try:
#             new_student = Student(**data)
#             db.session.add(new_student)
#             db.session.commit()
#             return new_student.to_dict(), 201
#         except Exception as e:
#             db.session.rollback()
#             return {'error': str(e)}, 500

#     @api.expect(student_model)
#     @api.doc(responses={200: 'Student Updated', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
#              params={'id': 'Specify the ID associated with the student', 'student': 'Student information'})
#     def put(self, id):
#         data = request.json
#         student = Student.query.get(id)
#         if student:
#             student.full_name = data.get('full_name', student.full_name)
#             student.subject = data.get('subject', student.subject)
#             student.semester_number = data.get('semester_number', student.semester_number)
#             student.grade = data.get('grade', student.grade)
#             student.start_year = data.get('start_year', student.start_year)
#             student.age = data.get('age', student.age)
#             db.session.commit()
#             return student.to_dict(), 200
#         else:
#             return {'error': 'Student not found'}, 404

#     @api.doc(responses={204: 'Student Deleted', 400: 'Invalid Argument', 500: 'Mapping Key Error'},
#              params={'id': 'Specify the ID associated with the student'})
    

#     def delete(self, id):
#         student = Student.query.filter_by(id=id).first()
#         if not student:
#             abort(404, message=f"Student with id={id} not found")
#         db.session.delete(student)
#         db.session.commit()
#         return '', 204


# api.add_resource(StudentResource, '/students', '/students/<int:id>')

@app.route('/api')
def api():  
    return redirect(url_for('swagger_ui', path='swagger.json'))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
