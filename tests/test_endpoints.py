import unittest
import json
from .context import app
from flask import Flask
from flask.ext.testing import TestCase
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)
import config

from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, Role, InstructorTrait, CourseTrait, InstructorTraits, CourseTraits

headers = {'Content-Type': 'application/json'}

class SignUpTestCase(TestCase):

    def create_app(self):
        app.config.from_object(config.TestingConfig)
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.close_all()
        db.drop_all()

    def test_signup_success(self):
        test_signup = {
            "email": "signupsuccess@villanova.edu",
            "firstName": "test",
            "lastName": "test",
            "password": "validpassword",
        }
        signup_success = self.client.post('/signup', data=json.dumps(test_signup), headers=headers)
        self.assert200(signup_success, "Successful signup should return a 200")

        new_user = Student.query.filter_by(email=test_signup['email']).first()
        self.assertIsNotNone(new_user, "User was not created")

    def test_signup_field_missing(self):
        field_missing = {
            "email": "signup@villanova.edu",
            "firstName": "sign",
            "password": "password"
        }
        signup_failure1 = self.client.post('/signup', data=json.dumps(field_missing), headers=headers)
        self.assert400(signup_failure1, "Field missing from json request")

    def test_signup_field_empty(self):
        field_empty = {
            "email": "testsignup@villanova.edu",
            "firstName": "",
            "lastName": "test",
            "password": "validpass",
        }
        signup_failure2 = self.client.post('/signup', data=json.dumps(field_empty), headers=headers)
        self.assert400(signup_failure2, "firstName is empty")

    def test_signup_invalid_email(self):
        invalid_email = {
            "email": "testsignup@gmail.com",
            "firstName": "test",
            "lastName": "test",
            "password": "validpass",
        }
        signup_failure3 = self.client.post('/signup', data=json.dumps(invalid_email), headers=headers)
        self.assert400(signup_failure3, "Invalid villanova email")

    def test_signup_invalid_password(self):
        invalid_pass = {
            "email": "testsignup@gmail.com",
            "firstName": "test",
            "lastName": "test",
            "password": "test",
        }
        signup_failure4 = self.client.post('/signup', data=json.dumps(invalid_pass), headers=headers)
        self.assert400(signup_failure4, "Invalid Password")

if __name__ == "__main__":
    unittest.main()





