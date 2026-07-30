from services.tax_engine.tax_utils import TaxUtils

print("===== TAX UTILS TEST =====\n")

print("Clean Amount:")
print(TaxUtils.clean_amount("Rs. 9,00,000"))

print("\nCess:")
print(TaxUtils.calculate_cess(50000))

print("\nTotal Tax:")
print(TaxUtils.calculate_total_tax(50000))

print("\nCurrency:")
print(TaxUtils.format_currency(900000))