from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, abort
from flask_restx import Api, Resource, fields
from database import db, Students, initialize_database



app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Инициализация объекта Api
api = Api(app, version='1.0', title='Student API', description='API for managing student data')

# Определение модели студента
student_model = api.model('Student', {
    'full_name': fields.String(required=True, description='Full name of the student'),
    'subject': fields.String(required=True, description='Subject of study'),
    'semester_number': fields.Integer(required=True, description='Semester number'),
    'grade': fields.Integer(required=True, description='Grade'),
    'start_year': fields.Integer(required=True, description='Year of enrollment'),
    'age': fields.Integer(required=True, description='Age of the student')
})

# Пример данных о студентах
students = []

# Конечная точка для получения всех студентов
@api.route('/students')
class StudentsResource(Resource):
    @api.doc('get_all_students')
    @api.marshal_list_with(student_model)
    def get(self):
        return students

    @api.doc('create_student')
    @api.expect(student_model)
    @api.marshal_with(student_model, code=201)
    def post(self):
        payload = request.json
        name = payload['full_name']
        subject = payload['subject']
        semester = payload['semester_number']
        grade = payload['grade']
        year = payload['start_year']
        age = payload['age']
        new_student = {
            'full_name': name,
            'subject': subject,
            'semester_number': semester,
            'grade': grade,
            'start_year': year,
            'age': age
        }
        students.append(new_student)
        return payload, 201

@api.route('/students/<string:full_name>')
@api.doc(params={'full_name': 'Full name of the student'})
class StudentResource(Resource):
    @api.doc('get_student')
    @api.marshal_with(student_model)
    def get(self, full_name):
        for student in students:
            if student['full_name'] == full_name:
                return student
        api.abort(404, f'Student {full_name} not found')

    @api.doc('update_student')
    @api.expect(student_model)
    @api.marshal_with(student_model)
    def put(self, full_name):
        for student in students:
            if student['full_name'] == full_name:
                payload = request.json
                student['full_name'] = payload['full_name']  # Обновление имени студента
                student['subject'] = payload['subject']
                student['semester_number'] = payload['semester_number']
                student['grade'] = payload['grade']
                student['start_year'] = payload['start_year']
                student['age'] = payload['age']
                return student
        api.abort(404, f'Student {full_name} not found')

    @api.doc('delete_student')
    @api.response(204, 'Student deleted')
    def delete(self, full_name):
        for student in students:
            if student['full_name'] == full_name:
                students.remove(student)
                return '', 204
        abort(404, f'Student {full_name} not found')

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
        return f'<Student {self.full_name}>'


@app.route('/students', methods=['GET'])
def get_all_students():
    student = Student.query.all()
    return render_template('all_students.html', students=student)


@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['full_name']
        subject = request.form['subject']
        semester = request.form['semester_number']
        grade = request.form['grade']
        year = request.form['start_year']
        age = request.form['age']
        new_student = Student(full_name=name, subject=subject, semester_number=semester, grade=grade, start_year=year,
                              age=age)
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
    return render_template('stats.html', average_grade=average_grade, max_grade=max_grade, min_grade=min_grade,
                           oldest_student=oldest_student, youngest_student=youngest_student)


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
        student.subject = request.form['subject']
        student.semester_number = request.form['semester_number']
        student.start_year = request.form['start_year']
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




@app.route('/api')
def api():
    return redirect(url_for('swagger_ui', path='swagger.json'))


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    initialize_database(app)
    app.run(debug=True)
