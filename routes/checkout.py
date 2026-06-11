from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection



checkout = Blueprint("checkout", __name__)

@checkout.route("/gotocheckout", methods=["POST"])
def gotocheckout():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    total = session['total']

    user_id = session['user_id']
    points_query = """
        SELECT reward_points
        FROM Users
        WHERE user_id = %s
    """
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute(points_query, (user_id,))
    user_points = cursor.fetchone()
    return render_template('voucher.html', total=total, curr_reward_points=f"{user_points['reward_points']}", message="")

@checkout.route('/voucher', methods=['POST'])
def voucher():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        # ===== voucher code handling =====
        entered_voucher_code = request.form.get('voucher_code').upper()
        session['entered_voucher_code'] = entered_voucher_code

        voucher_query = """
            SELECT reward_name, cost_multiplier, points
            FROM Rewards
            WHERE reward_name = %s AND active = TRUE
    """
        cursor.execute(voucher_query, (entered_voucher_code,))
        voucher = cursor.fetchone()

        # ===== user points handling =====
        user_id = session['user_id']
        points_query = """
            SELECT reward_points
            FROM Users
            WHERE user_id = %s
        """
        cursor.execute(points_query, (user_id,))
        user_points = cursor.fetchone()

        if voucher:
            if voucher.get('reward_name') == entered_voucher_code and user_points.get('reward_points') >= voucher['points']:
                session['discounted_total'] = session['total'] * voucher['cost_multiplier']
                return render_template('delivery.html', total=session['discounted_total'], message=f"Voucher '{voucher['reward_name']}' applied successfully! £{session['total']:.2f} reduced to £{session['discounted_total']:.2f}.<br><br>Reward points before: {user_points['reward_points']}<br>Reward points now: {user_points['reward_points'] - voucher['points']}.")
            elif voucher.get('reward_name') == entered_voucher_code and user_points.get('reward_points') <= voucher['points']:
                return render_template('voucher.html', total=session['total'], curr_reward_points=f"{user_points['reward_points']}", message=f"Not enough reward points for voucher '{voucher['reward_name']}'. You have {user_points['reward_points']} points but the voucher requires {voucher['points']} points. Try again or proceed without a voucher.")
            else:
                return render_template('delivery.html', total=session['total'], curr_reward_points=f"{user_points['reward_points']}", message="Invalid voucher code. Try again or proceed without a voucher.")
        else:
            return render_template('voucher.html', total=session['total'], curr_reward_points=f"{user_points['reward_points']}", message="Invalid voucher code. Try again or proceed without a voucher.")
    
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
    
    delivery_option = request.form.get('delivery')
    
    if session.get('discounted_total'):
        if delivery_option == 'delivery':
            session['discounted_total'] += 5.00
    else:
        if delivery_option == 'delivery':
            session['total'] += 5.00
    
    return render_template('payment.html', total=session.get('discounted_total', session['total']))

@checkout.route('/payment', methods=['POST'])
def payment():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = get_connection()
    cursor = db.cursor(dictionary=True)

    points_update_query = """
        UPDATE Users
        SET reward_points = reward_points - (
            SELECT points
            FROM Rewards
            WHERE reward_name = %s
        )
        WHERE user_id = %s
    """
    entered_voucher_code = session.get('entered_voucher_code')
    user_id = session['user_id']
    cursor.execute(points_update_query, (entered_voucher_code, user_id))
    db.commit()

    
    return f"""
            <h1>Payment Successful!</h1>
            <p>The order has been placed successfully.</p>
            <a href="/dashboard">Go to Dashboard</a>
        """