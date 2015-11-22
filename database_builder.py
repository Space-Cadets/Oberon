from oberon import create_app
from mappings import departments
from database.models import db, Department, Instructor, Attribute, Section, Restriction, Course

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
        self.build()

    def build(self):
        self._insert_all_instructors()
        self._insert_all_departments()
        self._insert_all_attributes()
        self._insert_all_sections()
        self._insert_all_restrictions()
        self._insert_all_courses()

    def _insert_all_instructors(self):
        for course in self.courses:
            for instructor in course.instructor:
                instructor_record = Instructor(instructor)
                with self.app.app_context():
                    if not Instructor.query.filter_by(name=instructor).first():
                        db.session.add(instructor_record)
                        print "Adding \"%s\" to instructors" % instructor
                        db.session.commit()

    def _insert_all_departments(self):
        for course in self.courses:
            department_record = Department(course.subject, departments[course.subject])
            with self.app.app_context():
                if not Department.query.get(course.subject):
                    db.session.add(department_record)
                    print "Adding \"%s\" to Departments" % course.subject
                    db.session.commit()

    def _insert_all_attributes(self):
        for course in self.courses:
            for attribute in course.attributes:
                attribute_record = Attribute(attribute)
                with self.app.app_context():
                    if not Attribute.query.filter_by(name=attribute).first():
                        db.session.add(attribute_record)
                        print "Adding \"%s\" to attributes" % attribute
                        db.session.commit()

    def _insert_all_sections(self):
        for course in self.courses:
            section_record = Section("Spring 2016", course.crn, course.start_time,
                                     course.end_time, course.days, course.enrollment)
            with self.app.app_context():
                if not Section.query.filter_by(crn=course.crn).first():
                    db.session.add(section_record)
                    print "Adding \"%s-%s-%s\" to sections" % (course.subject, course.course_number, course.section_number)
                    db.session.commit()

    def _insert_all_restrictions(self):
        for course in self.courses:
            for restriction in course.restrictions:
                restriction_record = Restriction(restriction)
                with self.app.app_context():
                    if not Restriction.query.filter_by(text=restriction).first():
                        db.session.add(restriction_record)
                        print "Adding \"%s\" to restrictions" % restriction
                        db.session.commit()


    def _insert_all_courses(self):
        for course in self.courses:
            course_record = Course(course.course_name, course.subject, course.course_number)
            with self.app.app_context():
                if not Course.query.filter_by(subject=course.subject).filter_by(subject_level=course.course_number).first():
                    db.session.add(course_record)
                    print "Adding \"%s-%s\" to Courses" % (course.subject, course.course_number)
                    db.session.commit()
