import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from functools import wraps
from flask_login import current_user, login_required
from models import User, Book, Video, Rental, Category, BookDownload, AccessRequest, DownloadRequest, db
from models import ChangePasswordForm, ProfileForm, CategoryForm, BookForm, VideoForm
from datetime import datetime, timedelta
 

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


def isAdmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return decorated_function

# Admin Routes
@admin_bp.route('/dashboard')
@login_required
@isAdmin
def dashboard():
    return render_template('admin/dashboard.html', d_active="active")

# Profile Route
@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@isAdmin
def profile():
    if request.method == 'POST':
        form = ProfileForm()
        if form.validate_on_submit():
            current_user.name = form.name.data
            current_user.email = form.email.data
            db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('admin.profile'))
    else:
        return render_template('admin/edit_profile.html', d_active="active")

# Reports
@admin_bp.route('/reports')
@login_required
@isAdmin
def reports():
    # do some data analysis using the existing database and generate some key statistics

    # Most Popular Books
    popular_books = Book.query.join(Rental).group_by(Book.id).order_by(db.func.count(Rental.id).desc()).limit(10).all()

    # User Engagement
    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)
    downloads_count = BookDownload.query.filter(BookDownload.date_created >= week_ago).count()
    rentals_count = Rental.query.filter(Rental.date_rented >= week_ago).count()
    access_requests_count = AccessRequest.query.filter(AccessRequest.date_requested >= week_ago).count()

    # Most Active Users
    active_users = User.query.join(Rental).group_by(User.id).order_by(db.func.count(Rental.id).desc()).limit(10).all()

    # Categories
    categories = Category.query.all()
    categories_books_counts = [(c.name, len(c.books)) for c in categories]
    categories_videos_counts = [(c.name, len(c.videos)) for c in categories]

    # Rental Duration
    rentals_duration = Rental.query.all()
    avg_rental_duration = sum((r.date_due - r.date_rented).days for r in rentals_duration) / len(rentals_duration)

    # Total number of books, users, and rentals
    total_books = Book.query.count()
    total_users = User.query.count()
    total_rentals = Rental.query.count()

    return render_template('admin/reports.html', rep_active="active", popular_books=popular_books, downloads_count=downloads_count,
                           rentals_count=rentals_count, access_requests_count=access_requests_count,
                           active_users=active_users, categories_books_counts=categories_books_counts,
                           categories_videos_counts=categories_videos_counts, avg_rental_duration=avg_rental_duration,
                           total_books=total_books, total_users=total_users, total_rentals=total_rentals)


# Category Routes
@admin_bp.route('/categories')
@login_required
@isAdmin
def categories():
    # get all categories from the database and pass them to the template
    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories, c_active="active")

@admin_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@isAdmin
def new_category():
    if request.method == 'POST':
        form = CategoryForm()
        if form.validate_on_submit():
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            flash('Category created successfully!', 'success')
        return redirect(url_for('admin.categories'))
    else:
        return render_template('admin/new_category.html')


@admin_bp.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
@isAdmin
def delete_category(id):
    # delete the category with the given id from the database
    category = Category.query.get_or_404(id)
    db.session.delete(category)

    # delete all books and videos in the category
    for book in category.books:
        db.session.delete(book)
    for video in category.videos:
        db.session.delete(video)

    db.session.commit()
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin_bp.categories'))

# Book Routes
@admin_bp.route('/books')
@login_required
@isAdmin
def books():
    # get all books from the database and pass them to the template
    books = Book.query.all()
    return render_template('admin/books.html', books=books)

@admin_bp.route('/books/new', methods=['GET', 'POST'])
@login_required
@isAdmin
def new_book():
    if request.method == 'POST':
        form = BookForm()
        if form.validate_on_submit():
            book = Book(title=form.title.data, description=form.description.data, author=form.author.data, category_id=form.category.data.id)
            db.session.add(book)
            

            # upload book cover and book file (pdf)
            if form.cover.data:
                cover_filename = f'cover_{book.id}.jpg'
                cover_path = os.path.join(current_app.root_path, 'static/images/covers', cover_filename)
                form.cover.data.save(cover_path)
                book.cover_path = cover_path

            if form.file.data:
                file_filename = f'book_{book.id}.pdf'
                file_path = os.path.join(current_app.root_path, 'static/books', file_filename)
                form.file.data.save(file_path)
                book.file_path = file_path
            
            db.session.commit()
            flash('Book created successfully!', 'success')
        return redirect(url_for('admin.books'))
    else:
        return render_template('admin/new_book.html', b_active="active")

@admin_bp.route('/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@isAdmin
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

            # Update book cover photo
            if form.cover.data:
                # delete former cover 
                if book.cover_path:
                    os.remove(book.cover_path)

                cover_filename = f'cover_{book.id}.jpg'
                cover_path = os.path.join(current_app.root_path, 'static/images/covers', cover_filename)
                form.cover.data.save(cover_path)
                book.cover_path = cover_path

            # Commit the changes to the database
            db.session.commit()
            flash('Book updated successfully!', 'success')
        return redirect(url_for('admin.books'))
    else:
        # get the book with the given id from the database and pass it to the template
        return render_template('admin/edit_book.html', book=book, b_active="active")

@admin_bp.route('/books/<int:id>/delete', methods=['POST'])
@login_required
@isAdmin
def delete_book(id):
    # delete the book with the given id from the database
    book = Book.query.get_or_404(id)

    # delete the book cover
    if book.cover_path:
        os.remove(book.cover_path)

    # delete the book's file from the filesystem
    if book.file:
        os.remove(os.path.join(current_app.root_path, 'static', book.file_path))

    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('admin.books'))

# Request routes
@admin_bp.route('/requests')
@login_required
@isAdmin
def requests():
    # get all access and download requests from the database and pass them to the template
    access_requests = AccessRequest.query.all()
    download_requests = DownloadRequest.query.all()

    return render_template('admin/requests.html', access_requests=access_requests, download_requests=download_requests, req_active="active")

@admin_bp.route('/grant-access-request/<int:request_id>', methods=['POST'])
@login_required
@isAdmin
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

    # commit the changes to the database
    db.session.commit()

    return redirect(url_for('admin.requests'))

@admin_bp.route('/grant-download-request/<int:request_id>', methods=['POST'])
@login_required
@isAdmin
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

    # commit the changes to the database
    db.session.commit()
    
    return redirect(url_for('admin.requests'))



# Video Routes

# Renders a list of all the videos
@admin_bp.route('/videos')
@login_required
@isAdmin
def videos():
    videos = Video.query.all()
    return render_template('admin/videos.html', videos=videos, v_active="active")


# Renders a form to create a new video
@admin_bp.route('/videos/new', methods=['GET', 'POST'])
@login_required
@isAdmin
def new_video():
    if request.method == 'POST':
        form = VideoForm()
        if form.validate_on_submit():
            video = Video(title=form.title.data, description=form.description.data, author=form.author.data, category_id=form.category.data.id)
            db.session.add(video)
            

            # upload video cover and video file (mp4)
            if form.cover.data:
                cover_filename = f'cover_{video.id}.jpg'
                cover_path = os.path.join(current_app.root_path, 'static/images/covers', cover_filename)
                form.cover.data.save(cover_path)
                video.cover_path = cover_path

            if form.file.data:
                file_filename = f'video_{video.id}.mp4'
                file_path = os.path.join(current_app.root_path, 'static/videos', file_filename)
                form.file.data.save(file_path)
                video.file_path = file_path
            
            db.session.commit()
            flash('Video created successfully!', 'success')
        return redirect(url_for('admin.videos'))
    else:
        return render_template('admin/new_video.html', v_active="active")
    

# Renders a form to edit a video
@admin_bp.route('/videos/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@isAdmin
def edit_video(id):
    # Retrieve the video from the database
    video = Video.query.get(id)
    if request.method == 'POST':
        form = VideoForm()
        if form.validate_on_submit():

            # Update the video attributes
            video.title = form.title.data
            video.description = form.description.data
            video.author = form.author.data
            video.category_id = form.category.data.id

            # Upload the video cover
            if form.cover.data:
                # delete former cover photo
                if video.cover_path:
                    os.remove(video.cover_path)

                # upload new cover photo
                cover_filename = f'cover_{video.id}.jpg'
                cover_path = os.path.join(current_app.root_path, 'static/images/covers', cover_filename)
                form.cover.data.save(cover_path)
                video.cover_path = cover_path


            # Commit the changes to the database
            db.session.commit()
            flash('Video updated successfully!', 'success')
        return redirect(url_for('admin.videos'))
    else:
        # get the video with the given id from the database and pass it to the template
        return render_template('admin/edit_video.html', video=video, v_active="active")
    

# Deletes a video
@admin_bp.route('/videos/<int:id>/delete', methods=['POST'])
@login_required
@isAdmin
def delete_video(id):
    # delete the video with the given id from the database
    video = Video.query.get_or_404(id)

    # delete the video's file from the filesystem
    if video.file_path:
        os.remove(os.path.join(current_app.root_path, 'static', video.file_path))

    # delete the video's cover from the filesystem
    if video.cover_path:
        os.remove(os.path.join(current_app.root_path, 'static', video.cover_path))

    db.session.delete(video)
    db.session.commit()
    flash('Video deleted successfully!', 'success')
    return redirect(url_for('admin.videos'))
