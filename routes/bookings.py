from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from db import get_connection
from datetime import date
from flask_jwt_extended import  create_access_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, unset_jwt_cookies 


booking_bp = Blueprint("bookings", __name__)


@booking_bp.route("/bookings", methods=["GET"])
@jwt_required()
def bookings():
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login", next=request.path))

    # return render_template("bookings.html", today=date.today().isoformat())
    return render_template( "bookings.html", today=date.today().isoformat(), csrf_token=get_jwt()["csrf"] ), 200


@booking_bp.route("/submitbooking", methods=["POST"])
@jwt_required()
def submit_booking():
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login", next=url_for("bookings.bookings")))
    
    user_id = int(get_jwt_identity())

    booking_date = request.form.get("date")
    booking_time = request.form.get("time")
    guests = request.form.get("guests")

    if guests == "7+":
        guests = 7
    else:
        guests = int(guests)

    if booking_time < "09:00" or booking_time > "17:30":
        return """
            <h3>Bookings are only available between 9:00 AM and 5:30 PM.</h3>
            <a href="/bookings">Choose Another Time</a>
        """, 400

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
            user_id,
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
            """, 409

        cursor.execute("""
            INSERT INTO Reservations
            (user_id, booking_date, booking_time, size, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            booking_date,
            booking_time,
            guests,
            "booked"
        ))

        db.commit()

        return redirect(url_for("bookings.manage_bookings")), 303

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
@jwt_required()
def manage_bookings():
    # if "user_id" not in session:
    #     return redirect(
    #         url_for("auth.login", next=request.path)
    #     )

    user_id = int(get_jwt_identity())

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
        """, (user_id,))

        reservations = cursor.fetchall()

        return render_template( "manage_bookings.html", reservations=reservations, csrf_token=get_jwt()["csrf"] ), 200

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


@booking_bp.route("/manage_bookings/edit/<int:reservation_id>",methods=["GET", "POST"])
@jwt_required()
def edit_booking(reservation_id):
    # if "user_id" not in session:
    #     return redirect(
    #         url_for("auth.login", next=request.path)
    #     )
    
    user_id = int(get_jwt_identity())

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
                user_id
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
                reservation=reservation,
                today=date.today().isoformat(),
                csrf_token=get_jwt()["csrf"]
            ), 200

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

        if booking_time < "09:00" or booking_time > "17:30":
            return """
                <h3>Bookings are only available between 9:00 AM and 5:30 PM.</h3>
                <a href="/manage_bookings">Go Back</a>
            """, 400

        
        cursor.execute("""
            SELECT reservation_id
            FROM Reservations
            WHERE user_id = %s
            AND booking_date = %s
            AND booking_time = %s
            AND reservation_id != %s
            AND status != 'cancelled'
            LIMIT 1
        """, (
            user_id,
            booking_date,
            booking_time,
            reservation_id
        ))

        duplicate_booking = cursor.fetchone()

        if duplicate_booking:
            return """
                <h3>You already have a reservation for this date and time.</h3>
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
            user_id
        ))


        db.commit()

        return redirect(
            url_for("bookings.manage_bookings")
        ), 303

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
@jwt_required()
def cancel_booking(reservation_id):
    # if "user_id" not in session:
    #     return redirect(
    #         url_for("auth.login")
    #     )
    
    user_id = int(get_jwt_identity())

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
            user_id
        ))

        db.commit()

        return redirect(
            url_for("bookings.manage_bookings")
        ), 303

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
            
# @booking_bp.route( "/manage_bookings/edit/<int:reservation_id>", methods=["GET", "POST"] ) 
# @jwt_required() 
# def edit_booking(reservation_id): 
#     user_id = int(get_jwt_identity()) 
    
#     db = None 
#     cursor = None 
    
#     try: 
#         db = get_connection() 
#         cursor = db.cursor(dictionary=True) 
        
#         # Check that the reservation exists and belongs to this user 
#         cursor.execute(""" SELECT reservation_id, booking_date, TIME_FORMAT(booking_time, '%H:%i') AS booking_time, size, status FROM Reservations WHERE reservation_id = %s AND user_id = %s """, ( reservation_id, user_id )) 
        
#         reservation = cursor.fetchone() 
#         if reservation is None: 
#             return """ <h3>Reservation not found.</h3> <a href="/manage_bookings">Go Back</a> """, 404 
#         if reservation["status"] == "cancelled": 
#             return """ <h3>Cancelled reservations cannot be edited.</h3> <a href="/manage_bookings">Go Back</a> """, 400 
        
#         # Display the edit form 
#         if request.method == "GET": 
#             return render_template( "edit_booking.html", reservation=reservation, today=date.today().isoformat(), csrf_token=get_jwt()["csrf"] ) 
        
#         # Process the submitted edit form 
#         booking_date = request.form.get("date", "").strip() 
#         booking_time = request.form.get("time", "").strip() 
#         guests = request.form.get("guests", "").strip() 
        
#         if not booking_date or not booking_time or not guests: 
#             return """ <h3>Please complete every field.</h3> <a href="/manage_bookings">Go Back</a> """, 400 
        
#         try: 
#             selected_date = date.fromisoformat(booking_date) 
            
#         except ValueError: 
#             return """ <h3>Invalid booking date.</h3> <a href="/manage_bookings">Go Back</a> """, 400 
        
#         if selected_date < date.today(): 
#             return """ <h3>The booking date cannot be in the past.</h3> <a href="/manage_bookings">Go Back</a> """, 400 
        
#         try: 
#             guests = int(guests) 
        
#         except ValueError: 
#             return """ <h3>The number of guests must be a number.</h3> <a href="/manage_bookings">Go Back</a> """, 400 
        
#         if guests < 1 or guests > 20: 
#             return """ <h3>The number of guests must be between 1 and 20.</h3> <a href="/manage_bookings">Go Back</a> """, 400 
        
#         # Prevent the user from editing this booking into # the same date and time as another active booking 
#         cursor.execute(""" SELECT reservation_id FROM Reservations WHERE user_id = %s AND booking_date = %s AND booking_time = %s AND reservation_id != %s AND status != 'cancelled' LIMIT 1 """, ( user_id, booking_date, booking_time, reservation_id )) 
        
#         duplicate_booking = cursor.fetchone() 
        
#         if duplicate_booking: 
#             return """ <h3> You already have another reservation at this date and time. </h3> <a href="/manage_bookings">Go Back</a> """, 409 
        
#         cursor.execute(""" UPDATE Reservations SET booking_date = %s, booking_time = %s, size = %s WHERE reservation_id = %s AND user_id = %s AND status != 'cancelled' """, ( booking_date, booking_time, guests, reservation_id, user_id )) 
        
#         db.commit() 
        
#         return redirect( url_for("bookings.manage_bookings") ) 
    
#     except mysql.connector.Error as err: 
#         if db: db.rollback() 
#         return f""" <h3>Database Error</h3> <p>{err}</p> <a href="/manage_bookings">Go Back</a> """, 500 
    
#     finally: 
#         if cursor: cursor.close() 
        
#         if db: db.close()
