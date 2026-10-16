"""
financial_profile_validator.py
------------------------------
Validates the standardized financial profile
created by FinancialProfileBuilder.

The validator performs:
1. Identity consistency
2. PAN validation
3. Employment validation
4. FY / AY consistency
5. Income consistency
6. Bank salary-credit consistency
7. Bank interest consistency
8. Investment validation
9. Completeness checks

Important:
This validator checks data consistency.
It does NOT independently calculate tax.
"""

import re
from datetime import datetime


class FinancialProfileValidator:

    def validate(self, profile):

        errors = []
        warnings = []

        checks = {
            "identity": "PASS",
            "pan": "PASS",
            "fy_ay": "PASS",
            "employment": "PASS",
            "income": "PASS",
            "investments": "PASS",
            "completeness": "PASS"
        }

        # --------------------------------------------------
        # 1. Identity
        # --------------------------------------------------

        identity_errors, identity_warnings = self.validate_identity(profile)

        errors.extend(identity_errors)
        warnings.extend(identity_warnings)

        if identity_errors:
            checks["identity"] = "FAIL"
        elif identity_warnings:
            checks["identity"] = "WARNING"

        # --------------------------------------------------
        # 2. PAN
        # --------------------------------------------------

        pan_errors = self.validate_pan(profile)

        errors.extend(pan_errors)

        if pan_errors:
            checks["pan"] = "FAIL"

        # --------------------------------------------------
        # 3. Employment
        # --------------------------------------------------

        employment_errors = self.validate_employment(profile)

        errors.extend(employment_errors)

        if employment_errors:
            checks["employment"] = "FAIL"

        # --------------------------------------------------
        # 4. FY / AY
        # --------------------------------------------------

        fy_errors = self.validate_financial_year(profile)

        errors.extend(fy_errors)

        if fy_errors:
            checks["fy_ay"] = "FAIL"

        # --------------------------------------------------
        # 5. Income
        # --------------------------------------------------

        income_errors, income_warnings = self.validate_income(profile)

        errors.extend(income_errors)
        warnings.extend(income_warnings)

        if income_errors:
            checks["income"] = "FAIL"
        elif income_warnings:
            checks["income"] = "WARNING"

        # --------------------------------------------------
        # 6. Investments
        # --------------------------------------------------

        investment_errors, investment_warnings = self.validate_investments(
            profile
        )

        errors.extend(investment_errors)
        warnings.extend(investment_warnings)

        if investment_errors:
            checks["investments"] = "FAIL"
        elif investment_warnings:
            checks["investments"] = "WARNING"

        # --------------------------------------------------
        # 7. Completeness
        # --------------------------------------------------

        completeness_errors = self.validate_completeness(profile)

        errors.extend(completeness_errors)

        if completeness_errors:
            checks["completeness"] = "FAIL"

        # --------------------------------------------------
        # Overall validity
        # --------------------------------------------------

        valid = len(errors) == 0

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "checks": checks
        }

    # ======================================================
    # IDENTITY VALIDATION
    # ======================================================

    def validate_identity(self, profile):

        errors = []
        warnings = []

        personal = profile.get("personal", {})
        banking = profile.get("banking", {})
        investments = profile.get("investments", [])

        name = self.normalize_text(
            personal.get("name")
        )

        bank_name = self.normalize_text(
            banking.get("account_holder")
        )

        if name and bank_name:

            if name != bank_name:

                warnings.append(
                    "Name mismatch between personal profile and bank statement."
                )

        # Check investment holder names
        investments = investments or []

        if not isinstance(investments, list):
            investments = []

        for investment in investments:
            if not isinstance(investment, dict):
                continue

            investor_name = self.normalize_text(
                investment.get("investor_name")
            )

            if investor_name and name and investor_name != name:
                warnings.append(
                    "Investment proof holder name differs "
                    "from the primary profile name."
                )

        return errors, warnings

    # ======================================================
    # PAN VALIDATION
    # ======================================================

    def validate_pan(self, profile):

        errors = []

        pan = profile.get(
            "personal", {}
        ).get("pan")

        if not pan:

            errors.append(
                "PAN is missing from the financial profile."
            )

            return errors

        pan = pan.strip().upper()

        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"

        if not re.match(pattern, pan):

            errors.append(
                "PAN format is invalid."
            )

        return errors

    # ======================================================
    # EMPLOYMENT VALIDATION
    # ======================================================

    def validate_employment(self, profile):

        errors = []

        employment = profile.get(
            "employment", {}
        )

        employer_name = employment.get(
            "employer_name"
        )

        if not employer_name:

            errors.append(
                "Employer name is missing."
            )

        return errors

    # ======================================================
    # FY / AY VALIDATION
    # ======================================================

    def validate_financial_year(self, profile):

        errors = []

        tax = profile.get(
            "tax", {}
        )

        financial_year = tax.get(
            "financial_year"
        )

        assessment_year = tax.get(
            "assessment_year"
        )

        if not financial_year:

            errors.append(
                "Financial year is missing."
            )

            return errors

        if not assessment_year:

            errors.append(
                "Assessment year is missing."
            )

            return errors

        expected_ay = self.expected_assessment_year(
            financial_year
        )

        if expected_ay and assessment_year != expected_ay:

            errors.append(
                f"Financial year {financial_year} "
                f"should correspond to assessment year "
                f"{expected_ay}, but found {assessment_year}."
            )

        return errors

    # ======================================================
    # INCOME VALIDATION
    # ======================================================

    def validate_income(self, profile):

        errors = []
        warnings = []

        income = profile.get(
            "income", {}
        )

        # ----------------------------------------------
        # Extract values
        # ----------------------------------------------

        gross_salary = self.to_number(
            income.get("gross_salary")
        )

        salary_income = self.to_number(
            income.get("salary_income")
        )

        taxable_income = self.to_number(
            income.get("taxable_income")
        )

        salary_slip_gross = self.to_number(
            income.get("salary_slip_gross_salary")
        )

        bank_salary_credits = self.to_number(
            income.get("salary_credits")
        )

        bank_interest = self.to_number(
            income.get("interest_income")
        )

        # ----------------------------------------------
        # Basic numerical validation
        # ----------------------------------------------

        if gross_salary is None:

            errors.append(
                "Gross salary is missing."
            )

        elif gross_salary < 0:

            errors.append(
                "Gross salary cannot be negative."
            )

        if salary_income is not None:

            if salary_income < 0:

                errors.append(
                    "Salary income cannot be negative."
                )

            if (
                gross_salary is not None
                and salary_income > gross_salary
            ):

                errors.append(
                    "Salary income exceeds gross salary."
                )

        if taxable_income is not None:

            if taxable_income < 0:

                errors.append(
                    "Taxable income cannot be negative."
                )

            if (
                gross_salary is not None
                and taxable_income > gross_salary
            ):

                errors.append(
                    "Taxable income exceeds gross salary."
                )

        # ==================================================
        # FORM 16 ↔ SALARY SLIP
        # ==================================================

        if (
            gross_salary is not None
            and salary_slip_gross is not None
        ):

            annualized_salary = self.annualize_salary_slip(
                salary_slip_gross,
                profile
            )

            if annualized_salary is not None:

                difference = abs(
                    annualized_salary - gross_salary
                )

                tolerance = max(
                    10000,
                    gross_salary * 0.05
                )

                if difference > tolerance:

                    warnings.append(
                        "Annualized salary-slip amount differs "
                        "materially from Form 16 gross salary."
                    )

        # ==================================================
        # FORM 16 ↔ BANK SALARY CREDITS
        # ==================================================

        if (
            gross_salary is not None
            and bank_salary_credits is not None
        ):

            difference = abs(
                bank_salary_credits - gross_salary
            )

            tolerance = max(
                10000,
                gross_salary * 0.10
            )

            if difference > tolerance:

                warnings.append(
                    "Bank salary credits differ materially "
                    "from Form 16 gross salary."
                )

        # ==================================================
        # BANK INTEREST
        # ==================================================

        if bank_interest is not None:

            if bank_interest < 0:

                errors.append(
                    "Bank interest income cannot be negative."
                )

            elif bank_interest > 0:

                warnings.append(
                    "Bank interest income is present and "
                    "should be considered when determining "
                    "taxable income."
                )

        return errors, warnings

    # ======================================================
    # ANNUALIZE SALARY SLIP
    # ======================================================

    def annualize_salary_slip(
        self,
        monthly_salary,
        profile
    ):

        employment = profile.get(
            "employment", {}
        )

        pay_period = employment.get(
            "pay_period"
        )

        if not pay_period:

            return monthly_salary * 12

        pay_period_lower = pay_period.lower()

        monthly_keywords = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december"
        ]

        for month in monthly_keywords:

            if month in pay_period_lower:

                return monthly_salary * 12

        # Handle formats such as:
        # Mar 2026
        # March-2026
        # 03/2026

        if re.search(
            r"\b(0?[1-9]|1[0-2])[/\-]\d{4}\b",
            pay_period
        ):

            return monthly_salary * 12

        if re.search(
            r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\-]?\d{4}\b",
            pay_period_lower
        ):

            return monthly_salary * 12

        # Default assumption for a salary slip
        return monthly_salary * 12

    # ======================================================
    # INVESTMENT VALIDATION
    # ======================================================

    
    def validate_investments(self, profile):

        errors = []
        warnings = []

        raw_investments = profile.get("investments")
        profile_fy = profile.get("tax", {}).get("financial_year")

        # Handle missing or malformed investment collections.
        if raw_investments is None:
            investments = []
        elif isinstance(raw_investments, list):
            investments = raw_investments
        else:
            investments = []
            warnings.append(
                "Investment data is not in the expected list format."
            )

        # Missing documents are not proof of zero investments.
        if not investments:
            warnings.append(
                "No investment proofs are available for validation. "
                "Confirm whether investments or eligible deductions exist."
            )

        for index, investment in enumerate(investments, start=1):

            if not isinstance(investment, dict):
                warnings.append(
                    f"Investment {index}: record is not a valid object."
                )
                continue

            investment_type = investment.get("investment_type")

            amount = self.to_number(
                investment.get("amount")
                if investment.get("amount") is not None
                else investment.get("investment_amount")
            )

            investment_fy = investment.get("financial_year")

            # Investment type
            if not investment_type:
                errors.append(
                    f"Investment {index}: investment type is missing."
                )

            # Investment amount
            if amount is None:
                errors.append(
                    f"Investment {index}: investment amount is missing."
                )
            elif amount <= 0:
                errors.append(
                    f"Investment {index}: investment amount "
                    f"must be greater than zero."
                )

            # Financial-year matching
            if not investment_fy:
                warnings.append(
                    f"Investment {index}: financial year is missing."
                )
            elif profile_fy and investment_fy != profile_fy:
                warnings.append(
                    f"Investment {index}: financial year "
                    f"{investment_fy} differs from profile "
                    f"financial year {profile_fy}."
                )

        return errors, warnings


    # ======================================================
    # COMPLETENESS
    # ======================================================

    def validate_completeness(self, profile):

        errors = []

        personal = profile.get(
            "personal", {}
        )

        income = profile.get(
            "income", {}
        )

        tax = profile.get(
            "tax", {}
        )

        required_fields = {
            "personal.name":
                personal.get("name"),

            "personal.pan":
                personal.get("pan"),

            "income.gross_salary":
                income.get("gross_salary"),

            "tax.financial_year":
                tax.get("financial_year"),

            "tax.assessment_year":
                tax.get("assessment_year")
        }

        for field, value in required_fields.items():

            if value is None or str(value).strip() == "":

                errors.append(
                    f"Required profile information missing: {field}"
                )

        return errors

    # ======================================================
    # HELPERS
    # ======================================================

    @staticmethod
    def normalize_text(value):

        if value is None:
            return ""

        return " ".join(
            str(value)
            .strip()
            .lower()
            .split()
        )

    @staticmethod
    def to_number(value):

        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        try:

            cleaned = (
                str(value)
                .replace(",", "")
                .replace("₹", "")
                .strip()
            )

            return float(cleaned)

        except (ValueError, TypeError):

            return None

    @staticmethod
    def expected_assessment_year(financial_year):

        if not financial_year:
            return None

        match = re.search(
            r"(20\d{2})\s*[-–/]\s*(?:(20)?(\d{2}))",
            str(financial_year)
        )

        if not match:
            return None

        start_year = int(match.group(1))
        end_two_digits = match.group(3)

        expected_end = (start_year + 1) % 100

        if int(end_two_digits) != expected_end:
            return None

        return f"{start_year + 1}-{str(start_year + 2)[-2:]}"