
"""
database_service.py
-------------------

Stores Tax Engine results.

Author: CAAI Team
"""

import json

from database.database import db
from database.models import TaxCalculation


class TaxDatabaseService:

    def save(self, document_id, tax_result, report):

        record = TaxCalculation(

    document_id=document_id,

    gross_salary=tax_result["old_regime"]["gross_salary"],

    taxable_income=tax_result["old_regime"]["calculated_taxable_income"],

    total_deductions=tax_result["old_regime"]["total_deductions"],

    old_regime_tax=tax_result["old_regime"]["total_tax"],

    new_regime_tax=tax_result["new_regime"]["total_tax"],

    recommended_regime=tax_result["recommended_regime"],

    tax_saved=tax_result["tax_saved"],

    report=json.dumps(report, indent=4)

)
    
        db.session.add(record)

        db.session.commit()

        return record