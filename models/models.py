import os, sys
from sqlalchemy.engine.url      import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import relationship, backref
from sqlalchemy					import ForeignKey, Column
from sqlalchemy                 import create_engine, Integer, String, DateTime

# Relative path support -- great snippet
lib_path = os.path.abspath(os.path.join('..'))
sys.path.append(lib_path)
# You need to add db credentials
import private 

DeclarativeBase = declarative_base()

class Student(DeclarativeBase):
	# SQL Alchemy Models structured like so
	__tablename__ = "students"

	student_id    = Column(Integer, primary_key=True)
	email         = Column('email', String)
	first_name    = Column('first_name', String)
	last_name     = Column('last_name', String)
	password      = Column('phash', String)
	date_created  = Column('date_created', DateTime)

	reviews = relationship('reviews', order_by='review.id', backref='student')


class Review(DeclarativeBase):
	__tablename__ = "reviews"

	review_id     = Column(Integer, primary_key=True)
	user_id       = Column(Integer, ForeignKey('user.id'))

	student       = relationship('student', backref=backref('addresses', order_by=review_id))

class Location(DeclarativeBase):
	__tablename__ = "locations"

	location_id   = Column(Integer, primary_key=True)
	location_name = Column('location_name', String)

class Instructor(DeclarativeBase):
	__tablename__ = "instructors"

	instructor_id = Column(Integer, primary_key=True)
	title         = Column('title', String)
	department    = Column('department', String) # Needs to be a relationship 

"""
To Implement in Schema

class Section(DeclarativeBase):
	__tablename__ = "sections"

class Attribute(DeclarativeBase):
	__tablename__ = "attributes"

class Semester(DeclarativeBase):
	__tablename__ = "semester"

class Course(DeclarativeBase):
	__tablename__ = "courses"

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