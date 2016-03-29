from scraper import NovaCourseScraper
from database_builder import DatabaseBuilder
    
def populate_db(html_file):
    semester_courses = NovaCourseScraper()
    semester_courses.scrape_html(html_file)
    courses = semester_courses.courses
    builder = DatabaseBuilder(courses)
    builder.build()

if __name__ == '__main__':
    fall16 = NovaCourseScraper()
    fall16.scrape_html('output2.html')
    courses = fall16.courses
    builder = DatabaseBuilder(courses)
    builder.build()

