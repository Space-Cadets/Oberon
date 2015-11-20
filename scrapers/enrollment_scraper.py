import urllib2
import re

# Other Imports
from bs4 import BeautifulSoup

class Enrollment(object):

    def __init__(self, crn, count):
        self.crn   = crn
        self.count = count


    def __str__(self):
        return "{0} : {1}".format(self.crn, self.count)


class EnrollmentScraper(object):

    def __init__(self):
        self.courses = []

    def scrape_html(self, filename):
        """
        Scrapes the course object from a HTML file supplied as input
        """
        print "Scraping {}".format(filename)
        course_page  = BeautifulSoup(open('{}'.format(filename)), 'html.parser')
        self.courses = self._create_course_objects(course_page)

    def scrape_request(self, request):
        """
        Scrapes the course object from a live request which is supplied as input
        """
        course_page  = BeautifulSoup(request.text)
        self.courses = self._create_course_objects(course_page)

    def _get_course_subject_groupings(self, course_page):
        """
        Given a BS4 tag for the entire course listing, returns a list of course groupings by subject
        """
        return course_page.findAll('table', {'class': 'datadisplaytable'})

    def _get_course_tags(self, course_page):
        """
        Given a the course_page tag, return two arrays:
        an array of course headings(bs4 Tags), and an array of course descriptions(bs4 tags)
        """
        course_headings = course_page.findAll('th') # return an array of all of the course headings
        course_info     = course_page.findAll('td', {'class': 'dddefault'})

        return (course_headings, course_info)

    def _get_course_header_info(self, course_heading):
        """
        Given a course heading (bs4 Tag), string and and returns a tuple of:
          - subject            (String)
          - course number      (String)
          - section number     (String)
          - course name        (String)
          - crn                (String)
          - enrollment         (String)

        >>> _get_course_header_info(course_heading) -- my boy levitin as an example

        stringified -> u'CSC 1700 - 001 Analysis of Algorithms CRN: 22966 Enrollment: FULL 29 students.'
        returns -> ('CSC', '1700', '001', 'Analysis of Algorithms', '22966', 'FULL 29')
        """
        match = re.match('(.*?)(\d*)( - )(\S{0,4})(.*)(CRN: )(.*)( Enrollment: )(.*) students', course_heading.text)
        if match == None:
            print "No regex match for string {}".format(course_heading.text)
            raise AttributeError

        subject        = match.group(1).strip()
        course_number  = match.group(2).strip()
        section_number = match.group(4).strip()
        course_name    = match.group(5).strip()
        crn            = match.group(7).strip()
        enrollment     = match.group(9).strip()

        return (subject, course_number, section_number, course_name, crn, enrollment)

    def _get_course_body_info(self, course_body):
        """
        Given a course info body (bs4 Tag), returns a dictionary b/c entries need further processing:

        >>> _get_course_body_info(course_info#719)
        {'attributes': None,
        'comment': None,
        'days': u'MWF from 11:30 am to 12:20 pm',
        'instructors': u'Anany Levitin',
        'location': u'TBA',
        'restrictions': u'Must be enrolled in one of the following Levels: Undergraduate May not be enrolled in one of the following Campuses: University Alliance Prerequisites: ( CSC 1300 or MAT 2600) and ( CSC 1052 or ECE 2620)'}
        """
        match = re.match(r'(?:Syllabus Available )?(Days:.*?)(Location:.*?)?(Comment:.*?)?(Instructors:.*?)?(Attributes:.*?)?(Comment:.*?)?(Restrictions:.*?)?(Prerequisites:.*)?\Z', ' '.join(course_body.text.split()))
        info_dict = {
            'days': None,
            'location': None,
            'instructors': None,
            'comment': None,
            'attributes': None,
            'restrictions': None
        }
        for re_match in match.groups():
            if re_match is not None:
                if re_match.startswith('Days:'):
                    info_dict['days'] = re_match[6:].strip()
                elif re_match.startswith('Location:'):
                    info_dict['location'] = re_match[10:].strip()
                elif re_match.startswith('Instructors:'):
                    info_dict['instructors'] = re_match[13:].strip()
                elif re_match.startswith('Comment:'):
                    info_dict['comment'] = re_match[9:].strip()
                elif re_match.startswith('Attributes:'):
                    info_dict['attributes'] = re_match[12:].strip()
                    if info_dict['attributes'] == " Core Social Science":
                        print info_dict['attributes']
                elif re_match.startswith('Restrictions:'):
                    info_dict['restrictions'] = re_match[14:].strip()
        return info_dict

    def _get_time_and_days(self, course_dict):
        """
        Takes in a dictionary of the format from _get_course_body_info and returns a tuple of:
          - days of the week
          - start time
          - end time

        if course_dict['days'] is None, returns (None, None, None)
        """
        day_and_time = course_dict['days'].replace('TBA', '').strip()

        if bool(day_and_time) == False:
            return (None, None, None)

        day_and_time_array = day_and_time.split(' ')
        
        if len(day_and_time_array) == 1:
            return (day_and_time_array[0], None, None)
        else:
            return (day_and_time_array[0], day_and_time_array[2], day_and_time_array[5])

    def _get_location(self, course_dict):
        """
        Takes in a dictionary of the format from _get_course_body_info and returns a string

        >>> _get_location(example)
        u'TBA'
        """
        return course_dict['location']

    def _get_instructors(self, course_dict):
        """
        Returns a list of the instructors of a course

        >>> _get_instructors(example)
        [u'Anany Levitin']
        """
        if course_dict['instructors'] == None:
            return []

        return [ prof.strip() for prof in course_dict['instructors'].replace('(P)', '').split(',') ]

    def _get_comment(self, course_dict):
        """
        Returns the comment information for the course.
        """
        if course_dict['comment'] == None:
            return ""
        return course_dict['comment']

    def _get_attributes(self, course_dict):
        """
        Takes in a dictionary of the format from _get_course_body_info and returns an array of strings

        >>> dict = {'attributes': 'GB Finance, GB Real Estate '}

        >>> _get_attributes(dict)
        ['GB Finance', 'GB Real Estate']
        """
        if course_dict['attributes'] == None:
            return []

        attributes = []
        attributes_no_quotes = course_dict['attributes'].split("\'") # split on quotes
        
        for attribute in attributes_no_quotes:
            if attribute == 'Eth, Econ, Public Pol Elect' or attribute == 'Ethics, Politics, Law Elect':
                attributes.append(attribute)
            else:
                attributes = attributes + attribute.split(',')
        
        return [attribute.strip() for attribute in attributes if attribute != u' ' and attribute != u'']

    def _create_course_object(self, course_heading_tag):
        """
        For one entry in the list of courses, create a course object
        """

        subject, course_number, section_number, course_name, crn, enrollment = self._get_course_header_info(course_heading_tag)

        return Enrollment(crn, enrollment)

    def _create_course_objects(self, course_page):
        """
        Insert the courses header information as dictionaries
        """
        course_objects = []
        course_headings_tags, course_info_bodies_tags = self._get_course_tags(course_page)
        
        for i in range(len(course_headings_tags)):
            course_objects.append(self._create_course_object(course_headings_tags[i]).__dict__)

        return course_objects

if __name__ == '__main__':
    enr = EnrollmentScraper()
    enr.scrape_html('output.html')
    print enr.courses
    #for c in enr.courses:
    #   print c