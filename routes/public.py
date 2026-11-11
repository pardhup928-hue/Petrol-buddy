"""Petrol Buddy – Public (unauthenticated) routes."""

from flask import Blueprint, render_template, session
from db import query

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def index():
    prices = {}
    feedback_list = []
    try:
        rows = query("SELECT fuel_type, price_per_litre FROM fuel_prices")
        prices = {r["fuel_type"]: float(r["price_per_litre"]) for r in rows}
        feedback_list = query("""
            SELECT f.rating, f.message, f.created_at,
                   c.full_name, c.city, o.fuel_type
            FROM feedback f
            JOIN customers c ON f.customer_id = c.id
            JOIN orders    o ON f.order_id    = o.id
            ORDER BY f.created_at DESC
            LIMIT 3
        """)
    except Exception:
        pass
    return render_template("index.html", prices=prices, feedback_list=feedback_list)


@public_bp.route("/about")
def about():
    return render_template("about.html")


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    from flask import request, flash, redirect, url_for
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        email   = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if name and email and message:
            flash(f"Thank you, {name}! Your message has been received. We'll contact you shortly.", "success")
            return redirect(url_for("public.contact"))
        flash("Please fill in all required fields.", "danger")
    return render_template("contact.html")
