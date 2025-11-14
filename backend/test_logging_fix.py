from services.logging_service import clean_data_for_logging
from decimal import Decimal

print("Testing clean_data_for_logging...")
test_data = {
    'id': 1,
    'nom': 'Test',
    'salaire': Decimal('25000.00'),
    'prime': Decimal('750.00')
}

result = clean_data_for_logging(test_data)

print(f"\nInput:")
print(f"  salaire: {test_data['salaire']} (type: {type(test_data['salaire']).__name__})")
print(f"  prime: {test_data['prime']} (type: {type(test_data['prime']).__name__})")

print(f"\nOutput:")
print(f"  salaire: {result['salaire']} (type: {type(result['salaire']).__name__})")
print(f"  prime: {result['prime']} (type: {type(result['prime']).__name__})")

if isinstance(result['salaire'], float) and isinstance(result['prime'], float):
    print("\n✅ Fix is WORKING! Decimals converted to floats.")
else:
    print("\n❌ Fix NOT working! Still has Decimal types.")
