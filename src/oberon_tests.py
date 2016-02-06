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

from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore

headers = {'Content-Type': 'application/json'}

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
        user_datastore.create_user(email="testuser@villanova.edu", password_hash=pwd_context.encrypt("password"))
        user_datastore.commit()

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
        print auth_failure.json
        self.assert401(auth_failure, "Response should be a 401")

    def test_auth_wrong_password(self):
        auth_failure = self.client.post('/auth', data=json.dumps({'username': 'testuser@villanova.edu', 'password': 'wrongpass'}), headers=headers)
        self.assert401(auth_failure, "Response should be a 401")


    def tearDown(self):
        self.db.session.commit()
        self.db.drop_all()


if __name__ == "__main__":
    unittest.main()





