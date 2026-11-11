"""Petrol Buddy – Admin routes."""

import datetime
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)
from werkzeug.security import generate_password_hash
from auth_helpers import role_required
from db import query, transaction

admin_bp = Blueprint("admin", __name__)


# ── DASHBOARD ──────────────────────────────────────────────────────────────────
@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    stats, recent, low_stock = {}, [], []
    try:
        stats["orders_total"]   = query("SELECT COUNT(*) AS n FROM orders", one=True)["n"]
        stats["orders_today"]   = query("SELECT COUNT(*) AS n FROM orders WHERE DATE(created_at)=CURDATE()", one=True)["n"]
        stats["pending"]        = query("SELECT COUNT(*) AS n FROM orders WHERE status='Placed'", one=True)["n"]
        stats["active"]         = query("SELECT COUNT(*) AS n FROM orders WHERE status IN ('Confirmed','Partner Assigned','Out for Delivery')", one=True)["n"]
        stats["delivered"]      = query("SELECT COUNT(*) AS n FROM orders WHERE status='Delivered'", one=True)["n"]
        stats["revenue"]        = query("SELECT COALESCE(SUM(amount),0) AS s FROM payments WHERE payment_status='Paid'", one=True)["s"]
        stats["customers"]      = query("SELECT COUNT(*) AS n FROM customers", one=True)["n"]
        stats["partners_ready"] = query("SELECT COUNT(*) AS n FROM delivery_partners WHERE is_available=1", one=True)["n"]

        recent = query("""
            SELECT o.*, c.full_name AS customer_name, d.full_name AS partner_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            LEFT JOIN delivery_partners d ON o.delivery_partner_id = d.id
            ORDER BY o.created_at DESC LIMIT 10
        """)
        low_stock = query("SELECT * FROM fuel_inventory WHERE available_litres <= minimum_threshold")
    except Exception as e:
        flash(f"Dashboard error: {e}", "danger")

    return render_template("admin/dashboard.html", stats=stats, recent=recent, low_stock=low_stock)


# ── MANAGE ORDERS ──────────────────────────────────────────────────────────────
@admin_bp.route("/orders", methods=["GET", "POST"])
@role_required("admin")
def manage_orders():
    # Handle POST actions
    if request.method == "POST":
        action   = request.form.get("action")
        order_id = request.form.get("order_id", 0, type=int)

        try:
            order = query("SELECT * FROM orders WHERE id=%s LIMIT 1", (order_id,), one=True)
            if not order:
                flash("Order not found.", "danger")
                return redirect(url_for("admin.manage_orders"))

            if action == "confirm" and order["status"] == "Placed":
                query("UPDATE orders SET status='Confirmed' WHERE id=%s", (order_id,), commit=True)
                flash(f"Order {order['order_code']} confirmed.", "success")

            elif action == "reject" and order["status"] in ("Placed", "Confirmed"):
                reason = request.form.get("rejection_reason", "No reason given.").strip()
                transaction([
                    ("UPDATE orders SET status='Rejected', rejection_reason=%s WHERE id=%s", (reason, order_id)),
                    ("UPDATE fuel_inventory SET available_litres=available_litres+%s WHERE fuel_type=%s",
                     (float(order["quantity_litres"]), order["fuel_type"])),
                    ("UPDATE payments SET payment_status='Refunded' WHERE order_id=%s", (order_id,)),
                ])
                flash(f"Order {order['order_code']} rejected.", "warning")

            elif action == "assign":
                partner_id = request.form.get("partner_id", 0, type=int)
                if order["status"] != "Confirmed":
                    flash("Only confirmed orders can have a partner assigned.", "warning")
                elif not partner_id:
                    flash("Please select a delivery partner.", "danger")
                else:
                    query("UPDATE orders SET delivery_partner_id=%s, status='Partner Assigned' WHERE id=%s",
                          (partner_id, order_id), commit=True)
                    flash("Delivery partner assigned successfully.", "success")

            elif action == "status_update":
                new_status = request.form.get("new_status", "")
                ALLOWED = {
                    "Confirmed":        ["Partner Assigned"],
                    "Partner Assigned": ["Out for Delivery", "Cancelled"],
                    "Out for Delivery": ["Delivered", "Cancelled"],
                }
                if new_status in ALLOWED.get(order["status"], []):
                    stmts = [("UPDATE orders SET status=%s WHERE id=%s", (new_status, order_id))]
                    if new_status == "Delivered":
                        stmts.append(("UPDATE payments SET payment_status='Paid' WHERE order_id=%s AND payment_method='Cash on Delivery'", (order_id,)))
                    if new_status == "Cancelled":
                        stmts.append(("UPDATE fuel_inventory SET available_litres=available_litres+%s WHERE fuel_type=%s",
                                      (float(order["quantity_litres"]), order["fuel_type"])))
                        stmts.append(("UPDATE payments SET payment_status='Refunded' WHERE order_id=%s", (order_id,)))
                    transaction(stmts)
                    flash(f"Order status updated to '{new_status}'.", "success")
                else:
                    flash("Invalid status transition.", "danger")
        except Exception as e:
            flash(f"Action failed: {e}", "danger")

        return redirect(url_for("admin.manage_orders"))

    # GET – list orders with filters
    status_filter = request.args.get("status", "")
    search        = request.args.get("q", "").strip()
    date_from     = request.args.get("from", "")
    date_to       = request.args.get("to", "")

    sql    = """SELECT o.*, c.full_name AS customer_name, d.full_name AS partner_name
                FROM orders o
                JOIN customers c ON o.customer_id = c.id
                LEFT JOIN delivery_partners d ON o.delivery_partner_id = d.id
                WHERE 1=1"""
    params = []

    if status_filter:
        sql += " AND o.status=%s"; params.append(status_filter)
    if search:
        sql += " AND (o.order_code LIKE %s OR c.full_name LIKE %s OR c.phone LIKE %s)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    if date_from:
        sql += " AND DATE(o.created_at) >= %s"; params.append(date_from)
    if date_to:
        sql += " AND DATE(o.created_at) <= %s"; params.append(date_to)
    sql += " ORDER BY o.created_at DESC"

    orders   = query(sql, params)
    partners = query("SELECT id, full_name, phone FROM delivery_partners WHERE is_available=1 ORDER BY full_name")
    statuses = ["Placed","Confirmed","Partner Assigned","Out for Delivery","Delivered","Cancelled","Rejected"]

    return render_template("admin/manage_orders.html",
                           orders=orders, partners=partners, statuses=statuses,
                           status_filter=status_filter, search=search,
                           date_from=date_from, date_to=date_to)


# ── INVENTORY ──────────────────────────────────────────────────────────────────
@admin_bp.route("/inventory", methods=["GET", "POST"])
@role_required("admin")
def manage_inventory():
    if request.method == "POST":
        fuel_type = request.form.get("fuel_type")
        action    = request.form.get("action")
        try:
            amount = float(request.form.get("amount", 0))
        except ValueError:
            amount = 0

        if fuel_type in ("Petrol", "Diesel") and amount > 0:
            if action == "add":
                query("UPDATE fuel_inventory SET available_litres=available_litres+%s WHERE fuel_type=%s",
                      (amount, fuel_type), commit=True)
                flash(f"Added {amount}L to {fuel_type} stock.", "success")
            elif action == "set":
                query("UPDATE fuel_inventory SET available_litres=%s WHERE fuel_type=%s",
                      (amount, fuel_type), commit=True)
                flash(f"{fuel_type} stock set to {amount}L.", "success")
            elif action == "threshold":
                query("UPDATE fuel_inventory SET minimum_threshold=%s WHERE fuel_type=%s",
                      (amount, fuel_type), commit=True)
                flash(f"{fuel_type} low-stock threshold updated.", "success")
        else:
            flash("Invalid data provided.", "danger")
        return redirect(url_for("admin.manage_inventory"))

    inventory = query("SELECT * FROM fuel_inventory ORDER BY fuel_type")
    return render_template("admin/manage_inventory.html", inventory=inventory)


# ── PRICES ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/prices", methods=["GET", "POST"])
@role_required("admin")
def manage_prices():
    if request.method == "POST":
        for ft in ("Petrol", "Diesel"):
            price_key = f"price_{ft.lower()}"
            try:
                price = float(request.form.get(price_key, 0))
                if price > 0:
                    query("UPDATE fuel_prices SET price_per_litre=%s WHERE fuel_type=%s",
                          (price, ft), commit=True)
            except ValueError:
                pass
        flash("Fuel prices updated successfully.", "success")
        return redirect(url_for("admin.manage_prices"))

    prices = query("SELECT * FROM fuel_prices ORDER BY fuel_type")
    return render_template("admin/manage_prices.html", prices=prices)


# ── CUSTOMERS ──────────────────────────────────────────────────────────────────
@admin_bp.route("/customers", methods=["GET", "POST"])
@role_required("admin")
def manage_customers():
    if request.method == "POST":
        user_id = request.form.get("user_id", 0, type=int)
        action  = request.form.get("action")
        new_status = "active" if action == "activate" else "inactive"
        query("UPDATE users SET status=%s WHERE id=%s AND role='customer'",
              (new_status, user_id), commit=True)
        flash(f"Customer account {'activated' if new_status=='active' else 'deactivated'}.", "success")
        return redirect(url_for("admin.manage_customers"))

    search = request.args.get("q", "").strip()
    sql = """SELECT c.*, u.email, u.status, u.created_at AS joined
             FROM customers c JOIN users u ON c.user_id=u.id WHERE 1=1"""
    params = []
    if search:
        sql += " AND (c.full_name LIKE %s OR u.email LIKE %s OR c.phone LIKE %s)"
        params += [f"%{search}%", f"%{search}%", f"%{search}%"]
    sql += " ORDER BY u.created_at DESC"
    customers = query(sql, params)
    return render_template("admin/manage_customers.html", customers=customers, search=search)


# ── DELIVERY PARTNERS ──────────────────────────────────────────────────────────
@admin_bp.route("/delivery-partners", methods=["GET", "POST"])
@role_required("admin")
def manage_delivery_partners():
    errors = []
    if request.method == "POST":
        action = request.form.get("action")

        if action == "add":
            full_name      = request.form.get("full_name", "").strip()
            email          = request.form.get("email", "").strip().lower()
            phone          = request.form.get("phone", "").strip()
            address        = request.form.get("address", "").strip()
            vehicle_number = request.form.get("vehicle_number", "").strip()
            password       = request.form.get("password", "").strip()

            if not all([full_name, email, phone, address, vehicle_number, password]):
                errors.append("All fields are required.")
            elif query("SELECT id FROM users WHERE email=%s LIMIT 1", (email,), one=True):
                errors.append("A user with that email already exists.")
            else:
                try:
                    hashed = generate_password_hash(password)
                    user_id = query("INSERT INTO users (email, password, role, status) VALUES (%s,%s,'delivery','active')",
                                    (email, hashed), commit=True)
                    query("INSERT INTO delivery_partners (user_id, full_name, phone, address, vehicle_number) VALUES (%s,%s,%s,%s,%s)",
                          (user_id, full_name, phone, address, vehicle_number), commit=True)
                    flash(f"Delivery partner '{full_name}' added.", "success")
                    return redirect(url_for("admin.manage_delivery_partners"))
                except Exception as e:
                    errors.append(f"Failed to add partner: {e}")

        elif action in ("activate", "deactivate"):
            user_id    = request.form.get("user_id", 0, type=int)
            new_status = "active" if action == "activate" else "inactive"
            query("UPDATE users SET status=%s WHERE id=%s", (new_status, user_id), commit=True)
            flash(f"Partner account {action}d.", "success")
            return redirect(url_for("admin.manage_delivery_partners"))

        elif action == "toggle_availability":
            partner_id = request.form.get("partner_id", 0, type=int)
            partner    = query("SELECT is_available FROM delivery_partners WHERE id=%s LIMIT 1",
                               (partner_id,), one=True)
            if partner:
                new_avail = 0 if partner["is_available"] else 1
                query("UPDATE delivery_partners SET is_available=%s WHERE id=%s",
                      (new_avail, partner_id), commit=True)
                flash("Availability updated.", "success")
            return redirect(url_for("admin.manage_delivery_partners"))

    partners = query("""
        SELECT dp.*, u.email, u.status
        FROM delivery_partners dp JOIN users u ON dp.user_id=u.id
        ORDER BY dp.full_name
    """)
    return render_template("admin/manage_delivery_partners.html",
                           partners=partners, errors=errors)


# ── PAYMENTS ───────────────────────────────────────────────────────────────────
@admin_bp.route("/payments", methods=["GET", "POST"])
@role_required("admin")
def manage_payments():
    if request.method == "POST":
        payment_id = request.form.get("payment_id", 0, type=int)
        import random, string
        ref = "COD-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        query("UPDATE payments SET payment_status='Paid', transaction_ref=%s WHERE id=%s",
              (ref, payment_id), commit=True)
        flash("Payment marked as Paid.", "success")
        return redirect(url_for("admin.manage_payments"))

    payments = query("""
        SELECT p.*, o.order_code, o.fuel_type, c.full_name AS customer_name
        FROM payments p
        JOIN orders o ON p.order_id = o.id
        JOIN customers c ON o.customer_id = c.id
        ORDER BY p.payment_date DESC
    """)
    return render_template("admin/manage_payments.html", payments=payments)


# ── FEEDBACK ───────────────────────────────────────────────────────────────────
@admin_bp.route("/feedback")
@role_required("admin")
def manage_feedback():
    feedback_list = query("""
        SELECT f.*, c.full_name AS customer_name, o.order_code, o.fuel_type
        FROM feedback f
        JOIN customers c ON f.customer_id = c.id
        JOIN orders    o ON f.order_id    = o.id
        ORDER BY f.created_at DESC
    """)
    avg = query("SELECT ROUND(AVG(rating),1) AS avg FROM feedback", one=True)
    avg_rating = avg["avg"] if avg and avg["avg"] else 0
    return render_template("admin/manage_feedback.html",
                           feedback_list=feedback_list, avg_rating=avg_rating)


# ── REPORTS ────────────────────────────────────────────────────────────────────
@admin_bp.route("/reports")
@role_required("admin")
def reports():
    from_date   = request.args.get("from", datetime.date.today().replace(day=1).isoformat())
    to_date     = request.args.get("to",   datetime.date.today().isoformat())
    fuel_filter = request.args.get("fuel", "")
    if fuel_filter not in ("Petrol", "Diesel"):
        fuel_filter = ""

    where  = "WHERE DATE(o.created_at) BETWEEN %s AND %s"
    params = [from_date, to_date]
    if fuel_filter:
        where += " AND o.fuel_type=%s"
        params.append(fuel_filter)

    summary = query(f"""
        SELECT COUNT(*) AS total_orders,
               SUM(CASE WHEN o.status='Delivered' THEN 1 ELSE 0 END) AS delivered,
               SUM(CASE WHEN o.status IN ('Cancelled','Rejected') THEN 1 ELSE 0 END) AS lost,
               COALESCE(SUM(CASE WHEN o.status NOT IN ('Cancelled','Rejected') THEN o.quantity_litres ELSE 0 END),0) AS litres,
               COALESCE(SUM(CASE WHEN o.status NOT IN ('Cancelled','Rejected') THEN o.total_amount ELSE 0 END),0) AS gross
        FROM orders o {where}
    """, params, one=True)

    revenue_collected = query(f"""
        SELECT COALESCE(SUM(p.amount),0) AS paid
        FROM payments p JOIN orders o ON o.id=p.order_id
        {where} AND p.payment_status='Paid'
    """, params, one=True)

    fuel_breakdown = query(f"""
        SELECT o.fuel_type,
               COUNT(*) AS orders,
               COALESCE(SUM(o.quantity_litres),0) AS litres,
               COALESCE(SUM(o.total_amount),0) AS revenue
        FROM orders o {where} AND o.status NOT IN ('Cancelled','Rejected')
        GROUP BY o.fuel_type
    """, params)

    daily = query(f"""
        SELECT DATE(o.created_at) AS day, COUNT(*) AS orders,
               COALESCE(SUM(o.total_amount),0) AS revenue
        FROM orders o {where}
        GROUP BY DATE(o.created_at)
        ORDER BY day DESC
    """, params)

    return render_template("admin/reports.html",
                           summary=summary,
                           revenue_collected=revenue_collected,
                           fuel_breakdown=fuel_breakdown,
                           daily=daily,
                           from_date=from_date,
                           to_date=to_date,
                           fuel_filter=fuel_filter)
