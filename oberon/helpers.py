from models import Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, InstructorTrait, CourseTrait, InstructorTraits, CourseTraits
from passlib.context import CryptContext
from flask import Flask, jsonify, request, make_response
pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)

from validate_email import validate_email
import itertools

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


def get_instructor_courses(instructor):
    """
    Given an instructor object, returns a list of course objects taught by the instructor
    """
    print instructor
    course_names = list(set([section.course.name for section in instructor.sections]))
    return [Course.query.filter_by(name=course_name).first() for course_name in course_names]


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
    #review_objects = list(itertools.chain.from_iterable([section.reviews for section in course.sections]))
    review_objects = course.reviews
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
        'sections': sorted([section.crn for section in course.sections]),
       'traits': [], # blank for now
   }

def trait_to_json(trait):
    """
    Given an InstructorTrait or CourseTrait object, returns it's json representation
    """
    return {
        'id': trait.id,
        'description': trait.description
    }

#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#------------------BELOW THIS IS THE NEW FUNCTIONS -- REWRITES FOR OLD FUNCS ---------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#--------- All Functions should take a db as a first argument
#--------- This makes the function usable across apps (just plug in a database) ------------


def add_user(db, email, first_name, last_name, password):
    """
    adds a user
    """
    user = user_datastore.create_user(email=email, first_name=first_name, last_name=last_name, password_hash=pwd_context.encrypt(password))#, roles=['user'])
    user_datastore.commit()
    return user

def user_exists(email):
    """Checks database for email and returns whether or not there is a record with that email"""
    return bool(Student.query.filter_by(email=email).first())

