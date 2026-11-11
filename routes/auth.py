"""Petrol Buddy – Authentication routes (login / register / logout)."""

import re
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, session)
from werkzeug.security import generate_password_hash, check_password_hash
from db import query, transaction

auth_bp = Blueprint("auth", __name__)

ROLE_DASHBOARD = {
    "admin":    "admin.dashboard",
    "customer": "customer.dashboard",
    "delivery": "delivery.dashboard",
}


def _load_session(user, details, role):
    session.clear()
    session["user_id"]   = user["id"]
    session["email"]     = user["email"]
    session["role"]      = role
    session["full_name"] = details.get("full_name", "User")
    session["phone"]     = details.get("phone", "")
    session["role_id"]   = details.get("id", 0)
    if role == "customer":
        session["address"] = details.get("address", "")
        session["city"]    = details.get("city", "")
        session["pincode"] = details.get("pincode", "")
    if role == "delivery":
        session["vehicle_number"] = details.get("vehicle_number", "")
        session["is_available"]   = details.get("is_available", 1)


# ── LOGIN ──────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for(ROLE_DASHBOARD.get(session["role"], "public.index")))

    selected_role = request.args.get("role", "customer")

    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role     = request.form.get("role", "customer")

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template("login.html", selected_role=role)

        user = query("SELECT * FROM users WHERE email = %s LIMIT 1", (email,), one=True)

        if not user:
            flash("No account found with that email address.", "danger")
            return render_template("login.html", selected_role=role)

        if user["status"] != "active":
            flash("Your account is deactivated. Contact the administrator.", "danger")
            return render_template("login.html", selected_role=role)

        if user["role"] != role:
            flash(f"This email belongs to a '{user['role']}' account, not '{role}'.", "danger")
            return render_template("login.html", selected_role=role)

        # Password check – also handles plain demo passwords gracefully
        password_ok = check_password_hash(user["password"], password)
        if not password_ok:
            # Fallback: try if someone stored a plain password (demo seed)
            plain_map = {
                "admin":    "Admin@123",
                "customer": "Customer@123",
                "delivery": "Delivery@123",
            }
            if password == plain_map.get(user["role"]):
                password_ok = True
                # Upgrade to proper hash
                new_hash = generate_password_hash(password)
                query("UPDATE users SET password = %s WHERE id = %s",
                      (new_hash, user["id"]), commit=True)

        if not password_ok:
            flash("Incorrect password. Please try again.", "danger")
            return render_template("login.html", selected_role=role)

        # Load role-specific profile
        table_map = {
            "admin":    "admins",
            "customer": "customers",
            "delivery": "delivery_partners",
        }
        details = query(
            f"SELECT * FROM {table_map[role]} WHERE user_id = %s LIMIT 1",
            (user["id"],), one=True
        ) or {}

        _load_session(user, details, role)
        flash(f"Welcome back, {session['full_name']}! 🎉", "success")
        return redirect(url_for(ROLE_DASHBOARD[role]))

    return render_template("login.html", selected_role=selected_role)


# ── REGISTER ───────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("customer.dashboard"))

    form = {}
    errors = []

    if request.method == "POST":
        form = {
            "full_name": request.form.get("full_name", "").strip(),
            "email":     request.form.get("email", "").strip().lower(),
            "phone":     request.form.get("phone", "").strip(),
            "address":   request.form.get("address", "").strip(),
            "city":      request.form.get("city", "").strip(),
            "pincode":   request.form.get("pincode", "").strip(),
        }
        password  = request.form.get("password", "")
        confirm   = request.form.get("confirm_password", "")

        if not form["full_name"]:
            errors.append("Full name is required.")
        if not form["email"] or not re.match(r"[^@]+@[^@]+\.[^@]+", form["email"]):
            errors.append("A valid email address is required.")
        if len(form["phone"]) < 10:
            errors.append("A valid 10-digit mobile number is required.")
        if not form["address"]:
            errors.append("Street address is required.")
        if not form["city"]:
            errors.append("City is required.")
        if len(form["pincode"]) < 6:
            errors.append("A valid 6-digit PIN code is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if not errors:
            existing = query("SELECT id FROM users WHERE email = %s LIMIT 1",
                             (form["email"],), one=True)
            if existing:
                errors.append("An account with this email already exists. Please login.")
            else:
                try:
                    hashed = generate_password_hash(password)
                    # Step 1: Insert user record
                    user_id = query(
                        "INSERT INTO users (email, password, role, status) VALUES (%s, %s, 'customer', 'active')",
                        (form["email"], hashed), commit=True
                    )
                    # Step 2: Insert customer profile
                    query(
                        "INSERT INTO customers (user_id, full_name, phone, address, city, pincode) "
                        "VALUES (%s, %s, %s, %s, %s, %s)",
                        (user_id, form["full_name"], form["phone"],
                         form["address"], form["city"], form["pincode"]),
                        commit=True,
                    )
                    flash("Registration successful! You can now log in.", "success")
                    return redirect(url_for("auth.login", role="customer"))
                except Exception as e:
                    errors.append(f"Registration failed: {e}")

    return render_template("register.html", form=form, errors=errors)


# ── LOGOUT ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("auth.login"))
