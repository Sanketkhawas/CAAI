"""
tax_engine.py
-------------

Main Tax Engine.

Coordinates:
- Old Regime Calculator
- New Regime Calculator
- Tax Comparison
- Recommendation

Author: CAAI Team
"""

from services.tax_engine.old_regime import OldRegimeCalculator
from services.tax_engine.new_regime import NewRegimeCalculator


class TaxEngine:

    def __init__(self):

        self.old_calculator = OldRegimeCalculator()
        self.new_calculator = NewRegimeCalculator()

    def calculate(self, entities):
        """
        Calculate tax under both regimes and recommend the better one.

        Parameters
        ----------
        entities : dict
            Extracted Form 16 entities.

        Returns
        -------
        dict
        """

        old_result = self.old_calculator.calculate(entities)

        new_result = self.new_calculator.calculate(entities)

        old_tax = old_result["total_tax"]
        new_tax = new_result["total_tax"]

        if old_tax < new_tax:

            recommended = "Old Regime"
            tax_saved = round(new_tax - old_tax, 2)

        elif new_tax < old_tax:

            recommended = "New Regime"
            tax_saved = round(old_tax - new_tax, 2)

        else:

            recommended = "Either"
            tax_saved = 0

        return {

            "old_regime": old_result,

            "new_regime": new_result,

            "recommended_regime": recommended,

            "tax_saved": tax_saved

        }