from flask import Blueprint, render_template, request, flash
from models import Book, Rental, db
from sqlalchemy import or_

views = Blueprint("views", __name__)


def get_popular_books():
    return (
        Book.query.join(Rental)
        .group_by(Book.id)
        .order_by(db.func.count(Rental.id).desc())
        .limit(3)
        .all()
    )


@views.route("/")
def home():
    return render_template("home.html")


@views.route("/books")
def books():
    # get popular books

    books = Book.query.all()
    return render_template("book.html", books=books, popular_books=get_popular_books())


@views.route("/search", methods=["POST"])
def search():
    search_query = request.form.get(
        "search"
    )  # Retrieve the value from the search input field

    books = Book.query.all()

    if search_query:
        # Perform the search query using a case-insensitive search on the title and author fields
        search_results = Book.query.filter(
            or_(
                Book.title.ilike(f"%{search_query}%"),
                Book.author.ilike(f"%{search_query}%"),
            )
        ).all()

    if not search_results:
        flash(f'No books matching "{search_query}" was found')

    return render_template(
        "book.html",
        search_results=search_results,
        books=books,
        popular_books=get_popular_books(),
    )
