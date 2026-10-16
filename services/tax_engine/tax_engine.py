
from services.tax_engine.old_regime import OldRegimeCalculator
from services.tax_engine.new_regime import NewRegimeCalculator


class TaxEngine:
    def __init__(self):
        self.old_calculator = OldRegimeCalculator()
        self.new_calculator = NewRegimeCalculator()

    
    def calculate(self, entities):
        old_result = self.old_calculator.calculate(entities)
        new_result = self.new_calculator.calculate(entities)

        old_tax = old_result["total_tax"]
        new_tax = new_result["total_tax"]

        if old_tax < new_tax:
            recommended = "Old Regime"
            tax_saved = round(new_tax - old_tax, 2)
            recommended_result = old_result
        elif new_tax < old_tax:
            recommended = "New Regime"
            tax_saved = round(old_tax - new_tax, 2)
            recommended_result = new_result
        else:
            recommended = "Either"
            tax_saved = 0
            recommended_result = new_result

        # Only include validations that are actually comparable.
        validations = [
            result["validation"]
            for result in (old_result, new_result)
            if result["validation"].get("status") != "not_comparable"
        ]

        validation_passed = (
            all(v["passed"] for v in validations)
            if validations
            else None
        )

        if validation_passed is True:
            recommendation_status = "Validated estimate"
        elif validation_passed is False:
            recommendation_status = (
                "Provisional - reconcile income and deductions"
            )
        else:
            recommendation_status = "Validation incomplete"

        return {
            "old_regime": old_result,
            "new_regime": new_result,
            "recommended_regime": recommended,
            "recommended_result": recommended_result,
            "tax_saved": tax_saved,
            "validation_passed": validation_passed,
            "recommendation_status": recommendation_status
        }
