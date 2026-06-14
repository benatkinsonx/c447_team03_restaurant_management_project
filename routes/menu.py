from flask import Blueprint, session, redirect, render_template, url_for, request
import mysql.connector
from db import get_connection
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

menu_bp = Blueprint("menu", __name__)


def is_admin_owner():
    claims = get_jwt()
    raw = claims.get("role_id")
    try:
        role = int(raw) if raw is not None else None
    except (TypeError, ValueError):
        role = None
    return role in [2, 3, 4]


@menu_bp.route("/admin/menu", methods=["GET"])
@jwt_required()
def admin_menu():
    if not is_admin_owner():
        return """
            <p>Not admin</p>
            <a href="/customer/menu">View customer menu</a>
        """, 403

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


@menu_bp.route("/admin/menu/change/<int:menu_id>", methods=["GET", "POST"])
@jwt_required()
def change_menu_item(menu_id):
    if not is_admin_owner():
        return """
            <p>Not admin</p>
            <a href="/customer/menu">View customer menu</a>
        """, 403
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        if request.method == "GET":
            cursor.execute("""
                SELECT menu_id, cat_id, item_name, is_veg, price, is_available
                FROM MenuItems
                WHERE menu_id = %s
            """, (menu_id,))

            item = cursor.fetchone()

            cursor.execute("""
                SELECT cat_id, category
                FROM Category
                ORDER BY category
            """)

            categories = cursor.fetchall()

            return render_template(
                "change_menu.html",
                item=item,
                categories=categories
            )

        item_name = request.form.get("item_name")
        cat_id = request.form.get("cat_id")
        is_veg = request.form.get("is_veg")
        price = request.form.get("price")
        is_available = request.form.get("is_available")

        cursor.execute("""
            UPDATE MenuItems
            SET item_name = %s,
                cat_id = %s,
                is_veg = %s,
                price = %s,
                is_available = %s
            WHERE menu_id = %s
        """, (item_name, cat_id, is_veg, price, is_available, menu_id))

        db.commit()

        return redirect(url_for("menu.admin_menu"))

    except mysql.connector.Error as err:
        if db:
            db.rollback()

        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/admin/menu">Go Back</a>
        """, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@menu_bp.route("/basket/add/<int:menu_id>", methods=["POST"])
@jwt_required()
def add_to_basket(menu_id):
    
    quantity = int(request.form.get("quantity", 1))

    try:
        quantity = int(request.form.get("quantity", "1"))
    except ValueError:
        quantity = 0

    if quantity < 1 or quantity > 50:
        return """
        <h3>Invalid quantity.</h3>
        <a href="/customer/menu">Go Back</a>
        """
    
    basket = session.get("basket", {})

    menu_id_str=str(menu_id)

    # check how many of item is in basket
    if menu_id_str in basket:
        basket[menu_id_str] += quantity

    else:
        basket[menu_id_str] = quantity

    session["basket"] = basket
    session.modified = True

    return redirect(url_for('menu.customer_menu'))

@menu_bp.route("/basket", methods=["GET"])
@jwt_required()
def view_basket():

    basket = session.get("basket", {})

    if not basket:
        return render_template("basket.html", basket_items=[], total=0)

    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)

        menu_ids = list(basket.keys())
        placeholders = ", ".join(["%s"] * len(menu_ids))

        cursor.execute(f"""
            SELECT menu_id, item_name, price
            FROM MenuItems
            WHERE menu_id IN ({placeholders})
        """, menu_ids)

        items = cursor.fetchall()

        basket_items = []
        total = 0

        for item in items:
            quantity = basket[str(item["menu_id"])]
            subtotal = float(item["price"]) * quantity
            total += subtotal

            basket_items.append({
                "menu_id": item["menu_id"],
                "item_name": item["item_name"],
                "price": item["price"],
                "quantity": quantity,
                "subtotal": subtotal
            })

        session['total'] = total
        return render_template(
            "basket.html",
            basket_items=basket_items,
            total=total
        )

    except mysql.connector.Error as err:
        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/customer/menu">Go Back</a>
        """, 500

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@menu_bp.route("/admin/menu/delete/<int:menu_id>", methods=["POST"])
def delete_menu_item(menu_id):
    db = None
    cursor = None

    try:
        db = get_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE MenuItems
            SET is_available = FALSE
            WHERE menu_id = %s
        """, (menu_id,))

        db.commit()

        return redirect(url_for("menu.admin_menu"))

    except mysql.connector.Error as err:
        if db:
            db.rollback()

        return f"""
            <h3>Database Error</h3>
            <p>{err}</p>
            <a href="/admin/menu">Go Back</a>
        """, 500

    finally:
        if cursor:
            cursor.close()

        if db:
            db.close()


@menu_bp.route("/basket/remove/<int:menu_id>", methods=["POST"])
def remove_from_basket(menu_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    basket = session.get("basket", {})
    basket.pop(str(menu_id), None)

    session["basket"] = basket
    session.modified = True

    return redirect(url_for("menu.view_basket"))