import os, sys
from sqlalchemy.engine.url      import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import relationship, backref
from sqlalchemy					import ForeignKey, Column
from sqlalchemy                 import create_engine, Integer, String, DateTime


# Relative path support -> great snippet
lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)
# You need to add db credentials
import private 

DeclarativeBase = declarative_base()

class Student(DeclarativeBase):
	# SQL Alchemy Models structured like so
	__tablename__ = "students"

	id            = Column(Integer, primary_key=True) # Each table needs one of these
	email         = Column(String)
	first_name    = Column(String)
	last_name     = Column(String)
	password      = Column(String)
	date_created  = Column(DateTime)

	# This is how to establish relationship in the ORM
	reviews = relationship('Review', order_by='review.id', backref='student')


class Review(DeclarativeBase):
	__tablename__ = "reviews"

	id            = Column(Integer, primary_key=True)
	course_id     = Column(Integer, ForeignKey('courses.id'))
	section_id    = Column(Integer, ForeignKey('sections.id'))
	student_id    = Column(Integer, ForeignKey('students.id'))
	instructor_id = Column(Integer, ForeignKey('instructors.id'))
	class_rating  = Column(Integer)
	inst_rating   = Column(Integer)                    
	review_body   = Column(String,  nullable=True)    # Nullable flag means not required

	# Establish relationships in class in addition to foreign keys
	student       = relationship('Student',    order_by='students.id',    backref='review')
	course        = relationship('Course',     order_by='courses.id',     backref='review')
	section       = relationship('Section',    order_by='sections.id',    backref='review')
	instructor    = relationship('Instructor', order_by='instructors.id', backref='review')

class Location(DeclarativeBase):
	__tablename__ = "locations"

	id            = Column(Integer, primary_key=True)
	name          = Column(String)

class Instructor(DeclarativeBase):
	__tablename__ = "instructors"

	id            = Column(Integer, primary_key=True)
	title         = Column(String)
	department    = Column(String) # Needs to be a relationship 
	course_list   = Column(String) # (TODO) create join table and fix this relationship

class Section(DeclarativeBase):
	__tablename__ = "sections"

	id            = Column(Integer, primary_key=True)
	crn           = Column(Integer)
	days          = Column(String,  nullable=True)
	enrollment    = Column(String,  nullable=True) 


class Attribute(DeclarativeBase):
	__tablename__ = "attributes"

	id            = Column(Integer, primary_key=True)
	name          = Column(String)


class Course(DeclarativeBase):
	__tablename__ = "courses"

	id            = Column(Integer, primary_key=True)
	name          = Column(String)
	number        = Column(String) # Ex. VSB 1000


class Restriction(DeclarativeBase):
	__tablename__ = "restrictions"

	id            = Column(Integer, primary_key=True)
	text          = Column(String)	

class CourseRestriction(DeclarativeBase):
	__tablename__ = "course_restrictions"

	id            = Column(Integer, primary_key=True)
	course_id     = Column(Integer, ForeignKey('courses.id'))	
	restiction_id = Column(Integer, ForeignKey('restrictions.id'))


class CourseAttribute(DeclarativeBase):
	__tablename__ = "course_attributes"

	id            = Column(Integer, primary_key=True)
	course_id     = Column(Integer, ForeignKey('courses.id'))	
	attribute_id  = Column(Integer, ForeignKey('attributes.id'))

class InstructorSection(DeclarativeBase):
	__tablename__ = "instructor_sections"

	id            = Column(Integer, primary_key=True)
	course_id     = Column(Integer, ForeignKey('courses.id'))	
	restiction_id = Column(Integer, ForeignKey('restrictions.id'))


def db_connect():
	"""
	Performs database connection using database settings from settings.py.
	Returns sqlalchemy engine instance
	"""
	return create_engine(URL(**private.db))

def create_tables(engine):
	DeclarativeBase.metadata.create_all(engine)

if __name__ == '__main__':
	myengine = db_connect()
	create_tables(myengine)