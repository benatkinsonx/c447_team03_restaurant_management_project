from flask import Blueprint, render_template, session, redirect, url_for
from db import get_connection
from flask_jwt_extended import  get_jwt, get_jwt_identity, jwt_required 

dashboard_route = Blueprint("dashboard", __name__)


@dashboard_route.route("/dashboard")
@jwt_required()
# def dashboard():
#     if "user_id" not in session:
#         return redirect(url_for("auth.login"))

#     return render_template("dash.html")

def dashboard(): 
    claims = get_jwt()

    # Ensure role_id is an integer for consistent template comparisons
    raw_role = claims.get("role_id")
    try:
        role_id = int(raw_role) if raw_role is not None else None
    except (TypeError, ValueError):
        role_id = None

    current_user = {
        "user_id": int(get_jwt_identity()),
        "email": claims.get("email"),
        "first_name": claims.get("first_name"),
        "role_id": role_id,
    }

    return render_template("dash.html", current_user=current_user), 200


@dashboard_route.route("/payment_history")
@jwt_required()
def payment_history():
    # if "user_id" not in session:
    #     return redirect(url_for("auth.login"))

    # user_id = session['user_id']
    user_id = int(get_jwt_identity())
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
        return render_template("payment_history.html", purchase_history=purchase_history), 200
    except Exception as e:
        return f"<h3>Database Error</h3><p>{e}</p><a href=\"/dashboard\">Back to Dashboard</a>", 500
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
