from scraper import NovaCourseScraper
from database_builder import DatabaseBuilder

if __name__ == '__main__':
    fall16 = NovaCourseScraper()
    fall16.scrape_html('output2.html')
    courses = fall16.courses
    builder = DatabaseBuilder(courses)
    builder.build()
    
