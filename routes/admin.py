import os
from flask import Blueprint, render_template, redirect, url_for, flash, send_file, abort, request, current_app
from flask_login import current_user, login_required
from models import User, Book, Rental,Category, BookDownload, AccessRequest, DownloadRequest, Report, db
from models import ChangePasswordForm, ProfileForm, CategoryForm, BookForm
 

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Admin Routes
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html')

# Profile Route
@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        form = ProfileForm()
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin_bp.profile'))
    else:
        return render_template('admin/profile.html')

# Reports
@admin_bp.route('/reports')
@login_required
def reports():
    reports = Report.query.all()
    return render_template('admin/reports.html', reports=reports)

# Change Password Route
@admin_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if current_user.check_password(form.old_password.data):
                current_user.password = form.new_password.data
                db.session.commit()
        flash('Password updated successfully!', 'success')
        return redirect(url_for('admin_bp.change_password'))
    else:
        return render_template('admin/change_password.html')

# Category Routes
@admin_bp.route('/categories')
@login_required
def categories():
    # get all categories from the database and pass them to the template
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
def new_category():
    if request.method == 'POST':
        form = CategoryForm()
        if form.validate_on_submit():
            category = Category(name=form.name.data, description=form.description.data)
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
        return redirect(url_for('admin_bp.categories'))
    else:
        return render_template('admin/new_category.html')

@admin_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    if request.method == 'POST':
        form = CategoryForm()
        if form.validate_on_submit():
            # Retrieve the category from the database
            category = Category.query.get(id)

            # Update the category attributes
            category.name = form.name.data
            category.description = form.description.data

            # Commit the changes to the database
            db.session.commit()
            flash('Category updated successfully!', 'success')
        return redirect(url_for('admin_bp.categories'))
    else:
        # get the category with the given id from the database and pass it to the template
        return render_template('admin/edit_category.html')

@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    # delete the category with the given id from the database
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_bp.categories'))

# Book Routes
@admin_bp.route('/books')
@login_required
def books():
    # get all books from the database and pass them to the template
    books = Book.query.all()
    return render_template('admin/books.html', books=books)

@admin_bp.route('/books/new', methods=['GET', 'POST'])
@login_required
def new_book():
    if request.method == 'POST':
        form = BookForm()
        if form.validate_on_submit():
            book = Book(title=form.title.data, description=form.description.data, author=form.author.data, category_id=form.category.data.id)
            db.session.add(book)
            db.session.commit()
            flash('Book created successfully!', 'success')
        return redirect(url_for('admin_bp.books'))
    else:
        return render_template('admin/new_book.html')

@admin_bp.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    # Retrieve the book from the database
    book = Book.query.get(id)
    if request.method == 'POST':
        form = BookForm()
        if form.validate_on_submit():

            # Update the book attributes
            book.title = form.title.data
            book.description = form.description.data
            book.author = form.author.data
            book.category_id = form.category.data.id

            # Commit the changes to the database
            db.session.commit()
            flash('Book updated successfully!', 'success')
        return redirect(url_for('admin_bp.books'))
    else:
        # get the book with the given id from the database and pass it to the template
        return render_template('admin/edit_book.html', book=book)

@admin_bp.route('/books/<int:id>/delete', methods=['POST'])
@login_required
def delete_book(id):
    # delete the book with the given id from the database
    book = Book.query.get_or_404(id)

    # delete the book's file from the filesystem
    if book.file:
        os.remove(os.path.join(current_app.root_path, 'static', book.file))

    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin_bp.books'))

# Request routes
@admin_bp.route('/requests')
@login_required
def requests():
    # get all access and download requests from the database and pass them to the template
    access_requests = AccessRequest.query.all()
    download_requests = DownloadRequest.query.all()

    return render_template('admin/requests.html', access_requests=access_requests, download_requests=download_requests)

@admin_bp.route('/grant-access-request/<int:request_id>', methods=['POST'])
@login_required
def grant_access_request(request_id):
    # grant access to the user's request with the given id
    request = AccessRequest.query.get_or_404(request_id)
    user = request.user
    book = request.book
    date_due = request.date_due

    # add the Access Request to the Rentals Table
    rental = Rental(user_id=user.id, book_id=book.id, date_due=date_due)
    db.session.add(rental)

    # delete the request from the database
    db.session.delete(request)

    # add to reports table
    report = Report(user_id=user.id, activity="Access Request Granted")
    db.session.add(report)

    # commit the changes to the database
    db.session.commit()

    return redirect(url_for('admin_bp.requests'))

@admin_bp.route('/grant-download-request/<int:request_id>', methods=['POST'])
@login_required
def grant_download_request(request_id):
    # grant download to the user's request with the given id
    request = DownloadRequest.query.get_or_404(request_id)
    user = request.user
    book = request.book

    # add the Access Request to the Rentals Table
    download = BookDownload(user_id=user.id, book_id=book.id)
    db.session.add(download)

    # delete the request from the database
    db.session.delete(request)

    # add to reports table
    report = Report(user_id=user.id, activity="Download Request Granted")
    db.session.add(report)

    # commit the changes to the database
    db.session.commit()
    
    return redirect(url_for('admin_bp.requests'))

