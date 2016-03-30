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

from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore, Role, Trait

headers = {'Content-Type': 'application/json'}

class AuthTestCase(TestCase):

    def create_app(self):
        app.config.from_object(config.TestingConfig)
        return app

    def setUp(self):
        db.create_all()
        user = user_datastore.create_user(email="testuser@villanova.edu", first_name="first", last_name="last", password_hash=pwd_context.encrypt("password"))
        user_datastore.commit()

    def tearDown(self):
        db.session.close_all()
        db.drop_all()

    def test_auth_success(self):
        auth_success = self.client.post('/auth', data=json.dumps({'username': 'testuser@villanova.edu', 'password': 'password'}), headers=headers)
        self.assert200(auth_success, "Response should be a 200")
        self.assertIsNotNone(auth_success.json.get('access_token'), "/auth auth_success should return access token on user verification")

    def test_auth_user_does_not_exist(self):
        auth_failure = self.client.post('/auth', data=json.dumps({'username': 'doesnotexist@villanova.edu', 'password': 'test'}), headers=headers)
        self.assert401(auth_failure, "Response should be a 401")

    def test_auth_wrong_password(self):
        auth_failure = self.client.post('/auth', data=json.dumps({'username': 'testuser@villanova.edu', 'password': 'wrongpass'}), headers=headers)
        self.assert401(auth_failure, "Response should be a 401")

