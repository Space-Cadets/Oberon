import os, sys
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

student_sections = db.Table('student_sections',
                            db.Column('student', db.String(), db.ForeignKey('student.email')),
                            db.Column('section_crn', db.Integer, db.ForeignKey('section.crn'))
                            )

class Student(db.Model):
    # SQL Alchemy Models structured like so
    email         = db.Column(db.String(), primary_key=True)
    first_name    = db.Column(db.String())
    last_name     = db.Column(db.String())
    password      = db.Column(db.String())
    date_created  = db.Column(db.DateTime)
    #reviews       = db.relationship('Review', backref='student', lazy='dynamic')
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

    id              = db.Column(db.Integer, primary_key=True)
    class_rating    = db.Column(db.Integer)
    inst_rating     = db.Column(db.Integer)
    review_body     = db.Column(db.String(),  nullable=True)    # Nullable flag means not required
    date_created    = db.Column(db.DateTime)

    student_email   = db.Column(db.String(), db.ForeignKey('student.email'))
    student         = db.relationship('Student', backref=db.backref('reviews'))
    instructor_name = db.Column(db.String(), db.ForeignKey('instructor.name'))
    section_crn     = db.Column(db.Integer, db.ForeignKey('section.crn'))
    instructor      = db.relationship('Instructor', backref=db.backref('reviews'))
    section         = db.relationship('Section', backref=db.backref('reviews'))

    def __init__(self, class_rating, inst_rating, review_body):
        #self.student = student
        self.class_rating = class_rating
        self.inst_rating = inst_rating
        self.review_body = review_body

    # Establish db.relationships in class in addition to foreign keys

instructor_departments = db.Table('instructor_departments',
                                  db.Column('instructor', db.String(), db.ForeignKey('instructor.name')),
                                  db.Column('department_code', db.String(), db.ForeignKey('department.code')))


class Instructor(db.Model):

    name          = db.Column(db.String(), primary_key=True)
    #reviews       = db.relationship('Review', backref=db.backref('instructors'))
    departments   = db.relationship('Department',
                                    secondary=instructor_departments,
                                    backref=db.backref('instructors', lazy='dynamic'))

    def __init__(self, name):
        self.name = name
        #self.department = department

    def __repr__(self):
        #return '<Instructor(name=%s, department=%s)' % (self.name, self.department)
        return '<Instructor(name=%s, departments=%s)' % (self.name, str([department.code for department in self.departments]))

instructor_sections = db.Table('instructor_sections',
                               db.Column('instructor', db.String(), db.ForeignKey('instructor.name')),
                               db.Column('section_crn', db.Integer, db.ForeignKey('section.crn')))

class Section(db.Model):

    crn           = db.Column(db.Integer, primary_key = True)
    semester      = db.Column(db.String())
    location      = db.Column(db.String(), nullable=True)
    start_time    = db.Column(db.String(),  nullable=True)
    end_time      = db.Column(db.String(),  nullable=True)
    days          = db.Column(db.String(),  nullable=True)
    enrollment    = db.Column(db.String(),  nullable=True)
    course_id     = db.Column(db.Integer, db.ForeignKey('course.id'))

    
    course        = db.relationship('Course', backref=db.backref('sections'))
    #reviews       = db.relationship('Review', backref=db.backref('section'))
    instructors   = db.relationship('Instructor',
                                    secondary=instructor_sections,
                                    backref=db.backref('sections', lazy='dynamic'))




    def __init__(self, semester, crn, start_time, end_time, days, enrollment):
        self.semester = semester
        self.crn = crn
        self.start_time = start_time
        self.end_time = end_time
        self.days = days
        self.enrollment = enrollment

    def __repr__(self):
        return '<Section(crn=%s)>' % self.crn


class Attribute(db.Model):

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String())

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Attribute(name=%s)>' % self.name

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
    department_id = db.Column(db.String(), db.ForeignKey('department.code'))
    subject_level = db.Column(db.String(),  nullable=True)
    description   = db.Column(db.String(),  nullable=True)
    credits       = db.Column(db.Integer, nullable=True)
    prerequisites = db.Column(db.String(),  nullable=True)
    department    = db.relationship('Department', backref=db.backref('courses'))
    attributes    = db.relationship('Attribute',
                                    secondary=course_attributes,
                                    backref=db.backref('courses', lazy='dynamic'))
    restrictions  = db.relationship('Restriction',
                                    secondary=course_restrictions,
                                    #primaryjoin=("course_restrictions.c.course_id==id"),
                                    backref=db.backref('courses', lazy='dynamic'))

    def __init__(self, name, subject, subject_level):
            self.name = name
            self.subject = subject
            self.subject_level = subject_level
            #self.description = description

    def __repr__(self):
        return '<Course(name=%s, subject=%s, subject_level=%s)>' % (self.name, self.subject, self.subject_level)

class Restriction(db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    text          = db.Column(db.String())

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return '<Restriction(text=%s)>' % self.text
    
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

    def __repr__(self):
        return "<Department(code=%s, name=%s)>" % (self.code, self.name)
