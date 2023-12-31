from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import UserAuth
from werkzeug.security import generate_password_hash, check_password_hash
from . import DB
from flask_login import login_user, login_required, logout_user, current_user
import re

def enforce_strong_password(password: str):
    # length constraints
    if (len(password)<=8):
        return False
    # characters needed constraints
    elif (not re.search("[a-z]", password)) or (not re.search("[A-Z]", password)) or (not re.search("[0-9]", password)):
        return False
    # unallowed characters constraints
    elif re.search("\s" , password):
        return False
    else:
        return True
 


auth = Blueprint("auth", __name__)


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        db = DB()
        cursor = db.cursor()
        userExists = cursor.execute('SELECT COUNT() FROM User WHERE username = ?', (username,)).fetchone()[0]
        db.close()
        # username already exists
        if userExists > 0:
            flash("Username taken!", category="warn")
        # password and confirm password are not the same
        elif password1 != password2:
            flash("Passwords do not match!", category="error")
        elif not enforce_strong_password(password1):
            flash("Password not strong enough!", category="error")
        else:
            passwordHash = generate_password_hash(password1, method='scrypt')
            db = DB()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO User (username, firstname, lastname, userPassword, profilePicLink) VALUES (?, ?, ?, ?, ?)",
                (username, firstName, lastName, passwordHash, "https://powerusers.microsoft.com/t5/image/serverpage/image-id/98171iCC9A58CAF1C9B5B9/image-size/large/is-moderation-mode/true?v=v2&px=999"),
            )
            db.commit()
            db.close()
            flash("Account created!", category="success")
            loggedUser = UserAuth(username=username, userPasswordHash=passwordHash)
            login_user(loggedUser, remember=True)
            return redirect(url_for('views.home'))
        
    return render_template("sign_up.html", user=current_user)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usr = request.form.get("username")
        pwd = request.form.get("password")

        # TODO: do basic check like does username exist?
        db = DB()
        cursor = db.cursor()
        userExists = cursor.execute('SELECT COUNT() FROM User WHERE username = ?', (usr,)).fetchone()[0]
        db.close()
        if userExists > 0:
            db = DB()
            cursor = db.cursor()
            hash_password = cursor.execute('SELECT userPassword FROM User WHERE username = ?', (usr,)).fetchone()[0]
            db.close()
            if check_password_hash(hash_password, pwd):
                flash("Successfully logged in!", category="success")
                loggedUser = UserAuth(username=usr, userPasswordHash=hash_password)
                login_user(loggedUser, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash("Password incorrect!", category="error")
        else:
            flash("User does not exist!", category="error")
    
    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
