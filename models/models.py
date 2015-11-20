#from flask import flask
from sqlalchemy import *
from sqlalchemy.engine.url import URL
import os, sys

# Relative path support -- great snippet
lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)

import private

print private.db

"""
class Student(db.Model):
    pass

class Course(db.Model):
    pass

class Section(db.Model):
    pass

class Restriction(db.Model):
    pass

class Attribute(db.Model):
    pass

class Instructor(db.Model):
    pass

class Review(db.Model):
    pass

class Semester(db.Model):
    pass

class Location(db.Model):
    pass
"""