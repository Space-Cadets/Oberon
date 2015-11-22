from oberon import create_app
from mappings import departments
from database.models import db, Department, Instructor

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
        #self._insert_all_instructors()
        #self._insert_departments()

    def build(self):
        pass


    def _insert_all_instructors(self):
        for course in self.courses:
            for instructor in course.instructor:
                instructor_record = Instructor(instructor)
                with self.app.app_context():
                    if not Instructor.query.filter_by(name=instructor).first():
                        db.session.add(instructor_record)
                        print "Adding %s to instructors" % instructor
                        db.session.commit()


    def _insert_departments(self):
        for course in self.courses:
            department_record = Department(course.subject, departments[course.subject])
            with self.app.app_context():
                if not Department.query.get(course.subject):
                    db.session.add(department_record)
                    print "Adding %s to Departments" % course.subject
                    db.session.commit()

    
