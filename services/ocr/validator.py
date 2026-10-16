
"""
validator.py
------------

Document-specific validation for the AI Tax Advisor OCR pipeline.
Compatible with:
    validator.validate(entities)
    validator.validate(entities, document_type="salary-slip")
"""


class OCRValidator:

    REQUIRED_FIELDS = {
        "form16": ["employee_pan"],
        "salary-slip": ["employee_name"],
        "bank-statement": ["account_number"],
        "investment-proof": ["investor_name"],
    }

    DOCUMENT_ALIASES = {
        "form-16": "form16",
        "form16": "form16",
        "salary": "salary-slip",
        "salary-slip": "salary-slip",
        "payslip": "salary-slip",
        "pay-slip": "salary-slip",
        "bank": "bank-statement",
        "bank-statement": "bank-statement",
        "investment": "investment-proof",
        "investment-proof": "investment-proof",
    }

    def validate(self, entities, document_type="form16"):
        """
        Validate extracted entities for the selected document type.

        Returns:
            {
                "valid": bool,
                "missing": list,
                "errors": list
            }
        """

        if not isinstance(entities, dict):
            return {
                "valid": False,
                "missing": [],
                "errors": ["Entities must be provided as a dictionary."]
            }

        document_type = (document_type or "form16").strip().lower()
        document_type = document_type.replace("_", "-").replace(" ", "-")
        document_type = self.DOCUMENT_ALIASES.get(
            document_type, document_type
        )

        if document_type not in self.REQUIRED_FIELDS:
            return {
                "valid": False,
                "missing": [],
                "errors": [
                    f"Unsupported document type: {document_type}"
                ]
            }

        # Check required fields
        required_fields = self.REQUIRED_FIELDS[document_type]

        missing = [
            field
            for field in required_fields
            if entities.get(field) is None
            or str(entities.get(field)).strip() == ""
        ]

        errors = []

        # Validate PAN format when available
        pan_fields = [
            "employee_pan",
            "investor_pan",
            "employer_pan",
        ]

        for field in pan_fields:
            value = entities.get(field)

            if value:
                import re

                if not re.fullmatch(
                    r"[A-Z]{5}[0-9]{4}[A-Z]",
                    str(value).strip().upper()
                ):
                    errors.append(f"Invalid PAN format in {field}.")

        # Validate extracted financial amounts
        amount_fields = [
            "gross_salary",
            "basic_salary",
            "hra",
            "special_allowance",
            "exemptions",
            "standard_deduction",
            "professional_tax",
            "section_80c",
            "section_80d",
            "other_deductions",
            "total_deductions",
            "taxable_income",
            "total_tax",
            "tds",
            "provident_fund",
            "other_earnings",
            "net_salary",
            "opening_balance",
            "closing_balance",
            "total_deposits",
            "total_withdrawals",
            "investment_amount",
            "eligible_deduction",
        ]

        for field in amount_fields:
            value = entities.get(field)

            if value is not None:
                try:
                    amount = float(value)

                    if amount < 0:
                        errors.append(
                            f"{field} cannot be negative."
                        )

                except (TypeError, ValueError):
                    errors.append(
                        f"{field} must be a numeric amount."
                    )

        # A bank statement should have account information.
        # Transaction rows are not mandatory because some
        # statements may cover periods without transactions.
        if document_type == "bank-statement":
            transactions = entities.get("transactions", [])

            if not isinstance(transactions, list):
                errors.append(
                    "Transactions must be provided as a list."
                )

        return {
            "valid": len(missing) == 0 and len(errors) == 0,
            "missing": missing,
            "errors": errors
        }
