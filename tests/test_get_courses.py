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
        #test_database_builder.build()
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
        f_courses = self.client.post('/')

