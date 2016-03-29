import unittest
import json
from .context import app
from flask import Flask
from flask.ext.testing import TestCase
from passlib.context import CryptContext
import sys
import os
pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)
import config

from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, Role, InstructorTrait, CourseTrait, InstructorTraits, CourseTraits
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../oberon'))
#sys.path.insert(0, os.path.abspath('../oberon/sample_data'))
from oberon.sample_data.sample_courses import courses as courses
from database_builder import DatabaseBuilder
test_database_builder = DatabaseBuilder(courses, config.TestingConfig)

headers = {'Content-Type': 'application/json'}
auth_header ={'Content-Type': 'application/json', 'Authorization': 'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZGVudGl0eSI6InNpZ251cHN1Y2Nlc3NAdmlsbGFub3ZhLmVkdSIsImlhdCI6MTQ1OTA0NzM0MSwibmJmIjoxNDU5MDQ3MzQxLCJleHAiOjE0NjE2MzkzNDF9.FJNtmmS8pCSFkqJREXjvmMPI_CZdMNw17Ce0k2BWwU8'}


valid_post_review_req = {
    "classRating": "5",
    "instRating": "5",
    "student": "signupsuccess@villanova.edu",
    "reviewBody": "This is a test review body.",
    "instructor": "Anany Levitin",
    "course": "Analysis of Algorithms"
}

invalid_post_review_req = {
    "classRating": "5",
    "instRating": "5",
    "student": "signupsuccess@villanova.edu",
    "reviewBody": "This is a test review body.",
    "instructor": "Anany Levitin",
    #"course": "Analysis of Algorithms"

    # Request is malformed due to missing "course" key
   
}

class GetCoursesTestCase(TestCase):

    def create_app(self):
        app.config.from_object(config.TestingConfig)
        return app

    def setUp(self):
        db.create_all()
        user = {
            "email": "signupsuccess@villanova.edu",
            "firstName": "test",
            "lastName": "test",
            "password": "validpassword",
        }
        test_database_builder.build(output=False)
        signup_success = self.client.post('/signup', data=json.dumps(user), headers=headers)
        self.assert200(signup_success, "Signup in test setup did not succeed")
        test_auth = {
            'username': user['email'],
            'password': user['password']
        }
        auth_success = self.client.post('/auth', data=json.dumps({'username': user['email'], 'password': user['password']}), headers=headers)
        self.assert200(auth_success)

    def tearDown(self):
        db.session.close_all()
        db.drop_all()

    def test_get_courses_unauth(self):
        f_courses = self.client.get('/courses/f/analysis', headers=headers)
        self.assert401(f_courses, "/courses/f/<course_name> should return 401 if not authorized")

    def test_get_courses_auth(self):
        response = self.client.get('/courses/f/analysis', headers=auth_header)
        self.assert200(response, "/courses/f/<course> should return 200 if authorized")
        data = json.loads(response.data)
        self.assertTrue("data" in data, "Response must have top level key \"data\"")
        data_keys = ["attributes", "course_name", "department", "level", "match"]
        for course in data["data"]:
            for key in data_keys:
                self.assertTrue(key in course, "Course in response must have key %s" % key)

    def test_get_course_unauth(self):
        response = self.client.get('/courses/analysis of algorithms', headers=headers)
        self.assert401(response, "/courses/<course_name> should return 401 if not authorized")

        response2 = self.client.get('/courses/analysis of algirhtms', headers=headers)
        self.assert401(response2, "/courses/<course_name> should return 401 if not authorized and resource does not exist")

    def test_get_course_auth(self):
        response = self.client.get('/courses/Analysis of Algorithms', headers=auth_header)
        data = json.loads(response.data)
        self.assertTrue("data" in data, "Response must have top level key \"data\"")
        self.assertTrue("status" in data, "Response must have top level key \"status\"")
        second_level = ["instructors", "name", "reviews", "sections", "subject", "subject_level", "traits"]
        for key in second_level:
            self.assertTrue(key in data["data"], "Response[\"data\"] must have key \"%s\"" % key)


    def test_get_instructors_unauth(self):
        response = self.client.get('/instructors/f/levitin', headers=headers)
        self.assert401(response, "/instructors/f/<instructor> should return 401 if not authorized")

    def test_get_instructors_auth(self):
        response = self.client.get('/instructors/f/levitin', headers = auth_header)
        print response.data
        self.assert200(response, "/instructors/f/<instructor> should return 200 on authorized GET request")
        data = json.loads(response.data)
        self.assertTrue("data" in data, "Response must have top level key \"data\"")
        self.assertTrue("status" in data, "Response must have top level key \"status\"")
        second_level = ["courses", "departments", "name", "rating", "traits"]
        for instructor in data["data"]:
            for key in second_level:
                self.assertTrue(key in instructor, "Response[\"data\"] must have key \"%s\"" % key)

    def test_get_instructor_unauth(self):
        response = self.client.get('/instructors/Anany Levitin', headers = headers)
        self.assert401(response, "/instructors/<instructor> should return 401 if not authorized")

        response2 = self.client.get('/instructors/abcdefghi', headers = headers)
        self.assert401(response2, "/instructors/<instructor> should return 401 if not authorized")

    def test_get_instructor_auth(self):
        response = self.client.get('/instructors/Anany Levitin', headers = auth_header)
        self.assert200(response, '/instructors/<instructor> should return 200 if authorized and resource exists')

        response2 = self.client.get('/instructors/abcdefghi', headers = auth_header)
        self.assert400(response2, '/instructors/<instructor> should return 400 if authorized and resource does not exist')


    def test_post_review_unauth(self):
        response = self.client.post('/reviews', data=json.dumps(valid_post_review_req), headers=headers)
        self.assert401(response, 'POST to /reviews should return 401 if not authorized')

        response2 = self.client.post('/reviews', data=json.dumps(invalid_post_review_req), headers=headers)
        self.assert401(response2, 'POST to /reviews should return 401 if not authorized')

    def test_post_review_auth(self):
        # valid post request
        response = self.client.post('/reviews', data=json.dumps(valid_post_review_req), headers = auth_header)
        self.assert200(response, "POST to /reviews should return 200 if authorized and request is valid")

        # malformed post request
        malformed_response = self.client.get('/reviews', data=json.dumps(invalid_post_review_req), headers=auth_header)
        self.assert405(malformed_response, "POST to /reviews should return 405 if authorized but the request is malformed")

        # Check for existence of review
        response2 = self.client.get('/reviews/student/signupsuccess@villanova.edu', headers = auth_header)
        self.assert200(response2, "GET /reviews/student/<student_email> should return 200 if authorized")

        # Check for existence of review
        data = json.loads(response2.data)
        self.assertTrue('reviews' in data, "Response from GET /reviews/student/<student_email> should have a top level key \"reviews\"")
        self.assertTrue(len(data['reviews']) > 0, "Response from GET /reviews/student/<student_email should contain a review")
