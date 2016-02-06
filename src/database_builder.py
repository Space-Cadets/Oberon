from oberon import create_app
from mappings import departments
from models import db, Department, Instructor, Attribute, Section, Restriction, Course, Student, Review
from test_users import test_users
from test_reviews import test_reviews

class DatabaseBuilder(object):
    """
    Builds the initial database from a list of courses
    """

    def __init__(self, courses):
        """
        Courses is a list of course objects
        """
        self.courses = courses
        self.app = create_app()
        self.app.app_context().push()

        self.instructors = {}
        self.departments = {}
        self.course_names = {}
        self.crns = {}

        self.num_courses = 0
        self.num_new_courses = 0
        self.num_instructors = 0
        self.num_new_instructors = 0
        self.num_departments = 0
        self.num_new_departments = 0
        self.num_sections = 0
        self.num_new_sections = 0

    def build(self):
        for course in self.courses:
            self._add_course_data(course)
        self.print_status()
        self.add_users()
        self.add_reviews()

    def print_status(self):
        print "Summary for Courses parsed"
        print "Total number of courses: %s" % self.num_courses
        print "Total number of sections: %s" % self.num_sections
        print "Total number of departments: %s" % self.num_departments
        print "Total number of instructors: %s" %self.num_instructors
        print "------------------------------------------------------------------"
        print "Number of new courses: %s" % self.num_new_courses
        print "Number of new sections: %s" % self.num_new_sections
        print "Number of new instructors: %s" % self.num_new_instructors
        print "Number of new departments: %s" % self.num_new_departments

    def _add_course_data(self, course):
        department = self._get_or_create_department(course)
        instructors = self._get_or_create_instructors(course)
        attributes = self._get_or_create_attributes(course)
        restrictions = self._get_or_create_restrictions(course)
        section = self._get_or_create_section(course, instructors)
        course = self._get_or_create_course(course, department, instructors, attributes, restrictions, section)


    def _get_or_create_department(self, course):
        department_record = Department.query.get(course.subject)
        if not department_record:
            department_record = Department(course.subject, departments[course.subject])
            db.session.add(department_record)
            print "Adding Department: \"%s\"" % course.subject
            db.session.commit()
            self.num_new_departments += 1
        if course.subject not in self.departments:
            self.departments
            self.num_departments += 1
            self.departments[course.subject] = True
        return department_record

    def _get_or_create_instructors(self, course):
        """
        Adds an instructor to the database or returns the record for that instructor
        Also adds department to an instructor record
        """
        instructor_list = []
        for instructor in course.instructor:
            instructor_record = Instructor.query.filter_by(name=instructor).first()
            if not instructor_record:
                instructor_record = Instructor(instructor)
                print "Adding Instructor: \"%s\"" % instructor
                self.num_new_instructors += 1
            instructor_record.departments.append(self._get_or_create_department(course))
            db.session.add(instructor_record)
            db.session.commit()
            instructor_list.append(instructor_record)
            if instructor not in self.instructors:
                self.num_instructors += 1
                self.instructors[instructor] = True
        return instructor_list

    def _get_or_create_attributes(self, course):
        attribute_list = []
        for attribute in course.attributes:
            attribute_record = Attribute.query.filter_by(name=attribute).first()
            if not attribute_record:
                attribute_record = Attribute(attribute)
                print "Adding Attribute: \"%s\"" % attribute
                db.session.add(attribute_record)
                db.session.commit()
            attribute_list.append(attribute_record)
        return attribute_list

    def _get_or_create_restrictions(self, course):
        restriction_list = []
        for restriction in course.restrictions:
            restriction_record = Restriction.query.filter_by(text=restriction).first()
            if not restriction_record:
                restriction_record = Restriction(restriction)
                print "Adding Restriction: \"%s\"" % restriction
                db.session.add(restriction_record)
                db.session.commit()
            restriction_list.append(restriction_record)
        return restriction_list

    def _get_or_create_section(self, course, instructors):
        section_record = Section.query.filter_by(crn=course.crn).first()
        if not section_record:
            section_record = Section("Spring 2015", course.crn, course.start_time,
                                     course.end_time, course.days, course.enrollment)
            print "Adding Section: \"%s\"" % course.crn
            self.num_new_sections += 1
        section_record.instructors = instructors
        db.session.add(section_record)
        db.session.commit()
        if course.crn not in self.crns:
            self.num_sections += 1
            self.crns[course.crn] = True
        return section_record

    def _get_or_create_course(self, course, department, instructors, attributes, restrictions, section):
        course_record = Course.query.filter_by(name=course.course_name).first()
        if not course_record:
            course_record = Course(course.course_name, course.subject, course.course_number)
            print "Adding Course: \"%s-%s\"" % (course.subject, course.course_number)
            self.num_new_courses += 1
        if course.course_name not in self.course_names:
            self.num_courses += 1
            self.course_names[course.course_name] = True
        course_record.department = department
        course_record.attributes = attributes
        course_record.restrictions = restrictions
        course_record.sections.append(section)
        db.session.add(course_record)
        db.session.commit()
        return course_record

    def add_users(self):
        print "Adding users"
        for user in test_users:
            student_record = Student.query.filter_by(email=user['email']).first()
            if not student_record:
                student_record = Student(user['email'], user['first_name'], user['last_name'], user['password'])
                print "Added student: %s" % user['email']
                db.session.add(student_record)
                db.session.commit()
            else:
                print "Student %s already exists" % user['email']

    def add_reviews(self):
        print "Adding Reviews"
        for review in test_reviews:
            print "Adding review: %s, %s" % (review['student'], review['section'])
            review_record = Review(review['student'], review['class_rating'], review['inst_rating'], review['review_body'])
            student_record = Student.query.filter_by(email=review['student']).first()
            section_record = Section.query.filter_by(crn=review['section']).first()
            print section_record.instructors[0]
            student_record.reviews.append(review_record)
            section_record.reviews.append(review_record)
            section_record.instructors[0].reviews.append(review_record)
            print student_record.reviews
            print section_record.reviews
            print section_record.instructors[0].reviews
            db.session.add(review_record)
            db.session.add(student_record)
            db.session.add(section_record)
            db.session.add(section_record.instructors[0])
        db.session.commit()
