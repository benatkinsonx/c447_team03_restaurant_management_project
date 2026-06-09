from flask import Flask, render_template, request, redirect, url_for, jsonify, session, Blueprint
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_connection



checkout = Blueprint("checkout", __name__)

@checkout.route('/pay', methods=['POST'])
def pay():
    return  """
            <h1>Payments Complete!</h1>
            <p>The payment has been completed successfully.</p><a href='/'>go back home to log in</a>
            """