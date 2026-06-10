from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection



checkout = Blueprint("checkout", __name__)

@checkout.route("/gotocheckout", methods=["POST"])
def gotocheckout():
    session['total'] = 78
    total = session['total']
    return render_template('voucher.html', total=total, message="")

@checkout.route('/voucher', methods=['POST'])
def voucher():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        db = get_connection()
        cursor = db.cursor()

        voucher_code = request.form.get('voucher_code')

        voucher_name_query = """
            SELECT reward_name
            FROM Rewards
            WHERE reward_name = %s AND active = TRUE
    """
        cursor.execute(voucher_name_query, (voucher_code,))
        voucher_name_result = cursor.fetchone()
    
        if voucher_name_result:
            cost_multiplier_query = """
                SELECT cost_multiplier
                FROM Rewards
                WHERE reward_name = %s AND active = TRUE
            """
            cursor.execute(cost_multiplier_query, (voucher_code,))
            cost_multiplier_result = cursor.fetchone()
            session['discounted_total'] = session['total'] * cost_multiplier_result[0]
            return render_template('delivery.html', total=session['discounted_total'], message=f"Voucher '{voucher_code}' applied successfully! £{session['total']:.2f} reduced to £{session['discounted_total']:.2f}")
        else:
            return render_template('voucher.html', total=session['total'], message="Invalid voucher code. Try again or proceed without a voucher.")
    
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

@checkout.route('/delivery', methods=['POST'])
def delivery():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    return render_template('payment.html')

@checkout.route('/payment', methods=['POST'])
def payment():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    return f"""
            <h1>Payment Successful!</h1>
            <p>The order has been placed successfully.</p>
            <a href="/dashboard">Go to Dashboard</a>
        """