import os, sys
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    # SQL Alchemy Models structured like so

    id            = db.Column(db.Integer, primary_key=True) # Each table needs one of these
    email         = db.Column(db.String())
    first_name    = db.Column(db.String())
    last_name     = db.Column(db.String())
    password      = db.Column(db.String())
    date_created  = db.Column(db.DateTime)
    reviews       = db.relationship('Review', backref='student', lazy='dynamic')
    sections      = db.relationship('Section', backref='students', lazy='dynamic')

    def __init__(self, email, first_name, last_name, password):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.date_created = datetime.now()

    def __repr__(self):
        return '<Student(email=%s, name=%s %s)' % (self.email, self.first_name, self.last_name)

class Review(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    section_id    = db.Column(db.Integer, db.ForeignKey('section.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    class_rating  = db.Column(db.Integer)
    inst_rating   = db.Column(db.Integer)
    review_body   = db.Column(db.String(),  nullable=True)    # Nullable flag means not required

    # Establish db.relationships in class in addition to foreign keys

class Location(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())

class Instructor(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())
    department    = db.Column(db.String()) # Needs to be a db.relationship 
    reviews       = db.relationship('Review', backref=db.backref('reviews', lazy='dynamic'))

    def __init__(self, name, department):
        self.name = name
        self.department = department

    def __repr__(self):
        return '<Instructor(name=%s, department=%s)' % (self.name, self.department)

instructor_sections = db.Table('instructor_sections',
                               db.Column('instructor_id', db.Integer, db.ForeignKey('instructor.id')),
                               db.Column('section_id', db.Integer, db.ForeignKey('section.id')))

class Section(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    semester      = db.Column(db.String())
    crn           = db.Column(db.Integer)
    start_time    = db.Column(db.String(),  nullable=True)
    end_time      = db.Column(db.String(),  nullable=True)
    days          = db.Column(db.String(),  nullable=True)
    enrollment    = db.Column(db.String(),  nullable=True)
    reviews       = db.relationship('Review', backref=db.backref('reviews', lazy='dynamic'))

class Attribute(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())

course_attributes = db.Table('course_attributes',
                             db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                             db.Column('attribute_id', db.Integer, db.ForeignKey('attribute.id')))

class Course(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())
    subject       = db.Column(db.String(),  nullable=True)
    subject_level = db.Column(db.String(),  nullable=True)
    description   = db.Column(db.String(),  nullable=True)
    credits       = db.Column(db.Integer, nullable=True)
    prerequisites = db.Column(db.String(),  nullable=True)
    restrictions  = db.relationship('Restriction', backref=db.backref('courses', lazy='dynamic'))

course_restrictions = db.Table('course_restrictions',
                               db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                               db.Column('restriction_id', db.Integer, db.ForeignKey('restriction.id')))

class Restriction(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    text          = db.Column(db.String())

class Department(db.Model):
    code = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
