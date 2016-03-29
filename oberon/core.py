from flask import Flask, jsonify, request, make_response
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore, UserMixin, RoleMixin, login_required
from sqlalchemy import desc
from helpers import *
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)
from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, InstructorTrait, CourseTrait, InstructorTraits, CourseTraits
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

app = create_json_app(config.Config)
# Set up security -------------------------------
security = Security(app, user_datastore)

jwt = JWT(app, authenticate, jwt_identity)
jwt.jwt_payload_handler(jwt_payload_handler)

# Endpoints -------------------------------------
@app.route('/')
@jwt_required()
def index():
    return "Hello World!"

@app.route('/signup', methods=['POST'])
def signup():
    # input validation here
    signup_request = request.get_json()
    #print "Signup info is: %s" % signup_request
    if validate_signup(signup_request):
        user = Student.query.filter_by(email=signup_request['email']).first()
        user = user_exists(signup_request['email'])
        if user:
            return json_response({'status': 'failure',
                                  'message': 'User already exists'}, 409)
        else:
            add_user(db, signup_request['email'], signup_request['firstName'], signup_request['lastName'], password=signup_request['password'])
            return json_response({'status': 'success',
                                  'message': 'User successfully created'}, 200)
    else:
        return json_response({'status': 'failure',
                              'message': 'Bad Request'}, 400)

@app.route('/courses/f/<search_string>', methods=['GET'])
@jwt_required()
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
    return json_response({'status': 'success',
                          'data': instructor_data}, 200)

@app.route('/instructors/<instructor_name>', methods=['GET'])
def get_instructor(instructor_name):
    try:
        instructor = Instructor.query.filter_by(name=instructor_name).first()
        if instructor:
            instructor_data = get_instructor_json(instructor)
            return json_response({'status': 'success',
                                  'data': instructor_data}, 200)
        else:
            message = "Bad Request. No instructor named %s" % instructor_name
            return json_response({'status': 'failure',
                                  'message': message}, 400)
    except:
        return json_response({'status': 'failure',
                              'message': 'Server Error has occured'}, 500)

@app.route('/courses/<course_name>', methods=['GET'])
def get_course(course_name):
    #try:
    course = Course.query.filter_by(name=course_name).first()
    if course:
        course_data = get_course_json(course)
            #course_data['sections'] = sorted([section.crn for section in course.sections])
        return json_response({'status': 'success',
                                  'data': course_data}, 200)
    else:
        message = "Bad Request. No course named %s" % course_name
        return json_response({'status': 'failure',
                              'message': message}, 400)
    # except:
    #     return json_response({'status': 'failure',
    #                           'message': 'Server error has occured'}, 500)

@app.route('/reviews', methods=['POST'])
def post_review():
    #try:
    review_request = request.get_json()
    review_record = Review(class_rating=review_request['classRating'], inst_rating=review_request['instRating'], review_body=review_request['reviewBody'], date_created=datetime.now())
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
    db.session.commit()
    return json_response({'status': 'success',
                          'message': 'Review Successfully Added'}, 200)
    #except:
    #    return json_response({'status': 'failure'}, 500)

@app.route('/reviews/student/<student_email>', methods=['GET'])
def get_student_reviews(student_email):
    student = Student.query.filter_by(email=student_email).first()
    reviews = [review_to_json(review) for review in student.reviews]
    return json_response({'reviews': reviews}, 200)

@app.route('/reviews/<id>', methods=['GET'])
def get_single_review(id):
    try:
        review = Review.query.get(id)
        if review:
            return json_response({'status': 'success',
                                  'data': review_to_json(review)}, 200)
        else:
            return json_response({'status': 'failure',
                                  'message': 'No review with this id'}, 400)
    except:
        return json_response({'status': 'failure',
                              'message': 'A server error has occured.'}, 500)

@app.route('/recent', methods=['GET'])
def get_recent_reviews():
    try:
        reviews = Review.query.order_by(desc(Review.date_created)).limit(10).all()
        review_data = [review_to_json(review) for review in reviews]
        return json_response({'status': 'success',
                              'data': review_data}, 200)
    except:
        return json_response({'status': 'failure',
                              'message': 'A server error has occurred.'}, 500)

def increment_or_add_trait(trait_type, course, instructor, id):
    record = None
    if trait_type == "instructor":
        record = InstructorTraits.query.filter_by(instructor_name=instructor).filter_by(trait_id=id).first()
        if not record:
            record = InstructorTraits(instructor_name=instructor, trait_id=id, count=1)
        else:
            record.count += 1
    if trait_type == "course":
        record = CourseTraits.query.filter_by(course_name=course).filter_by(trait_id=id).first()
        if not record:
            record = CourseTraits(course_name=course, trait_id=id, count=1)
        else:
            record.count += 1
    if record:
        db.session.add(record)
        db.session.commit()
    return None


@app.route('/traits', methods=['GET', 'POST'])
def get_all_traits():
    if request.method == 'GET':
        instructor_traits = [ trait_to_json(trait) for trait in InstructorTrait.query.all() ]
        course_traits = [ trait_to_json(trait) for trait in CourseTrait.query.all() ]
        return json_response({'status': 'success',
                              'instructor_traits': instructor_traits,
                              'course_traits': course_traits}, 200)
    elif request.method == 'POST':
        data = request.get_json()
        instructor = data['instructor']
        course = data['course']
        inst_trait_ids = data['instructor_traits']
        course_trait_ids = data['course_traits']
        for trait_id in inst_trait_ids:
            increment_or_add_trait('instructor', course, instructor, trait_id)
        for trait_id in course_trait_ids:
            increment_or_add_trait('course', course, instructor, trait_id)
        return json_response({'status': 'success',
                              'message': 'All traits added successfully'}, 200)

@app.route('/user', methods=['GET'])
@jwt_required()
def get_user_info():
    token = request.headers['Authorization'].split(' ')[1]
    user_info = jwt.jwt_decode_callback(token)
    user_record = Student.query.filter_by(email=user_info['identity']).first()
    user_info['first_name'] = user_record.first_name
    user_info['last_name'] = user_record.last_name
    return json_response({'status': 'success',
                          'user': user_info}, 200)

if __name__ == "__main__":
    app.run(debug=True)
