"""
Petrol Buddy – Authentication Helpers
Role-based access control decorators for Flask routes.
"""

import functools
from flask import session, redirect, url_for, flash


def login_required(f):
    """Redirect to login if not authenticated."""
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def role_required(*allowed_roles):
    """Redirect to correct dashboard if the user's role is not allowed."""
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("auth.login"))
            role = session.get("role")
            if role not in allowed_roles:
                flash("You are not authorized to view that page.", "danger")
                dashboard_map = {
                    "admin":    "admin.dashboard",
                    "customer": "customer.dashboard",
                    "delivery": "delivery.dashboard",
                }
                return redirect(url_for(dashboard_map.get(role, "public.index")))
            return f(*args, **kwargs)
        return decorated
    return decorator
