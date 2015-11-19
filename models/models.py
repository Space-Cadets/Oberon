#from flask import flask
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()

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


