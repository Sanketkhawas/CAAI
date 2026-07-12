"""
Dashboard Routes
----------------
Phase 3 of CAAI (AI Tax Advisor).

This blueprint owns exactly one job: render the post-login home screen
and feed it the logged-in user's basic info. It does NOT do OCR, tax
calculation, or AI logic — those belong to their own modules and will
be wired in later through the placeholder routes below.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def dashboard_home():
    """
    Main dashboard screen.

    @login_required already handles the redirect-to-login behavior:
    if login_manager.login_view = 'auth.login' is set in app.py,
    an unauthenticated visit to /dashboard bounces to /login
    automatically — no manual check needed here.
    """

    # ---- Stats: hardcoded placeholders for now -----------------------
    # Replace these with real queries once Upload/OCR/Tax Engine exist, e.g.:
    #   documents_uploaded = Document.query.filter_by(user_id=current_user.id).count()
    stats = {
        "documents_uploaded": 0,
        "estimated_tax": 0,
        "potential_savings": 0,
        "ai_recommendations": 0,
    }

    # ---- Recent activity: empty until Upload/Reports/Chatbot exist ----
    recent_activity = []  # e.g. [{"icon": "upload", "text": "Uploaded Form 16", "time": "2h ago"}]

    # ---- Tax calendar: static for now, can be generated later ---------
    tax_calendar = [
        {"date": "15 Jun 2026", "label": "Advance Tax (1st Installment)"},
        {"date": "15 Sep 2026", "label": "Advance Tax (2nd Installment)"},
        {"date": "15 Dec 2026", "label": "Advance Tax (3rd Installment)"},
        {"date": "31 Jul 2026", "label": "ITR Filing Deadline"},
    ]

    ai_tip = "Investments under Section 80C — like ELSS, PPF, or life insurance premiums — can reduce your taxable income by up to ₹1.5 lakh."

    return render_template(
        "dashboard.html",
        user=current_user,
        stats=stats,
        recent_activity=recent_activity,
        tax_calendar=tax_calendar,
        ai_tip=ai_tip,
    )


# ---------------------------------------------------------------------
# Placeholder routes for modules not built yet.
# Upload is real now (see routes/upload_routes.py) — Quick Action
# buttons and the sidebar link to upload.upload_hub / upload.upload_*
# directly instead of a placeholder here.
# ---------------------------------------------------------------------

@dashboard.route("/tax-summary")
@login_required
def tax_summary_placeholder():
    return "Tax summary module coming soon."


@dashboard.route("/chatbot")
@login_required
def chatbot_placeholder():
    return "AI Assistant module coming soon."


@dashboard.route("/reports")
@login_required
def reports_placeholder():
    return "Reports module coming soon."


@dashboard.route("/profile")
@login_required
def profile_placeholder():
    return "Profile module coming soon."