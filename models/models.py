from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import random, string

def generate_id():
    """Generate an ID."""
    return ''.join(random.choice(string.digits) for _ in range(6))


db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.String, primary_key=True, default=lambda: 'USR' + generate_id())
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    rentals = db.relationship('Rental', backref='user', lazy=True)

class Category(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: 'C' + generate_id())
    name = db.Column(db.String(100), nullable=False)
    books = db.relationship('Book', backref='category', lazy=True)
    videos = db.relationship('Video', backref='category', lazy=True)

class Book(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover_path = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.String, db.ForeignKey('category.id'), nullable=False)
    rentals = db.relationship('Rental', backref='book', lazy=True)

class Video(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cover_path = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.String, db.ForeignKey('category.id'), nullable=False)


class Rental(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: 'RNT' + generate_id())
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String, db.ForeignKey('book.id'), nullable=False)
    downloadable = db.Column(db.Boolean, default=False)
    date_rented = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_due = db.Column(db.DateTime, nullable=False)

class DownloadRequest(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: 'DR' + generate_id())
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String, db.ForeignKey('book.id'), nullable=False)


class AccessRequest(db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: 'AR' + generate_id())
    user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.String, db.ForeignKey('book.id'), nullable=False)
    date_requested = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_due = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    book = db.relationship('Book', backref='access_requests')
    



    
