"""Script de migration pour ajouter prime_nuit_agent_securite"""
from database import engine
import sqlalchemy as sa

sql = """
ALTER TABLE employes 
ADD COLUMN prime_nuit_agent_securite BOOLEAN NOT NULL DEFAULT FALSE;
"""

with engine.connect() as conn:
    conn.execute(sa.text(sql))
    conn.commit()
    print('✅ Migration prime_nuit_agent_securite effectuée')
