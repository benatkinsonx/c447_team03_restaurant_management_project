from flask import Blueprint, render_template, session, redirect, url_for
from db import get_connection

dashboard_route = Blueprint("dashboard", __name__)


@dashboard_route.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("dash.html")


@dashboard_route.route("/payment_history")
def payment_history():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session['user_id']
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT
                o.order_id,
                o.order_date,
                o.order_status,
                o.total_price,
                p.payment_status,
                p.payment_date,
                p.amount
            FROM Orders o
            LEFT JOIN Payments p ON o.order_id = p.order_id
            WHERE o.user_id = %s
            ORDER BY o.order_date DESC
        """, (user_id,))

        purchase_history = cursor.fetchall()
        return render_template("payment_history.html", purchase_history=purchase_history)
    except Exception as e:
        return f"<h3>Database Error</h3><p>{e}</p><a href=\"/dashboard\">Back to Dashboard</a>", 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
