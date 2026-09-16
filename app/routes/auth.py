from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user
from flask import session

from app.extensions import db
from app.models import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)
        user = User(
            username=username,
            email=email,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash("Registration Successful!", "success")
        return redirect(url_for("auth.register"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            remember = request.form.get("remember")
            login_user(
                user,
                remember=True if remember else False
            )
            flash("Login Successful!", "success")
            return redirect(url_for("dashboard.dashboard"))
        flash("Invalid Email or Password!", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():

    logout_user()
    return redirect(url_for("main.index"))