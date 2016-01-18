from scraper import NovaCourseScraper
from database_builder import DatabaseBuilder

if __name__ == '__main__':
    spring16 = NovaCourseScraper()
    spring16.scrape_html('output2.html')
    courses = spring16.courses
    builder = DatabaseBuilder(courses)
    builder.build()
    
