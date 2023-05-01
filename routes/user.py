from flask import Blueprint, render_template, redirect, url_for, flash, send_file, abort, request
from flask_login import current_user, login_required
from models import User, Book, Rental, BookDownload, AccessRequest, DownloadRequest, db, ChangePasswordForm, ProfileForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

# render the search page, if they are logged in as users set a variable logged_in to true so that the frontend can allow them to request access to a book
@user_bp.route('/search')
@login_required
def search():
    return render_template('user/search.html')


# Render the user dashboard
@user_bp.route('/')
@login_required
def user_dashboard():
    user = User.query.get(current_user.id)
    return render_template('user/dashboard.html', user=user)

# Render the user profile page
@user_bp.route('/profile')
@login_required
def user_profile():
    user = current_user
    return render_template('user/profile.html', user=user)

# Handle the user profile form submission
@user_bp.route('/profile', methods=['POST'])
@login_required
def update_user_profile():
    user = current_user
    form = ProfileForm(request.form)
    if form.validate():
        user.name = form.name.data
        user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('user_profile'))
    else:
        flash('There was an error updating your profile.', 'danger')
        return redirect(url_for('user_profile'))

# Render the change password page
@user_bp.route('/change_password')
@login_required
def change_password():
    form = ChangePasswordForm()
    return render_template('user/change_password.html', form=form)

# Handle the change password form submission
@user_bp.route('/change_password', methods=['POST'])
@login_required
def update_password():
    user = current_user
    form = ChangePasswordForm(request.form)
    if form.validate():
        if user.check_password(form.old_password.data):
            user.password = form.new_password.data
            db.session.commit()
            flash('Your password has been updated.', 'success')
            return redirect(url_for('user_profile'))
        else:
            flash('The current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))
    else:
        flash('There was an error updating your password.', 'danger')
        return redirect(url_for('change_password'))

# Render the list of books available in the E-Library
@user_bp.route('/books')
@login_required
def list_books():
    books = Book.query.all()
    return render_template('user/books.html', books=books)

# Render the details of a specific book
@user_bp.route('/books/<int:id>')
@login_required
def book_details(id):
    return render_template('user/book_details.html', book=book)

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
