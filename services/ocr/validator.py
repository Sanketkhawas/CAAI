"""
validator.py
------------

Validates extracted OCR entities before they are stored
or passed to the Tax Engine.

Author: CAAI Team
"""

import re


class OCRValidator:
    """
    Validates extracted OCR entities.
    """

    REQUIRED_FIELDS = [
        "employee_pan",
        "employee_name",
        "employer_name",
        "gross_salary",
        "assessment_year",
        "financial_year"
    ]

    PAN_PATTERN = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

    def validate(self, entities):
        """
        Validate extracted entities.

        Returns
        -------
        dict
        {
            "valid": True,
            "missing": [],
            "errors": []
        }
        """

        missing = []
        errors = []

        # -----------------------------
        # Required fields
        # -----------------------------
        for field in self.REQUIRED_FIELDS:

            value = entities.get(field)

            if value is None or value == "":
                missing.append(field)

        # -----------------------------
        # PAN validation
        # -----------------------------
        pan = entities.get("employee_pan")

        if pan:

            if not re.match(self.PAN_PATTERN, pan):

                errors.append("Invalid Employee PAN")

        employer_pan = entities.get("employer_pan")

        if employer_pan:

            if not re.match(self.PAN_PATTERN, employer_pan):

                errors.append("Invalid Employer PAN")

        # -----------------------------
        # Salary validation
        # -----------------------------
        salary = entities.get("gross_salary")

        if salary is not None:

            if salary <= 0:
                errors.append("Gross Salary must be greater than zero")

        taxable = entities.get("taxable_income")

        if taxable is not None:

            if taxable < 0:
                errors.append("Invalid Taxable Income")

        # -----------------------------
        # Assessment Year
        # -----------------------------
        ay = entities.get("assessment_year")

        if ay:

            if not re.match(r"^\d{4}-\d{2}$", ay):
                errors.append("Invalid Assessment Year")

        # -----------------------------
        # Financial Year
        # -----------------------------
        fy = entities.get("financial_year")

        if fy:

            if not re.match(r"^\d{4}-\d{2}$", fy):
                errors.append("Invalid Financial Year")

        # -----------------------------
        # Validation Result
        # -----------------------------
        valid = (len(missing) == 0 and len(errors) == 0)

        return {

            "valid": valid,

            "missing": missing,

            "errors": errors

        }