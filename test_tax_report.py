from pprint import pprint

from services.tax_engine.tax_engine import TaxEngine
from services.tax_engine.tax_report import TaxReport

entities = {

    "gross_salary":900000,

    "standard_deduction":50000,

    "professional_tax":2400,

    "section_80c":100000,

    "section_80d":15000,

    "taxable_income":732600

}

engine = TaxEngine()

result = engine.calculate(entities)

report = TaxReport().generate(result)

print("\n=========== TAX REPORT ===========\n")

pprint(report, width=120)