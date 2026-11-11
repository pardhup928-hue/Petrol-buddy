"""
Petrol Buddy – Online Petrol Delivery System
Main Flask Application Entry Point
Tech Stack: Flask + MySQL (mysql-connector-python) + Jinja2 + Werkzeug
"""

import os
from flask import Flask, render_template, redirect, url_for, flash, session, request
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "petrolbuddy_dev_secret_2026")
    app.config["DB_HOST"]     = os.getenv("DB_HOST", "localhost")
    app.config["DB_PORT"]     = int(os.getenv("DB_PORT", 3306))
    app.config["DB_USER"]     = os.getenv("DB_USER", "root")
    app.config["DB_PASSWORD"] = os.getenv("DB_PASSWORD", "")
    app.config["DB_NAME"]     = os.getenv("DB_NAME", "petrol_buddy")

    # ── Blueprints ────────────────────────────────────────────────────
    from routes.auth     import auth_bp
    from routes.customer import customer_bp
    from routes.admin    import admin_bp
    from routes.delivery import delivery_bp
    from routes.public   import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp,     url_prefix="/auth")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(admin_bp,    url_prefix="/admin")
    app.register_blueprint(delivery_bp, url_prefix="/delivery")

    # ── Global template helpers ───────────────────────────────────────
    from db import get_db
    import datetime

    @app.context_processor
    def inject_globals():
        user = None
        if "user_id" in session:
            user = {
                "id":        session.get("user_id"),
                "email":     session.get("email"),
                "role":      session.get("role"),
                "role_id":   session.get("role_id"),
                "full_name": session.get("full_name", "User"),
                "phone":     session.get("phone", ""),
                "address":   session.get("address", ""),
                "city":      session.get("city", ""),
                "pincode":   session.get("pincode", ""),
            }
        return {"current_user": user, "now": datetime.datetime.now()}

    @app.template_filter("currency")
    def currency_filter(value):
        try:
            return "₹{:,.2f}".format(float(value))
        except (TypeError, ValueError):
            return "₹0.00"

    @app.template_filter("fmt_date")
    def fmt_date_filter(value):
        if not value:
            return "N/A"
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.strftime("%d %b %Y")
        try:
            return datetime.datetime.strptime(str(value), "%Y-%m-%d").strftime("%d %b %Y")
        except Exception:
            return str(value)

    @app.template_filter("fmt_datetime")
    def fmt_datetime_filter(value):
        if not value:
            return "N/A"
        if isinstance(value, datetime.datetime):
            return value.strftime("%d %b %Y, %I:%M %p")
        try:
            return datetime.datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S").strftime("%d %b %Y, %I:%M %p")
        except Exception:
            return str(value)

    @app.template_filter("stars")
    def stars_filter(rating):
        try:
            n = int(rating)
            return "★" * n + "☆" * (5 - n)
        except Exception:
            return "★★★★★"

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("  🔥 PETROL BUDDY — Online Petrol Delivery System")
    print("  ✅ Flask Dev Server starting...")
    print("  🌐 Open: http://127.0.0.1:5000")
    print("  🛑 Press CTRL+C to stop")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
