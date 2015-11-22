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
    section_id    = db.Column(db.Integer, db.ForeignKey('sections.id'))
    student_id    = db.Column(db.Integer, db.ForeignKey('students.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'))
    class_rating  = db.Column(db.Integer)
    inst_rating   = db.Column(db.Integer)
    review_body   = db.Column(db.String(),  nullable=True)    # Nullable flag means not required

    # Establish db.relationships in class in addition to foreign keys
    student       = db.relationship('Student',    order_by='students.id',    backref='review')
    section       = db.relationship('Section',    order_by='sections.id',    backref='review')
    instructor    = db.relationship('Instructor', order_by='instructors.id', backref='review')

class Location(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())

class Instructor(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())
    department    = db.Column(db.String()) # Needs to be a db.relationship 

    def __init__(self, name, department):
        self.name = name
        self.department = department

    def __repr__(self):
        return '<Instructor(name=%s, department=%s)' % (self.name, self.department)

class InstructorSection(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    course_id     = db.Column(db.Integer, db.ForeignKey('courses.id'))    
    restiction_id = db.Column(db.Integer, db.ForeignKey('restrictions.id'))

class Section(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    semester      = db.Column(db.String())
    crn           = db.Column(db.Integer)
    start_time    = db.Column(db.String(),  nullable=True)
    end_time      = db.Column(db.String(),  nullable=True)
    days          = db.Column(db.String(),  nullable=True)
    enrollment    = db.Column(db.String(),  nullable=True)

class Attribute(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())

class CourseAttribute(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    course_id     = db.Column(db.Integer, db.ForeignKey('courses.id'))	
    attribute_id  = db.Column(db.Integer, db.ForeignKey('attributes.id'))

    course        = db.relationship('Course',  order_by='courses.id',  backref='course_attributes')
    section       = db.relationship('Section', order_by='sections.id', backref='course_attributes')

class Course(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())
    subject       = db.Column(db.String(),  nullable=True)
    subject_level = db.Column(db.String(),  nullable=True)
    description   = db.Column(db.String(),  nullable=True)
    credits       = db.Column(db.Integer, nullable=True)
    prerequisites = db.Column(db.String(),  nullable=True)

class CourseRestriction(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    course_id     = db.Column(db.Integer, db.ForeignKey('courses.id'))
    restiction_id = db.Column(db.Integer, db.ForeignKey('restrictions.id'))

    course        = db.relationship('Course',  order_by='courses.id',  backref='course_restrictions')
    restriction   = db.relationship('Section', order_by='sections.id', backref='course_restrictions')

class Restriction(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    text          = db.Column(db.String())
