import os
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    abort,
    flash,
    request,
    current_app,
)
from functools import wraps
from flask_login import current_user, login_required, logout_user
from models import (
    User,
    Book,
    Video,
    Rental,
    Category,
    AccessRequest,
    DownloadRequest,
    db,
)
from models import CategoryForm, BookForm, VideoForm
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Decorator to verify if a user is an admin before they can acccess admin routes
def isAdmin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            logout_user(current_user)
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated_function


# delete a file
def delete_file(file_path):
    os.remove(os.path.join(current_app.root_path, "static", file_path))


# update the rentals
def update_rentals():
    today = datetime.utcnow()
    rentals = Rental.query.filter(Rental.date_due < today).all()
    for rental in rentals:
        db.session.delete(rental)
    db.session.commit()


# Admin Routes
@admin_bp.route("/dashboard")
@login_required
@isAdmin
def dashboard():
    # update rentals
    update_rentals()

    # get popular books
    popular_books = (
        Book.query.join(Rental)
        .group_by(Book.id)
        .order_by(db.func.count(Rental.id).desc())
        .limit(3)
        .all()
    )

    # get popular categories
    popular_categories = Category.query.order_by(func.random()).limit(4).all()

    today = datetime.utcnow()
    week_ago = today - timedelta(days=7)

    # get number of  rentals
    rentals_count = Rental.query.filter(Rental.date_rented >= week_ago).count()

    # count access requests
    access_requests_count = AccessRequest.query.filter(
        AccessRequest.date_requested >= week_ago
    ).count()

    # get access requests
    access_requests = (
        AccessRequest.query.order_by(AccessRequest.date_requested.desc()).limit(8).all()
    )

    # get number of users
    total_users = User.query.count()
    users = User.query.all()
    return render_template(
        "admin/dashboard.html",
        d_active="active",
        rentals_count=rentals_count,
        access_requests_count=access_requests_count,
        total_users=total_users,
        users=users,
        popular_books=popular_books,
        popular_categories=popular_categories,
        access_requests=access_requests,
    )


# Profile Route
@admin_bp.route("/profile", methods=["GET", "POST"])
@login_required
@isAdmin
def edit_profile():
    if request.method == "POST":
        form = request.form
        current_user.name = form["name"]
        current_user.email = form["email"]
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("admin.profile"))
    else:
        return render_template("admin/edit_profile.html")


# Reports
@admin_bp.route("/reports")
@login_required
@isAdmin
def reports():
    # do some data analysis using the existing database and generate some key statistics

    # Most Popular Books
    popular_books = (
        Book.query.join(Rental)
        .group_by(Book.id)
        .order_by(db.func.count(Rental.id).desc())
        .limit(10)
        .all()
    )

    # Most Active Users
    active_users = (
        User.query.join(Rental)
        .group_by(User.id)
        .order_by(db.func.count(Rental.id).desc())
        .limit(10)
        .all()
    )

    # Categories
    categories = Category.query.all()

    # Rental Duration
    rentals_duration = Rental.query.all()
    avg_rental_duration = sum(
        (r.date_due - r.date_rented).days for r in rentals_duration
    ) / (len(rentals_duration) or 1)

    # Total number of books, users, and rentals
    total_books = Book.query.count()
    total_users = User.query.count()
    total_rentals = Rental.query.count()
    total_categories = Category.query.count()
    total_videos = Video.query.count()

    # Percentage of rented books
    rented_books_per = (
        (db.session.query(func.count(Rental.book_id.distinct())).scalar())
        / (total_books or 1)
    ) * 100

    # Percentage of active users
    active_users = (
        (User.query.filter(User.rentals.any()).count()) / (total_users or 1)
    ) * 100

    # Ratio of Books to Videos
    book_to_video_per = (total_books / ((total_books + total_videos) or 1)) * 100

    # rentals due today
    now = datetime.now()
    rentals_due_today = Rental.query.filter_by(date_due=now.date()).count()

    # rentals due in One Week
    next_week = now + timedelta(days=7)
    rentals_due_soon = Rental.query.filter(
        Rental.date_due >= now, Rental.date_due <= next_week
    ).count()

    return render_template(
        "admin/reports.html",
        rep_active="active",
        popular_books=popular_books,
        active_users=round(active_users),
        total_categories=total_categories,
        avg_rental_duration=avg_rental_duration,
        total_books=total_books,
        total_users=total_users,
        total_rentals=total_rentals,
        total_videos=total_videos,
        rentals_due_soon=round(rentals_due_soon),
        rentals_due_today=round(rentals_due_today),
        book_to_video_per=round(book_to_video_per),
        rented_books_per=round(rented_books_per),
    )


# Render list of users
@admin_bp.route("/users")
@login_required
@isAdmin
def users():
    all_users = User.query.all()
    users = [user for user in all_users if not user.is_admin]
    return render_template(
        "admin/users_info.html", users=users, u_active="active", total_users=len(users)
    )


# Category Routes
@admin_bp.route("/categories")
@login_required
@isAdmin
def categories():
    # get all categories from the database and pass them to the template
    categories = Category.query.all()
    return render_template(
        "admin/categories.html", categories=categories, c_active="active"
    )


@admin_bp.route("/categories/new", methods=["GET", "POST"])
@login_required
@isAdmin
def new_category():
    form = CategoryForm()
    if request.method == "POST":
        if form.validate_on_submit():
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()
            flash("Category created successfully!", "success")
        return redirect(url_for("admin.categories"))
    else:
        return render_template("admin/new_category.html", form=form)


@admin_bp.route("/categories/<string:id>/delete", methods=["POST"])
@login_required
@isAdmin
def delete_category(id):
    # delete all videos in the category
    category = Category.query.get_or_404(id)

    # delete all books and videos in the category
    for book in category.books:
        db.session.delete(book)
        delete_file("images/covers/" + book.cover_path)
        delete_file("books/" + book.file_path)
    for video in category.videos:
        db.session.delete(video)
        delete_file("cover/" + book.cover_path)
        delete_file("images/covers/" + book.file_path)

    db.session.delete(category)
    db.session.commit()
    flash("Category deleted successfully!", "success")
    return redirect(url_for("admin.categories"))


# Book Routes
@admin_bp.route("/books")
@login_required
@isAdmin
def books():
    # get all books from the database and pass them to the template
    books = Book.query.all()
    return render_template("admin/books.html", books=books, b_active="active")


# new books route
@admin_bp.route("/books/new", methods=["GET", "POST"])
@login_required
@isAdmin
def new_book():
    form = BookForm()
    if request.method == "POST":
        if form.validate_on_submit():
            timestamp = str(datetime.now().timestamp()).replace(".", "")
            book = Book(
                id=timestamp,
                title=form.title.data,
                description=form.description.data,
                author=form.author.data,
                category_id=form.category_id.data,
            )
            db.session.add(book)

            # upload book cover and book file (pdf)
            if form.cover.data:
                cover_filename = f"cover_{timestamp}.jpg"
                cover_path = os.path.join(
                    current_app.root_path, "static/images/covers", cover_filename
                )
                form.cover.data.save(cover_path)
                book.cover_path = cover_filename

            if form.file.data:
                file_filename = f"book_{timestamp}.pdf"
                file_path = os.path.join(
                    current_app.root_path, "static/books", file_filename
                )
                form.file.data.save(file_path)
                book.file_path = file_filename

            db.session.commit()
            flash("Book created successfully!", "success")
        return redirect(url_for("admin.books"))
    else:
        return render_template("admin/new_book.html", b_active="active", form=form)


# edit book route
@admin_bp.route("/books/<string:id>/edit", methods=["GET", "POST"])
@login_required
@isAdmin
def edit_book(id):
    # Retrieve the book from the database
    book = Book.query.get(id)
    all_categories = Category.query.all()

    if request.method == "POST":
        # Update details of the book available in the request form
        form = request.form

        if form.get("title"):
            book.title = form["title"]

        if form.get("description"):
            book.description = form["description"]

        if form.get("author"):
            book.author = form["author"]

        if form.get("category"):
            book.category_id = form["category_id"]

        if request.files["cover"].filename != "":
            cover_filename = f"cover_{book.id}.jpg"
            cover_path = os.path.join(
                current_app.root_path, "static/images/covers", cover_filename
            )
            request.files["cover"].save(cover_path)
            book.cover_path = cover_filename

        if request.files["file"].filename != "":
            file_filename = f"book_{book.id}.pdf"
            file_path = os.path.join(
                current_app.root_path, "static/books", file_filename
            )
            request.files["file"].save(file_path)
            book.file_path = file_filename

        db.session.commit()
        flash("Book updated successfully!", "success")
        return redirect(url_for("admin.books"))
    else:
        # get the book with the given id from the database and pass it to the template
        return render_template(
            "admin/edit_book.html",
            book=book,
            b_active="active",
            all_categories=all_categories,
        )


# delete book route
@admin_bp.route("/books/<string:id>/delete", methods=["POST"])
@login_required
@isAdmin
def delete_book(id):
    # delete the book with the given id from the database
    book = Book.query.get_or_404(id)

    # Make sure book is not rented
    if book.rentals:
        flash("Book is currently rented out", "warning")
        return redirect(url_for("admin.books"))

    # delete the book cover
    if book.cover_path:
        os.remove(
            os.path.join(current_app.root_path, "static/images/covers", book.cover_path)
        )

    # delete the book's file from the filesystem
    if book.file_path:
        os.remove(os.path.join(current_app.root_path, "static/books", book.file_path))

    db.session.delete(book)
    db.session.commit()
    flash("Book deleted successfully!", "success")
    return redirect(url_for("admin.books"))


# Request routes
@admin_bp.route("/requests")
@login_required
@isAdmin
def requests():
    # get all access and download requests from the database and pass them to the template
    access_requests = AccessRequest.query.all()
    download_requests = DownloadRequest.query.all()
    total_requests = len(access_requests) + len(download_requests)

    return render_template(
        "admin/requests.html",
        access_requests=access_requests,
        download_requests=download_requests,
        req_active="active",
        total_requests=total_requests,
    )


# grant request
@admin_bp.route("/grant-access-request/<string:request_id>", methods=["POST"])
@login_required
@isAdmin
def grant_access_request(request_id):
    # grant access to the user's request with the given id
    access_request = AccessRequest.query.get_or_404(request_id)
    user = access_request.user_id
    book = access_request.book_id
    date_due = datetime.now() + timedelta(days=int(request.form.get("due_date")))

    # add the Access Request to the Rentals Table
    rental = Rental(user_id=user, book_id=book, date_due=date_due)
    db.session.add(rental)

    # delete the request from the database
    db.session.delete(access_request)

    # commit the changes to the database
    db.session.commit()

    return redirect(url_for("admin.requests"))


# Reject access request
@admin_bp.route("/reject-access-request/<string:request_id>", methods=["POST"])
@login_required
@isAdmin
def reject_access_request(request_id):
    # reject access to the user's request with the given id
    request = AccessRequest.query.get_or_404(request_id)

    # delete the request from the database
    db.session.delete(request)

    # commit the changes to the database
    db.session.commit()

    return redirect(url_for("admin.requests"))


# grant download request
@admin_bp.route("/grant-download-request/<string:request_id>", methods=["POST"])
@login_required
@isAdmin
def grant_download_request(request_id):
    # grant download to the user's request with the given id
    download_request = DownloadRequest.query.get_or_404(request_id)
    user = download_request.user_id
    book = download_request.book_id

    # make book downloadable in rentals table
    rental = Rental.query.filter_by(user_id=user, book_id=book).first()
    rental.downloadable = True

    # delete the request from the database
    db.session.delete(download_request)

    # commit the changes to the database
    db.session.commit()

    return redirect(url_for("admin.requests"))


# reject download request
@admin_bp.route("/reject-download-request/<string:request_id>", methods=["POST"])
@login_required
@isAdmin
def reject_download_request(request_id):
    # reject download to the user's request with the given id
    request = DownloadRequest.query.get_or_404(request_id)

    # delete the request from the database
    db.session.delete(request)

    # commit the changes to the database
    db.session.commit()

    return redirect(url_for("admin.requests"))


# Video Routes
# Renders a list of all the videos
@admin_bp.route("/videos")
@login_required
@isAdmin
def videos():
    videos = Video.query.all()
    return render_template("admin/videos.html", videos=videos, v_active="active")


# Renders a form to create a new video
@admin_bp.route("/videos/new", methods=["GET", "POST"])
@login_required
@isAdmin
def new_video():
    form = VideoForm()
    if request.method == "POST":
        if form.validate_on_submit():
            timestamp = str(datetime.now().timestamp()).replace(".", "")
            video = Video(
                id=timestamp,
                title=form.title.data,
                description=form.description.data,
                category_id=form.category_id.data,
            )
            db.session.add(video)

            # upload video cover and video file (mp4)
            if form.cover.data:
                cover_filename = f"cover_{timestamp}.jpg"
                cover_path = os.path.join(
                    current_app.root_path, "static/images/covers", cover_filename
                )
                form.cover.data.save(cover_path)
                video.cover_path = cover_filename

            if form.file.data:
                file_filename = f"video_{timestamp}.mp4"
                file_path = os.path.join(
                    current_app.root_path, "static/videos", file_filename
                )
                form.file.data.save(file_path)
                video.file_path = file_filename

            db.session.commit()
            flash("Video created successfully!", "success")
        return redirect(url_for("admin.videos"))
    else:
        return render_template("admin/new_video.html", v_active="active", form=form)


# Renders a form to edit a video
@admin_bp.route("/videos/<string:id>/edit", methods=["GET", "POST"])
@login_required
@isAdmin
def edit_video(id):
    # get the video with the given id from the database
    video = Video.query.get_or_404(id)
    if request.method == "POST":
        form = request.form

        # update the video's details
        if form.get("title"):
            video.title = form.get("title")

        if form.get("description"):
            video.description = form.get("description")

        if form.get("category"):
            video.category_id = form.get("category")

        if request.files["cover"].filename != "":
            cover_filename = f"cover_{video.id}.jpg"
            cover_path = os.path.join(
                current_app.root_path, "static/images/covers", cover_filename
            )
            request.files["cover"].save(cover_path)
            video.cover_path = cover_filename

        if request.files["video"].filename != "":
            file_filename = f"video_{video.id}.mp4"
            file_path = os.path.join(
                current_app.root_path, "static/videos", file_filename
            )
            request.files["video"].save(file_path)
            video.file_path = file_filename

        db.session.commit()

        flash("Video updated successfully!", "success")
        return redirect(url_for("admin.videos"))
    else:
        # get the video with the given id from the database and pass it to the template
        return render_template("admin/edit_video.html", video=video, v_active="active")


# Deletes a video
@admin_bp.route("/videos/<string:id>/delete", methods=["POST"])
@login_required
@isAdmin
def delete_video(id):
    # delete the video with the given id from the database
    video = Video.query.get_or_404(id)

    # delete the video's file from the filesystem
    if video.file_path:
        os.remove(os.path.join(current_app.root_path, "static/videos", video.file_path))

    # delete the video's cover from the filesystem
    if video.cover_path:
        os.remove(
            os.path.join(
                current_app.root_path, "static/images/covers", video.cover_path
            )
        )

    db.session.delete(video)
    db.session.commit()
    flash("Video deleted successfully!", "success")
    return redirect(url_for("admin.videos"))
