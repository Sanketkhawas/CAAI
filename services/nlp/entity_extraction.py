"""
entity_extraction.py
--------------------

Extracts structured information from cleaned OCR text.

Author: CAAI Team
"""

import re


class EntityExtractor:

    def __init__(self):
        pass

    # ----------------------------------------------------
    # Helper
    # ----------------------------------------------------

    def extract_pattern(self, pattern, text):

        match = re.search(pattern, text, re.DOTALL)

        if match:
            return " ".join(match.group(1).split())

        return None

    # ----------------------------------------------------
    # Money helper
    # ----------------------------------------------------

    def extract_amount(self, label, text):
        """
        Extract amount after a label.

        Example:
        Gross Salary
        Rs. 900,000
        """

        pattern = rf"{label}.*?Rs\.\s*([\d,]+)"

        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)

        if match:
            return int(match.group(1).replace(",", ""))

        return None

    # ----------------------------------------------------
    # Main extractor
    # ----------------------------------------------------

    def extract(self, text):

        entities = {}

        # -------------------------------
        # Employee
        # -------------------------------

        entities["employee_pan"] = self.extract_pattern(
            r"PAN of Employee\s*([A-Z]{5}[0-9]{4}[A-Z])",
            text,
        )

        entities["employee_name"] = self.extract_pattern(
            r"Name\s*Address of Employee\s*([A-Za-z\s]+?)\s*Flat",
            text,
        )
#--------------------------------------------------------------------------------
        address = self.extract_pattern(
            r"Address of Employee\s*(.*?)PAN of Employee",
            text,
        )

        if address and entities.get("employee_name"):
            address = address.replace(entities["employee_name"], "").strip()

        entities["employee_address"] = address
#--------------------------------------------------------------------------------
        # -------------------------------
        # Employer
        # -------------------------------

        entities["employer_name"] = self.extract_pattern(
            r"Address of Employer\s*(.*?)\s*Plot",
            text,
        )

        entities["employer_pan"] = self.extract_pattern(
            r"PAN of Employer\s*([A-Z0-9]+)",
            text,
        )

        entities["employer_tan"] = self.extract_pattern(
            r"TAN of Employer\s*([A-Z0-9]+)",
            text,
        )

        # -------------------------------
        # Years
        # -------------------------------

        entities["assessment_year"] = self.extract_pattern(
            r"Assessment Year\s*([\d-]+)",
            text,
        )

        entities["financial_year"] = self.extract_pattern(
            r"Financial Year\s*([\d-]+)",
            text,
        )

        entities["employment_period"] = self.extract_pattern(
            r"Period of Employment\s*(.*?)Summary",
            text,
        )

        # -------------------------------
        # Salary
        # -------------------------------

        entities["gross_salary"] = self.extract_amount(
            "Gross Salary",
            text,
        )

        entities["basic_salary"] = self.extract_amount(
            "Basic Salary",
            text,
        )

        entities["hra"] = self.extract_amount(
            "House Rent Allowance",
            text,
        )

        entities["special_allowance"] = self.extract_amount(
            "Special Allowance",
            text,
        )

        entities["standard_deduction"] = self.extract_amount(
            "Standard Deduction",
            text,
        )

        entities["professional_tax"] = self.extract_amount(
            "Professional Tax",
            text,
        )

        entities["income_from_salary"] = self.extract_amount(
            "Income Chargeable Under Head Salaries",
            text,
        )

        entities["taxable_income"] = self.extract_amount(
            "Total Taxable Income",
            text,
        )

        entities["tds"] = self.extract_amount(
            "Total Tax Deducted at Source",
            text,
        )

        # -------------------------------
        # Deductions
        # -------------------------------

        entities["section_80c"] = self.extract_amount(
            "Section 80C",
            text,
        )

        entities["section_80d"] = self.extract_amount(
            "Section 80D|Section 8OD",
            text,
        )

        # -------------------------------
        # Dates
        # -------------------------------

        entities["issue_date"] = self.extract_pattern(
            r"Date:\s*([\dA-Za-z-]+)",
            text,
        )

        entities["place"] = self.extract_pattern(
            r"Place:\s*([A-Za-z ]+)",
            text,
        )

        return entities