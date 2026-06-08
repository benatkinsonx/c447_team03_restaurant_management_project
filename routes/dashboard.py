from flask import Blueprint, render_template, session, redirect, url_for

dashboard_route = Blueprint("dashboard", __name__)


@dashboard_route.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("dash.html")