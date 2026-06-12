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
            SELECT reservation_id
            FROM Reservations
            WHERE user_id = %s
            AND booking_date = %s
            AND booking_time = %s
            AND status != 'cancelled'
            LIMIT 1
        """, (
            session["user_id"],
            booking_date,
            booking_time
        ))

        existing_booking = cursor.fetchone()

        if existing_booking:
            return """
                <h3>You already have a reservation for this date and time.</h3>
                <a href="/bookings">Choose Another Time</a>
                <br>
                <a href="/manage_bookings">Manage Reservations</a>
            """

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

        return redirect(url_for("bookings.manage_bookings"))

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

# manage bookings

@booking_bp.route("/manage_bookings", methods=["GET"])
def manage_bookings():
    if "user_id" not in session:
        return redirect(
            url_for("auth.login", next=request.path)
        )

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                Reservations.reservation_id,
                Reservations.booking_date,
                TIME_FORMAT(
                    Reservations.booking_time,
                    '%H:%i'
                ) AS booking_time,
                Reservations.size,
                Reservations.status,
                RestaurantTables.table_num
            FROM Reservations
            LEFT JOIN RestaurantTables
                ON Reservations.table_id = RestaurantTables.table_id
            WHERE Reservations.user_id = %s
            ORDER BY
                Reservations.booking_date ASC,
                Reservations.booking_time ASC
        """, (session["user_id"],))

        reservations = cursor.fetchall()

        return render_template(
            "manage_bookings.html",
            reservations=reservations
        )

    except mysql.connector.Error as err:
        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/dashboard">Go Back</a>
        """, 500

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@booking_bp.route(
    "/manage_bookings/edit/<int:reservation_id>",
    methods=["GET", "POST"]
)
def edit_booking(reservation_id):
    if "user_id" not in session:
        return redirect(
            url_for("auth.login", next=request.path)
        )

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == "GET":
            cursor.execute("""
                SELECT
                    reservation_id,
                    booking_date,
                    TIME_FORMAT(
                        booking_time,
                        '%H:%i'
                    ) AS booking_time,
                    size,
                    status
                FROM Reservations
                WHERE reservation_id = %s
                  AND user_id = %s
            """, (
                reservation_id,
                session["user_id"]
            ))

            reservation = cursor.fetchone()

            if reservation is None:
                return """
                    <h3>Reservation not found.</h3>
                    <a href="/manage_bookings">Go Back</a>
                """, 404

            if reservation["status"] == "cancelled":
                return """
                    <h3>A cancelled reservation cannot be edited.</h3>
                    <a href="/manage_bookings">Go Back</a>
                """, 400

            return render_template(
                "edit_booking.html",
                reservation=reservation
            )

        booking_date = request.form.get("date")
        booking_time = request.form.get("time")
        guests = request.form.get("guests")

        if not booking_date or not booking_time or not guests:
            return """
                <h3>Please complete every field.</h3>
                <a href="/manage_bookings">Go Back</a>
            """, 400

        try:
            guests = int(guests)
        except ValueError:
            return """
                <h3>Invalid number of guests.</h3>
                <a href="/manage_bookings">Go Back</a>
            """, 400

        cursor.execute("""
            UPDATE Reservations
            SET
                booking_date = %s,
                booking_time = %s,
                size = %s
            WHERE reservation_id = %s
              AND user_id = %s
              AND status != 'cancelled'
        """, (
            booking_date,
            booking_time,
            guests,
            reservation_id,
            session["user_id"]
        ))

        if cursor.rowcount == 0:
            return """
                <h3>Reservation could not be updated.</h3>
                <a href="/manage_bookings">Go Back</a>
            """, 404

        db.commit()

        return redirect(
            url_for("bookings.manage_bookings")
        )

    except mysql.connector.Error as err:
        if db:
            db.rollback()

        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/manage_bookings">Go Back</a>
        """, 500

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@booking_bp.route(
    "/manage_bookings/cancel/<int:reservation_id>",
    methods=["POST"]
)
def cancel_booking(reservation_id):
    if "user_id" not in session:
        return redirect(
            url_for("auth.login")
        )

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE Reservations
            SET status = 'cancelled'
            WHERE reservation_id = %s
              AND user_id = %s
              AND status != 'cancelled'
        """, (
            reservation_id,
            session["user_id"]
        ))

        db.commit()

        return redirect(
            url_for("bookings.manage_bookings")
        )

    except mysql.connector.Error as err:
        if db:
            db.rollback()

        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/manage_bookings">Go Back</a>
        """, 500

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()