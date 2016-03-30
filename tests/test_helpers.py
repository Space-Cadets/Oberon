import unittest
import json
from .context import app
from oberon import helpers
from flask import Flask
from flask.ext.testing import TestCase
import config

from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, Role, Trait

headers = {'Content-Type': 'application/json'}

def populate_db():
    """
    Populates the database from the sample data present in oberon.sample_data
    """
    #pass
    #user_datastore.create_user(email="testuser@villanova.edu", password_hash=pwd_context.encrypt("password"))
    #user_datastore.commit()
    user_role = Role(name='user', description="Just regular guy")
    db.session.add(user_role)
    #db.session.commit()

class HelpersTestCase(TestCase):

    def create_app(self):
        app.config.from_object(config.TestingConfig)
        return app

    def setUp(self):
        db.create_all()
        populate_db()

    def testAddUser(self):
        user = helpers.add_user(db, "testuser2@villanova.edu", "firstName", "lastName", "password1")
        self.assertIsNotNone(Student.query.filter_by(email="testuser2@villanova.edu").first(), "testuser2@villanova.edu should exist")
        self.assertIsNone(Student.query.filter_by(email="DoesNotExist@villanova.edu").first(), "DoesNotExist@villanova.edu should not exist")

    def testUserExists(self):
        user = user_datastore.create_user(email="testuser@villanova.edu", first_name="first", last_name="last", password_hash="password_hash")
        user_datastore.commit()
        self.assertTrue(helpers.user_exists("testuser@villanova.edu"))
        self.assertFalse(helpers.user_exists("doesnotexist@villanova.edu"))

    def tearDown(self):
        db.session.close_all()
        db.drop_all()

