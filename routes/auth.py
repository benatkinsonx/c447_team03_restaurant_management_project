import os
import re
from datetime import datetime, timedelta, timezone

import jwt
import mysql.connector
from dotenv import load_dotenv
from flask import Blueprint, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_connection

load_dotenv()


auth = Blueprint("auth", __name__)

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET is missing from the .env file")

def validate_password(password):
    if not password:
        return "Password is required."

    if len(password) < 8:
        return "Password must be at least 8 characters long."

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number."

    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character."

    if re.search(r"\s", password):
        return "Password must not contain spaces."

    return None

@auth.route('/register', methods=['GET'])
def show_register_form():
    return render_template('register.html')

@auth.route('/register', methods=['POST'])
def register():
    db = get_connection()
    cursor = db.cursor()

    try:
        # get personal data 
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email').strip().lower()
        phone_num = request.form.get('phone')         
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # get address 
        addr1 = request.form.get('address1')           
        addr2 = request.form.get('address2')           
        city = request.form.get('city')
        post_code = request.form.get('postal_code')    

        if password != confirm_password:
            return "<h3>Error: Passwords do not match!</h3><a href='/register'>Go Back</a>", 400
        
        password_error = validate_password(password)

        if password_error:
            return f"""
                <h3>Invalid Password</h3>
                <p>{password_error}</p>
                <a href="/register">Go Back</a>
            """

        # Secure and encrypt the user password
        password_hash = generate_password_hash(password)

        # Insert into the Address Table
        address_sql = "INSERT INTO Address (addr1, addr2, city, post_code) VALUES (%s, %s, %s, %s)"
        address_val = (addr1, addr2, city, post_code)
        cursor.execute(address_sql, address_val)

        # newly generated ID for the foreign key reference

        addr_id = cursor.lastrowid
        


        # Insert into the Users table
        user_sql = """
            INSERT INTO Users (addr_id, first_name, last_name, email, password_hash, phone_num) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        user_val = (addr_id, first_name, last_name, email, password_hash, phone_num)
        cursor.execute(user_sql, user_val)

        user_id = cursor.lastrowid

        session["user_id"] = user_id
        session["email"] = email
        session["first_name"] = first_name
        session["role_id"] = 1
        db.commit()

        # Create JWT token
        token = jwt.encode(
            {
                "user_id": user_id,
                "email": email,
                "first_name": first_name,
                "role_id": 1,
                "exp": datetime.now(timezone.utc) + timedelta(hours=2)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

        session["jwt_token"] = token



        
        return redirect(url_for("dashboard.dashboard"))

    except mysql.connector.Error as err:
        # If any single query errors out, rollback the database to prevent incomplete data states
        db.rollback() 
        return f"""<h3>Database Error!</h3>
            <p>Details: {err}</p>
            <a href='/register'>Try Again</a>"""

    finally:
        cursor.close()
        db.close()


@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        select_query = """
            SELECT user_id, first_name, last_name, email, password_hash, role_id
            FROM Users
            WHERE email = %s
        """

        cursor.execute(select_query, (email,))
        user = cursor.fetchone()

        if user is None:
            return """
                <h3>Invalid email or password.</h3>
                <a href="/login">Try Again</a>
            """

        if not check_password_hash(user['password_hash'], password):
            return """
                <h3>Invalid email or password.</h3>
                <a href="/login">Try Again</a>
            """

        session['user_id'] = user['user_id']
        session['email'] = user['email']
        session['first_name'] = user['first_name']
        session['role_id'] = user['role_id']

        token = jwt.encode(
            {
                "user_id": user['user_id'],
                "email": user["email"],
                "role_id": user["role_id"],
                "exp": datetime.now(timezone.utc) + timedelta(hours=2)
            },
            JWT_SECRET,
            algorithm=JWT_ALGORITHM
        )

        session["jwt_token"] = token

        return redirect(url_for("dashboard.dashboard"))

    except mysql.connector.Error as err:
        return f"""
            <h3>Database Error!</h3>
            <p>{err}</p>
            <a href="/login">Try Again</a>
        """

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# logout
@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))
    