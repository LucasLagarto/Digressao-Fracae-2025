from flask import render_template, session

def index():
    return render_template("excel.html", ulogin=session.get("user"))