from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from models import Book, Rental, Request, db
from .forms import ProfileForm, ChangePasswordForm

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)

@user_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been changed.', 'success')
            return redirect(url_for('user.change_password'))
        else:
            flash('Current password is incorrect.', 'danger')
    return render_template('user/change_password.html', form=form)

@user_bp.route('/books')
@login_required
def books():
    books = Book.query.all()
    return render_template('user/books.html', books=books)

@user_bp.route('/books/<int:id>')
@login_required
def book_details(id):
    book = Book.query.get_or_404(id)
    return render_template('user/book_details.html', book=book)

@user_bp.route('/books/<int:id>/read')
@login_required
def read_book(id):
    book = Book.query.get_or_404(id)
    return render_template('user/read_book.html', book=book)

@user_bp.route('/books/<int:id>/download')
@login_required
def download_book(id):
    book = Book.query.get_or_404(id)
    return send_file(book.file_path, attachment_filename=book.title+'.pdf')

@user_bp.route('/books/<int:id>/request', methods=['POST'])
@login_required
def request_book(id):
    book = Book.query.get_or_404(id)
    rental = Rental.query.filter_by(user_id=current_user.id, book_id=book.id).first()
    if rental:
        flash('You have already rented this book.', 'warning')
        return redirect(url_for('user.book_details', id=id))
    request = Request(user_id=current_user.id, book_id=book.id)
    db.session.add(request)
    db.session.commit()
    flash('Your request has been submitted. You will be notified once the book is available for rent.', 'success')
    return redirect(url_for('user.book_details', id=id))

