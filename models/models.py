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

	student_id    = Column(Integer, primary_key=True) # Each table needs one of these
	email         = Column(String)
	first_name    = Column(String)
	last_name     = Column(String)
	password      = Column(String)
	date_created  = Column(DateTime)

	# This is how to establish relationship in the ORM
	reviews = relationship('Review', order_by='review.id', backref='student')


class Review(DeclarativeBase):
	__tablename__ = "reviews"

	review_id     = Column(Integer, primary_key=True) 
	student_id    = Column(Integer, ForeignKey('student.id'))
	course_id     = Column(Integer, ForeignKey('course.id'))
	section_id    = Column(Integer, ForeignKey('section.id'))
	class_rating  = Column(Integer)
	inst_rating   = Column(Integer)                    
	instructor    = Column(String)                    # Maybe Int Foreign key
	course_name   = Column(String)
	review_body   = Column(String,  nullable=True)    # Nullable flag means not required

	# Needs relationship for tags, instructor, and course as well
	student       = relationship('Student', order_by='student.id', backref='review')
	course        = relationship('Course',  order_by='course.id',  backref='review')

class Location(DeclarativeBase):
	__tablename__ = "locations"

	location_id   = Column(Integer, primary_key=True)
	location_name = Column(String)

class Instructor(DeclarativeBase):
	__tablename__ = "instructors"

	instructor_id = Column(Integer, primary_key=True)
	title         = Column(String)
	department    = Column(String) # Needs to be a relationship 
	course_list   = Column(String) # (TODO) create join table and fix this relationship

class Section(DeclarativeBase):
	__tablename__ = "sections"

	section_id    = Column(Integer, primary_key=True)
	days          = Column(String,  nullable=True)
	enrollment    = Column(String,  nullable=True) 


class Attribute(DeclarativeBase):
	__tablename__ = "attributes"

	attribute_id  = Column(Integer, primary_key=True) 


class Course(DeclarativeBase):
	__tablename__ = "courses"

	course_id     = Column(Integer, primary_key=True) 

class Restriction(DeclarativeBase):
	__tablename__ = "restrictions"

	restiction_id = Column(Integer, primary_key=True)
	text          = Column(String)	

"""
To Implement in Schema

Veto making semester -- just do key or separate DBs with the same schema
class Semester(DeclarativeBase):
	__tablename__ = "semester"

class Restriction(DeclarativeBase):
	__tablename__ = "restrictions"
	
"""

def db_connect():
	"""
	Performs database connection using database settings from settings.py.
	Returns sqlalchemy engine instance
	"""
	return create_engine(URL(**private.db))

def create_tables(engine):
	DeclarativeBase.metadata.create_all(engine)