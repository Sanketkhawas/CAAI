from services.tax_engine.old_regime import OldRegimeCalculator

entities = {

    "gross_salary":900000,

    "standard_deduction":50000,

    "professional_tax":2400,

    "section_80c":100000,

    "section_80d":15000,

    "taxable_income": 732600 #ocr taxable income
}

calculator = OldRegimeCalculator()

result = calculator.calculate(entities)

print("\n===== OLD REGIME =====\n")

for key, value in result.items():

    if isinstance(value, dict):

        print(f"\n{key.upper()}")

        for k, v in value.items():
            print(f"   {k:15}: {v}")

    else:

        print(f"{key:25}: {value}")