"""
recommendation_engine.py
------------------------

Explainable Recommendation Engine for CAAI.

Responsibilities:
- Consume Financial Profile
- Consume Tax Engine output
- Consume Profile Validation output
- Generate rule-based recommendations
- Explain why each recommendation was generated
- Use Tax Engine as the source of truth for regime selection

The Recommendation Engine does NOT calculate tax.
"""

from services import financial_profile
from services.recommendation.recommendation_rules import (
    REGIME_RULES,
    DEDUCTION_RULES,
    INVESTMENT_RULES,
    DATA_RULES,
    HIGH,
    MEDIUM,
    LOW,
)


class RecommendationEngine:

    def __init__(self):
        pass

    # ============================================================
    # MAIN GENERATOR
    # ============================================================

    def generate(
        self,
        financial_profile,
        tax_result,
        validation_result=None
    ):
        """
        Generate explainable recommendations.

        Parameters
        ----------
        financial_profile : dict
            Validated financial profile.

        tax_result : dict
            Output directly from TaxEngine.calculate().

        validation_result : dict, optional
            Output from FinancialProfileValidator.

        Returns
        -------
        dict
        """

        recommendations = []

        # --------------------------------------------------------
        # 1. Validation Errors
        # --------------------------------------------------------

        if validation_result:

            errors = validation_result.get("errors", [])

            if errors:
                recommendations.append(
                    self.add_recommendation(
                        DATA_RULES["MISSING_INFORMATION"],
                        message=(
                            "Important financial information could not be "
                            "validated and should be reviewed before using "
                            "the recommendations."
                        ),
                        reason=(
                            "The Financial Profile Validator reported "
                            "validation errors."
                        ),
                        evidence={
                            "errors": errors
                        }
                    )
                )

        # --------------------------------------------------------
        # 2. Tax Regime Recommendation
        # --------------------------------------------------------

        regime_recommendation = self.evaluate_regime(
            tax_result
        )

        if regime_recommendation:
            recommendations.append(
                regime_recommendation
            )

        # --------------------------------------------------------
        # 3. Deduction Recommendations
        # --------------------------------------------------------

        recommendations.extend(
            self.evaluate_deductions(
                financial_profile
            )
        )

        # --------------------------------------------------------
        # 4. Investment Recommendations
        # --------------------------------------------------------

        recommendations.extend(
            self.evaluate_investments(
                financial_profile
            )
        )

        # --------------------------------------------------------
        # 5. Income / Data Consistency
        # --------------------------------------------------------

        recommendations.extend(
            self.evaluate_income_consistency(
                financial_profile,
                validation_result
            )
        )

        # --------------------------------------------------------
        # 6. Missing Information
        # --------------------------------------------------------

        missing_recommendation = (
            self.evaluate_missing_information(
                financial_profile
            )
        )

        if missing_recommendation:
            recommendations.append(
                missing_recommendation
            )

        # --------------------------------------------------------
        # 7. Recommended Regime
        # --------------------------------------------------------

        recommended_regime = (
            tax_result.get("recommended_regime")
        )

        # --------------------------------------------------------
        # 8. Confidence
        # --------------------------------------------------------

        confidence = self.calculate_confidence(
            recommendations,
            validation_result
        )

        # --------------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------------

        return {

            "summary": {

                "recommended_regime":
                    recommended_regime,

                "confidence":
                    confidence,

                "recommendation_count":
                    len(recommendations)
            },

            "recommendations":
                recommendations
        }

    # ============================================================
    # REGIME EVALUATION
    # ============================================================

    def evaluate_regime(self, tax_result):

        """
        Evaluate the tax regime using TaxEngine output.

        IMPORTANT:
        TaxEngine is the source of truth for regime selection.
        """

        if not tax_result:
            return None

        old_result = tax_result.get(
            "old_regime",
            {}
        )

        new_result = tax_result.get(
            "new_regime",
            {}
        )

        old_tax = self.to_number(
            old_result.get("total_tax")
        )

        new_tax = self.to_number(
            new_result.get("total_tax")
        )

        recommended_regime = (
            tax_result.get(
                "recommended_regime"
            )
        )

        tax_saved = self.to_number(
            tax_result.get("tax_saved")
        )

        # --------------------------------------------------------
        # Missing tax values
        # --------------------------------------------------------

        if old_tax is None or new_tax is None:

            return None

        # --------------------------------------------------------
        # New Regime
        # --------------------------------------------------------

        if recommended_regime == "New Regime":

            rule = REGIME_RULES[
                "NEW_REGIME_BETTER"
            ]

            return self.add_recommendation(

                rule,

                message=(
                    "The New Tax Regime appears more beneficial "
                    "based on the current financial profile."
                ),

                reason=(
                    f"Estimated tax under the New Regime is "
                    f"₹{new_tax:,.2f}, compared with "
                    f"₹{old_tax:,.2f} under the Old Regime."
                ),

                evidence={

                    "old_regime_tax":
                        old_tax,

                    "new_regime_tax":
                        new_tax,

                    "tax_saved":
                        tax_saved
                }
            )

        # --------------------------------------------------------
        # Old Regime
        # --------------------------------------------------------

        if recommended_regime == "Old Regime":

            rule = REGIME_RULES[
                "OLD_REGIME_BETTER"
            ]

            return self.add_recommendation(

                rule,

                message=(
                    "The Old Tax Regime appears more beneficial "
                    "based on the current financial profile."
                ),

                reason=(
                    f"Estimated tax under the Old Regime is "
                    f"₹{old_tax:,.2f}, compared with "
                    f"₹{new_tax:,.2f} under the New Regime."
                ),

                evidence={

                    "old_regime_tax":
                        old_tax,

                    "new_regime_tax":
                        new_tax,

                    "tax_saved":
                        tax_saved
                }
            )

        # --------------------------------------------------------
        # Either
        # --------------------------------------------------------

        if recommended_regime == "Either":

            rule = REGIME_RULES[
                "REGIME_SIMILAR"
            ]

            return self.add_recommendation(

                rule,

                message=(
                    "The estimated tax under both regimes is "
                    "similar based on the current profile."
                ),

                reason=(
                    f"Old Regime tax is ₹{old_tax:,.2f} "
                    f"and New Regime tax is ₹{new_tax:,.2f}."
                ),

                evidence={

                    "old_regime_tax":
                        old_tax,

                    "new_regime_tax":
                        new_tax,

                    "tax_saved":
                        tax_saved
                }
            )

        return None

    # ============================================================
    # DEDUCTIONS
    # ============================================================

    def evaluate_deductions(self, profile):

        recommendations = []

        deductions = profile.get(
            "deductions",
            {}
        )

        section_80c = self.to_number(
            deductions.get("section_80c")
        )

        section_80d = self.to_number(
            deductions.get("section_80d")
        )

        # --------------------------------------------------------
        # 80C
        # --------------------------------------------------------

        if section_80c and section_80c > 0:

            rule = DEDUCTION_RULES[
                "SECTION_80C_PRESENT"
            ]

            recommendations.append(

                self.add_recommendation(

                    rule,

                    message=(
                        "Documented Section 80C investment "
                        "information is available in the profile."
                    ),

                    reason=(
                        f"The profile contains "
                        f"₹{section_80c:,.2f} under Section 80C."
                    ),

                    evidence={
                        "section_80c":
                            section_80c
                    }
                )
            )

        # --------------------------------------------------------
        # 80D
        # --------------------------------------------------------

        if section_80d and section_80d > 0:

            rule = DEDUCTION_RULES[
                "SECTION_80D_PRESENT"
            ]

            recommendations.append(

                self.add_recommendation(

                    rule,

                    message=(
                        "Documented Section 80D deduction "
                        "information is available in the profile."
                    ),

                    reason=(
                        f"The profile contains "
                        f"₹{section_80d:,.2f} under Section 80D."
                    ),

                    evidence={
                        "section_80d":
                            section_80d
                    }
                )
            )

        # --------------------------------------------------------
        # General deductions
        # --------------------------------------------------------

        if section_80c or section_80d:

            rule = DEDUCTION_RULES[
                "DEDUCTIONS_AVAILABLE"
            ]

            evidence = {}

            if section_80c:
                evidence["section_80c"] = section_80c

            if section_80d:
                evidence["section_80d"] = section_80d

            recommendations.append(

                self.add_recommendation(

                    rule,

                    message=(
                        "Documented deductions should be "
                        "included when comparing applicable "
                        "tax regimes."
                    ),

                    reason=(
                        "The financial profile contains "
                        "deduction-related information."
                    ),

                    evidence=evidence
                )
            )

        return recommendations

    # ============================================================
    # INVESTMENTS
    # ============================================================
    
    def evaluate_investments(self, profile):
        recommendations = []

        # Read investment data from the supplied profile dictionary.
        investments = profile.get("investments") or []

        if not isinstance(investments, list):
            investments = []

        tax_info = profile.get("tax") or {}
        profile_financial_year = tax_info.get("financial_year")

        for investment in investments:
            if not isinstance(investment, dict):
                continue

            investment_type = (
                investment.get("investment_type")
                or investment.get("type")
                or "Investment"
            )

            financial_year = investment.get("financial_year")
            section = investment.get("section")

            # Keep extracted amounts separate to avoid double counting.
            amount_fields = [
                ("amount", investment.get("amount")),
                ("investment_amount", investment.get("investment_amount")),
                (
                    "employer_nps_contribution",
                    investment.get("employer_nps_contribution"),
                ),
                (
                    "mutual_fund_invested",
                    investment.get("mutual_fund_invested"),
                ),
            ]

            found_amount = False

            for amount_field, raw_amount in amount_fields:
                amount = self.to_number(raw_amount)

                if amount is None or amount <= 0:
                    continue

                found_amount = True

                rule = INVESTMENT_RULES["INVESTMENT_FOUND"]

                recommendations.append(
                    self.add_recommendation(
                        rule,
                        message=(
                            f"{investment_type}: ₹{amount:,.2f} "
                            "was extracted from the investment proof."
                        ),
                        reason=(
                            "This amount was extracted from the uploaded "
                            "document. Verify its eligibility and tax "
                            "treatment before claiming a deduction."
                        ),
                        evidence={
                            "amount": amount,
                            "amount_field": amount_field,
                            "financial_year": financial_year,
                            "investment_type": investment_type,
                            "deduction_claim_status": investment.get(
                                "deduction_claim_status"
                            ),
                            "eligible_deduction": investment.get(
                                "eligible_deduction"
                            ),
                        },
                    )
                )

            if not found_amount:
                recommendations.append(
                    self.add_recommendation(
                        DATA_RULES["MISSING_INFORMATION"],
                        message=(
                            f"The amount for {investment_type} "
                            "could not be confirmed."
                        ),
                        reason=(
                            "The investment proof does not contain a "
                            "usable positive amount in the recognized "
                            "amount fields."
                        ),
                        evidence={
                            "investment_type": investment_type,
                            "financial_year": financial_year,
                            "profile_financial_year": profile_financial_year,
                        },
                    )
                )

            if not section:
                recommendations.append(
                    self.add_recommendation(
                        INVESTMENT_RULES["INVESTMENT_SECTION_MISSING"],
                        message=(
                            "The tax section associated with this "
                            "investment should be reviewed."
                        ),
                        reason=(
                            "The extracted proof does not explicitly "
                            "identify a tax-section classification."
                        ),
                        evidence={
                            "investment_type": investment_type,
                            "financial_year": financial_year,
                            "profile_financial_year": profile_financial_year,
                        },
                    )
                )

        return recommendations

    
    def evaluate_income_consistency(self, financial_profile, validation_result):
        """
        Generate a recommendation when financial profile validation
        reports inconsistencies or warnings.
        """
        recommendations = []

        if not isinstance(validation_result, dict):
            return recommendations

        warnings = validation_result.get("warnings") or []
        errors = validation_result.get("errors") or []

        if errors:
            recommendations.append({
                "id": "PROFILE_VALIDATION_001",
                "category": "Data Validation",
                "priority": "HIGH",
                "title": "Review your financial profile",
                "message": (
                    "Some financial details could not be validated. "
                    "Review your uploaded documents and extracted values."
                ),
                "reason": "; ".join(str(error) for error in errors),
                "evidence": {
                    "errors": errors
                }
            })

        if warnings:
            recommendations.append({
                "id": "PROFILE_VALIDATION_002",
                "category": "Income Consistency",
                "priority": "MEDIUM",
                "title": "Verify your income details",
                "message": (
                    "Some financial details require verification before "
                    "you rely on the tax estimate."
                ),
                "reason": "; ".join(str(warning) for warning in warnings),
                "evidence": {
                    "warnings": warnings
                }
            })

        return recommendations


    # ============================================================
    # MISSING INFORMATION
    # ============================================================

    def evaluate_missing_information(
        self,
        profile
    ):

        required = [

            (
                "personal",
                "name"
            ),

            (
                "personal",
                "pan"
            ),

            (
                "income",
                "gross_salary"
            ),

            (
                "tax",
                "financial_year"
            ),

            (
                "tax",
                "assessment_year"
            )
        ]

        missing = []

        for section, field in required:

            value = (
                profile
                .get(section, {})
                .get(field)
            )

            if value is None or value == "":

                missing.append(
                    f"{section}.{field}"
                )

        if not missing:
            return None

        rule = DATA_RULES[
            "MISSING_INFORMATION"
        ]

        return self.add_recommendation(

            rule,

            message=(
                "Some required financial profile "
                "information is missing."
            ),

            reason=(
                "The recommendation engine requires "
                "complete financial information for "
                "reliable decision support."
            ),

            evidence={
                "missing_fields":
                    missing
            }
        )

    # ============================================================
    # RECOMMENDED REGIME
    # ============================================================

    def get_recommended_regime(
        self,
        tax_result
    ):

        """
        Return the regime selected by TaxEngine.

        TaxEngine remains the source of truth.
        """

        if not tax_result:
            return None

        return tax_result.get(
            "recommended_regime"
        )

    # ============================================================
    # CONFIDENCE
    # ============================================================

    def calculate_confidence(
        self,
        recommendations,
        validation_result=None
    ):

        # --------------------------------------------------------
        # Validation errors = Low confidence
        # --------------------------------------------------------

        if validation_result:

            errors = validation_result.get(
                "errors",
                []
            )

            if errors:
                return "Low"

        # --------------------------------------------------------
        # High-priority recommendations
        # --------------------------------------------------------

        high_priority_count = sum(

            1

            for recommendation
            in recommendations

            if recommendation.get(
                "priority"
            ) == HIGH
        )

        # --------------------------------------------------------
        # A clean profile with regime recommendation
        # gets High confidence.
        # --------------------------------------------------------

        regime_found = any(

            recommendation.get(
                "category"
            ) == "Tax Regime"

            for recommendation
            in recommendations
        )

        if regime_found and high_priority_count > 0:

            return "High"

        # --------------------------------------------------------
        # Otherwise Medium
        # --------------------------------------------------------

        if recommendations:

            return "Medium"

        return "Low"

    # ============================================================
    # RECOMMENDATION BUILDER
    # ============================================================

    def add_recommendation(
        self,
        rule,
        message,
        reason,
        evidence
    ):

        return {

            "id":
                rule["id"],

            "category":
                rule["category"],

            "title":
                rule["title"],

            "priority":
                rule["priority"],

            "message":
                message,

            "reason":
                reason,

            "evidence":
                evidence
        }

    # ============================================================
    # NUMBER CONVERSION
    # ============================================================

    @staticmethod
    def to_number(value):

        if value is None:
            return None

        try:
            return float(value)

        except (
            ValueError,
            TypeError
        ):
                return None