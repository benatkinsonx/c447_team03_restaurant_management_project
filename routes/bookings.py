from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection

from flask import request, render_template, redirect, url_for, session
import mysql.connector
from db import get_connection

booking_bp = Blueprint("bookings", __name__)


@booking_bp.route("/bookings", methods=["GET"])
def bookings():
    if "user_id" not in session:
        return redirect(url_for("auth.login", next=request.path))

    return render_template("bookings.html")


@booking_bp.route("/submitbooking", methods=["POST"])
def submit_booking():
    if "user_id" not in session:
        return redirect(url_for("auth.login", next=url_for("bookings")))

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    booking_date = request.form.get("date")
    booking_time = request.form.get("time")
    guests = request.form.get("guests")

    if guests == "7+":
        guests = 7
    else:
        guests = int(guests)

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO Reservations
            (user_id, booking_date, booking_time, size, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            session["user_id"],
            booking_date,
            booking_time,
            guests,
            "booked"
        ))

        db.commit()

        return render_template("submit_booking.html")

    except mysql.connector.Error as err:
        if db:
            db.rollback()

        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/bookings">Try Again</a>
        """, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()