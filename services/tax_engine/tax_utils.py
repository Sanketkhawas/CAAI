"""
tax_utils.py
------------

Utility functions for the Tax Engine.

Responsibilities:
- Convert strings to numeric values
- Format currency
- Calculate Health & Education Cess
- Round tax values
- Safe extraction of values

Author: CAAI Team
"""

import re


class TaxUtils:

    @staticmethod
    def clean_amount(value):
        """
        Converts amount strings into float.

        Examples:
            "Rs. 9,00,000" -> 900000.0
            "900000" -> 900000.0
            None -> 0.0
        """

        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        value = str(value)

        value = value.replace("Rs.", "")
        value = value.replace("Rs", "")
        value = value.replace(",", "")
        value = value.strip()

        value = re.sub(r"[^\d.]", "", value)

        if value == "":
            return 0.0

        return float(value)

    @staticmethod
    def calculate_cess(income_tax):
        """
        Calculates 4% Health & Education Cess.
        """

        return round(income_tax * 0.04, 2)

    @staticmethod
    def round_tax(amount):
        """
        Rounds tax to two decimal places.
        """

        return round(amount, 2)

    @staticmethod
    def calculate_total_tax(income_tax):
        """
        Returns total tax including cess.
        """

        cess = TaxUtils.calculate_cess(income_tax)

        return {
            "income_tax": TaxUtils.round_tax(income_tax),
            "cess": TaxUtils.round_tax(cess),
            "total_tax": TaxUtils.round_tax(income_tax + cess)
        }

    @staticmethod
    def safe_get(data, key, default=0):
        """
        Safely fetch a value from dictionary.
        """

        value = data.get(key, default)

        if value is None:
            return default

        return value

    @staticmethod
    def format_currency(amount):
        """
        Returns Indian currency formatted string.

        Example:
            900000 -> ₹900,000.00
        """

        amount = TaxUtils.clean_amount(amount)

        return f"₹{amount:,.2f}"