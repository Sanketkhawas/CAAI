"""
recommendation_rules.py
-----------------------
Rule definitions for the CAAI Recommendation Engine.

These rules operate on the validated Financial Profile
and Tax Engine results.

The rules do not directly perform tax calculations.
They identify situations where a user should review,
consider, or verify something.
"""

# ==========================================================
# PRIORITY LEVELS
# ==========================================================

HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"


# ==========================================================
# REGIME RECOMMENDATION RULES
# ==========================================================

REGIME_RULES = {
    "OLD_REGIME_BETTER": {
        "id": "REGIME_001",
        "category": "Tax Regime",
        "title": "Old Regime appears more beneficial",
        "priority": HIGH,
    },
    "NEW_REGIME_BETTER": {
        "id": "REGIME_002",
        "category": "Tax Regime",
        "title": "New Regime appears more beneficial",
        "priority": HIGH,
    },
    "REGIME_SIMILAR": {
        "id": "REGIME_003",
        "category": "Tax Regime",
        "title": "Tax difference between regimes is small",
        "priority": MEDIUM,
    },
}


# ==========================================================
# DEDUCTION RULES
# ==========================================================

DEDUCTION_RULES = {
    "SECTION_80C_PRESENT": {
        "id": "DEDUCTION_001",
        "category": "Deductions",
        "title": "80C investment identified",
        "priority": MEDIUM,
    },
    "SECTION_80D_PRESENT": {
        "id": "DEDUCTION_002",
        "category": "Deductions",
        "title": "80D deduction identified",
        "priority": MEDIUM,
    },
    "DEDUCTIONS_AVAILABLE": {
        "id": "DEDUCTION_003",
        "category": "Deductions",
        "title": "Documented deductions should be considered",
        "priority": MEDIUM,
    },
}


# ==========================================================
# INVESTMENT RULES
# ==========================================================

INVESTMENT_RULES = {
    "INVESTMENT_FOUND": {
        "id": "INVESTMENT_001",
        "category": "Investment",
        "title": "Investment proof identified",
        "priority": MEDIUM,
    },
    "INVESTMENT_SECTION_MISSING": {
        "id": "INVESTMENT_002",
        "category": "Investment",
        "title": "Investment tax section should be reviewed",
        "priority": MEDIUM,
    },
}


# ==========================================================
# INCOME / DATA CONSISTENCY RULES
# ==========================================================

DATA_RULES = {
    "SALARY_MISMATCH": {
        "id": "DATA_001",
        "category": "Data Consistency",
        "title": "Salary information differs across documents",
        "priority": MEDIUM,
    },
    "BANK_INTEREST_PRESENT": {
        "id": "DATA_002",
        "category": "Income",
        "title": "Bank interest income identified",
        "priority": MEDIUM,
    },
    "MISSING_INFORMATION": {
        "id": "DATA_003",
        "category": "Data Completeness",
        "title": "Additional financial information may be required",
        "priority": HIGH,
    },
}


# ==========================================================
# PROFILE VALIDATION RULES
# ==========================================================

PROFILE_VALIDATION_RULES = {
    "PROFILE_VALIDATION_001": {
        "id": "PROFILE_VALIDATION_001",
        "category": "Data Validation",
        "title": "Review your financial profile",
        "priority": HIGH,
    },
    "PROFILE_VALIDATION_002": {
        "id": "PROFILE_VALIDATION_002",
        "category": "Income Consistency",
        "title": "Verify your income details",
        "priority": MEDIUM,
    },
}


# ==========================================================
# ALL RULE GROUPS
# ==========================================================

RULE_GROUPS = (
    REGIME_RULES,
    DEDUCTION_RULES,
    INVESTMENT_RULES,
    DATA_RULES,
    PROFILE_VALIDATION_RULES,
)


# ==========================================================
# HELPERS
# ==========================================================

def get_rule(rule_group, rule_name):
    """
    Retrieve a rule definition from a rule group.

    Example:
        get_rule(REGIME_RULES, "OLD_REGIME_BETTER")
    """
    if not isinstance(rule_group, dict):
        return None

    return rule_group.get(rule_name)


def get_rule_by_id(rule_id):
    """Retrieve a registered rule using its recommendation ID."""
    if not isinstance(rule_id, str):
        return None

    for group in RULE_GROUPS:
        for rule in group.values():
            if rule.get("id") == rule_id:
                return rule

    return None


def get_valid_rule_ids():
    """Return all registered recommendation IDs."""
    return {
        rule["id"]
        for group in RULE_GROUPS
        for rule in group.values()
        if isinstance(rule.get("id"), str)
    }


def is_valid_recommendation_id(rule_id):
    """Return whether a recommendation ID is registered."""
    return rule_id in get_valid_rule_ids()