from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from db import get_connection

booking_page = Blueprint("bookings", __name__)

@booking_page.route("/bookings", methods=["GET", "POST"])
def bookings():
    #get form input
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    date = request.form.get("date")
    time = request.form.get("time")
    guests = request.form.get("guests")

    
    return render_template("bookings.html")

# @bookings.route("/submitbooking")
# def submit_booking():
#     return render_template("submit_booking.html")