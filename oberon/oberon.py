from flask import Flask, jsonify, request
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
import config
from flask.ext.sqlalchemy import SQLAlchemy
from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review
from fuzzywuzzy import fuzz, process
from validate_email import validate_email
import itertools

class CourseNameException(Exception):
    def __init(self, length):
        self.length = length
    def __str__(self):
        return repr(self.length)

def create_app():
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
        return response

    app = Flask(__name__)
    app.config.from_object(config.Config)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.app_context().push()
    return app

app = create_app()

instructors = {instructor.name: [department.name for department in instructor.departments] for instructor in Instructor.query.all()}
instructor_names = instructors.keys()
courses = {course.name: [attribute.name for attribute in course.attributes] for course in Course.query.all()}
course_names = courses.keys()

@app.route('/update')
def update():
    instructors = {instructor.name: [department.name for department in instructor.departments] for instructor in Instructor.query.all()}
    instructor_names = instructors.keys()
    courses = {course.name: [attribute.name for attribute in course.attributes] for course in Course.query.all()}
    course_names = courses.keys()
    return jsonify({'success': True})

@app.route('/')
def index():
    return "Hello World!"

@app.route('/signup', methods=['POST'])
def signup():
    # input validation here
    signup_request = request.get_json()
    if signup_request['email'] != signup_request['confirmEmail']:
        return jsonify({'status': 'Emails do not match'})
    elif Student.query.filter_by(email=signup_request['email']).scalar():  #student already has an account
        return jsonify({'status': 'User already exists'})
    elif not validate_email(signup_request['email']) or signup_request['email'][-13:] != 'villanova.edu':
        return jsonify({'status': 'Please enter a valid villanova.edu email address'})
    else:
        # Send the user an email to activate their account
        # For now, just creating the user
        student_record = Student(signup_request['email'],
                                 signup_request['firstName'],
                                 signup_request['lastName'],
                                 signup_request['password'])
        db.session.add(student_record)
        db.session.commit()
        return jsonify({'status': 'SUCCESS: Check your email'})

@app.route('/login', methods=['POST'])
def login():
    login_request = request.get_json()
    student_record = Student.query.filter_by(email=login_request['email']).first()
    if not student_record:
        return jsonify({'status': 'User does not exist. Please Register'})
    # simple check for password for now before hashing/salting/authentication is added
    elif student_record.password != login_request['password']:
        return jsonify({'status': 'Invalid Password, please Try Again'})
    else:
        return jsonify({'status': '(fake)Authenticated'})

@app.route('/courses/f/<search_string>', methods=['GET'])
def get_courses(search_string):
    course_data = [{'course_name': course[0],
                    'attributes': courses[course[0]],
                    'match': course[1]} for course in process.extract(search_string, course_names, limit=100) if course[1] > 60]
    return jsonify({'courses': course_data})


@app.route('/instructors/f/<search_string>', methods=['GET'])
def get_instructors(search_string):
    instructor_data = [{instructor[0]:instructors[instructor[0]]} for instructor in process.extract(search_string, instructor_names, limit=100) if instructor[1] > 60]
    return jsonify({'data': instructor_data})

@app.route('/instructors/<instructor_name>', methods=['GET'])
def get_instructor(instructor_name):
    instructor = Instructor.query.filter_by(name=instructor_name).first()
    instructor_data = {
        'name': instructor.name,
    }
    return jsonify(instructor_data)

@app.route('/courses/<course_name>', methods=['GET'])
def get_course(course_name):
    course = Course.query.filter_by(name=course_name).first()
    course_data = {
        'name': course.name,
        'subject_level': course.subject_level,
        'subject': course.subject
    }
    return jsonify(course_data)

@app.route('/reviews/student/<student_email>', methods=['GET'])
def get_student_reviews(student_email):
    student = Student.query.filter_by(email=student_email).first()
    reviews = [{'text': review.review_body} for review in student.reviews]
    return jsonify({'data': reviews})

@app.route('/reviews/instructor/<instructor>', methods=['GET'])
def get_instructor_reviews(instructor):
    print instructor
    instructor = Instructor.query.filter_by(name=instructor).first()
    reviews = [{'text': review.review_body} for review in instructor.reviews]
    return jsonify({'data': reviews})

@app.route('/reviews/course/<course>', methods=['GET'])
def get_course_reviews(course):
    print course
    course = Course.query.filter_by(name=course).first()#.sections
    review_objects = list(itertools.chain.from_iterable([section.reviews for section in course.sections]))
    reviews = [{'text': review.review_body} for review in review_objects]
    return jsonify({'data': reviews})

if __name__ == "__main__":
    app.run(debug=True)
