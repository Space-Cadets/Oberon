from oberon import db
from mappings import departments

class DatabaseBuilder(object):
    """
    Builds the initial database from a list of courses
    """


    def __init__(self, courses):
        """
        Courses is a list of course objects
        """
        self.courses = courses
        #for course in self.courses:
            #print course
        #self._insert_all_instructors()
        self._insert_departments()

    def build(self):
        pass


    def _insert_all_instructors(self):
        for course in self.courses:
            for instructor in course.instructor:
                instructor_record = Instructor(instructor, course.subject)
                db.session.add(instructor_record)
                db.session.commit()


    def _insert_departments(self):
        for course in self.courses:
            try:
                test = departments[course.subject]
            except KeyError as e:
                print course.__dict__
