from flask import Blueprint, render_template, redirect, url_for, flash, send_file, abort, request
from flask_login import current_user, login_required
from models import User, Book, Rental, BookDownload, AccessRequest, DownloadRequest, db, ChangePasswordForm, ProfileForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

# render the search page
@user_bp.route('/discover')
@login_required
def search():
    # get the most popular books from the database
    popular_books = Book.query.join(Rental).group_by(Book.id).order_by(db.func.count(Rental.id).desc()).limit(10).all()


    return render_template('user/discover.html',di_active="active")


# Render the user dashboard
@user_bp.route('/dashboard')
@login_required
def user_dashboard():
    user = User.query.get(current_user.id)
    return render_template('user/dashboard.html', user=user, d_active="active")

# Render the user profile page
@user_bp.route('/edit_profile')
@login_required
def user_profile():
    user = User.query.get(current_user.id)
    return render_template('user/edit_profile.html', user=user, d_active="active")

# Handle the user profile form submission
@user_bp.route('/edit_profile', methods=['POST'])
@login_required
def update_user_profile():
    user = current_user
    form = request.form
    current_user.name = form['name']
    current_user.email = form['email']
    db.session.commit()
    flash('Your profile has been updated.', 'success')
    return redirect(url_for('user_profile'))
    

# Render the list of books requests made by the user
@user_bp.route('/requests')
@login_required
def list_requests():
    access_requests = AccessRequest.query.filter_by(user_id=current_user.id)
    download_requests = DownloadRequest.query.filter_by(user_id=current_user.id)
    return render_template('user/requests.html', access_requests=access_requests, download_requests=download_requests)

# Render the details of a specific book
@user_bp.route('/books/<int:id>')
@login_required
def book_details(id):
    return render_template('user/book_details.html', book=Book.query.get(id), di_active="active")



# Render the page to read the book online
@user_bp.route('/books/<int:id>/read')
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
    return render_template('user/read_book.html', book=book)


# Handle the request to download a specific book
@user_bp.route('/books/<int:id>/download-request', methods=['POST'])
@login_required
def request_download(id):
    book = Book.query.get(id)
    download_request = DownloadRequest(user_id=current_user.id, book_id=book.id)
    db.session.add(download_request)
    db.session.commit()
    flash('Your request to download this book has been submitted.', 'success')
    return redirect(url_for('book_details', id=id))

# Handle the download of a specific book
@user_bp.route('/books/<int:id>/download')
@login_required
def download_book(id):
    # Get the currently logged in user
    user = User.query.get(current_user.id)
    
    # Check if the user has permission to download the book
    book_download = BookDownload.query.filter_by(book_id=id, user_id=user.id).first()
    if not book_download:
        abort(403, "You don't have permission to download this book")
    
    # Get the book object
    book = Book.query.get(id)
    if not book:
        abort(404, "Book not found")
    
    # Serve the book file to the user's browser
    return send_file(book.file_path, as_attachment=True, attachment_filename=book.title)


# Handle the access request for specific book
@user_bp.route('/books/<int:id>/request-access', methods=['POST'])
@login_required
def request_access(id):
    book = Book.query.get(id)
    access_request = AccessRequest(user_id=current_user.id, book_id=book.id)
    db.session.add(access_request)
    db.session.commit()
    flash('Your request to access this book has been submitted.', 'success')
    return redirect(url_for('book_details', id=id))



# Render the page to watch a specific video online
@user_bp.route('/videos/<int:id>/watch')
@login_required
def watch_video(id):
    # Get the currently logged in user
    user = User.query.get(current_user.id)
    
    # Get the video object
    video = Book.query.get(id)
    if not video:
        abort(404, "Video not found")

    # Render the book reader page
    return render_template('user/watch_video.html', video=video)
