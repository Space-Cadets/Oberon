from scrapers.bulk_course_scraper import NovaCourseScraper
from database.database_builder import DatabaseBuilder

if __name__ == '__main__':
    spring16 = NovaCourseScraper()
    spring16.scrape_html('test_html/output2.html')
    courses = spring16.courses
    builder = DatabaseBuilder(courses)
