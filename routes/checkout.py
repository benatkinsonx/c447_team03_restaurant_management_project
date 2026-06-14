import datetime
import os
import stripe

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt


checkout = Blueprint("checkout", __name__)

# configure stripe (set STRIPE_SECRET_KEY in environment)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')

@checkout.route("/gotocheckout", methods=["POST"])
@jwt_required()
def gotocheckout():
    user_id = int(get_jwt_identity())
    
    total = session['total']

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
@jwt_required()
def voucher():
    user_id = int(get_jwt_identity())
    
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        # ===== voucher code handling =====
        entered_voucher_code = (request.form.get('voucher_code') or '').strip().upper()
        # don't store the code in session until we've validated it

        voucher_query = """
            SELECT reward_name, cost_multiplier, points
            FROM Rewards
            WHERE reward_name = %s AND active = TRUE
    """
        cursor.execute(voucher_query, (entered_voucher_code,))
        voucher = cursor.fetchone()

        # ===== user points handling =====
        points_query = """
            SELECT reward_points
            FROM Users
            WHERE user_id = %s
        """
        cursor.execute(points_query, (user_id,))
        user_points = cursor.fetchone()

        # if the user didn't enter a code, clear any previous voucher state and continue
        if entered_voucher_code == "":
            session.pop('discounted_total', None)
            session.pop('entered_voucher_code', None)
            return render_template('delivery.html', total=session['total'], curr_reward_points=f"{user_points['reward_points']}", message="")

        # validate voucher exists
        if voucher:
            # valid voucher name found
            if voucher.get('reward_name') == entered_voucher_code and user_points.get('reward_points') >= voucher['points']:
                session['discounted_total'] = session['total'] * voucher['cost_multiplier']
                session['entered_voucher_code'] = entered_voucher_code
                return render_template('delivery.html', total=session['discounted_total'], message=f"Voucher '{voucher['reward_name']}' applied successfully! £{session['total']:.2f} reduced to £{session['discounted_total']:.2f}.<br><br>Reward points before: {user_points['reward_points']}<br>Reward points now: {user_points['reward_points'] - voucher['points']}.")
            # user doesn't have enough points
            elif voucher.get('reward_name') == entered_voucher_code and user_points.get('reward_points') < voucher['points']:
                session.pop('discounted_total', None)
                session.pop('entered_voucher_code', None)
                return render_template('voucher.html', total=session['total'], curr_reward_points=f"{user_points['reward_points']}", message=f"Not enough reward points for voucher '{voucher['reward_name']}'. You have {user_points['reward_points']} points but the voucher requires {voucher['points']} points. Try again or proceed without a voucher.")
            else:
                session.pop('discounted_total', None)
                session.pop('entered_voucher_code', None)
                return render_template('voucher.html', total=session['total'], curr_reward_points=f"{user_points['reward_points']}", message="Invalid voucher code. Try again or proceed without a voucher.")
        else:
            # no matching voucher found
            session.pop('discounted_total', None)
            session.pop('entered_voucher_code', None)
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

@checkout.route('/delivery', methods=['GET', 'POST'])
@jwt_required()
def delivery():
    
    delivery_option = request.form.get('delivery')
    
    if session.get('discounted_total'):
        if delivery_option == 'delivery':
            session['discounted_total'] += 5.00
    else:
        if delivery_option == 'delivery':
            session['total'] += 5.00
    
    # create Stripe PaymentIntent now and render payment page
    total = session.get('discounted_total', session['total'])
    amount_cents = int(round(float(total) * 100))
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency='gbp',
        metadata={'integration_check': 'accept_a_payment'}
    )

    client_secret = intent.client_secret
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')

    return render_template('payment.html', client_secret=client_secret, publishable_key=publishable_key, total=total)

@checkout.route('/payment', methods=['POST'])
@jwt_required()
def payment():

    total = session.get('discounted_total', session['total'])
    amount_cents = int(round(float(total) * 100))

    # create payment intent (test mode when using test keys)
    intent = stripe.PaymentIntent.create(
        amount=amount_cents,
        currency='gbp',
        metadata={'integration_check': 'accept_a_payment'}
    )

    client_secret = intent.client_secret
    publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY', '')

    return render_template('payment.html', client_secret=client_secret, publishable_key=publishable_key, total=total)


@checkout.route('/payment/confirm', methods=['POST'])
@jwt_required()
def payment_confirm():
    user_id = int(get_jwt_identity())
    
    data = request.get_json(silent=True) or {}
    payment_intent_id = data.get('paymentIntentId')

    if not payment_intent_id:
        return jsonify({'error': 'missing paymentIntentId'}), 400

    intent = stripe.PaymentIntent.retrieve(payment_intent_id)
    if intent.status != 'succeeded':
        return jsonify({'error': 'payment not successful', 'status': intent.status}), 400

    # record order and payment
    db = get_connection()
    cursor = db.cursor(dictionary=True)
    try:
        # deduct reward points if voucher applied
        entered_voucher_code = session.get('entered_voucher_code')
        if entered_voucher_code:
            points_update_query = """
                UPDATE Users
                SET reward_points = reward_points - (
                    SELECT points
                    FROM Rewards
                    WHERE reward_name = %s
                )
                WHERE user_id = %s
            """
            cursor.execute(points_update_query, (entered_voucher_code, user_id))
            db.commit()

        # reward the user with 5 points for completing a payment
        reward_bonus_query = """
            UPDATE Users
            SET reward_points = reward_points + 5
            WHERE user_id = %s
        """
        cursor.execute(reward_bonus_query, (user_id,))
        db.commit()

        order_insert_query = """
            INSERT INTO Orders (user_id, order_date, order_status, total_price)
            VALUES (%s, %s, %s, %s)
        """
        order_date = datetime.datetime.now()
        order_status = 'completed'
        total_price = session.get('discounted_total', session['total'])

        cursor.execute(order_insert_query, (user_id, order_date, order_status, total_price))
        db.commit()
        order_id = cursor.lastrowid
        session['order_id'] = order_id

        payments_log_query = """
            INSERT INTO Payments (user_id, order_id, amount, payment_status, payment_date)
            VALUES (%s, %s, %s, %s, %s)
        """
        amount = total_price
        payment_status = 'completed'
        payment_date = datetime.datetime.now()

        cursor.execute(payments_log_query, (user_id, order_id, amount, payment_status, payment_date))
        db.commit()

        # store amount for the success page and clear temporary session keys
        session['last_payment_amount'] = amount
        session.pop('discounted_total', None)
        session.pop('entered_voucher_code', None)
        session.pop('order_id', None)
        session.pop('basket', None)
        session.pop('total', None)

        return jsonify({'success': True, 'redirect_url': url_for('checkout.payment_success')}), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        db.close()


@checkout.route('/payment_success')
def payment_success():
    # show the payment success page using the stored amount
    amount = session.pop('last_payment_amount', None)
    return render_template('payment_success.html', amount=amount)
