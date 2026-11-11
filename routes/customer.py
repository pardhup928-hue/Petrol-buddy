"""Petrol Buddy – Customer routes."""

import datetime, random, string
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)
from werkzeug.security import generate_password_hash, check_password_hash
from auth_helpers import login_required, role_required
from db import query, transaction

customer_bp = Blueprint("customer", __name__)


def _cid():
    return int(session.get("role_id", 0))


def _gen_order_code():
    year = datetime.datetime.now().year
    suffix = "".join(random.choices(string.digits, k=4))
    return f"ORD-{year}-{suffix}"


# ── DASHBOARD ──────────────────────────────────────────────────────────────────
@customer_bp.route("/dashboard")
@role_required("customer")
def dashboard():
    cid = _cid()
    stats = {}
    recent = []
    try:
        stats["total"]     = query("SELECT COUNT(*) AS n FROM orders WHERE customer_id=%s", (cid,), one=True)["n"]
        stats["active"]    = query("SELECT COUNT(*) AS n FROM orders WHERE customer_id=%s AND status IN ('Placed','Confirmed','Partner Assigned','Out for Delivery')", (cid,), one=True)["n"]
        stats["delivered"] = query("SELECT COUNT(*) AS n FROM orders WHERE customer_id=%s AND status='Delivered'", (cid,), one=True)["n"]
        stats["spent"]     = query("SELECT COALESCE(SUM(total_amount),0) AS s FROM orders WHERE customer_id=%s AND status NOT IN ('Cancelled','Rejected')", (cid,), one=True)["s"]
        recent = query("""
            SELECT o.*, d.full_name AS partner_name
            FROM orders o
            LEFT JOIN delivery_partners d ON o.delivery_partner_id = d.id
            WHERE o.customer_id = %s
            ORDER BY o.created_at DESC LIMIT 5
        """, (cid,))
    except Exception as e:
        flash(f"Dashboard error: {e}", "danger")
    return render_template("customer/dashboard.html", stats=stats, recent=recent)


# ── PLACE ORDER ────────────────────────────────────────────────────────────────
@customer_bp.route("/place-order", methods=["GET", "POST"])
@role_required("customer")
def place_order():
    cid = _cid()
    # Load fuel catalog
    fuel_catalog = {}
    try:
        rows = query("""
            SELECT p.fuel_type, p.price_per_litre, i.available_litres
            FROM fuel_prices p
            JOIN fuel_inventory i ON p.fuel_type = i.fuel_type
        """)
        fuel_catalog = {r["fuel_type"]: r for r in rows}
    except Exception as e:
        flash(f"Could not load fuel data: {e}", "danger")

    errors = []
    form = {
        "fuel_type":               "Petrol",
        "quantity_litres":         "",
        "delivery_address":        session.get("address", ""),
        "city":                    session.get("city", ""),
        "pincode":                 session.get("pincode", ""),
        "landmark":                "",
        "location_description":    "",
        "latitude":                "",
        "longitude":               "",
        "preferred_date":          (datetime.date.today() + datetime.timedelta(days=1)).isoformat(),
        "preferred_time":          "10:00",
        "payment_method":          "Cash on Delivery",
        "additional_instructions": "",
    }

    if request.method == "POST":
        form.update({
            "fuel_type":               request.form.get("fuel_type", "Petrol"),
            "quantity_litres":         request.form.get("quantity_litres", ""),
            "delivery_address":        request.form.get("delivery_address", "").strip(),
            "city":                    request.form.get("city", "").strip(),
            "pincode":                 request.form.get("pincode", "").strip(),
            "landmark":                request.form.get("landmark", "").strip(),
            "location_description":    request.form.get("location_description", "").strip(),
            "latitude":                request.form.get("latitude", "").strip(),
            "longitude":               request.form.get("longitude", "").strip(),
            "preferred_date":          request.form.get("preferred_date", ""),
            "preferred_time":          request.form.get("preferred_time", ""),
            "payment_method":          request.form.get("payment_method", "Cash on Delivery"),
            "additional_instructions": request.form.get("additional_instructions", "").strip(),
        })

        try:
            qty = float(form["quantity_litres"])
        except ValueError:
            qty = 0

        if form["fuel_type"] not in fuel_catalog:
            errors.append("Invalid fuel type selected.")
        if qty < 5 or qty > 100:
            errors.append("Quantity must be between 5 and 100 litres.")
        if not form["delivery_address"]:
            errors.append("Delivery address is required.")
        if not form["city"]:
            errors.append("City is required.")
        if len(form["pincode"]) < 6:
            errors.append("Valid 6-digit PIN code is required.")
        if not form["preferred_date"]:
            errors.append("Preferred delivery date is required.")

        if not errors:
            catalog_row  = fuel_catalog[form["fuel_type"]]
            stock        = float(catalog_row["available_litres"])
            price        = float(catalog_row["price_per_litre"])
            total        = round(qty * price, 2)

            if qty > stock:
                errors.append(f"Insufficient stock! Only {stock:.1f} L of {form['fuel_type']} available.")

        if not errors:
            try:
                order_code = _gen_order_code()
                # Ensure unique code
                while query("SELECT id FROM orders WHERE order_code=%s", (order_code,), one=True):
                    order_code = _gen_order_code()

                # Demo online payment: generate fake txn ref
                txn_ref = None
                pay_status = "Pending"
                if form["payment_method"] == "Online Payment - Demo":
                    txn_ref    = "DEMO-TXN-" + "".join(random.choices(string.digits, k=6))
                    pay_status = "Paid"

                ids = transaction([
                    (
                        """INSERT INTO orders
                           (order_code, customer_id, fuel_type, quantity_litres,
                            price_per_litre, total_amount, delivery_address,
                            location_description, city, pincode, landmark,
                            latitude, longitude, preferred_date, preferred_time,
                            additional_instructions, payment_method, status)
                           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'Placed')""",
                        (order_code, cid, form["fuel_type"], qty,
                         price, total, form["delivery_address"],
                         form["location_description"] or None,
                         form["city"], form["pincode"],
                         form["landmark"] or None,
                         form["latitude"] or None,
                         form["longitude"] or None,
                         form["preferred_date"], form["preferred_time"],
                         form["additional_instructions"] or None,
                         form["payment_method"]),
                    ),
                    (
                        """UPDATE fuel_inventory
                           SET available_litres = available_litres - %s
                           WHERE fuel_type = %s AND available_litres >= %s""",
                        (qty, form["fuel_type"], qty),
                    ),
                ])
                order_id = ids[0]
                # Create payment record
                query(
                    """INSERT INTO payments (order_id, payment_method, amount, payment_status, transaction_ref)
                       VALUES (%s,%s,%s,%s,%s)""",
                    (order_id, form["payment_method"], total, pay_status, txn_ref),
                    commit=True,
                )
                flash(f"Order {order_code} placed successfully! 🎉 Total: ₹{total:,.2f}", "success")
                return redirect(url_for("customer.my_orders"))
            except Exception as e:
                errors.append(f"Order could not be placed: {e}")

    return render_template("customer/place_order.html",
                           form=form, fuel_catalog=fuel_catalog, errors=errors)


# ── MY ORDERS ──────────────────────────────────────────────────────────────────
@customer_bp.route("/my-orders")
@role_required("customer")
def my_orders():
    cid = _cid()
    orders = query("""
        SELECT o.*, d.full_name AS partner_name, d.phone AS partner_phone
        FROM orders o
        LEFT JOIN delivery_partners d ON o.delivery_partner_id = d.id
        WHERE o.customer_id = %s
        ORDER BY o.created_at DESC
    """, (cid,))
    return render_template("customer/my_orders.html", orders=orders)


# ── CANCEL ORDER ───────────────────────────────────────────────────────────────
@customer_bp.route("/cancel-order/<int:order_id>", methods=["POST"])
@role_required("customer")
def cancel_order(order_id):
    cid = _cid()
    order = query("SELECT * FROM orders WHERE id=%s AND customer_id=%s LIMIT 1",
                  (order_id, cid), one=True)
    if not order:
        flash("Order not found.", "danger")
        return redirect(url_for("customer.my_orders"))

    if order["status"] not in ("Placed", "Confirmed"):
        flash("This order cannot be cancelled at its current stage.", "warning")
        return redirect(url_for("customer.my_orders"))

    try:
        transaction([
            ("UPDATE orders SET status='Cancelled' WHERE id=%s", (order_id,)),
            ("UPDATE fuel_inventory SET available_litres = available_litres + %s WHERE fuel_type=%s",
             (float(order["quantity_litres"]), order["fuel_type"])),
            ("UPDATE payments SET payment_status='Refunded' WHERE order_id=%s", (order_id,)),
        ])
        flash(f"Order {order['order_code']} has been cancelled and stock restored.", "success")
    except Exception as e:
        flash(f"Cancellation failed: {e}", "danger")
    return redirect(url_for("customer.my_orders"))


# ── TRACK ORDER ────────────────────────────────────────────────────────────────
@customer_bp.route("/track-order")
@role_required("customer")
def track_order():
    cid = _cid()
    order_id = request.args.get("id", 0, type=int)

    all_orders = query(
        "SELECT id, order_code, fuel_type, status, preferred_date FROM orders WHERE customer_id=%s ORDER BY created_at DESC",
        (cid,)
    )
    order   = None
    payment = None

    if order_id:
        order = query("""
            SELECT o.*, d.full_name AS partner_name, d.phone AS partner_phone,
                   d.vehicle_number AS partner_vehicle
            FROM orders o
            LEFT JOIN delivery_partners d ON o.delivery_partner_id = d.id
            WHERE o.id=%s AND o.customer_id=%s LIMIT 1
        """, (order_id, cid), one=True)

        if order:
            payment = query("SELECT * FROM payments WHERE order_id=%s LIMIT 1",
                            (order_id,), one=True)

    STAGES = [
        ("Placed",           "Order Placed"),
        ("Confirmed",        "Order Confirmed"),
        ("Partner Assigned", "Delivery Partner Assigned"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered",        "Delivered"),
    ]
    return render_template("customer/track_order.html",
                           all_orders=all_orders,
                           order=order,
                           payment=payment,
                           stages=STAGES,
                           selected_id=order_id)


# ── FEEDBACK ───────────────────────────────────────────────────────────────────
@customer_bp.route("/feedback", methods=["GET", "POST"])
@role_required("customer")
def feedback():
    cid = _cid()
    delivered_orders = query("""
        SELECT o.id, o.order_code, o.fuel_type, o.created_at
        FROM orders o
        LEFT JOIN feedback f ON f.order_id = o.id
        WHERE o.customer_id=%s AND o.status='Delivered' AND f.id IS NULL
        ORDER BY o.created_at DESC
    """, (cid,))

    if request.method == "POST":
        order_id = request.form.get("order_id", 0, type=int)
        rating   = request.form.get("rating", 5, type=int)
        message  = request.form.get("message", "").strip()

        if not order_id or not message or not (1 <= rating <= 5):
            flash("Please select an order, give a rating, and write a message.", "danger")
        else:
            # verify order belongs to customer and is delivered
            ord_row = query("SELECT id FROM orders WHERE id=%s AND customer_id=%s AND status='Delivered' LIMIT 1",
                            (order_id, cid), one=True)
            if not ord_row:
                flash("Invalid order selected for feedback.", "danger")
            else:
                try:
                    query("INSERT INTO feedback (order_id, customer_id, rating, message) VALUES (%s,%s,%s,%s)",
                          (order_id, cid, rating, message), commit=True)
                    flash("Thank you for your feedback! ⭐", "success")
                    return redirect(url_for("customer.feedback"))
                except Exception as e:
                    flash(f"Could not submit feedback: {e}", "danger")

    return render_template("customer/feedback.html", delivered_orders=delivered_orders)


# ── PROFILE ────────────────────────────────────────────────────────────────────
@customer_bp.route("/profile", methods=["GET", "POST"])
@role_required("customer")
def profile():
    cid     = _cid()
    user_id = session.get("user_id")
    errors  = []
    success = False

    cust = query("SELECT * FROM customers WHERE id=%s LIMIT 1", (cid,), one=True)
    user = query("SELECT * FROM users WHERE id=%s LIMIT 1", (user_id,), one=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            full_name = request.form.get("full_name", "").strip()
            phone     = request.form.get("phone", "").strip()
            address   = request.form.get("address", "").strip()
            city      = request.form.get("city", "").strip()
            pincode   = request.form.get("pincode", "").strip()

            if not full_name: errors.append("Full name required.")
            if len(phone) < 10: errors.append("Valid phone number required.")
            if not address: errors.append("Address required.")

            if not errors:
                query("UPDATE customers SET full_name=%s, phone=%s, address=%s, city=%s, pincode=%s WHERE id=%s",
                      (full_name, phone, address, city, pincode, cid), commit=True)
                session["full_name"] = full_name
                session["phone"]     = phone
                session["address"]   = address
                session["city"]      = city
                session["pincode"]   = pincode
                flash("Profile updated successfully!", "success")
                return redirect(url_for("customer.profile"))

        elif action == "change_password":
            cur_pw  = request.form.get("current_password", "")
            new_pw  = request.form.get("new_password", "")
            conf_pw = request.form.get("confirm_password", "")

            if not check_password_hash(user["password"], cur_pw):
                errors.append("Current password is incorrect.")
            if len(new_pw) < 6:
                errors.append("New password must be at least 6 characters.")
            if new_pw != conf_pw:
                errors.append("New passwords do not match.")

            if not errors:
                query("UPDATE users SET password=%s WHERE id=%s",
                      (generate_password_hash(new_pw), user_id), commit=True)
                flash("Password changed successfully!", "success")
                return redirect(url_for("customer.profile"))

    return render_template("customer/profile.html",
                           cust=cust, user=user, errors=errors)
