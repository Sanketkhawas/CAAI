
"""
Intent Classifier
-----------------
Classifies common Indian income-tax questions using keyword matching.
No external AI call is required.
"""

import re
import unicodedata


INTENTS = {
    "tax_regime": [
        "regime",
        "old regime",
        "new regime",
        "which regime",
        "better regime",
        "compare tax",
        "tax comparison",
    ],
    "salary": [
        "salary",
        "gross income",
        "annual income",
        "taxable income",
        "total income",
        "income from salary",
        "salary income",
    ],
    "refund": [
        "refund",
        "tax refund",
        "refund status",
        "return money",
        "refund amount",
    ],
    "tds": [
        "tds",
        "tax deducted",
        "tax deduction at source",
        "form 26as",
        "form 16a",
    ],
    "deduction": [
        "80c",
        "80d",
        "80ccd",
        "deduction",
        "deductions",
        "save tax",
        "saving tax",
        "tax saving",
        "investment",
        "elss",
        "ppf",
        "nps",
    ],
    "form16": [
        "form 16",
        "form16",
        "form sixteen",
    ],
    "filing": [
        "file itr",
        "income tax return",
        "itr filing",
        "file my return",
        "itr deadline",
        "filing deadline",
        "due date",
        "assessment year",
        "financial year",
    ],
    "tax_calculation": [
        "calculate tax",
        "tax calculation",
        "tax liability",
        "how much tax",
        "tax payable",
        "tax amount",
        "tax saved",
    ],
}


def _normalize(text):
    """Normalize user text for predictable matching."""
    text = unicodedata.normalize("NFKC", text or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def detect_intent(question):
    """
    Return the first matching intent, or 'general'.

    Specific categories are checked before broad categories to reduce
    accidental classification from generic words.
    """
    question = _normalize(question)

    if not question:
        return "general"

    # Check specific categories before broader salary/deduction terms.
    priority = [
        "form16",
        "tax_regime",
        "tax_calculation",
        "tds",
        "refund",
        "filing",
        "deduction",
        "salary",
    ]

    for intent in priority:
        for keyword in INTENTS[intent]:
            keyword = _normalize(keyword)

            # Use word boundaries for short keywords such as "tds"
            # and "80c" to avoid matching unrelated words.
            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            if re.search(pattern, question):
                return intent

    return "general"
