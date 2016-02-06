import oberon
import unittest
from oberon import app
from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review, user_datastore

class OberonTestCase(unittest.TestCase):
    def setUp(self):


