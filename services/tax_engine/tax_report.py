"""
tax_report.py
-------------

Generates a professional tax report
from the Tax Engine output.

Author: CAAI Team
"""

from services.tax_engine.tax_utils import TaxUtils


class TaxReport:

    def generate(self, tax_result):

        old = tax_result["old_regime"]
        new = tax_result["new_regime"]

        report = {

            "summary": {

                "status": "Completed",

                "recommended_regime":
                    tax_result["recommended_regime"],

                "estimated_saving":
                    TaxUtils.format_currency(
                        tax_result["tax_saved"]
                    ),

                "reason":
                    self._recommendation_reason(
                        old,
                        new,
                        tax_result["recommended_regime"]
                    ),

                "comparison":

                    f"Old Regime Tax: "
                    f"{TaxUtils.format_currency(old['total_tax'])} | "

                    f"New Regime Tax: "
                    f"{TaxUtils.format_currency(new['total_tax'])}"

            },

            "taxpayer": {

                "gross_salary":
                    TaxUtils.format_currency(
                        old["gross_salary"]
                    ),

                "taxable_income":
                    TaxUtils.format_currency(
                        old["calculated_taxable_income"]
                    ),

                "deductions":
                    TaxUtils.format_currency(
                        old["total_deductions"]
                    )

            },

            "old_regime": {

                "income_tax":
                    TaxUtils.format_currency(
                        old["income_tax"]
                    ),

                "cess":
                    TaxUtils.format_currency(
                        old["cess"]
                    ),

                "total_tax":
                    TaxUtils.format_currency(
                        old["total_tax"]
                    )

            },

            "new_regime": {

                "income_tax":
                    TaxUtils.format_currency(
                        new["income_tax"]
                    ),

                "cess":
                    TaxUtils.format_currency(
                        new["cess"]
                    ),

                "total_tax":
                    TaxUtils.format_currency(
                        new["total_tax"]
                    )

            },

            "validation": {

                "old_regime":

                    old["validation"],

                "new_regime":

                    new["validation"]

            }

        }

        return report

    def _recommendation_reason(self, old, new, regime):

        if regime == "Old Regime":

            return (

                "Old Tax Regime results in a lower tax "
                "liability after considering eligible "
                "deductions."

            )

        elif regime == "New Regime":

            return (

                "New Tax Regime results in a lower tax "
                "liability based on your income and "
                "available deductions."

            )

        return "Both tax regimes produce nearly identical tax liability."