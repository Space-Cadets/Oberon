from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)
from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore
from fuzzywuzzy import fuzz, process
from validate_email import validate_email
from flask_jwt import JWT, jwt_required
from flask.ext.cors import CORS
from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review
from fuzzywuzzy import fuzz, process

import config
from datetime import datetime, timedelta
import itertools

class CourseNameException(Exception):
    def __init(self, length):
        self.length = length
    def __str__(self):
        return repr(self.length)

__all__ = ['create_json_app']

def make_json_error(ex):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    response = jsonify(message=str(ex))
    print response
    response.status_code = (ex.code
                                if isinstance(ex, HTTPException)
                                else 500)
    return response
def authenticate(username, password):
    user = user_datastore.find_user(email=username)
    if user and username == user.email and user.verify_password(password):
        return user
    return None

def jwt_identity(payload):
    print payload
    user = user_datastore.find_user(email=payload['identity'])
    return user

def jwt_payload_handler(identity):
    iat = datetime.utcnow()
    exp = iat + app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + app.config.get('JWT_NOT_BEFORE_DELTA')
    identity = getattr(identity, 'email') or identity['email']
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}

def create_json_app(config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config)
    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.app_context().push()
    return app

def json_response(body, code):
    return make_response(jsonify(body), code)

def validate_signup(signup_json):
    # check all fields are present and not none
    fields = ['email', 'firstName', 'lastName', 'password']
    for field in fields:
        if field not in signup_json:
            return False
        else:
            signup_json[field] = signup_json[field].strip()
            if signup_json[field] == "":
                return False
    # check valid villanova email
    if not validate_email(signup_json['email']) or signup_json['email'][-13:] != 'villanova.edu':
        return False
    #validated
    return True


app = create_json_app(config.Config)
# Set up security -------------------------------
security = Security(app, user_datastore)

jwt = JWT(app, authenticate, jwt_identity)
jwt.jwt_payload_handler(jwt_payload_handler)

#instructors = {instructor.name: [department.name for department in instructor.departments] for instructor in Instructor.query.all()}
#instructor_names = instructors.keys()
#courses = {course.name: [attribute.name for attribute in course.attributes] for course in Course.query.all()}
#course_names = courses.keys()

# Endpoints -------------------------------------
@app.route('/update')
def update():
    instructors = {instructor.name: [department.name for department in instructor.departments] for instructor in Instructor.query.all()}
    instructor_names = instructors.keys()
    courses = {course.name: [attribute.name for attribute in course.attributes] for course in Course.query.all()}
    course_names = courses.keys()
    return jsonify({'status': 'success'})

@app.route('/')
@jwt_required()
def index():
    return "Hello World!"

@app.route('/signup', methods=['POST'])
def signup():
    # input validation here
    signup_request = request.get_json()
    if validate_signup(signup_request):
        user_datastore.create_user(email=signup_request['email'],
                                   first_name=signup_request['firstName'],
                                   last_name=signup_request['lastName'],
                                   password_hash=pwd_context.encrypt(signup_request['password']),
                                   roles=['user'])
        user_datastore.commit()
        return json_response({'status': 'success'}, 200)
    else:
        return json_response({'status': 'failure'}, 400)

@app.route('/courses/f/<search_string>', methods=['GET'])
def get_courses(search_string):
    course_names = [course.name for course in Course.query.all()]
    courses = [course for course in process.extract(search_string, course_names, limit=100) if course[1] > 60]
    course_data = []
    for course in courses:
        course_record = Course.query.filter_by(name=course[0]).first()
        course_data.append({ 'course_name': course[0],
                             'department': course_record.subject,
                             'level': course_record.subject_level,
                             'attributes': [attribute.name for attribute in course_record.attributes],
                             'match': course[1]})
    return json_response({'status': 'success',
                          'data': course_data}, 200)

@app.route('/instructors/f/<search_string>', methods=['GET'])
def get_instructors(search_string):
    instructor_data = [{instructor[0]:instructors[instructor[0]]} for instructor in process.extract(search_string, instructor_names, limit=100) if instructor[1] > 60]
    return json_response({'status': 'success',
                          'data': instructor_data}, 200)

@app.route('/instructors/<instructor_name>', methods=['GET'])
def get_instructor(instructor_name):
    try:
        instructor = Instructor.query.filter_by(name=instructor_name).first()
        courses = list(set([section.course.name for section in instructor.sections]))
        instructor_data = {
            'name': instructor.name,
            'departments': [{'code': department.code,
                             'name': department.name} for department in instructor.departments],
            'traits': []
        }
        instructor_courses = []
        for course in courses:
            course_record = Course.query.filter_by(name=course).first()
            instructor_courses.append({
                'course_name': course,
                'department': course_record.subject,
                'level': course_record.subject_level,
                'attributes': [attribute.name for attribute in course_record.attributes]
            })
        instructor_data['courses'] = instructor_courses
        instructor_data['reviews'] = [{'text': review.review_body,
                                       'class_rating': review.class_rating,
                                       'section_crn': review.section_crn,
                                       'instructor_name': review.instructor_name,
                                       'inst_rating': review.inst_rating,
                                       'student': review.student_email} for review in instructor.reviews]
        instructor_data['rating'] = sum([review['class_rating'] for review in instructor_data['reviews']]) / len(instructor_data['reviews'])
        return json_response({'status': 'success',
                              'data': instructor_data}, 200)
    except:
        return json_response({'status': 'failure',
                              'message': 'Instructor does not exist'}, 400)

@app.route('/courses/<course_name>', methods=['GET'])
def get_course(course_name):
    try:
        course = Course.query.filter_by(name=course_name).first()
        course_data = {
            'name': course.name,
            'subject_level': course.subject_level,
            'subject': course.subject
        }
        return json_response({'status': 'success',
                              'data': course_data}, 200)
    except:
        return json_response({'status': 'failure',
                              'message': 'Course does not exist'}, 400)

@app.route('/reviews', methods=['POST'])
def post_review():
    try:
        review_request = request.get_json()
        review_record = Review(review_request['class_rating'], review_request['inst_rating'], review_request['review_body'])
        student_record = Student.query.filter_by(email=review_request['student']).first()
        section_record = Section.query.filter_by(crn=review_request['section']).first()
        instructor_record = Instructor.query.filter_by(name=review_request['instructor']).first()
        student_record.reviews.append(review_record)
        section_record.reviews.append(review_record)
        instructor_record.reviews.append(review_record)
        db.session.add(review_record)
        db.session.add(student_record)
        db.session.add(section_record)
        db.session.add(instructor_record)
    except:
        return json_repsonse({'status': 'failure'}, 500)
    return json_response({'status': 'success'}, 200)

@app.route('/reviews/student/<student_email>', methods=['GET'])
def get_student_reviews(student_email):
    student = Student.query.filter_by(email=student_email).first()
    reviews = [{'text': review.review_body} for review in student.reviews]
    return json_response({'reviews': reviews}, 200)

@app.route('/reviews/instructor/<instructor>', methods=['GET'])
def get_instructor_reviews(instructor):
    print instructor
    instructor = Instructor.query.filter_by(name=instructor).first()
    reviews = [{'text': review.review_body} for review in instructor.reviews]
    return json_response({'reviews': reviews}, 200)

@app.route('/reviews/course/<course>', methods=['GET'])
def get_course_reviews(course):
    print course
    course = Course.query.filter_by(name=course).first()#.sections
    review_objects = list(itertools.chain.from_iterable([section.reviews for section in course.sections]))
    reviews = [{'text': review.review_body} for review in review_objects]
    return json_response({'reviews': reviews}, 200)

if __name__ == "__main__":
    app.run(debug=True)
