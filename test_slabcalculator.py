from services.tax_engine.slab_calculator import SlabCalculator

print("===== OLD REGIME =====\n")

result = SlabCalculator.calculate_old_regime_tax(732600)

print(result)

print("\n===== NEW REGIME =====\n")

result = SlabCalculator.calculate_new_regime_tax(732600)

print(result)