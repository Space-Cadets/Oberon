from flask import Flask
import config
#from flask.ext.sqlalchemy import SQLAlchemy
from database.models import db

app = Flask(__name__)
app.config.from_object(config.Config)
db.init_app(app)

if __name__ == "__main__":
    db.create_all()
