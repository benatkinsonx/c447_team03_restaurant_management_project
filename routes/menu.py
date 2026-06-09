from flask import Blueprint, session, redirect, render_template, url_for
import mysql.connector
from db import get_connection

menu_bp = Blueprint("menu", __name__)


def is_admin_owner():
    return "role_id" in session and session.get("role_id") in [2, 3]


@menu_bp.route("/admin/menu", methods=["GET"])
def admin_menu():
    # Uncomment this later when admin login works properly
    # if not is_admin_owner():
    #     return """
    #         <p>Not admin</p>
    #         <a href="/customer/menu">View customer menu</a>
    #     """, 403

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                MenuItems.menu_id,
                MenuItems.item_name,
                MenuItems.is_veg,
                MenuItems.price,
                MenuItems.is_available,
                Category.category,
                Category.category_desc
            FROM MenuItems
            JOIN Category ON MenuItems.cat_id = Category.cat_id
            ORDER BY Category.category, MenuItems.item_name
        """)

        menu_items = cursor.fetchall()

        return render_template("admin_menu.html", menu_items=menu_items)

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


@menu_bp.route("/customer/menu", methods=["GET"])
def customer_menu():
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                MenuItems.menu_id,
                MenuItems.item_name,
                MenuItems.is_veg,
                MenuItems.price,
                MenuItems.is_available,
                Category.category,
                Category.category_desc
            FROM MenuItems
            JOIN Category ON MenuItems.cat_id = Category.cat_id
            WHERE MenuItems.is_available = TRUE
            ORDER BY Category.category, MenuItems.item_name
        """)

        menu_items = cursor.fetchall()

        return render_template("customer_menu.html", menu_items=menu_items)

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


@menu_bp.route("/admin/menu/change/<int:menu_id>", methods=["GET"])
def show_change_page(menu_id):
    return render_template("change_menu.html", menu_id=menu_id)