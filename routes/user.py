from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    send_file,
    abort,
    request,
    current_app,
)
from flask_login import current_user, login_required
from models import User, Book, Rental, AccessRequest, DownloadRequest, db, Video
from random import sample
from sqlalchemy import func
import os
from datetime import datetime

user_bp = Blueprint("user", __name__, url_prefix="/user")

# render the search page


@user_bp.route("/discover")
@login_required
def discover():
    # Get 4 random books from the database
    popular_books = Book.query.order_by(func.random()).limit(10).all()
    all_books = Book.query.all()
    return render_template(
        "user/discover.html",
        di_active="active",
        popular_books=popular_books,
        all_books=all_books,
    )


def get_user_books(user_id):
    """Return a list of books rented by a user."""
    user = User.query.get(user_id)
    if user:
        rentals = user.rentals
        books = []
        for rental in rentals:
            book = rental.book
            date_due = str(rental.date_due - datetime.now()).split(",")[0]
            books.append(
                {
                    "id": book.id,
                    "title": book.title,
                    "author": book.author,
                    "description": book.description,
                    "cover_path": book.cover_path,
                    "file_path": book.file_path,
                    "category": book.category.name,
                    "date_due": date_due,
                    "downloadable": rental.downloadable,
                }
            )
        return books
    else:
        return None


# Render the user dashboard
@user_bp.route("/dashboard")
@login_required
def dashboard():
    access_requests = AccessRequest.query.filter_by(user_id=current_user.id).count()
    download_requests = DownloadRequest.query.filter_by(user_id=current_user.id).count()

    # get all book details in book rentals and add them to a list
    rented_books = get_user_books(current_user.id)
    total_rented_books = len(rented_books)

    # total number of books available for download
    download_count = len(
        [rental for rental in current_user.rentals if rental.downloadable]
    )

    videos = Video.query.all()
    return render_template(
        "user/dashboard.html",
        user=current_user,
        d_active="active",
        access_requests=access_requests,
        download_requests=download_requests,
        videos=videos,
        rented_books=rented_books,
        total_rented_books=total_rented_books,
        download_count=download_count,
    )


# Render the user profile page


@user_bp.route("/edit_profile")
@login_required
def user_profile():
    user = User.query.get(current_user.id)
    return render_template("user/edit_profile.html", user=user)


# Handle the user profile form submission


@user_bp.route("/edit_profile", methods=["POST"])
@login_required
def update_user_profile():
    user = current_user
    form = request.form
    current_user.name = form["name"]
    current_user.email = form["email"]
    db.session.commit()
    flash("Your profile has been updated.", "success")
    return redirect(url_for("user_profile"))


# Render the list of books requests made by the user
@user_bp.route("/requests")
@login_required
def requests():
    access_requests = AccessRequest.query.filter_by(user_id=current_user.id)
    download_requests = DownloadRequest.query.filter_by(user_id=current_user.id)
    total_requests = access_requests.count() + download_requests.count()

    return render_template(
        "user/requests.html",
        access_requests=access_requests,
        download_requests=download_requests,
        total_requests=total_requests,
        r_active="active",
    )


# Render the details of a specific book


@user_bp.route("/books/<string:id>")
@login_required
def book_details(id):
    return render_template("user/book_details.html", book=Book.query.get(id), di_active="active")


# Render the page to read the book online
@user_bp.route("/books/<string:id>/read", methods=["GET"])
@login_required
def read_book(id):
    # Get the currently logged in user
    user = User.query.get(current_user.id)

    # Check if the user has permission to download the book
    rented = Rental.query.filter_by(book_id=id, user_id=user.id).first()
    if not rented:
        abort(403, "You don't have permission to read this book")

    # Get the book object
    book = Book.query.get(id)
    if not book:
        abort(404, "Book not found")

    # Render the book reader page
    return render_template("user/read_book.html", book=book)


# Handle the request to download a specific book
@user_bp.route("/books/<string:id>/download-request", methods=["POST"])
@login_required
def request_download(id):
    book = Book.query.get(id)
    download_request = DownloadRequest(user_id=current_user.id, book_id=book.id)
    db.session.add(download_request)
    db.session.commit()
    flash("Your request to download this book has been submitted.", "success")
    return redirect(url_for("user.dashboard", id=id))


# Handle the download of a specific book
@user_bp.route("/books/<string:id>/download")
@login_required
def download_book(id):
    # Get the currently logged in user
    user = User.query.get(current_user.id)

    # Check if the user has permission to download the book
    book_download = Rental.query.filter_by(book_id=id, user_id=user.id).first()
    if not book_download.downloadable:
        abort(403, "You don't have permission to download this book")

    # Get the book object
    book = Book.query.get(id)
    if not book:
        abort(404, "Book not found")

    file_path = file_path = os.path.join(
        current_app.root_path, "static/books", book.file_path
    )

    # Serve the book file to the user's browser
    return send_file(file_path, as_attachment=True, download_name=f"{book.title}.pdf")


# Handle the access request for specific book
@user_bp.route("/books/<string:id>/request-access", methods=["GET", "POST"])
@login_required
def request_access(id):
    book = Book.query.get(id)
    access_request = AccessRequest(user_id=current_user.id, book_id=book.id)
    db.session.add(access_request)
    db.session.commit()
    message = f'Your request to access "{book.title}" has been submitted.'
    return message


# Render the page to watch a specific video online
@user_bp.route("/videos/<string:id>/watch", methods=["GET"])
@login_required
def watch_video(id):
    # Get the currently logged in user
    user = User.query.get(current_user.id)

    # Get the video object
    video = Video.query.get(id)
    if not video:
        abort(404, "Video not found")

    # Render the book reader page
    return render_template("user/watch_video.html", video=video)
