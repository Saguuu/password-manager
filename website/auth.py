from flask import Blueprint, render_template, redirect, request, flash, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import CRYPTER, db 
from flask_login import current_user, login_required, login_user, logout_user 

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        name = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(name=name).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in", category="success")
                login_user(user, remember=True)
                return redirect(url_for("views.index", user=current_user))
            else:
                flash("Incorrect password", category="error")
        else:
            flash("Username does not exist", category="error")
    

    return render_template("login.html")

@auth.route("/logout")
@login_required
def logout():
    
    logout_user()

    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        email = request.form.get("email").strip()
        name = request.form.get("username").strip()

        # Hash user password
        password = generate_password_hash(request.form.get("password").strip(), method="sha256")
        question = request.form.get("question").strip()
        question_answer = request.form.get("answer").strip()

        # Convert secret question answer to bytes then encrypt it
        to_byte = bytes(question_answer.encode())
        question_answer = CRYPTER.encrypt(to_byte)

        get_name = User.query.filter_by(name=name).first()
        get_email = User.query.filter_by(email=email).first()
        if get_name:
            flash("Username already in use", category="error")
        elif get_email:
            flash("Email Already in use", category="error")
        else:
            if len(question) < 2 or question == "Choose a secret question":
                flash("Invalid secret question", category="error")
            elif len(request.form.get("answer")) <= 0:
                flash("Invalid secret question answer", category="error")
            elif len(email) < 2:
                flash("Email must be at least 2 characters long", category="error")
            elif len(name) < 2:
                flash("Username must be at least 2 characters long", category="error")
            elif len(request.form.get("password")) < 8:
                flash("Password must be at least 8 characters long", category="error")
            elif request.form.get("password") != request.form.get("password2"):
                flash("Passwords do not match", category="error")
            else:
                # add user to database
                new_user = User(email=email, name=name, password=password, secret_question=question, secret_question_answer=question_answer, tier=0)
                db.session.add(new_user)
                db.session.commit()
                flash("Account created!", category="success")
                return redirect(url_for("auth.login"))

    
    return render_template("register.html")

@auth.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":
        username = request.form.get("username").strip()
        user = User.query.filter_by(name=username).first()
        if user:
            name = user.name
            return redirect(url_for("auth.reset_password", n=name))
        else:
            flash("No such user exists", category="error")

    return render_template("/forgot_password.html")

@auth.route("/reset_password", methods=["GET", "POST"])
def reset_password():

    if request.method == "POST":
        name = request.form.get("username").strip()
        user = User.query.filter_by(name=name).first()
        if user:
            pass1 = request.form.get("password").strip()
            pass2 = request.form.get("password2").strip()
            question_answer = CRYPTER.decrypt(user.secret_question_answer).decode("utf-8")
            input = request.form.get("answer")
            if (input == question_answer) and (pass1 == pass2):
                user.password = generate_password_hash(pass1)
                db.session.commit()
                flash("Password changed", category="success")
                return redirect(url_for("auth.login"))
            else:
                flash("No such user exists, question answer inccorect or passwords do not match", category="error")
        else:
            flash("No such user exists", category="error")
            return redirect(url_for("auth.forgot_password"))

    name = request.args.get("n")
    user = User.query.filter_by(name=name).first()
    question = user.secret_question
    
    return render_template("/reset_password.html", question=question)
