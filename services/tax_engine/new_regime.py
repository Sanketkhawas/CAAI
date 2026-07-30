"""
new_regime.py
-------------

New Tax Regime Calculator.

Uses extracted Form 16 entities to calculate
tax liability under the New Tax Regime.

Author: CAAI Team
"""

from services.tax_engine.tax_utils import TaxUtils
from services.tax_engine.slab_calculator import SlabCalculator


class NewRegimeCalculator:

    def calculate(self, entities):

        gross_salary = TaxUtils.safe_get(
            entities,
            "gross_salary"
        )

        standard_deduction = TaxUtils.safe_get(
            entities,
            "standard_deduction"
        )

        professional_tax = TaxUtils.safe_get(
            entities,
            "professional_tax"
        )

        section_80c = TaxUtils.safe_get(
            entities,
            "section_80c"
        )

        section_80d = TaxUtils.safe_get(
            entities,
            "section_80d"
        )

        deductions = (

            standard_deduction +

            professional_tax +

            section_80c +

            section_80d

        )

        calculated_taxable_income = max(
            gross_salary - deductions,
            0
        )

        ocr_taxable_income = TaxUtils.safe_get(
            entities,
            "taxable_income"
        )

        difference = abs(
            calculated_taxable_income -
            ocr_taxable_income
        )

        tax = SlabCalculator.calculate_new_regime_tax(
            calculated_taxable_income
        )

        return {

            "regime": "New",

            "gross_salary": gross_salary,

            "total_deductions": deductions,

            "ocr_taxable_income": ocr_taxable_income,

            "calculated_taxable_income": calculated_taxable_income,

            "difference": difference,

            "validation": {

                "passed": difference <= 100,

                "difference": difference,

                "message": (
                    "OCR and calculated taxable income match."
                    if difference <= 100
                    else "Mismatch between OCR and calculated taxable income."
                )

            },

            "income_tax": tax["income_tax"],

            "cess": tax["cess"],

            "total_tax": tax["total_tax"]

        }