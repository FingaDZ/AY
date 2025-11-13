"""Test simplifié - Import direct des ENUMs"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

# Import direct sans passer par database
import enum

class SituationFamiliale(str, enum.Enum):
    CELIBATAIRE = "Célibataire"
    MARIE = "Marié"

class StatutContrat(str, enum.Enum):
    ACTIF = "Actif"
    INACTIF = "Inactif"

# Test des conversions
print("Test 1: String vers ENUM")
try:
    sf = SituationFamiliale("Marié")
    print(f"✓ SituationFamiliale('Marié') = {sf}")
    print(f"  Type: {type(sf)}")
    print(f"  Value: {sf.value}")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\nTest 2: ENUM vers string")
try:
    sf2 = SituationFamiliale.MARIE
    print(f"✓ SituationFamiliale.MARIE = {sf2}")
    print(f"  Type: {type(sf2)}")
    print(f"  Value: {sf2.value}")
    print(f"  Égalité avec 'Marié': {sf2 == 'Marié'}")
    print(f"  Égalité avec autre ENUM: {sf2 == SituationFamiliale('Marié')}")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\nTest 3: Assignation directe dans dict")
try:
    data = {"situation": "Marié"}
    print(f"✓ Dict avec string: {data}")
    # Simule ce que fait SQLAlchemy
    print(f"  Conversion: SituationFamiliale(data['situation']) = {SituationFamiliale(data['situation'])}")
except Exception as e:
    print(f"✗ Erreur: {e}")

print("\nTest 4: String invalide")
try:
    sf_invalid = SituationFamiliale("Invalid")
    print(f"✗ Pas d'erreur (ne devrait pas arriver): {sf_invalid}")
except ValueError as e:
    print(f"✓ ValueError attendue: {e}")
