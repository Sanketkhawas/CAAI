from flask import Blueprint, render_template

dashboard = Blueprint("dashboard", __name__)

@dashboard.route("/dashboard")
def dashboard_page():

    user = {
        "name": "Disha"
    }

    stats = {
        "documents": 0,
        "tax": "₹0",
        "savings": "₹0",
        "ai": 0
    }

    return render_template(
        "dashboard.html",
        user=user,
        stats=stats
    )