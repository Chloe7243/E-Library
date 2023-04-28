from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user with given email exists
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_is_admin'] = user.is_admin
            flash('You are now logged in.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))
    else:
        return render_template('login.html')

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
        return redirect(url_for('auth.login'))
    else:
        return render_template('signUp.html')

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
        return redirect(url_for('auth.login'))
    else:
        return render_template('register_admin.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

