from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from sqlalchemy import desc
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
    if not signup_json:
        return False
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

def review_to_json(review):
    """
    Given a review object, returns a JSON representation of a review
    and it's relevant information
    """
    return {
        'text': review.review_body,
        'class_rating': review.class_rating,
        'section_crn': review.section_crn,
        'course': review.section.course.name,
        'subject': review.section.course.subject,
        'subject_level': review.section.course.subject_level,
        'instructor_name': review.instructor_name,
        'inst_rating': review.inst_rating,
        'student': review.student_email,
        'date_created': review.date_created.isoformat()
    }

def reviews_to_json(list_of_reviews):
    """
    Given a list of review objects, returns a list of json objects
    """
    return [review_to_json(review) for review in list_of_reviews]

def average_reviews(reviews, key):
    """
    given a list of review JSON objects, returns the average rating of the reviews
    possible keys are 'inst_rating' or 'class_rating'
    """
    if reviews:
        return sum([float(review[key]) for review in reviews]) / len(reviews)
    else:
        return None

def get_instructor_courses(instructor):
    """
    Given an instructor object, returns a list of course objects taught by the instructor
    """
    course_names = list(set([section.course.name for section in instructor.sections]))
    return [Course.query.filter_by(name=course_name).first() for course_name in course_names]

def course_to_json(course):
    """
    Given a course object, returns a JSON object with relevant information
    """
    return {
        'course_name': course.name,
        'department': course.subject,
        'level': course.subject_level,
        'attributes': [attribute.name for attribute in course.attributes]
    }

def get_instructor_json(instructor):
    """
    Given an instructor object, returns it's JSON representation
    """
    courses = get_instructor_courses(instructor)
    reviews = reviews_to_json(instructor.reviews)
    return {
        'name': instructor.name,
        'departments': [{'code': department.code,
                         'name': department.name} for department in instructor.departments],
        'traits': [],
        'courses': courses_to_json(courses),
        'reviews': reviews,
        'rating': average_reviews(reviews, 'inst_rating')
    }

def get_less_instructor_json(instructor):
    """
    Given an instructor object, returns it's header information
    name
    departments
    traits
    rating
    """
    courses = get_instructor_courses(instructor)
    reviews = reviews_to_json(instructor.reviews)
    return {
        'name': instructor.name,
        'departments': [{'code': department.code,
                         'name': department.name} for department in instructor.departments],
        'traits': [],
        'courses': courses_to_json(courses),
        'rating': average_reviews(reviews, 'inst_rating')
    }

def courses_to_json(list_of_courses):
    """
    Given a list of course objects, returns a list of course JSON objects
    """
    return [course_to_json(course) for course in list_of_courses]

def get_course_reviews(course):
    """
    Given a course object, returns a list of all of the reviews of that course
    """
    review_objects = list(itertools.chain.from_iterable([section.reviews for section in course.sections]))
    return [review_to_json(review) for review in review_objects]

def get_course_instructors(course):
    """
    Given a course object, returns a list of all of the instructors of that course
    """
    course_instructors = list(set(itertools.chain.from_iterable([[instructor.name for instructor in section.instructors] for section in course.sections])))
    instructor_objects = [Instructor.query.filter_by(name=instructor).first() for instructor in course_instructors]
    return [get_less_instructor_json(instructor) for instructor in instructor_objects]

def get_course_json(course):
    """
    Given a course object, returns a list of it's json representation
    """
    return {
       'name': course.name,
       'subject_level': course.subject_level,
       'subject': course.subject,
       'reviews': get_course_reviews(course),
       'instructors': get_course_instructors(course),
       'traits': [], # blank for now
   }

app = create_json_app(config.Config)
# Set up security -------------------------------
security = Security(app, user_datastore)

jwt = JWT(app, authenticate, jwt_identity)
jwt.jwt_payload_handler(jwt_payload_handler)

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
    print "Signup info is: %s" % signup_request
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
    instructor_names = [instructor.name for instructor in Instructor.query.all()]
    instructors = [instructor for instructor in process.extract(search_string, instructor_names, limit=100) if instructor[1] > 60]
    instructor_data = [get_less_instructor_json(Instructor.query.filter_by(name=instructor[0]).first()) for instructor in instructors]
    instructor_data = [{get_less_instructor_json(instructor)}]
    instructor_data = [{instructor[0]:instructors[instructor[0]]} for instructor in process.extract(search_string, instructor_names, limit=100) if instructor[1] > 60]
    return json_response({'status': 'success',
                          'data': instructor_data}, 200)

@app.route('/instructors/<instructor_name>', methods=['GET'])
def get_instructor(instructor_name):
    try:
        instructor = Instructor.query.filter_by(name=instructor_name).first()
        instructor_data = get_instructor_json(instructor)
        return json_response({'status': 'success',
                          'data': instructor_data}, 200)
    except:
        return json_response({'status': 'failure',
                              'message': 'Server Error has occured'}, 500)

@app.route('/courses/<course_name>', methods=['GET'])
def get_course(course_name):
    try:
        course = Course.query.filter_by(name=course_name).first()
        course_data = get_course_json(course)
        return json_response({'status': 'success',
                              'data': course_data}, 200)
    except:
        return json_response({'status': 'failure',
                              'message': 'Server error has occured'}, 500)

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
        return json_response({'status': 'success'}, 200)
    except:
        return json_repsonse({'status': 'failure'}, 500)

@app.route('/reviews/student/<student_email>', methods=['GET'])
def get_student_reviews(student_email):
    student = Student.query.filter_by(email=student_email).first()
    reviews = [{'text': review.review_body} for review in student.reviews]
    return json_response({'reviews': reviews}, 200)

@app.route('/reviews/instructor/<instructor>', methods=['GET'])
def get_single_instructor_reviews(instructor):
    instructor = Instructor.query.filter_by(name=instructor).first()
    reviews = [{'text': review.review_body} for review in instructor.reviews]
    return json_response({'reviews': reviews}, 200)

@app.route('/reviews/course/<course>', methods=['GET'])
def get_single_course_reviews(course):
    course = Course.query.filter_by(name=course).first()#.sections
    review_objects = list(itertools.chain.from_iterable([section.reviews for section in course.sections]))
    reviews = [{'text': review.review_body} for review in review_objects]
    return json_response({'reviews': reviews}, 200)

@app.route('/reviews/<id>', methods=['GET'])
def get_single_review(id):
    review = Review.query.get(id)
    return json_response({'status': 'success',
                          'data': review_to_json(review)}, 200)

@app.route('/recent', methods=['GET'])
def get_recent_reviews():
    reviews = Review.query.order_by(desc(Review.date_created)).limit(10).all()
    review_data = [review_to_json(review) for review in reviews]
    return json_response({'status': 'success',
                          'data': review_data}, 200)

if __name__ == "__main__":
    app.run(debug=True)
