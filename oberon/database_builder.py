from oberon import create_app
from mappings import departments
from models import db, Department, Instructor, Attribute, Section, Restriction, Course

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
        self.build()

    def build(self):
        for course in self.courses:
            self._add_course_data(course)

    def _add_course_data(self, course):
        department = self._get_or_create_department(course)
        instructors = self._get_or_create_instructors(course)
        attributes = self._get_or_create_attributes(course)


    def _get_or_create_department(self, course):
        department_record = Department.query.get(course.subject)
        if not department_record:
            department_record = Department(course.subject, departments[course.subject])
            db.session.add(department_record)
            print "Adding Department: \"%s\"" % course.subject
            db.session.commit()
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
            instructor_record.departments.append(self._get_or_create_department(course))
            db.session.add(instructor_record)
            db.session.commit()
            instructor_list.append(instructor_record)
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

    def _insert_all_attributes(self):
        for course in self.courses:
            for attribute in course.attributes:
                attribute_record = Attribute(attribute)
                with self.app.app_context():
                    if not Attribute.query.filter_by(name=attribute).first():
                        db.session.add(attribute_record)
                        #print "Adding \"%s\" to attributes" % attribute
                        print "Adding Attribute: \"%s\"" % attribute
                        db.session.commit()

    def _insert_all_sections(self):
        for course in self.courses:
            section_record = Section("Spring 2016", course.crn, course.start_time,
                                     course.end_time, course.days, course.enrollment)
            with self.app.app_context():
                if not Section.query.filter_by(crn=course.crn).first():
                    db.session.add(section_record)
                    print "Adding Section: \"%s-%s-%s\"" % (course.subject, course.course_number, course.section_number)
                    db.session.commit()

    def _insert_all_restrictions(self):
        for course in self.courses:
            for restriction in course.restrictions:
                restriction_record = Restriction(restriction)
                with self.app.app_context():
                    if not Restriction.query.filter_by(text=restriction).first():
                        db.session.add(restriction_record)
                        #print "Adding \"%s\" to restrictions" % restriction
                        print "Adding Restriction: \"%s\"" % restriction
                        db.session.commit()


    def _insert_all_courses(self):
        for course in self.courses:
            course_record = Course(course.course_name, course.subject, course.course_number)
            with self.app.app_context():
                if not Course.query.filter_by(subject=course.subject).filter_by(subject_level=course.course_number).first():
                    db.session.add(course_record)
                    #print "Adding \"%s-%s\" to Courses" % (course.subject, course.course_number)
                    print "Adding Course: \"%s-%s\"" % (course.subject, course.course_number)
                    db.session.commit()
