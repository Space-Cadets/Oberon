import os, sys
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

student_sections = db.Table('student_sections',
                            db.Column('student_id', db.Integer, db.ForeignKey('student.id')),
                            db.Column('section_id', db.Integer, db.ForeignKey('section.id'))
                            )

class Student(db.Model):
    # SQL Alchemy Models structured like so
    id            = db.Column(db.Integer, primary_key=True) # Each table needs one of these
    email         = db.Column(db.String(), unique=True)
    first_name    = db.Column(db.String())
    last_name     = db.Column(db.String())
    password      = db.Column(db.String())
    date_created  = db.Column(db.DateTime)
    reviews       = db.relationship('Review', backref='student', lazy='dynamic')
    sections      = db.relationship('Section',
                                    secondary=student_sections,
                                    backref='students', lazy='dynamic')

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
    student_id    = db.Column(db.Integer, db.ForeignKey('student.id'))
    section_id    = db.Column(db.Integer, db.ForeignKey('section.id'))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.id'))
    class_rating  = db.Column(db.Integer)
    inst_rating   = db.Column(db.Integer)
    review_body   = db.Column(db.String(),  nullable=True)    # Nullable flag means not required

    # Establish db.relationships in class in addition to foreign keys

class Location(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())



instructor_departments = db.Table('instructor_departments',
                                  db.Column('instructor_id', db.Integer, db.ForeignKey('instructor.id')),
                                  db.Column('department_code', db.String(), db.ForeignKey('department.code')))


class Instructor(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())
    department    = db.Column(db.String()) # Needs to be a db.relationship 
    reviews       = db.relationship('Review', backref=db.backref('instructors'))
    departments   = db.relationship('Department',
                                    secondary=instructor_departments,
                                    backref=db.backref('instructors', lazy='dynamic'))

    def __init__(self, name):
        self.name = name
        #self.department = department

    def __repr__(self):
        #return '<Instructor(name=%s, department=%s)' % (self.name, self.department)
        return '<Instructor(name=%s)' % self.name

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
    reviews       = db.relationship('Review', backref=db.backref('section'))


    def __init__(self, semester, crn, start_time, end_time, days, enrollment):
        self.semester = semester
        self.crn = crn
        self.start_time = start_time
        self.end_time = end_time
        self.days = days
        self.enrollment = enrollment


class Attribute(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())

    def __init__(self, name):
        self.name = name

course_attributes = db.Table('course_attributes',
                             db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                             db.Column('attribute_id', db.Integer, db.ForeignKey('attribute.id')))

course_restrictions = db.Table('course_restrictions',
                               db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                               db.Column('restriction_id', db.Integer, db.ForeignKey('restriction.id')))

class Course(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())
    subject       = db.Column(db.String(),  nullable=True)
    subject_level = db.Column(db.String(),  nullable=True)
    description   = db.Column(db.String(),  nullable=True)
    credits       = db.Column(db.Integer, nullable=True)
    prerequisites = db.Column(db.String(),  nullable=True)
    restrictions  = db.relationship('Restriction',
                                    secondary=course_restrictions,
                                    #primaryjoin=("course_restrictions.c.course_id==id"),
                                    backref=db.backref('courses', lazy='dynamic'))

    def __init__(self, name, subject, subject_level):
            self.name = name
            self.subject = subject
            self.subject_level = subject_level

class Restriction(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    text          = db.Column(db.String())

    def __init__(self, text):
        self.text = text
    
class Department(db.Model):
    """
    Example code: 'MAT'
    Example name: 'Mathematics'
    """
    #id   = db.Column(db.String())
    code = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())

    def __init__(self, code, name):
            self.code = code
            self.name = name
