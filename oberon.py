from flask import Flask
import config
#from flask.ext.sqlalchemy import SQLAlchemy
from database.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_app()
