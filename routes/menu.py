from flask import Flask,Blueprint, session,redirect,render_template, url_for
import mysql.connector
from db import get_connection

menu = Blueprint("menu", __name__)

@menu.route("/menu", methods=["POST", "GET"])
def menu():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
