from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection



checkout = Blueprint("checkout", __name__)

@checkout.route("/gotocheckout", methods=["POST"])
def gotocheckout():
    session['total'] = 78
    total = session.get('total', 0)
    return render_template('voucher.html', total=total, message="voucher is valid/invalid")

@checkout.route('/voucher', methods=['GET','POST'])
def voucher():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    return render_template('delivery.html')

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