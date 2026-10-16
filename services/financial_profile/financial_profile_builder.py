"""
financial_profile_builder.py
----------------------------
Builds a standardized financial profile from OCR-extracted
entities collected from Form 16, salary slips, bank statements,
and investment proofs.

The profile schema is kept compatible with the CAAI
Recommendation Engine.
"""

from typing import Dict, Any, List


class FinancialProfileBuilder:

    def __init__(self):
        pass

    # =========================================================
    # HELPER: PRESERVE VALID ZERO VALUES
    # =========================================================

    @staticmethod
    def first_present(*values):
        """
        Return the first value that is not None or an empty string.

        Unlike `a or b`, this preserves valid numeric zero values.
        """
        for value in values:
            if value is not None and value != "":
                return value

        return None

    # =========================================================
    # MAIN BUILDER
    # =========================================================

    def build(
        self,
        form16: Dict[str, Any] = None,
        salary_slip: Dict[str, Any] = None,
        bank_statement: Dict[str, Any] = None,
        investment_proofs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        form16 = form16 or {}
        salary_slip = salary_slip or {}
        bank_statement = bank_statement or {}
        investment_proofs = investment_proofs or []

        profile = {
            "personal": self.build_personal(
                form16,
                salary_slip,
                investment_proofs
            ),
            "employment": self.build_employment(
                form16,
                salary_slip
            ),
            "income": self.build_income(
                form16,
                salary_slip,
                bank_statement
            ),
            "deductions": self.build_deductions(form16),
            "tax": self.build_tax(
                form16,
                salary_slip
            ),
            "banking": self.build_banking(bank_statement),
            "investments": self.build_investments(
                investment_proofs
            ),
            "documents": self.build_document_status(
                form16,
                salary_slip,
                bank_statement,
                investment_proofs
            ),
        }

        return profile

    # =========================================================
    # PERSONAL INFORMATION
    # =========================================================

    def build_personal(
        self,
        form16,
        salary_slip,
        investment_proofs
    ):

        name = self.first_present(
            form16.get("employee_name"),
            salary_slip.get("employee_name"),
            self.first_investor_name(investment_proofs),
        )

        pan = self.first_present(
            form16.get("employee_pan"),
            form16.get("pan"),
            salary_slip.get("employee_pan"),
            salary_slip.get("pan"),
        )

        address = self.first_present(
            form16.get("employee_address"),
            salary_slip.get("employee_address"),
        )

        return {
            "name": name,
            "pan": pan,
            "address": address,
        }

    # =========================================================
    # EMPLOYMENT
    # =========================================================

    def build_employment(
        self,
        form16,
        salary_slip
    ):

        employer = self.first_present(
            form16.get("employer_name"),
            salary_slip.get("employer_name"),
        )

        employment_period = form16.get("employment_period")

        pay_period = self.first_present(
            salary_slip.get("pay_period"),
            salary_slip.get("salary_period"),
        )

        return {
            "employer_name": employer,
            "employment_period": employment_period,
            "pay_period": pay_period,
        }

    # =========================================================
    # INCOME
    # =========================================================

    def build_income(
        self,
        form16,
        salary_slip,
        bank_statement
    ):

        gross_salary = self.first_present(
            form16.get("gross_salary"),
            salary_slip.get("gross_salary"),
        )

        salary_income = form16.get("income_from_salary")
        taxable_income = form16.get("taxable_income")

        basic_salary = self.first_present(
            form16.get("basic_salary"),
            salary_slip.get("basic_salary"),
        )

        hra = self.first_present(
            form16.get("hra"),
            salary_slip.get("hra"),
        )

        special_allowance = self.first_present(
            form16.get("special_allowance"),
            salary_slip.get("special_allowance"),
        )

        other_allowances = salary_slip.get("other_allowances")
        net_salary = salary_slip.get("net_salary")
        interest_income = bank_statement.get("interest_income")
        salary_credits = bank_statement.get("salary_credits")

        return {
            "gross_salary": gross_salary,
            "salary_slip_gross_salary": salary_slip.get(
                "gross_salary"
            ),
            "salary_income": salary_income,
            "taxable_income": taxable_income,
            "basic_salary": basic_salary,
            "hra": hra,
            "special_allowance": special_allowance,
            "other_allowances": other_allowances,
            "net_salary": net_salary,
            "interest_income": interest_income,
            "salary_credits": salary_credits,
        }

    # =========================================================
    # DEDUCTIONS
    # =========================================================

    def build_deductions(self, form16):

        return {
            "section_80c": form16.get("section_80c"),
            "section_80d": form16.get("section_80d"),
            "standard_deduction": form16.get(
                "standard_deduction"
            ),
            "professional_tax": form16.get(
                "professional_tax"
            ),
        }

    # =========================================================
    # TAX INFORMATION
    # =========================================================

    
    def build_tax(self, form16, salary_slip):
        import re

        form16 = form16 or {}
        salary_slip = salary_slip or {}

        tds = self.first_present(
            form16.get("tds"),
            form16.get("tax_deducted"),
            salary_slip.get("tds"),
            salary_slip.get("tax_deducted"),
        )

        assessment_year = self.first_present(
            form16.get("assessment_year"),
            form16.get("assessment_year_text"),
            salary_slip.get("assessment_year"),
            salary_slip.get("assessment_year_text"),
        )

        financial_year = self.first_present(
            form16.get("financial_year"),
            form16.get("financial_year_text"),
            form16.get("fy"),
            salary_slip.get("financial_year"),
            salary_slip.get("financial_year_text"),
            salary_slip.get("fy"),
        )

        # Derive FY from an explicit employment period if FY is missing.
        employment_period = (
            form16.get("employment_period")
            or salary_slip.get("salary_period")
            or ""
        )

        if not financial_year:
            match = re.search(
                r"(\d{1,2}[-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]\d{4})"
                r".*?"
                r"(\d{1,2}[-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]\d{4})",
                employment_period,
                re.IGNORECASE,
            )

            if match:
                from datetime import datetime

                def parse_date(value):
                    value = re.sub(r"\s+", "-", value.strip())
                    for fmt in (
                        "%d-%b-%Y",
                        "%d-%B-%Y",
                        "%d/%b/%Y",
                        "%d/%B/%Y",
                    ):
                        try:
                            return datetime.strptime(value.title(), fmt).date()
                        except ValueError:
                            continue
                    return None

                start_date = parse_date(match.group(1))
                end_date = parse_date(match.group(2))

                if (
                    start_date
                    and end_date
                    and start_date.month == 4
                    and start_date.day == 1
                    and end_date.month == 3
                    and end_date.day == 31
                    and end_date.year == start_date.year + 1
                ):
                    financial_year = (
                        f"{start_date.year}-{str(end_date.year)[-2:]}"
                    )

        # If the employment period was unavailable, derive FY from a
        # valid AY using the standard Indian FY/AY relationship.
        if not financial_year and assessment_year:
            ay_match = re.fullmatch(
                r"\s*(20\d{2})\s*[-–/]\s*(\d{2}|20\d{2})\s*",
                str(assessment_year),
            )

            if ay_match:
                ay_start = int(ay_match.group(1))
                ay_end = int(ay_match.group(2))
                if ay_end < 100:
                    ay_end += (ay_start // 100) * 100

                if ay_end == ay_start + 1:
                    financial_year = (
                        f"{ay_start - 1}-{str(ay_start)[-2:]}"
                    )

        return {
            "tds": tds,
            "assessment_year": assessment_year,
            "financial_year": financial_year,
        }


        # =========================================================
        # BANKING INFORMATION
        # =========================================================

        def build_banking(self, bank_statement):

            return {
                "account_holder": bank_statement.get(
                    "account_holder"
                ),
                "account_number": bank_statement.get(
                    "account_number"
                ),
                "bank_name": bank_statement.get("bank_name"),
                "branch": bank_statement.get("branch"),
                "statement_period": bank_statement.get(
                    "statement_period"
                ),
                "opening_balance": bank_statement.get(
                    "opening_balance"
                ),
                "closing_balance": bank_statement.get(
                    "closing_balance"
                ),
                "total_credits": bank_statement.get(
                    "total_credits"
                ),
                "total_debits": bank_statement.get(
                    "total_debits"
                ),
                "interest_income": bank_statement.get(
                    "interest_income"
                ),
                "salary_credits": bank_statement.get(
                    "salary_credits"
                ),
            }


    
    def build_banking(self, bank_statement):
        bank_statement = bank_statement or {}

        if not isinstance(bank_statement, dict):
            bank_statement = {}

        return {
            "account_holder": self.first_present(
                bank_statement.get("account_holder"),
                bank_statement.get("account_holder_name"),
                bank_statement.get("customer_name"),
            ),
            "bank_name": self.first_present(
                bank_statement.get("bank_name"),
                bank_statement.get("institution"),
            ),
            "account_number": self.first_present(
                bank_statement.get("account_number"),
                bank_statement.get("masked_account_number"),
            ),
            "ifsc": self.first_present(
                bank_statement.get("ifsc"),
                bank_statement.get("ifsc_code"),
            ),
            "opening_balance": bank_statement.get("opening_balance"),
            "closing_balance": bank_statement.get("closing_balance"),
            "total_credits": bank_statement.get("total_credits"),
            "total_debits": bank_statement.get("total_debits"),
            "salary_credits": bank_statement.get("salary_credits") or [],
            "interest_income": bank_statement.get("interest_income"),
            "financial_year": self.first_present(
                bank_statement.get("financial_year"),
                bank_statement.get("financial_year_text"),
                bank_statement.get("fy"),
            ),
            "transactions": bank_statement.get("transactions") or [],
        }

    # =========================================================
    # INVESTMENTS
    # =========================================================

    def build_investments(self, investment_proofs):

        investments = []

        for proof in investment_proofs:

            # Support both the normalized key and the common
            # OCR fallback key. Do not infer amounts from other
            # investment fields.
            investment_amount = self.first_present(
                proof.get("investment_amount"),
                proof.get("amount"),
            )

            investment_type = self.first_present(
                proof.get("investment_type"),
                proof.get("type"),
            )

            investments.append({
                "investor_name": proof.get("investor_name"),
                "investor_pan": self.first_present(
                    proof.get("investor_pan"),
                    proof.get("pan"),
                ),
                "investment_type": investment_type,
                "institution": proof.get("institution"),
                "investment_date": self.first_present(
                    proof.get("investment_date"),
                    proof.get("issue_date"),
                ),
                "financial_year": proof.get("financial_year"),

                # Keep the existing output key: "amount".
                "amount": investment_amount,

                # Keep these separate; neither is automatically
                # treated as a deductible investment amount.
                "employer_nps_contribution": proof.get(
                    "employer_nps_contribution"
                ),
                "mutual_fund_invested": proof.get(
                    "mutual_fund_invested"
                ),

                "eligible_deduction": proof.get(
                    "eligible_deduction"
                ),
                "deduction_claim_status": proof.get(
                    "deduction_claim_status"
                ),
                "section": proof.get("section"),
                "reference_number": proof.get(
                    "reference_number"
                ),
            })

        return
        # =========================================================
    # HELPER: FIRST INVESTOR NAME
    # =========================================================

    def first_investor_name(self, investment_proofs):
        """
        Return the investor name from the first investment proof
        that contains one.
        """
        if not investment_proofs:
            return None

        for proof in investment_proofs:
            if not isinstance(proof, dict):
                continue

            name = proof.get("investor_name")

            if name:
                return name

        return None
    
    def build_document_status(
        self,
        form16=None,
        salary_slips=None,
        bank_statements=None,
        investment_proofs=None
    ):
        """
        Summarize which financial documents are available.
        Keeps document-status output separate from extracted financial data.
        """

        salary_slips = salary_slips or []
        bank_statements = bank_statements or []
        investment_proofs = investment_proofs or []

        return {
            "form16_uploaded": bool(form16),
            "salary_slips_count": len(salary_slips),
            "bank_statements_count": len(bank_statements),
            "investment_proofs_count": len(investment_proofs),
            "total_documents": (
                int(bool(form16))
                + len(salary_slips)
                + len(bank_statements)
                + len(investment_proofs)
            )
        }
