
"""
new_regime.py
-------------
New Tax Regime Calculator for FY 2025-26 / AY 2026-27.
"""

from services.tax_engine.tax_utils import TaxUtils
from services.tax_engine.slab_calculator import SlabCalculator


class NewRegimeCalculator:

    def calculate(self, entities):
        gross_salary = TaxUtils.clean_amount(
            entities.get("gross_salary")
        )

        standard_deduction = min(
            TaxUtils.clean_amount(
                entities.get("standard_deduction")
                if entities.get("standard_deduction") is not None
                else 75000
            ),
            75000
        )

        professional_tax = 0.0
        other_income = TaxUtils.clean_amount(
            entities.get("other_sources_income")
        )
        house_property_income = TaxUtils.clean_amount(
            entities.get("house_property_income")
        )

        section_80ccd2 = TaxUtils.clean_amount(
            entities.get("section_80ccd2")
        )

        # Calculate income before Chapter VI-A deductions.
        salary_income = max(
            gross_salary - standard_deduction - professional_tax,
            0
        )

        gross_total_income = (
            salary_income
            + other_income
            + house_property_income
        )

        # Section 80CCD(2) is allowed under the new regime,
        # subject to applicable statutory eligibility and limits.
        total_deductions = section_80ccd2

        calculated_taxable_income = max(
            gross_total_income - total_deductions, 0
        )

        tax = SlabCalculator.calculate_new_regime_tax(
            calculated_taxable_income
        )

       # Form 16 taxable income reflects the regime used for
        # the employer's calculation. Do not assume it is the
        # correct reference for the independently calculated old regime.

        ocr_value = entities.get("taxable_income")
        ocr_taxable_income = (
            None if ocr_value is None
            else TaxUtils.clean_amount(ocr_value)
        )

        difference = (
            None if ocr_taxable_income is None
            else abs(
                calculated_taxable_income - ocr_taxable_income
            )
        )

        # A comparison against Form 16 alone cannot establish that
        # an alternative-regime calculation is invalid.
        # Report the difference, but do not call it a failed
        # document reconciliation.
        validation_passed = None

        return {
            "regime": "New",
            "gross_salary": gross_salary,
            "standard_deduction": standard_deduction,
            "salary_income": salary_income,
            "other_sources_income": other_income,
            "house_property_income": house_property_income,
            "gross_total_income": gross_total_income,
            "section_80ccd2": section_80ccd2,
            "total_deductions": (
                standard_deduction + professional_tax
                + section_80ccd2
            ),
            "calculated_taxable_income": calculated_taxable_income,
            "ocr_taxable_income": ocr_taxable_income,
            "difference": difference,
            "validation": {
                "passed": None,
                "status": "not_comparable",
                "difference": difference,
                "message": (
                    "The independently calculated New Regime taxable "
                    "income is shown for comparison. Form 16 may reflect "
                    "a different regime or different inputs."
                ),
            },
            "income_tax": tax["income_tax"],
            "cess": tax["cess"],
            "total_tax": tax["total_tax"]
        }
