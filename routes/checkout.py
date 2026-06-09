from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection



checkout = Blueprint("checkout", __name__)

@checkout.route('/voucher', methods=['GET','POST'])
def voucher():
    if request.method == 'GET':
        total = request.form.get('total', 25.00)
        return render_template('voucher.html', total=total, message="voucher is valid/invalid")
    return render_template('delivery.html')

@checkout.route('/delivery', methods=['POST'])
def delivery():
    return render_template('payment.html')

@checkout.route('/payment', methods=['POST'])
def payment():
    return f"""
            <h1>Payment Successful!</h1>
            <p>The order has been placed successfully.</p>
            <a href="/dashboard">Go to Dashboard</a>
        """