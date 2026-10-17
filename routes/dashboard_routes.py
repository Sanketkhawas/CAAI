
"""
Dashboard Routes
----------------
CAAI dashboard with per-user document activity and Form 16 overview.
OCR entities are read-only in this module.
"""
from flask import redirect, url_for
import json
from database.models import (
    Document,
    OCRData,
    Recommendation,
    TaxCalculation,
)
from flask import Blueprint, render_template
from flask_login import login_required, current_user

from database.models import Document, OCRData, Recommendation

from services.tax_engine.tax_engine import TaxEngine
from services.recommendation.recommendation_service import (
    RecommendationService,
)
from services.financial_profile.financial_profile_builder import (
    FinancialProfileBuilder,
)
from services.financial_profile.financial_profile_validator import (
    FinancialProfileValidator,
)

dashboard = Blueprint("dashboard", __name__)


def _display_value(value):
    """Format values for display without changing stored data."""
    if value is None or value == "":
        return "Not available"

    if isinstance(value, bool):
        return "Yes" if value else "No"

    if isinstance(value, (int, float)):
        return f"₹{value:,.0f}"

    return str(value)


def _humanize_key(key):
    """Convert OCR entity keys into readable labels."""
    labels = {
        "employee_pan": "Employee PAN",
        "employee_name": "Employee Name",
        "employee_address": "Employee Address",
        "employer_name": "Employer Name",
        "employer_address": "Employer Address",
        "employer_pan": "Employer PAN",
        "employer_tan": "Employer TAN",
        "assessment_year": "Assessment Year",
        "financial_year": "Financial Year",
        "employment_period": "Employment Period",
        "basic_salary": "Basic Salary",
        "gross_salary": "Gross Salary",
        "perquisites": "Perquisites",
        "profits_in_lieu_of_salary": "Profits in Lieu of Salary",
        "other_employer_salary": "Other Employer Salary",
        "travel_exemption": "Travel Exemption",
        "gratuity_exemption": "Gratuity Exemption",
        "pension_exemption": "Pension Exemption",
        "leave_encashment_exemption": "Leave Encashment Exemption",
        "hra": "HRA Exemption",
        "other_exemption": "Other Exemption",
        "exemptions": "Total Exemptions",
        "total_salary_current_employer": "Total Salary from Current Employer",
        "standard_deduction": "Standard Deduction",
        "entertainment_allowance": "Entertainment Allowance",
        "professional_tax": "Professional Tax",
        "total_section16_deductions": "Total Section 16 Deductions",
        "income_from_salary": "Income from Salary",
        "house_property_income": "Income from House Property",
        "other_sources_income": "Income from Other Sources",
        "total_other_income": "Total Other Income",
        "gross_total_income": "Gross Total Income",
        "section_80c": "Section 80C",
        "section_80ccc": "Section 80CCC",
        "section_80ccd1": "Section 80CCD(1)",
        "section_80ccd1b": "Section 80CCD(1B)",
        "section_80ccd2": "Section 80CCD(2)",
        "section_80d": "Section 80D",
        "section_80e": "Section 80E",
        "section_80g": "Section 80G",
        "section_80tta": "Section 80TTA",
        "other_chapter_via": "Other Chapter VI-A Deductions",
        "total_deductions": "Total Deductions",
        "taxable_income": "Taxable Income",
        "total_tax": "Total Tax",
        "rebate_87a": "Section 87A Rebate",
        "surcharge": "Surcharge",
        "cess": "Health and Education Cess",
        "tax_payable": "Tax Payable",
        "relief_89": "Section 89 Relief",
        "net_tax_payable": "Net Tax Payable",
        "tds": "Tax Deducted at Source (TDS)",
        "issue_date": "Issue Date",
        "place": "Place of Issue",
        "special_allowance": "Special Allowance",
    }

    return labels.get(key, key.replace("_", " ").title())


def _latest_document(user_id, document_type):
    """Return the latest document of a given type for this user."""
    return (
        Document.query
        .filter_by(
            user_id=user_id,
            document_type=document_type,
        )
        .order_by(Document.upload_date.desc(), Document.id.desc())
        .first()
    )


def _get_document_entities(document):
    """Read the latest saved OCR entities for a document."""
    if document is None:
        return {}

    record = (
        OCRData.query
        .filter_by(document_id=document.id)
        .order_by(OCRData.processed_at.desc(), OCRData.id.desc())
        .first()
    )

    if record is None:
        return {}

    try:
        entities = json.loads(record.entities)
    except (TypeError, ValueError):
        return {}

    return entities if isinstance(entities, dict) else {}


def _latest_ocr_entities(user_id, document_type):
    """Get entities from the user's latest document of this type."""
    document = _latest_document(user_id, document_type)
    return _get_document_entities(document)


def _all_investment_entities(user_id):
    """Read entities from all of this user's investment-proof documents."""
    documents = (
        Document.query
        .filter_by(
            user_id=user_id,
            document_type="investment-proof",
        )
        .order_by(Document.upload_date.desc(), Document.id.desc())
        .all()
    )

    entities_list = []

    for document in documents:
        entities = _get_document_entities(document)
        if entities:
            entities_list.append(entities)

    return entities_list


def _get_latest_form16(user_id):
    """Return the latest Form 16 document and its saved OCR entities."""
    document = _latest_document(user_id, "form16")
    entities = _get_document_entities(document)

    return document, entities or None


def _build_tax_engine_inputs(profile, form16):
    """Map profile/Form 16 fields to the tax calculators' expected inputs."""
    income = profile.get("income", {}) or {}
    deductions = profile.get("deductions", {}) or {}

    def first_available(*values):
        for value in values:
            if value is not None and value != "":
                return value
        return None

    return {
        "gross_salary": first_available(
            form16.get("gross_salary"),
            form16.get("total_salary_current_employer"),
            income.get("gross_salary"),
        ),
        "professional_tax": first_available(
            form16.get("professional_tax"),
            deductions.get("professional_tax"),
        ),
        "other_sources_income": first_available(
            form16.get("other_sources_income"),
            form16.get("total_other_income"),
            income.get("other_sources_income"),
        ),
        "house_property_income": first_available(
            form16.get("house_property_income"),
            income.get("house_property_income"),
        ),
        "section_80c": first_available(
            form16.get("section_80c"),
            deductions.get("section_80c"),
        ),
        "section_80d": first_available(
            form16.get("section_80d"),
            deductions.get("section_80d"),
        ),
        "section_80ccd2": first_available(
            form16.get("section_80ccd2"),
            deductions.get("section_80ccd2"),
        ),
        "taxable_income": first_available(
            form16.get("taxable_income"),
            income.get("taxable_income"),
        ),
    }


def _build_dashboard_tax_data(user_id):
    """Build the financial profile and calculate tax once per request."""
    form16 = _latest_ocr_entities(user_id, "form16")
    salary_slip = _latest_ocr_entities(user_id, "salary-slip")
    bank_statement = _latest_ocr_entities(user_id, "bank-statement")
    investment_proofs = _all_investment_entities(user_id)

    profile = FinancialProfileBuilder().build(
        form16=form16,
        salary_slip=salary_slip,
        bank_statement=bank_statement,
        investment_proofs=investment_proofs,
    )

    profile_validation = FinancialProfileValidator().validate(profile)

    tax_inputs = _build_tax_engine_inputs(profile, form16)
    gross_salary = tax_inputs.get("gross_salary")

    tax_result = None
    recommendation_result = None

    if gross_salary is not None and gross_salary != "":
        tax_result = TaxEngine().calculate(tax_inputs)

        recommendation_result = (
            RecommendationService().generate_recommendations(
                financial_profile=profile,
                tax_result=tax_result,
                validation_result=profile_validation,
            )
        )

    return {
        "profile": profile,
        "profile_validation": profile_validation,
        "tax_result": tax_result,
        "recommendation_result": recommendation_result,
    }



def _validation_passed(validation_result):
    """Return the overall validity reported by FinancialProfileValidator."""
    if not isinstance(validation_result, dict):
        return False

    return validation_result.get("valid") is True



@dashboard.route("/dashboard")
@login_required
def dashboard_home():
    user_id = current_user.id

    documents_uploaded = Document.query.filter_by(
        user_id=user_id
    ).count()

    recommendation_count = Recommendation.query.filter_by(
        user_id=user_id
    ).count()

    form16_document, form16_entities = _get_latest_form16(user_id)

    # Build tax/profile/recommendation data once.
    tax_data = _build_dashboard_tax_data(user_id)

    tax_result = tax_data["tax_result"]
    profile_validation = tax_data["profile_validation"]
    recommendation_result = tax_data["recommendation_result"]

    recommendations = []

    if (
        recommendation_result
        and recommendation_result.get("success")
    ):
        nested_result = (
            recommendation_result.get("recommendations") or {}
        )
        recommendations = nested_result.get("recommendations", [])

    # Do not show a calculated tax estimate unless the profile validator
    # explicitly reports success.
    estimated_tax = None
    potential_savings = 0

    if tax_result and _validation_passed(profile_validation):
        selected_result = tax_result.get("recommended_result") or {}
        estimated_tax = selected_result.get("total_tax")
        potential_savings = tax_result.get("tax_saved") or 0

        # Demonstration TDS values for the dashboard.
    # These are not verified from the user's Form 16.
    annual_tds = 208000
    monthly_tds = round(annual_tds / 12)

    stats = {
        "documents_uploaded": documents_uploaded,
        "estimated_tax": estimated_tax,
        "potential_savings": potential_savings,
        "ai_recommendations": len(recommendations),
        "annual_tds": annual_tds,
        "monthly_tds": monthly_tds,
    }

    recent_docs = (
        Document.query
        .filter_by(user_id=user_id)
        .order_by(Document.upload_date.desc(), Document.id.desc())
        .limit(5)
        .all()
    )

    recent_activity = [
        {
            "text": f"Uploaded {doc.document_type}",
            "time": (
                doc.upload_date.strftime("%d %b %Y")
                if doc.upload_date
                else "Date unavailable"
            ),
        }
        for doc in recent_docs
    ]

    tax_calendar = [
        {"date": "31 Jul", "label": "ITR Filing Due Date"},
        {"date": "15 Jun", "label": "Advance Tax Installment"},
    ]

    ai_tip = (
        "Upload your tax documents to build your financial profile. "
        "Review extracted details and validation warnings before relying "
        "on any tax estimate."
    )

    form16_summary = []
    form16_details = []

    if form16_entities:
        summary_keys = [
            ("employee_name", "Employee"),
            ("employer_name", "Employer"),
            ("assessment_year", "Assessment Year"),
            ("gross_salary", "Gross Salary"),
            ("gross_total_income", "Gross Total Income"),
            ("total_deductions", "Total Deductions"),
            ("taxable_income", "Taxable Income"),
            ("total_tax", "Total Tax"),
            ("cess", "Cess"),
            ("tax_payable", "Tax Payable"),
            ("net_tax_payable", "Net Tax Payable"),
            ("tds", "TDS"),
        ]

        for key, label in summary_keys:
            form16_summary.append({
                "label": label,
                "value": _display_value(form16_entities.get(key)),
            })

        for key, value in form16_entities.items():
            form16_details.append({
                "label": _humanize_key(key),
                "value": _display_value(value),
            })

    return render_template(
        "dashboard.html",
        user=current_user,
        stats=stats,
        recent_activity=recent_activity,
        tax_calendar=tax_calendar,
        ai_tip=ai_tip,
        form16_document=form16_document,
        form16_entities=form16_entities,
        form16_summary=form16_summary,
        form16_details=form16_details,
        tax_result=tax_result,
        profile_validation=profile_validation,
        recommendation_result=recommendation_result,
        recommendations=recommendations,
    )



@dashboard.route("/tax-summary")
@login_required
def tax_summary():
    """Display the current user's tax summary using saved records."""

    user_id = current_user.id

    # Find this user's latest Form 16.
    form16_document, form16_entities = _get_latest_form16(user_id)

    saved_calculation = None

    if form16_document:
        saved_calculation = (
            TaxCalculation.query
            .filter_by(document_id=form16_document.id)
            .order_by(
                TaxCalculation.created_at.desc(),
                TaxCalculation.id.desc(),
            )
            .first()
        )

    # Reuse the existing profile and tax-engine data builder.
    tax_data = _build_dashboard_tax_data(user_id)

    tax_result = tax_data.get("tax_result")
    profile_validation = tax_data.get("profile_validation") or {}

    old_result = (tax_result or {}).get("old_regime") or {}
    new_result = (tax_result or {}).get("new_regime") or {}
    recommended_result = (
        (tax_result or {}).get("recommended_result") or {}
    )

    # Prefer the saved calculation for the latest Form 16.
    if saved_calculation:
        old_tax = saved_calculation.old_regime_tax
        new_tax = saved_calculation.new_regime_tax
        recommended_regime = saved_calculation.recommended_regime
        estimated_tax = (
            old_tax if recommended_regime == "Old Regime"
            else new_tax if recommended_regime == "New Regime"
            else min(old_tax, new_tax)
        )
        tax_saved = saved_calculation.tax_saved or 0
        gross_salary = saved_calculation.gross_salary
        taxable_income = saved_calculation.taxable_income
        total_deductions = saved_calculation.total_deductions
        data_source = "Saved tax calculation"
    else:
        old_tax = old_result.get("total_tax")
        new_tax = new_result.get("total_tax")
        recommended_regime = (
            (tax_result or {}).get("recommended_regime")
        )
        estimated_tax = recommended_result.get("total_tax")
        tax_saved = (tax_result or {}).get("tax_saved", 0)
        gross_salary = recommended_result.get("gross_salary")
        taxable_income = recommended_result.get(
            "calculated_taxable_income"
        )
        total_deductions = recommended_result.get("total_deductions")
        data_source = "Current tax-engine estimate"

    # Form 16 values remain separate from calculated estimates.
    form16_summary = []
    if form16_entities:
        for key, label in [
            ("gross_salary", "Gross Salary"),
            ("gross_total_income", "Gross Total Income"),
            ("total_deductions", "Total Deductions"),
            ("taxable_income", "Form 16 Taxable Income"),
            ("total_tax", "Form 16 Total Tax"),
            ("tax_payable", "Form 16 Tax Payable"),
            ("net_tax_payable", "Form 16 Net Tax Payable"),
            ("tds", "TDS"),
            ("assessment_year", "Assessment Year"),
            ("financial_year", "Financial Year"),
        ]:
            value = form16_entities.get(key)
            if value is not None and value != "":
                form16_summary.append({
                    "label": label,
                    "value": _display_value(value),
                })

    return render_template(
        "tax_summary.html",
        user=current_user,
        form16_document=form16_document,
        form16_summary=form16_summary,
        saved_calculation=saved_calculation,
        tax_result=tax_result,
        old_tax=old_tax,
        new_tax=new_tax,
        recommended_regime=recommended_regime or "Not available",
        estimated_tax=estimated_tax,
        tax_saved=tax_saved,
        gross_salary=gross_salary,
        taxable_income=taxable_income,
        total_deductions=total_deductions,
        profile_validation=profile_validation,
        recommendation_status=(
            (tax_result or {}).get("recommendation_status")
            or "No current estimate available"
        ),
        data_source=data_source,
        format_value=_display_value,
    )


@dashboard.route("/chatbot")
@login_required
def chatbot_placeholder():
    return redirect(url_for("chatbot.chat_page"))


@dashboard.route("/reports")
@login_required
def reports_placeholder():
    """Display report data belonging to the logged-in user."""

    user_id = current_user.id

    # Get the user's latest Form 16 and extracted entities.
    form16_document, form16_entities = _get_latest_form16(user_id)

    # Load the latest saved tax calculation for that Form 16.
    saved_calculation = None

    if form16_document:
        saved_calculation = (
            TaxCalculation.query
            .filter_by(document_id=form16_document.id)
            .order_by(
                TaxCalculation.created_at.desc(),
                TaxCalculation.id.desc(),
            )
            .first()
        )

    # Build a current estimate using the existing tax engine.
    tax_data = _build_dashboard_tax_data(user_id)
    tax_result = tax_data.get("tax_result") or {}
    profile_validation = tax_data.get("profile_validation") or {}

    old_result = tax_result.get("old_regime") or {}
    new_result = tax_result.get("new_regime") or {}
    recommended_result = tax_result.get("recommended_result") or {}

    # Prefer saved values when available.
    if saved_calculation:
        gross_salary = saved_calculation.gross_salary
        taxable_income = saved_calculation.taxable_income
        total_deductions = saved_calculation.total_deductions
        old_tax = saved_calculation.old_regime_tax
        new_tax = saved_calculation.new_regime_tax
        tax_saved = saved_calculation.tax_saved or 0
        recommended_regime = saved_calculation.recommended_regime
        data_source = "Saved tax calculation"
    else:
        gross_salary = recommended_result.get("gross_salary")
        taxable_income = recommended_result.get(
            "calculated_taxable_income"
        )
        total_deductions = recommended_result.get("total_deductions")
        old_tax = old_result.get("total_tax")
        new_tax = new_result.get("total_tax")
        tax_saved = tax_result.get("tax_saved", 0)
        recommended_regime = tax_result.get("recommended_regime")
        data_source = "Current tax-engine estimate"

    # Only expose recommendations belonging to this user.
    recommendations = (
        Recommendation.query
        .filter_by(user_id=user_id)
        .order_by(
            Recommendation.created_at.desc(),
            Recommendation.id.desc(),
        )
        .limit(10)
        .all()
    )

    # Include this user's uploaded documents only.
    documents = (
        Document.query
        .filter_by(user_id=user_id)
        .order_by(Document.upload_date.desc(), Document.id.desc())
        .limit(10)
        .all()
    )

    form16_summary = []
    if form16_entities:
        for key, label in [
            ("assessment_year", "Assessment Year"),
            ("financial_year", "Financial Year"),
            ("gross_salary", "Gross Salary"),
            ("gross_total_income", "Gross Total Income"),
            ("total_deductions", "Form 16 Total Deductions"),
            ("taxable_income", "Form 16 Taxable Income"),
            ("total_tax", "Form 16 Total Tax"),
            ("tax_payable", "Form 16 Tax Payable"),
            ("net_tax_payable", "Form 16 Net Tax Payable"),
            ("tds", "Tax Deducted at Source"),
        ]:
            value = form16_entities.get(key)
            if value is not None and value != "":
                form16_summary.append({
                    "label": label,
                    "value": _display_value(value),
                })

    return render_template(
        "reports.html",
        user=current_user,
        form16_document=form16_document,
        form16_summary=form16_summary,
        saved_calculation=saved_calculation,
        gross_salary=gross_salary,
        taxable_income=taxable_income,
        total_deductions=total_deductions,
        old_tax=old_tax,
        new_tax=new_tax,
        tax_saved=tax_saved,
        recommended_regime=recommended_regime or "Not available",
        data_source=data_source,
        profile_validation=profile_validation,
        recommendations=recommendations,
        documents=documents,
        format_value=_display_value,
    )




@dashboard.route("/profile")
@login_required
def profile_placeholder():
    """Display the logged-in user's account and extracted financial profile."""

    user_id = current_user.id

    # Read the latest saved Form 16 OCR information.
    form16_document, form16_entities = _get_latest_form16(user_id)

    # Reuse the existing financial profile builder and validator.
    tax_data = _build_dashboard_tax_data(user_id)

    profile = tax_data.get("profile") or {}
    profile_validation = tax_data.get("profile_validation") or {}

    personal = profile.get("personal") or {}
    employment = profile.get("employment") or {}
    income = profile.get("income") or {}
    deductions = profile.get("deductions") or {}
    tax = profile.get("tax") or {}
    banking = profile.get("banking") or {}
    investments = profile.get("investments") or []

    # Retrieve only documents owned by the logged-in user.
    documents = (
        Document.query
        .filter_by(user_id=user_id)
        .order_by(
            Document.upload_date.desc(),
            Document.id.desc(),
        )
        .limit(10)
        .all()
    )

    # Mask sensitive identifiers before displaying them.
    def mask_pan(value):
        if not value:
            return "Not available"

        value = str(value).strip()

        if len(value) == 10:
            return value[:2] + "******" + value[-2:]

        return "Partially hidden"

    def mask_account(value):
        if not value:
            return "Not available"

        value = str(value).strip()

        if len(value) <= 4:
            return "****"

        return "*" * min(len(value) - 4, 12) + value[-4:]

    return render_template(
        "profile.html",
        user=current_user,

        # Account and identity
        personal=personal,
        employment=employment,

        # Extracted financial profile
        income=income,
        deductions=deductions,
        tax=tax,
        banking=banking,
        investments=investments,

        # Original Form 16 extraction
        form16_document=form16_document,
        form16_entities=form16_entities or {},

        # Validation and uploaded document history
        profile_validation=profile_validation,
        documents=documents,

        # Display helpers
        format_value=_display_value,
        mask_pan=mask_pan,
        mask_account=mask_account,
    )
