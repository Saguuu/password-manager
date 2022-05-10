from flask import Blueprint, render_template, request, flash, jsonify, url_for, redirect
from flask_login import current_user, login_required
from .models import Password
from . import CRYPTER, db
import json

views = Blueprint("views", __name__)

SITE_PICS = {"Facebook": "https://cdn-icons-png.flaticon.com/512/124/124010.png", 
            "Normal": "https://www.seekpng.com/png/detail/16-165938_png-file-web-site-icon-vector.png",
            "Twitter": "https://cdn-icons-png.flaticon.com/512/124/124021.png",
            "Youtube": "https://cdn-icons-png.flaticon.com/512/1384/1384060.png",
            "Instagram": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Instagram_icon.png/2048px-Instagram_icon.png",
            "Amazon": "https://cdn4.iconfinder.com/data/icons/social-media-2146/512/31_social-512.png",
            "Reddit": "https://cdn0.iconfinder.com/data/icons/social-flat-rounded-rects/512/reddit-512.png"
}

@views.route("/")
@login_required
def index():

    user_info = Password.query.filter_by(user_id=current_user.id)
    site_id = []
    websites = []
    passwords = []
    pics = []

    if user_info:
        for i in user_info:
            websites.append(i.website)
            passwords.append(CRYPTER.decrypt(i.password).decode("utf-8"))
            site_id.append(i.id)
            if i.website in SITE_PICS:
                pics.append(SITE_PICS[i.website])
            else:
                pics.append(SITE_PICS["Normal"])
    
    output = zip(websites, passwords, site_id, pics)

    return render_template("index.html", user=current_user, info=output)

@views.route("add_password", methods=["GET", "POST"])
@login_required
def add_password():

    if request.method == "POST":
        
        website = request.form.get("website").strip()
        pass1 = request.form.get("password").strip()
        pass2 = request.form.get("password2").strip()
        
        # Check user tier and total passwords to determine if they can add a password
        tier = current_user.tier
        user_info = Password.query.filter_by(user_id=current_user.id)
        total = 0
        if user_info:
            for password in user_info:
                total += 1
        max = 0

        if tier == 0:
            max = 10
        elif tier == 1:
            max = 25

        if not website or not pass1 or not pass2 or (pass1 != pass2):
            flash("Invalid input or passwords do not match", category="error")
        elif total >= max and tier != 2:
            flash("No password slots available, please upgrade for more", category="error")
        else:

            # Convert password to bytes then encrypt it, and add to database
            to_byte = bytes(pass1.encode())
            encrypted = CRYPTER.encrypt(to_byte)
            new_pass = Password(website=website, password=encrypted, user_id=current_user.id)
            db.session.add(new_pass)
            db.session.commit()
            flash("Password added!", category="success")

    return render_template("add_password.html", user=current_user)

@views.route("delete_password", methods=["POST"])
@login_required
def delete_password():
    
    password = json.loads(request.data)
    password_id = password["passId"]
    password = Password.query.get(password_id)

    if password:
        db.session.delete(password)
        db.session.commit()
    
    return jsonify({})

@views.route("upgrade_plan", methods=["GET", "POST"])
@login_required
def upgrade_plan():

    if request.method == "POST":

        plan = request.form.get("plan")

        if plan == '1':
            tier = 0
        elif plan == '2':
            tier = 1
        elif plan == '3':
            tier = 2
        else:
            tier = 0
        
        current_user.tier = tier
        db.session.commit()
        flash("Upgraded!", category="success")

    return render_template("upgrade_plan.html", user=current_user)
     