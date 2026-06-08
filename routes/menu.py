from flask import Blueprint, session, redirect, render_template, url_for
import mysql.connector
from db import get_connection

menu_bp = Blueprint("menu", __name__)


def is_admin_owner():
    return "role_id" in session and session.get("role_id") in [2, 3]


@menu_bp.route("/admin/menu", methods=["GET"])
def admin_menu():
    if not is_admin_owner():
        return """
            <p>Not admin</p>
            <a href="/customer/menu">view customer table</a>
        """

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

        print("MENU ITEMS:", menu_items)

        return render_template("admin_menu.html", menu_items=menu_items)

    except mysql.connector.Error as err:
        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/dashboard">Go Back</a>
        """

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@menu_bp.route("/customer/menu", methods=["GET"])
def customer_menu():
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

        print("MENU ITEMS:", menu_items)

        return render_template("customer_menu.html", menu_items=menu_items)

    except mysql.connector.Error as err:
        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/dashboard">Go Back</a>
        """

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()