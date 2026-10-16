
"""
old_regime.py
-------------
Old Tax Regime Calculator for FY 2025-26 / AY 2026-27.
"""

from services.tax_engine.tax_utils import TaxUtils
from services.tax_engine.slab_calculator import SlabCalculator


class OldRegimeCalculator:

    def calculate(self, entities):
        gross_salary = TaxUtils.clean_amount(
            entities.get("gross_salary")
        )

        standard_value = entities.get("standard_deduction")
        standard_deduction = min(
            TaxUtils.clean_amount(
                50000 if standard_value is None
                else standard_value
            ),
            50000
        )

        professional_tax = TaxUtils.clean_amount(
            entities.get("professional_tax")
        )

        other_income = TaxUtils.clean_amount(
            entities.get("other_sources_income")
        )

        house_property_income = TaxUtils.clean_amount(
            entities.get("house_property_income")
        )

        section_80c = min(
            TaxUtils.clean_amount(entities.get("section_80c")),
            150000
        )

        section_80d = TaxUtils.clean_amount(
            entities.get("section_80d")
        )

        section_80ccd2 = TaxUtils.clean_amount(
            entities.get("section_80ccd2")
        )

        salary_income = max(
                gross_salary - standard_deduction - professional_tax,
                0
            )

        gross_total_income = (
                salary_income
                + other_income
                + house_property_income
            )

        chapter_via_deductions = (
                section_80c + section_80d + section_80ccd2
            )

        total_deductions = (
                standard_deduction
                + professional_tax
                + chapter_via_deductions
            )

            # Salary deductions have already been applied above.
            # Subtract Chapter VI-A deductions only once.
        calculated_taxable_income = max(
                gross_total_income - chapter_via_deductions, 0
            )

    

        tax = SlabCalculator.calculate_old_regime_tax(
            calculated_taxable_income
        )

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

        validation_passed =  {
        "passed": None,
        "status": "not_comparable",
        "difference": difference,
        "message": (
        "Not compared: Form 16 taxable income may reflect "
        "the regime used for the source calculation. "
        "The old-regime result is an alternative estimate."
    )
}
        return {
            "regime": "Old",
            "gross_salary": gross_salary,
            "standard_deduction": standard_deduction,
            "professional_tax": professional_tax,
            "salary_income": salary_income,
            "other_sources_income": other_income,
            "house_property_income": house_property_income,
            "gross_total_income": gross_total_income,
            "section_80c": section_80c,
            "section_80d": section_80d,
            "section_80ccd2": section_80ccd2,
            "total_deductions": total_deductions,
            "calculated_taxable_income": calculated_taxable_income,
            "ocr_taxable_income": ocr_taxable_income,
            "difference": difference,
            "validation": {
                "passed": validation_passed,
                "difference": difference,
                "message": (
                    "Calculated taxable income matches Form 16."
                    if validation_passed
                    else
                    "Calculated taxable income differs from Form 16; "
                    "review the inputs and document."
                    if difference is not None
                    else
                    "Form 16 taxable income was not available "
                    "for reconciliation."
                )
            },
            "income_tax": tax["income_tax"],
            "cess": tax["cess"],
            "total_tax": tax["total_tax"]
        }
