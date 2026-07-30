from services.tax_engine.Tax_engine import TaxEngine

entities = {

    "gross_salary": 900000,

    "standard_deduction": 50000,

    "professional_tax": 2400,

    "section_80c": 100000,

    "section_80d": 15000,

    "taxable_income": 732600

}

engine = TaxEngine()

result = engine.calculate(entities)

print("\n========== TAX ENGINE ==========\n")

print("Recommended Regime :", result["recommended_regime"])
print("Tax Saved          : ₹", result["tax_saved"])

print("\n========== OLD REGIME ==========\n")

for key, value in result["old_regime"].items():

    if isinstance(value, dict):

        print(f"{key.upper()}")

        for k, v in value.items():
            print(f"   {k:15}: {v}")

    else:

        print(f"{key:25}: {value}")

print("\n========== NEW REGIME ==========\n")

for key, value in result["new_regime"].items():

    if isinstance(value, dict):

        print(f"{key.upper()}")

        for k, v in value.items():
            print(f"   {k:15}: {v}")

    else:

        print(f"{key:25}: {value}")