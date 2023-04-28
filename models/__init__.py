from flask_sqlalchemy import SQLAlchemy

# instantiate the database object
db = SQLAlchemy()

# import all models so that they are registered with the database
from .models import User, Category, Book, Video, BookDownload, Rental
