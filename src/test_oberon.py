import unittest
import json
from oberon import app
from flask import Flask
from flask.ext.testing import TestCase
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["sha512_crypt"],
                           default="sha512_crypt",
                           sha512_crypt__default_rounds=45000)
import config

from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, Role, InstructorTrait, CourseTrait, InstructorTraits, CourseTraits

headers = {'Content-Type': 'application/json'}

def populate_db():
    user_datastore.create_user(email="testuser@villanova.edu", password_hash=pwd_context.encrypt("password"))
    user_datastore.commit()
    user_role = Role(name='user', description="Just regular guy")
    db.session.add(user_role)
    db.session.commit()

class OberonTestCase(TestCase):

    def create_app(self):
        return app

    def setUp(self):
        app.config.from_object(config.TestingConfig)
        self.db = db
        self.db.init_app(app)
        app.app_context().push()
        self.db.drop_all()
        self.db.create_all()
        populate_db()
        
    def test_add_user(self):
        user_datastore.create_user(email="test@villanova.edu", password_hash=pwd_context.encrypt("testpass"))
        user_datastore.commit()
        user = Student.query.filter_by(email="test@villanova.edu")
        self.assertIsNotNone(user)

    def test_verify_password(self):
        user_datastore.create_user(email="test@villanova.edu", password_hash=pwd_context.encrypt("testpass"))
        user_datastore.commit()
        user = Student.query.filter_by(email="test@villanova.edu").first()
        self.assertTrue(user.verify_password("testpass"))

    def test_auth(self):
        self.assertIsNotNone(Student.query.filter_by(email="testuser@villanova.edu").first())
        auth_success = self.client.post('/auth', data=json.dumps({'username': 'testuser@villanova.edu', 'password': 'password'}), headers=headers)
        self.assert200(auth_success, "Response should be a 200")
        self.assertIsNotNone(auth_success.json.get('access_token'), "/auth auth_success should return access token on user verification")

    def test_auth_user_does_not_exist(self):
        auth_failure = self.client.post('/auth', data=json.dumps({'username': 'doesnotexist@villanova.edu', 'password': 'test'}), headers=headers)
        self.assert401(auth_failure, "Response should be a 401")

    def test_auth_wrong_password(self):
        auth_failure = self.client.post('/auth', data=json.dumps({'username': 'testuser@villanova.edu', 'password': 'wrongpass'}), headers=headers)
        self.assert401(auth_failure, "Response should be a 401")

    def test_signup_success(self):
        """
        /signup requires a json object
        {
          "email": valid villanova email (@villanova.edu),
          "firstName": non-empty,
          "lastName": non-empty,
          "password": more than 6 chars,
        }
        """
        test_signup = {
            "email": "testsignup@villanova.edu",
            "firstName": "test",
            "lastName": "test",
            "password": "validpass",
        }
        signup_success = self.client.post('/signup', data=json.dumps(test_signup), headers=headers)
        self.assert200(signup_success, "Successful signup should return a 200")

        new_user = Student.query.filter_by(email=test_signup['email']).first()
        self.assertTrue(new_user.verify_password('validpass'), "Something went wrong creating use password")

    def test_signup_failures(self):
        # field missing
        field_missing = {
            "email": "signup@villanova.edu",
            "firstName": "sign",
            "password": "password"
        }
        signup_failure1 = self.client.post('/signup', data=json.dumps(field_missing), headers=headers)
        self.assert400(signup_failure1, "Field missing from json request")

        field_empty = {
            "email": "testsignup@villanova.edu",
            "firstName": "",
            "lastName": "test",
            "password": "validpass",
        }
        signup_failure2 = self.client.post('/signup', data=json.dumps(field_empty), headers=headers)
        self.assert400(signup_failure2, "firstName is empty")

        invalid_email = {
            "email": "testsignup@gmail.com",
            "firstName": "test",
            "lastName": "test",
            "password": "validpass",
        }
        signup_failure3 = self.client.post('/signup', data=json.dumps(invalid_email), headers=headers)
        self.assert400(signup_failure3, "Invalid villanova email")

        invalid_pass = {
            "email": "testsignup@gmail.com",
            "firstName": "test",
            "lastName": "test",
            "password": "test",
        }
        signup_failure4 = self.client.post('/signup', data=json.dumps(invalid_pass), headers=headers)
        self.assert400(signup_failure4, "Invalid Password")


    def testAddInstructor(self):
        instructor_record = Instructor(name="Anany Levitin")
        db.session.add(instructor_record)
        db.session.commit()
        self.assertIsNotNone(Instructor.query.filter_by(name="Anany Levitin").first())

    #InstructorTrait tests ----------------------------------------------------------
    def testAddInstructorTraits(self):
        trait_record = InstructorTrait(description="Challenging")
        db.session.add(trait_record)
        db.session.commit()
        self.assertIsNotNone(InstructorTrait.query.get(1))

    def testGetNonExistantInstructorTrait(self):
        self.assertIsNone(InstructorTrait.query.get(1))

    def testAddTraitToInstructor(self):
        # Add instructor to db
        instructor_record = Instructor(name="Anany Levitin")
        db.session.add(instructor_record)
        db.session.commit()
        self.assertIsNotNone(Instructor.query.filter_by(name="Anany Levitin").first())

        #add Trait to db
        trait_record = InstructorTrait(description="Challenging")
        db.session.add(trait_record)
        db.session.commit()
        self.assertIsNotNone(InstructorTrait.query.get(1))

        # Add trait to instructor
        instructor_trait_record = InstructorTraits(instructor_name="Anany Levitin", trait_id=trait_record.id, count=0)
        db.session.add(instructor_trait_record)
        db.session.commit()
        self.assertTrue(instructor_record.traits)

        # Test Increment trait count
        instructor_trait_record.count += 1
        db.session.add(instructor_trait_record)
        db.session.commit()
        self.assertEquals(instructor_trait_record.count, 1)

    # CourseTrait tests ------------------------------------------------------------
    def testAddCourseTraits(self):
        trait_record = CourseTrait(description="Challenging")
        db.session.add(trait_record)
        db.session.commit()
        self.assertIsNotNone(CourseTrait.query.get(1))

    def testGetNonExistantCourseTrait(self):
        self.assertIsNone(CourseTrait.query.get(5))

    def testAddTraitToCourse(self):
        # Add course to db
        course_record = Course(name="Analysis of Algorithms")
        db.session.add(course_record)
        db.session.commit()
        self.assertIsNotNone(Course.query.filter_by(name="Analysis of Algorithms").first())

        #add Trait to db
        trait_record = CourseTrait(description="Challenging")
        db.session.add(trait_record)
        db.session.commit()
        self.assertIsNotNone(CourseTrait.query.get(1))

        # Add trait to course
        course_trait_record = CourseTraits(course_name="Analysis of Algorithms", trait_id=trait_record.id, count=0)
        db.session.add(course_trait_record)
        db.session.commit()
        self.assertTrue(course_record.traits)

        # Test Increment trait count
        course_trait_record.count += 1
        db.session.add(course_trait_record)
        db.session.commit()
        self.assertEquals(course_trait_record.count, 1)

    def tearDown(self):
        self.db.session.commit()
        self.db.drop_all()

if __name__ == "__main__":
    unittest.main()





