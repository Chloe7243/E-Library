from flask import Blueprint, render_template

auth = Blueprint('auth', __name__)

@auth.route("/login")
def login():
    return render_template("login.html")

@auth.route("/register")
def register():
    return render_template("signUp.html")

@auth.route("/reset_password")
def reset_password():
    return render_template("password.html", boolean=False)

@auth.route("/change_password")
def change_password():
    return render_template("password.html", boolean=True)
