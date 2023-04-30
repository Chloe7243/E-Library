import os
from flask import Blueprint, current_app, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_uploads import UploadSet, configure_uploads, IMAGES, DOCUMENTS
from werkzeug.utils import secure_filename
from models import Category, Book, Video, db
from .forms import CategoryForm, BookForm, VideoForm 


app = current_app
admin = Blueprint('admin', __name__, url_prefix='/admin')

ALLOWED_EXTENSIONS = {'mp4'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Set up the UploadSet for books
books = UploadSet('books', DOCUMENTS)
images = UploadSet('images', IMAGES)

# Configure the app to use the UploadSet for books
configure_uploads(app, books)
configure_uploads(app, images)


# Admin dashboard
@admin.route('/')
@login_required
def dashboard():
    # Only allow access to admin users
    if not current_user.is_admin:
        flash('You do not have permission to access that page.', 'danger')
        return redirect(url_for('main.index'))

    return render_template('admin/dashboard.html')

# Categories

# List all categories
@admin.route('/categories')
@login_required
def list_categories():
    # Only allow access to admin users
    if not current_user.is_admin:
        flash('You do not have permission to access that page.', 'danger')
        return redirect(url_for('main.index'))

    categories = Category.query.all()
    return render_template('admin/categories.html', categories=categories)

# Add a new category
@admin.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    # Only allow access to admin users
    if not current_user.is_admin:
        flash('You do not have permission to access that page.', 'danger')
        return redirect(url_for('main.index'))

    form = CategoryForm()

    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()

        flash('Category added successfully!', 'success')
        return redirect(url_for('admin.list_categories'))

    return render_template('admin/add_category.html', form=form)

# Edit a category
@admin.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    # Only allow access to admin users
    if not current_user.is_admin:
        flash('You do not have permission to access that page.', 'danger')
        return redirect(url_for('main.index'))

    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)

    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()

        flash('Category updated successfully!', 'success')
        return redirect(url_for('admin.list_categories'))

    return render_template('admin/edit_category.html', form=form)

# Delete a category
@admin.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    # Only allow access to admin users
    if not current_user.is_admin:
        flash('You do not have permission to access that page.', 'danger')
        return redirect(url_for('main.index'))

    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()

    flash('Category deleted successfully!', 'success')
    return redirect(url_for('admin.list_categories'))

# Books
@admin.route('/books')
def books():
    # Fetch all books from the database
    books = Book.query.all()
    return render_template('admin/books.html', books=books)

@admin.route('/books/add', methods=['GET', 'POST'])
def add_book():
    form = BookForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the uploaded files
            cover_image = images.save(form.cover_image.data)
            book_file = books.save(form.book_file.data)

            # Create a new book object and populate its attributes
            book = Book()
            book.title = form.title.data
            book.author = form.author.data
            book.description = form.description.data
            book.cover_image = cover_image
            book.file_path = book_file
            book.category_id = form.category.data.id

            # Add the book to the database
            db.session.add(book)
            db.session.commit()

            return redirect(url_for('admin.books'))

    # Render the add book form
    return render_template('admin/add_book.html', form=form)

@admin.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    # Fetch the book with the given ID from the database
    book = Book.query.get_or_404(book_id)

    form = BookForm(obj=book)

    if request.method == 'POST':
        if form.validate_on_submit():
            # Update the book's attributes
            book.title = form.title.data
            book.author = form.author.data
            book.description = form.description.data
            book.category_id = form.category.data.id

            # Check if a new cover image was uploaded
            if form.cover_image.data:
                cover_image = images.save(form.cover_image.data)
                book.cover_image = cover_image

            # Check if a new book file was uploaded
            if form.book_file.data:
                book_file = books.save(form.book_file.data)
                book.file_path = book_file

            # Update the book in the database
            db.session.commit()

            return redirect(url_for('admin.books'))

    # Render the edit book form
    return render_template('admin/edit_book.html', form=form, book=book)

@admin.route('/books/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    # Fetch the book with the given ID from the database
    book = Book.query.get_or_404(book_id)

    # Delete the book from the database
    db.session.delete(book)
    db.session.commit()

    return redirect(url_for('admin.books'))

# Videos

@admin.route('/videos/add', methods=['GET', 'POST'])
@login_required
def add_video():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_id = request.form['category']
        category = Category.query.filter_by(id=category_id).first()
        if 'file' not in request.files or 'cover' not in request.files:
            flash('No file or cover selected!', 'error')
            return redirect(request.url)
        file = request.files['file']
        cover = request.files['cover']
        if file.filename == '' or cover.filename == '':
            flash('No file or cover selected!', 'error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join('app/static/videos/', filename))
            file_path = os.path.join('videos/', filename)
        else:
            flash('Invalid file format for video!', 'error')
            return redirect(request.url)
        if cover and allowed_file(cover.filename):
            filename = secure_filename(cover.filename)
            cover.save(os.path.join('app/static/images/', filename))
            cover_image = os.path.join('images/', filename)
        else:
            flash('Invalid file format for cover image!', 'error')
            return redirect(request.url)
        video = Video(title=title, description=description, cover_image=cover_image, file_path=file_path, category=category)
        db.session.add(video)
        db.session.commit()
        flash('Video added successfully!', 'success')
        return redirect(url_for('admin.videos'))
    return render_template('admin/add_video.html', categories=categories)


# Edit a video
@admin.route('/videos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_video(id):
    video = Video.query.get_or_404(id)
    form = VideoForm(obj=video)
    if form.validate_on_submit():
        video.title = form.title.data
        video.description = form.description.data
        video.category = form.category.data
        if form.file.data:
            file = form.file.data
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['VIDEO_UPLOAD_PATH'], filename)
            file.save(file_path)
            video.file_path = file_path
        if form.cover_image.data:
            cover_image = save_image(form.cover_image.data, current_app.config['IMAGE_UPLOAD_PATH'])
            video.cover_image = cover_image
        db.session.commit()
        flash('Video updated successfully', 'success')
        return redirect(url_for('admin.manage_videos'))

    return render_template('admin/edit_video.html', form=form, video=video)


# Delete a video
@admin.route('/videos/delete/<int:id>', methods=['POST'])
@login_required
def delete_video(id):
    video = Video.query.get_or_404(id)
    db.session.delete(video)
    db.session.commit()
    flash('Video deleted successfully', 'success')
    return redirect(url_for('admin.manage_videos'))



