from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ChangePasswordForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user with given email exists
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('You are now logged in.', 'success')
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))
    else:
        return render_template('auth/login.html', href="/")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if user with given email already exists
        if User.query.filter_by(email=email).first():
            flash('An account with that email address already exists.', 'error')
            return redirect(url_for('auth.register'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))

        # Create new user and add to database
        new_user = User(name=name, email=email, password=generate_password_hash(password), is_admin=False)
        db.session.add(new_user)
        db.session.commit()

        flash('Your account has been created.', 'success')
        login_user(new_user)
        return redirect(url_for('auth.dashboard'))
    else:
        return render_template('auth/signUp.html',  href="/")

@auth_bp.route('/register-admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        passkey = request.form['passkey']

        # Check if passkey is correct
        if passkey != 'USIB324':
            flash('Invalid passkey.', 'error')
            return redirect(url_for('auth.register_admin'))

        # Check if user with given email already exists
        if User.query.filter_by(email=email).first():
            flash('An account with that email address already exists.', 'error')
            return redirect(url_for('auth.register_admin'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register_admin'))

        # Create new admin user and add to database
        new_admin = User(name=name, email=email, password=generate_password_hash(password), is_admin=True)
        db.session.add(new_admin)
        db.session.commit()

        flash('Admin account has been created.', 'success')
        login_user(new_admin)
        return redirect(url_for('admin.dashboard'))
    else:
        return render_template('auth/admin_signUp.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('views.home'))


# Render the change password page
@auth_bp.route('/change_password')
@login_required
def change_password():
    return render_template('auth/password.html')

# Handle the change password form submission
@auth_bp.route('/change_password', methods=['POST'])
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

