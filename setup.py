from subprocess import call
from oberon.scraper import NovaCourseScraper
from oberon.database_builder import DatabaseBuilder
from tests.context import app
from oberon import config
from oberon.models import db
app.config.from_object(config.Config)
import argparse
import os
from oberon.populate_db import populate_db

parser = argparse.ArgumentParser(description='Refresh the database (drop and recreate from courses)')
parser.add_argument('filename', help="an HTML file from which you want to build the database")
args = parser.parse_args()
print "Dropping database VillanovaCourseDB..."
db.drop_all()
print "Successfully dropped VillanovaCourseDB"
populate_db(args.filename)
