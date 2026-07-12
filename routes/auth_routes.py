from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from flask_bcrypt import Bcrypt

from database.database import db
from database.models import User
from datetime import datetime


auth = Blueprint('auth', __name__)

bcrypt = Bcrypt()
@auth.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 1. Check required fields
        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for('auth.register'))
        
        # 2. Check password length
        if len(password) < 8:
           flash("Password must be at least 8 characters long.", "danger")
           return redirect(url_for('auth.register'))

        # 2. Check passwords match
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('auth.register'))

        # 3. Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered.", "warning")
            return redirect(url_for('auth.register'))

        # 4. Hash password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # 5. Save user
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful!", "success")

        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

     email = request.form.get('email').strip().lower()
     password = request.form.get('password')

     user = User.query.filter_by(email=email).first()

     if user and bcrypt.check_password_hash(user.password, password):

        login_user(user)

        user.last_login = datetime.utcnow()
        db.session.commit()

        flash("Login Successful!", "success")

        return redirect(url_for("dashboard.dashboard_home")) 

     flash("Invalid Email or Password", "danger")

    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():

    logout_user()

    flash("Logged out successfully.", "info")

    return redirect(url_for('auth.login'))