
"""
slab_calculator.py
------------------
Income Tax Slab Calculator for Assessment Year 2026-27.

Calculates basic income tax for:
- Old Regime (individual below 60 years)
- New Regime

Cess and rebate should be handled separately.
"""

from services.tax_engine.tax_utils import TaxUtils


class SlabCalculator:

    @staticmethod
    def _calculate_progressive_tax(taxable_income, slabs):
        income = max(0, TaxUtils.clean_amount(taxable_income))
        tax = 0.0
        previous_limit = 0

        for limit, rate in slabs:
            if income <= previous_limit:
                break

            taxable_in_slab = min(income, limit) - previous_limit
            tax += taxable_in_slab * rate
            previous_limit = limit

        return round(tax, 2)

    @staticmethod
    def calculate_old_regime_tax(taxable_income):
        slabs = [
            (250000, 0.00),
            (500000, 0.05),
            (1000000, 0.20),
            (float("inf"), 0.30),
        ]

        tax = SlabCalculator._calculate_progressive_tax(
            taxable_income, slabs
        )
        return TaxUtils.calculate_total_tax(tax)

    @staticmethod
    def calculate_new_regime_tax(taxable_income):
        slabs = [
            (400000, 0.00),
            (800000, 0.05),
            (1200000, 0.10),
            (1600000, 0.15),
            (2000000, 0.20),
            (2400000, 0.25),
            (float("inf"), 0.30),
        ]

        tax = SlabCalculator._calculate_progressive_tax(
            taxable_income, slabs
        )
        return TaxUtils.calculate_total_tax(tax)
