"""Petrol Buddy – Delivery Partner routes."""

from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)
from werkzeug.security import generate_password_hash, check_password_hash
from auth_helpers import role_required
from db import query, transaction

delivery_bp = Blueprint("delivery", __name__)


def _pid():
    return int(session.get("role_id", 0))


# ── DASHBOARD ──────────────────────────────────────────────────────────────────
@delivery_bp.route("/dashboard")
@role_required("delivery")
def dashboard():
    pid = _pid()
    stats, active_jobs, recent_done, partner = {}, [], [], None
    try:
        partner = query("SELECT * FROM delivery_partners WHERE id=%s LIMIT 1", (pid,), one=True)
        stats["assigned"]  = query("SELECT COUNT(*) AS n FROM orders WHERE delivery_partner_id=%s AND status='Partner Assigned'", (pid,), one=True)["n"]
        stats["out"]       = query("SELECT COUNT(*) AS n FROM orders WHERE delivery_partner_id=%s AND status='Out for Delivery'", (pid,), one=True)["n"]
        stats["delivered"] = query("SELECT COUNT(*) AS n FROM orders WHERE delivery_partner_id=%s AND status='Delivered'", (pid,), one=True)["n"]
        stats["earnings"]  = query("SELECT COALESCE(SUM(p.amount),0) AS s FROM payments p JOIN orders o ON o.id=p.order_id WHERE o.delivery_partner_id=%s AND p.payment_status='Paid'", (pid,), one=True)["s"]

        active_jobs = query("""
            SELECT o.*, c.full_name AS customer_name, c.phone AS customer_phone
            FROM orders o JOIN customers c ON o.customer_id=c.id
            WHERE o.delivery_partner_id=%s AND o.status IN ('Partner Assigned','Out for Delivery')
            ORDER BY o.preferred_date, o.preferred_time
        """, (pid,))

        recent_done = query("""
            SELECT o.*, c.full_name AS customer_name
            FROM orders o JOIN customers c ON o.customer_id=c.id
            WHERE o.delivery_partner_id=%s AND o.status='Delivered'
            ORDER BY o.updated_at DESC LIMIT 5
        """, (pid,))
    except Exception as e:
        flash(f"Dashboard error: {e}", "danger")

    return render_template("delivery/dashboard.html",
                           stats=stats, active_jobs=active_jobs,
                           recent_done=recent_done, partner=partner)


# ── ASSIGNED ORDERS ────────────────────────────────────────────────────────────
@delivery_bp.route("/assigned-orders")
@role_required("delivery")
def assigned_orders():
    pid = _pid()
    orders = query("""
        SELECT o.*, c.full_name AS customer_name, c.phone AS customer_phone
        FROM orders o JOIN customers c ON o.customer_id=c.id
        WHERE o.delivery_partner_id=%s AND o.status IN ('Partner Assigned','Out for Delivery')
        ORDER BY o.preferred_date, o.preferred_time
    """, (pid,))
    return render_template("delivery/assigned_orders.html", orders=orders)


# ── ORDER DETAILS ──────────────────────────────────────────────────────────────
@delivery_bp.route("/order/<int:order_id>", methods=["GET", "POST"])
@role_required("delivery")
def order_details(order_id):
    pid = _pid()
    order = query("""
        SELECT o.*, c.full_name AS customer_name, c.phone AS customer_phone, c.address AS customer_address
        FROM orders o JOIN customers c ON o.customer_id=c.id
        WHERE o.id=%s AND o.delivery_partner_id=%s LIMIT 1
    """, (order_id, pid), one=True)

    if not order:
        flash("Order not found or not assigned to you.", "danger")
        return redirect(url_for("delivery.assigned_orders"))

    payment = query("SELECT * FROM payments WHERE order_id=%s LIMIT 1", (order_id,), one=True)

    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "start" and order["status"] == "Partner Assigned":
                query("UPDATE orders SET status='Out for Delivery' WHERE id=%s", (order_id,), commit=True)
                flash("Delivery started! Drive safely. 🚚", "success")
                return redirect(url_for("delivery.order_details", order_id=order_id))

            elif action == "complete" and order["status"] == "Out for Delivery":
                stmts = [
                    ("UPDATE orders SET status='Delivered' WHERE id=%s", (order_id,)),
                ]
                if order["payment_method"] == "Cash on Delivery":
                    import random, string
                    ref = "COD-" + "".join(random.choices(string.ascii_uppercase+string.digits, k=8))
                    stmts.append(("UPDATE payments SET payment_status='Paid', transaction_ref=%s WHERE order_id=%s", (ref, order_id)))
                transaction(stmts)
                flash(f"Order {order['order_code']} marked as Delivered! 🎉", "success")
                return redirect(url_for("delivery.delivery_history"))
            else:
                flash("Action not allowed at the current order status.", "warning")
        except Exception as e:
            flash(f"Action failed: {e}", "danger")

    return render_template("delivery/order_details.html", order=order, payment=payment)


# ── DELIVERY HISTORY ───────────────────────────────────────────────────────────
@delivery_bp.route("/history")
@role_required("delivery")
def delivery_history():
    pid = _pid()
    orders = query("""
        SELECT o.*, c.full_name AS customer_name, c.phone AS customer_phone
        FROM orders o JOIN customers c ON o.customer_id=c.id
        WHERE o.delivery_partner_id=%s AND o.status='Delivered'
        ORDER BY o.updated_at DESC
    """, (pid,))
    return render_template("delivery/delivery_history.html", orders=orders)


# ── PROFILE ────────────────────────────────────────────────────────────────────
@delivery_bp.route("/profile", methods=["GET", "POST"])
@role_required("delivery")
def profile():
    pid     = _pid()
    user_id = session.get("user_id")
    errors  = []

    partner = query("SELECT * FROM delivery_partners WHERE id=%s LIMIT 1", (pid,), one=True)
    user    = query("SELECT * FROM users WHERE id=%s LIMIT 1", (user_id,), one=True)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_profile":
            full_name      = request.form.get("full_name", "").strip()
            phone          = request.form.get("phone", "").strip()
            address        = request.form.get("address", "").strip()
            vehicle_number = request.form.get("vehicle_number", "").strip()

            if not full_name: errors.append("Full name required.")
            if len(phone) < 10: errors.append("Valid phone required.")

            if not errors:
                query("UPDATE delivery_partners SET full_name=%s, phone=%s, address=%s, vehicle_number=%s WHERE id=%s",
                      (full_name, phone, address, vehicle_number, pid), commit=True)
                session["full_name"] = full_name
                session["phone"]     = phone
                flash("Profile updated!", "success")
                return redirect(url_for("delivery.profile"))

        elif action == "change_password":
            cur_pw  = request.form.get("current_password", "")
            new_pw  = request.form.get("new_password", "")
            conf_pw = request.form.get("confirm_password", "")

            if not check_password_hash(user["password"], cur_pw):
                errors.append("Current password is incorrect.")
            if len(new_pw) < 6:
                errors.append("New password must be at least 6 characters.")
            if new_pw != conf_pw:
                errors.append("Passwords do not match.")

            if not errors:
                query("UPDATE users SET password=%s WHERE id=%s",
                      (generate_password_hash(new_pw), user_id), commit=True)
                flash("Password changed!", "success")
                return redirect(url_for("delivery.profile"))

        elif action == "toggle_availability":
            new_val = 0 if partner["is_available"] else 1
            query("UPDATE delivery_partners SET is_available=%s WHERE id=%s",
                  (new_val, pid), commit=True)
            session["is_available"] = new_val
            flash(f"Availability set to {'Available' if new_val else 'Unavailable'}.", "success")
            return redirect(url_for("delivery.profile"))

    return render_template("delivery/profile.html",
                           partner=partner, user=user, errors=errors)
