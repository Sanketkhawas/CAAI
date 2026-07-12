"""
Upload Routes
-------------
Phase 4 of CAAI (AI Tax Advisor).

One route per document type (as decided), each saving into a
per-user subfolder: uploads/<user_id>/<doc_type>/<filename>

This module does NOT do OCR or parsing — it only accepts, validates,
stores the file, and logs a Document row. OCR (Phase 5) will pick up
from the stored filepath.

NOTE ON THE Document MODEL:
This assumes database/models.py has a `Document` model with roughly:
    id, user_id, filename, filepath, doc_type, uploaded_at, status
If your actual field names differ, adjust the `Document(...)` calls
below to match — everything else (file handling, folder structure,
validation) will work unchanged.
"""

import os
import uuid
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from database.database import db
from database.models import Document

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_FILES_PER_REQUEST = 5

# Central config for each document type: label shown to the user,
# the subfolder name, and the doc_type value stored in the DB.
DOC_TYPES = {
    "form16": {
        "label": "Form 16",
        "folder": "form16",
        "hint": "Upload the Form 16 given by your employer (PDF or clear photo/scan).",
    },
    "salary-slip": {
        "label": "Salary Slip",
        "folder": "salary_slip",
        "hint": "Upload one or more monthly salary slips (PDF, PNG, or JPG).",
    },
    "bank-statement": {
        "label": "Bank Statement",
        "folder": "bank_statement",
        "hint": "Upload your bank statement covering the relevant financial year.",
    },
    "investment-proof": {
        "label": "Investment Proof",
        "folder": "investment_proof",
        "hint": "Upload proofs for 80C/80D investments — ELSS, PPF, insurance, etc.",
    },
}


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _user_upload_dir(doc_folder):
    """
    Builds (and creates if needed) uploads/<user_id>/<doc_folder>/
    """
    base = current_app.config.get("UPLOAD_FOLDER", "uploads/")
    path = os.path.join(base, str(current_user.id), doc_folder)
    os.makedirs(path, exist_ok=True)
    return path


# ---------------------------------------------------------------------
# Hub page: overview of all document types with links to each uploader.
# This is what the sidebar's "Upload Documents" nav item points to.
# ---------------------------------------------------------------------
@upload_bp.route("/")
@login_required
def upload_hub():
    return render_template("upload_hub.html", doc_types=DOC_TYPES)


# ---------------------------------------------------------------------
# One route per document type.
# ---------------------------------------------------------------------
@upload_bp.route("/form16", methods=["GET", "POST"])
@login_required
def upload_form16():
    return _handle_upload("form16")


@upload_bp.route("/salary-slip", methods=["GET", "POST"])
@login_required
def upload_salary_slip():
    return _handle_upload("salary-slip")


@upload_bp.route("/bank-statement", methods=["GET", "POST"])
@login_required
def upload_bank_statement():
    return _handle_upload("bank-statement")


@upload_bp.route("/investment-proof", methods=["GET", "POST"])
@login_required
def upload_investment_proof():
    return _handle_upload("investment-proof")


def _handle_upload(doc_key):
    """
    Shared logic for every document-type route above. Keeping this in
    one place means fixing a bug or adding a rule (e.g. antivirus scan
    later) only needs to happen once.
    """
    config = DOC_TYPES[doc_key]

    if request.method == "POST":
        files = request.files.getlist("documents")
        files = [f for f in files if f and f.filename]

        if not files:
            flash("Please choose at least one file to upload.", "danger")
            return redirect(url_for(request.endpoint))

        if len(files) > MAX_FILES_PER_REQUEST:
            flash(f"Please upload at most {MAX_FILES_PER_REQUEST} files at a time.", "danger")
            return redirect(url_for(request.endpoint))

        saved_count = 0
        target_dir = _user_upload_dir(config["folder"])

        for file in files:
            if not _allowed_file(file.filename):
                flash(f"'{file.filename}' was skipped — only PDF, PNG, or JPG files are allowed.", "warning")
                continue

            original_name = secure_filename(file.filename)
            unique_name = f"{datetime.utcnow():%Y%m%d%H%M%S}_{uuid.uuid4().hex[:8]}_{original_name}"
            filepath = os.path.join(target_dir, unique_name)

            file.save(filepath)

            doc = Document(
                user_id=current_user.id,
                filename=original_name,
                filepath=filepath,
                doc_type=doc_key,
                uploaded_at=datetime.utcnow(),
                status="uploaded",
            )
            db.session.add(doc)
            saved_count += 1

        db.session.commit()

        if saved_count:
            flash(f"{saved_count} file(s) uploaded successfully.", "success")
        return redirect(url_for(request.endpoint))

    # GET: show this document type's upload form + its previously uploaded files
    existing = (
        Document.query.filter_by(user_id=current_user.id, doc_type=doc_key)
        .order_by(Document.uploaded_at.desc())
        .all()
    )

    return render_template(
        "upload_form.html",
        doc_key=doc_key,
        config=config,
        existing=existing,
    )