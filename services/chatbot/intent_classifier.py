"""
Intent Classifier
-----------------
Detects what the user is asking.
"""

def detect_intent(question):
    question = question.lower().strip()

    intents = {

        "tax_regime": [
            "regime",
            "old regime",
            "new regime",
            "which regime",
            "better regime"
        ],

        "salary": [
            "salary",
            "income",
            "taxable income"
        ],

        "refund": [
            "refund",
            "return money"
        ],

        "tds": [
            "tds",
            "tax deducted"
        ],

        "deduction": [
            "80c",
            "80d",
            "deduction",
            "save tax",
            "investment"
        ],

        "form16": [
            "form 16",
            "form16"
        ]
    }

    for intent, keywords in intents.items():

        for word in keywords:

            if word in question:
                return intent

    return "general"