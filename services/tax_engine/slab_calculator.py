"""
slab_calculator.py
------------------

Income Tax Slab Calculator.

Calculates tax for:
- Old Regime
- New Regime

Author: CAAI Team
"""

from services.tax_engine.tax_utils import TaxUtils


class SlabCalculator:

    # -----------------------------
    # Old Regime
    # -----------------------------
    @staticmethod
    def calculate_old_regime_tax(taxable_income):

        taxable_income = TaxUtils.clean_amount(taxable_income)

        tax = 0

        if taxable_income <= 250000:
            tax = 0

        elif taxable_income <= 500000:
            tax = (taxable_income - 250000) * 0.05

        elif taxable_income <= 1000000:
            tax = (
                12500 +
                (taxable_income - 500000) * 0.20
            )

        else:
            tax = (
                112500 +
                (taxable_income - 1000000) * 0.30
            )

        return TaxUtils.calculate_total_tax(tax)

    # -----------------------------
    # New Regime
    # -----------------------------
    @staticmethod
    def calculate_new_regime_tax(taxable_income):

        taxable_income = TaxUtils.clean_amount(taxable_income)

        tax = 0

        if taxable_income <= 400000:
            tax = 0

        elif taxable_income <= 800000:
            tax = (taxable_income - 400000) * 0.05

        elif taxable_income <= 1200000:
            tax = (
                20000 +
                (taxable_income - 800000) * 0.10
            )

        elif taxable_income <= 1600000:
            tax = (
                60000 +
                (taxable_income - 1200000) * 0.15
            )

        elif taxable_income <= 2000000:
            tax = (
                120000 +
                (taxable_income - 1600000) * 0.20
            )

        elif taxable_income <= 2400000:
            tax = (
                200000 +
                (taxable_income - 2000000) * 0.25
            )

        else:
            tax = (
                300000 +
                (taxable_income - 2400000) * 0.30
            )

        return TaxUtils.calculate_total_tax(tax)