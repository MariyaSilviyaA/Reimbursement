from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        if not email:
            flash("Please enter your email address.",category='error')
        elif not password:
            flash("Please enter your password.",category='error')

        else:
            user = User.query.filter_by(email=email).first()
            if user:
                if check_password_hash(user.password, password):
                    flash("Logged in!", category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.home'))
                else:
                    flash('Password is incorrect.', category='error')
            else:
                flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route("/sign-up", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        errors = []

        if email_exists:
            errors.append('Email is already in use.')
        if username_exists:
            errors.append('Username is already in use.')
        if password1 != password2:
            errors.append("Passwords don't match!")
        if len(username) < 2:
            errors.append('Username is too short.')
        if len(password1) < 4:
            errors.append('Password is too short.')
        if len(email) < 4:
            errors.append('Email is invalid.')

        if errors:
            for error in errors:
                flash(error, category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("signup.html", user=current_user)



@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))

