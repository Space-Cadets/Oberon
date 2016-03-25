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

class OberonTestCase(TestCase):

    def create_app(self):
        app.config.from_object(config.TestingConfig)
        return app

    def setUp(self):
        db.create_all()

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
        self.assertTrue(new_user.verify_password('validpass'), "Something went wrong creating user")

    # def test_signup_failures(self):
    #     # field missing
    #     field_missing = {
    #         "email": "signup@villanova.edu",
    #         "firstName": "sign",
    #         "password": "password"
    #     }
    #     signup_failure1 = self.client.post('/signup', data=json.dumps(field_missing), headers=headers)
    #     self.assert400(signup_failure1, "Field missing from json request")

    #     field_empty = {
    #         "email": "testsignup@villanova.edu",
    #         "firstName": "",
    #         "lastName": "test",
    #         "password": "validpass",
    #     }
    #     signup_failure2 = self.client.post('/signup', data=json.dumps(field_empty), headers=headers)
    #     self.assert400(signup_failure2, "firstName is empty")

    #     invalid_email = {
    #         "email": "testsignup@gmail.com",
    #         "firstName": "test",
    #         "lastName": "test",
    #         "password": "validpass",
    #     }
    #     signup_failure3 = self.client.post('/signup', data=json.dumps(invalid_email), headers=headers)
    #     self.assert400(signup_failure3, "Invalid villanova email")

    #     invalid_pass = {
    #         "email": "testsignup@gmail.com",
    #         "firstName": "test",
    #         "lastName": "test",
    #         "password": "test",
    #     }
    #     signup_failure4 = self.client.post('/signup', data=json.dumps(invalid_pass), headers=headers)
    #     self.assert400(signup_failure4, "Invalid Password")


    # def testAddInstructor(self):
    #     instructor_record = Instructor(name="Anany Levitin")
    #     db.session.add(instructor_record)
    #     db.session.commit()
    #     self.assertIsNotNone(Instructor.query.filter_by(name="Anany Levitin").first())

    # #InstructorTrait tests ----------------------------------------------------------
    # def testAddInstructorTraits(self):
    #     trait_record = InstructorTrait(description="Challenging")
    #     db.session.add(trait_record)
    #     db.session.commit()
    #     self.assertIsNotNone(InstructorTrait.query.get(1))

    # def testGetNonExistantInstructorTrait(self):
    #     self.assertIsNone(InstructorTrait.query.get(1))

    # def testAddTraitToInstructor(self):
    #     # Add instructor to db
    #     instructor_record = Instructor(name="Anany Levitin")
    #     db.session.add(instructor_record)
    #     db.session.commit()
    #     self.assertIsNotNone(Instructor.query.filter_by(name="Anany Levitin").first())

    #     #add Trait to db
    #     trait_record = InstructorTrait(description="Challenging")
    #     db.session.add(trait_record)
    #     db.session.commit()
    #     self.assertIsNotNone(InstructorTrait.query.get(1))

    #     traits = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eigth"]
    #     for trait in traits:
    #         db.session.add(InstructorTrait(description=trait))
    #         db.session.commit()
    #     self.assertEquals(len(InstructorTrait.query.all()), 9)
    #     #print InstructorTrait.query.all()

    #     # Add trait to instructor
    #     instructor_trait_record = InstructorTraits(instructor_name="Anany Levitin", trait_id=trait_record.id, count=0)
    #     db.session.add(instructor_trait_record)
    #     db.session.commit()
    #     self.assertTrue(instructor_record.traits)

    #     # Test Increment trait count
    #     instructor_trait_record.count += 1
    #     db.session.add(instructor_trait_record)
    #     db.session.commit()
    #     self.assertEquals(instructor_trait_record.count, 1)

    #     record = InstructorTraits.query.filter_by(instructor_name="Anany Levitin").filter_by(trait_id=1).first()
    #     self.assertIsNotNone(record)
    #     record2 = InstructorTraits.query.filter_by(instructor_name="AnanyLevitin").filter_by(trait_id=1).first()
    #     self.assertIsNone(record2)

    #     traits_test = {
    #         'instructor': 'Anany Levitin',
    #         'course': 'Analysis of Algorithms',
    #         'instructor_traits': [1, 2, 3, 4, 5, 6, 7, 8, 9],
    #         'course_traits': []
    #     }
    #     add_traits_success = self.client.post('/traits', data=json.dumps(traits_test), headers=headers)
    #     self.assertEquals(len(Instructor.query.filter_by(name="Anany Levitin").first().traits), 9)
    #     self.assertEquals(InstructorTraits.query.filter_by(instructor_name="Anany Levitin").filter_by(trait_id=1).first().count, 2)

    #     traits_test2 = {
    #         'instructor': 'Anany Levitin',
    #         'course': 'Analysis of Algorithms',
    #         'instructor_traits': [1],
    #         'course_traits': []
    #     }
    #     add_traits_success2 = self.client.post('/traits', data=json.dumps(traits_test), headers=headers)
    #     self.assertEquals(InstructorTraits.query.filter_by(instructor_name="Anany Levitin").filter_by(trait_id=1).first().count, 3)

    # # CourseTrait tests ------------------------------------------------------------
    # def testAddCourseTraits(self):
    #     trait_record = CourseTrait(description="Challenging")
    #     db.session.add(trait_record)
    #     db.session.commit()
    #     self.assertIsNotNone(CourseTrait.query.get(1))

    # def testGetNonExistantCourseTrait(self):
    #     self.assertIsNone(CourseTrait.query.get(5))

    # def testAddTraitToCourse(self):
    #     # Add course to db
    #     course_record = Course(name="Analysis of Algorithms")
    #     db.session.add(course_record)
    #     db.session.commit()
    #     self.assertIsNotNone(Course.query.filter_by(name="Analysis of Algorithms").first())

    #     #add Trait to db
    #     trait_record = CourseTrait(description="Challenging")
    #     db.session.add(trait_record)
    #     db.session.commit()
    #     self.assertIsNotNone(CourseTrait.query.get(1))

    #     # Add trait to course
    #     course_trait_record = CourseTraits(course_name="Analysis of Algorithms", trait_id=trait_record.id, count=0)
    #     db.session.add(course_trait_record)
    #     db.session.commit()
    #     self.assertTrue(course_record.traits)

    #     # Test Increment trait count
    #     course_trait_record.count += 1
    #     db.session.add(course_trait_record)
    #     db.session.commit()
    #     self.assertEquals(course_trait_record.count, 1)

    def tearDown(self):
        db.session.close_all()
        db.drop_all()

if __name__ == "__main__":
    unittest.main()





