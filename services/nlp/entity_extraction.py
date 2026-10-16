
"""
entity_extraction.py
--------------------
Label-aware entity extraction for the CAAI AI Tax Advisor.

Supported document types:
    - form16
    - salary-slip
    - bank-statement
    - investment-proof

Designed to tolerate common OCR whitespace and line-break variations.
Missing information is returned as None rather than fabricated as zero.
"""

import re
from typing import Any, Dict, List, Optional

from pyparsing import line


class EntityExtractor:
    DOCUMENT_ALIASES = {
        "form16": "form16",
        "form-16": "form16",
        "form_16": "form16",
        "salary": "salary-slip",
        "salary-slip": "salary-slip",
        "salary_slip": "salary-slip",
        "payslip": "salary-slip",
        "pay-slip": "salary-slip",
        "bank": "bank-statement",
        "bank-statement": "bank-statement",
        "bank_statement": "bank-statement",
        "investment": "investment-proof",
        "investment-proof": "investment-proof",
        "investment_proof": "investment-proof",
    }

    # Indian PAN format. This checks the format, not whether a PAN is real.
    PAN_PATTERN = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    TAN_PATTERN = r"\b[A-Z]{4}[0-9]{5}[A-Z]\b"

    # Supports Indian and international-style grouped amounts.
    AMOUNT_PATTERN = re.compile(
        r"(?<![A-Za-z])"
        r"(?:₹|Rs\.?|INR)?\s*"
        r"\(?-?\s*\d[\d,]*(?:\.\d{1,2})?\s*\)?"
    )

    def extract(self, text: str, document_type: str = "form16") -> Dict[str, Any]:
        """Public entry point. Compatible with pipeline.extract(text, document_type=...)."""
        if not isinstance(text, str):
            text = ""

        doc_type = (document_type or "form16").strip().lower()
        doc_type = doc_type.replace(" ", "-")
        doc_type = self.DOCUMENT_ALIASES.get(doc_type, doc_type)

        if doc_type == "form16":
            return self.extract_form16(text)
        if doc_type == "salary-slip":
            return self.extract_salary_slip(text)
        if doc_type == "bank-statement":
            return self.extract_bank_statement(text)
        if doc_type == "investment-proof":
            return self.extract_investment_proof(text)

        raise ValueError(f"Unsupported document type: {document_type}")

    # ---------------------------------------------------------
    # Shared text helpers
    # ---------------------------------------------------------

    @staticmethod
    def _clean(text: str) -> str:
        text = text.replace("\x0c", "\n").replace("\u00a0", " ")
        text = text.replace("–", "-").replace("—", "-")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n[ \t]+", "\n", text)
        text = re.sub(r"\n{2,}", "\n", text)
        return text.strip()

    @staticmethod
    def _normalise_label(text: str) -> str:
        text = text.lower()
        text = text.replace("₹", " rs ")
        text = re.sub(r"[\t ]+", " ", text)
        return text.strip()

    @staticmethod
    def _amount_value(value: str) -> Optional[float]:
        """Parse a numeric amount, preserving whole rupee values as integers."""
        if not value:
            return None

        value = value.strip()
        negative = value.startswith("-") or (
            value.startswith("(") and value.endswith(")")
        )
        value = value.replace(",", "")
        value = re.sub(r"^(₹|Rs\.?|INR)\s*", "", value, flags=re.I)
        value = value.replace("(", "").replace(")", "").replace(" ", "")

        try:
            number = float(value)
            if negative:
                number = -abs(number)
            return int(number) if number.is_integer() else number
        except (TypeError, ValueError):
            return None

    @classmethod
    def _amounts_in_line(cls, line: str) -> List[float]:
        values = []
        for match in cls.AMOUNT_PATTERN.finditer(line):
            raw = match.group(0).strip()
            # Ignore isolated section numbers such as "(a)" or "17(1)".
            parsed = cls._amount_value(raw)
            if parsed is not None:
                values.append(parsed)
        return values

    
    @classmethod
    def _numeric_line_values(cls, line):
        """
        Return amounts only when the entire line contains numeric values.
        This prevents section numbers like 17(1) from being treated as salary.
        """
        line = line.strip()
        if not line:
            return []

        pattern = (
            r"(?:₹|Rs\.?|INR)?\s*"
            r"\(?-?\s*\d[\d,]*(?:\.\d{1,2})?\s*\)?"
        )

        matches = list(re.finditer(pattern, line, re.I))
        if not matches:
            return []

        # Ensure that nothing except whitespace or separators remains.
        remainder = line
        for match in reversed(matches):
            remainder = (
                remainder[:match.start()]
                + " "
                + remainder[match.end():]
            )

        if re.sub(r"[\s,;|]+", "", remainder):
            return []

        values = []
        for match in matches:
            value = cls._amount_value(match.group(0))
            if value is not None:
                values.append(value)

        return values

    @classmethod
    def _label_amount(
        cls,
        text,
        label_patterns,
        exclude_patterns=None,
        occurrence=0,
    ):
        """
        Extract amounts from labelled rows.

        Priority:
        1. Numeric value immediately after the label on the same line.
        2. A standalone numeric line immediately following the label.
        3. A numeric line within the next few lines if OCR split the row.
        """
        lines = cls._clean(text).splitlines()
        labels = [re.compile(p, re.I) for p in label_patterns]
        excludes = [
            re.compile(p, re.I)
            for p in (exclude_patterns or [])
        ]

        candidates = []

        for index, line in enumerate(lines):
            if not any(p.search(line) for p in labels):
                continue

            if any(p.search(line) for p in excludes):
                continue

            # Find the matched label and examine only text after it.
            label_match = None
            for pattern in labels:
                label_match = pattern.search(line)
                if label_match:
                    break

            if label_match:
                trailing_text = line[label_match.end():].strip().lstrip(" :-")

            # Accept a value after the label only if the remaining text is
            # a single monetary amount, not a calculation such as (9-11).
            amount_only_pattern = (
                r"(?:₹|Rs\.?|INR)?\s*"
                r"\(?-?\s*\d[\d,]*(?:\.\d{1,2})?\s*\)?"
            )

            if re.fullmatch(amount_only_pattern, trailing_text, re.I):
                parsed_amount = cls._amount_value(trailing_text)
                if parsed_amount is not None:
                    candidates.append(parsed_amount)
                    continue

            # OCR often places the amount on the next line.
            # Skip section headings and explanatory text, but stop at
            # another financial label to avoid taking a neighbouring row.
            for next_index in range(index + 1, min(index + 4, len(lines))):
                next_line = lines[next_index].strip()

                if not next_line:
                    continue

                # A new labelled row means this field's value was not found.
                if any(p.search(next_line) for p in labels):
                    break

                values = cls._numeric_line_values(next_line)
                if values:
                    candidates.append(values[-1])
                    break

                # Do not search through another descriptive row.
                if re.search(r"[A-Za-z]{3,}", next_line):
                    break

        if occurrence < 0 or occurrence >= len(candidates):
            return None

        return candidates[occurrence]


    @staticmethod
    def _first_match(patterns: List[str], text: str, group: int = 1) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.I | re.M)
            if match:
                value = re.sub(r"\s+", " ", match.group(group)).strip(" :-\t")
                if value:
                    return value
        return None

    @classmethod
    def _pan_values(cls, text: str) -> List[str]:
        return list(dict.fromkeys(
            match.upper()
            for match in re.findall(cls.PAN_PATTERN, text.upper())
        ))

    @classmethod
    def _tan_values(cls, text: str) -> List[str]:
        return list(dict.fromkeys(
            match.upper()
            for match in re.findall(cls.TAN_PATTERN, text.upper())
        ))

    @staticmethod
    def _date(text: str) -> Optional[str]:
        patterns = [
            r"\b\d{1,2}[-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]\d{4}\b",
            r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
            r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                return match.group(0)
        return None

    @staticmethod
    def _year_value(text: str) -> Optional[str]:
        match = re.search(r"\b(20\d{2}\s*[-/]\s*\d{2,4})\b", text)
        return re.sub(r"\s+", "", match.group(1)) if match else None

    @classmethod
    def _field_after_heading(
        cls,
        text: str,
        heading_pattern: str,
        stop_pattern: Optional[str] = None,
        max_lines: int = 8,
    ) -> Optional[str]:
        """
        Get text after a heading, useful for table-like Form 16 layouts.
        It deliberately skips the heading itself.
        """
        lines = cls._clean(text).splitlines()
        heading = re.compile(heading_pattern, re.I)
        stop = re.compile(stop_pattern, re.I) if stop_pattern else None

        for index, line in enumerate(lines):
            if not heading.search(line):
                continue

            collected = []
            for next_line in lines[index + 1:index + 1 + max_lines]:
                candidate = next_line.strip()
                if stop and stop.search(candidate):
                    break
                if candidate:
                    collected.append(candidate)

            if collected:
                return " ".join(collected)
        return None

    @classmethod
    def _extract_addresses_and_names(cls, text: str) -> Dict[str, Optional[str]]:
        """
        Extract names and addresses from common Form 16 Part B layouts.
        Uses nearby labels and company-like names instead of treating the
        label 'Name and address of the Employee' as the employer name.
        """
        lines = cls._clean(text).splitlines()
        employee_name = None
        employer_name = None
        employee_address = None
        employer_address = None

        # Case 1: OCR preserves the two-column table as one line.
        for line in lines:
            if re.search(r"\bEmployee\s+Code\b", line, re.I) and re.search(
                r"\bEmployee\s+Name\b", line, re.I
            ):
                # Look at the following line, which often contains:
                # SYN-20417 Aarav Deshmukh
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1]
                    next_line = re.sub(
                        r"\b[A-Z]{2,8}[-/]?\d{3,}\b", " ", next_line,
                        flags=re.I
                    ).strip()
                    if next_line and not re.search(
                        r"employee|designation|department", next_line, re.I
                    ):
                        employee_name = next_line
                break

        # Case 2: explicit "Employee Name: ..." OCR output.
        if not employee_name:
            employee_name = cls._first_match([
                r"\bEmployee\s+Name\s*[:\-]\s*([A-Z][A-Za-z.' -]{2,60})",
                r"\bName\s+of\s+the\s+Employee\s*[:\-]\s*([A-Z][A-Za-z.' -]{2,60})",
            ], text)

        # Remove trailing table labels from a name candidate.
        if employee_name:
            employee_name = re.split(
                r"\b(?:Designation|Department|Name and address)\b",
                employee_name, flags=re.I
            )[0].strip(" :-")

        # Employer name: prefer a company-like line, not the column heading.
        company_suffix = re.compile(
            r"\b(?:Pvt\.?\s*Ltd\.?|Private\s+Limited|Limited|Ltd\.?|LLP|"
            r"Inc\.?|Corporation|Company|Industries|Enterprises)\b",
            re.I
        )
        for line in lines:
            candidate = line.strip()
            if not candidate:
                continue
            if re.search(
                r"name and address|employee|employer|deductor|assessment year|"
                r"period with the employer|pan of the|tan of the",
                candidate, re.I
            ):
                continue
            if company_suffix.search(candidate):
                # Avoid salary rows and other text that happen to mention a company.
                if len(candidate) <= 100 and not re.search(r"\d{5,}", candidate):
                    employer_name = candidate
                    break

        # Generic labelled fallback.
        if not employer_name:
            employer_name = cls._first_match([
                r"\bName\s+of\s+the\s+Employer\s*[:\-]\s*([A-Za-z0-9&.,'() -]{3,100})",
                r"\bEmployer\s+Name\s*[:\-]\s*([A-Za-z0-9&.,'() -]{3,100})",
            ], text)

        # Address candidates are taken from labelled or location-like lines.
        for index, line in enumerate(lines):
            if re.search(r"\bName and address of the Employee\b", line, re.I):
                nearby = " ".join(lines[index + 1:index + 5])
                # The employee name is already extracted separately.
                if employee_name:
                    nearby = nearby.replace(employee_name, " ")
                address_match = re.search(
                    r"((?:Flat|House|H\.?No\.?|Plot|Room|Block|Street|Road|"
                    r"Lane|Building|Apartment|Apt\.?)[^\\n]{5,160})",
                    nearby, re.I
                )
                if address_match:
                    employee_address = address_match.group(1).strip()
                    break

        for index, line in enumerate(lines):
            if re.search(r"\bName and address of employer\b", line, re.I):
                nearby = " ".join(lines[index + 1:index + 5])
                nearby = nearby.replace(employer_name or "", " ")
                address_match = re.search(
                    r"((?:Plot|Office|Unit|Building|Survey|Road|Street|"
                    r"Industrial|MIDC)[^\\n]{5,160})",
                    nearby, re.I
                )
                if address_match:
                    employer_address = address_match.group(1).strip()
                    break

        # Explicitly labelled address fallbacks.
        if not employee_address:
            employee_address = cls._first_match([
                r"\bEmployee\s+Address\s*[:\-]\s*(.{8,180})",
                r"\bAddress\s+of\s+the\s+Employee\s*[:\-]\s*(.{8,180})",
            ], text)

        if not employer_address:
            employer_address = cls._first_match([
                r"\bEmployer\s+Address\s*[:\-]\s*(.{8,180})",
                r"\bAddress\s+of\s+the\s+Employer\s*[:\-]\s*(.{8,180})",
            ], text)

        return {
            "employee_name": employee_name,
            "employee_address": employee_address,
            "employer_name": employer_name,
            "employer_address": employer_address,
        }

    # ---------------------------------------------------------
    # Form 16 Part B
    # ---------------------------------------------------------

    def extract_form16(self, text: str) -> Dict[str, Any]:
        text = self._clean(text)
        lines = text.splitlines()
        details = self._extract_addresses_and_names(text)
        
        lines = text.splitlines()

        if not details.get("employee_name"):
            for index, line in enumerate(lines):
                if re.search(r"\bEmployee\s+Name\b", line, re.I):
                    for candidate in lines[index + 1:index + 6]:
                        candidate = candidate.strip()

                        if not candidate:
                            continue

                        # Skip employee codes and table headings.
                        if re.fullmatch(
                            r"[A-Z]{2,8}[-/]?\d{3,}",
                            candidate,
                            re.I
                        ):
                            continue

                        if re.search(
                            r"employee|designation|department|address|PAN|TAN",
                            candidate,
                            re.I
                        ):
                            continue

                        if re.fullmatch(
                            r"[A-Za-z][A-Za-z.'-]*(?:\s+[A-Za-z][A-Za-z.'-]*){1,4}",
                            candidate
                        ):
                            details["employee_name"] = candidate
                            break

                    break

       
                # Extract PAN and TAN values without allowing a label regex
        # to cross line breaks and accidentally capture another person's PAN.
        pans = self._pan_values(text)
        tans = self._tan_values(text)

        # Same-line labelled values are preferred.
        employee_pan = self._first_match([
            r"\bPAN\s+of\s+the\s+employee[ \t]*[:\-]?[ \t]*("
            + self.PAN_PATTERN + r")",
            r"\bEmployee\s+PAN[ \t]*[:\-][ \t]*("
            + self.PAN_PATTERN + r")",
        ], text)

        employer_pan = self._first_match([
            r"\bPAN\s+of\s+the\s+Deductor[ \t]*[:\-]?[ \t]*("
            + self.PAN_PATTERN + r")",
            r"\bEmployer\s+PAN[ \t]*[:\-][ \t]*("
            + self.PAN_PATTERN + r")",
            r"\bDeductor\s+PAN[ \t]*[:\-]?[ \t]*("
            + self.PAN_PATTERN + r")",
        ], text)

        employer_tan = self._first_match([
            r"\bTAN\s+of\s+the\s+Deductor[ \t]*[:\-]?[ \t]*("
            + self.TAN_PATTERN + r")",
            r"\bEmployer\s+TAN[ \t]*[:\-][ \t]*("
            + self.TAN_PATTERN + r")",
            r"\bDeductor\s+TAN[ \t]*[:\-]?[ \t]*("
            + self.TAN_PATTERN + r")",
        ], text)

        # Fallback for OCR tables where all labels appear before their values.
        # Use the ordering only when the expected labels are present.
        has_employee_pan_label = bool(re.search(
            r"\bPAN\s+of\s+the\s+employee\b|\bEmployee\s+PAN\b",
            text, re.I
        ))
        has_employer_pan_label = bool(re.search(
            r"\bPAN\s+of\s+the\s+Deductor\b|\bEmployer\s+PAN\b|"
            r"\bDeductor\s+PAN\b",
            text, re.I
        ))

        if has_employer_pan_label and has_employee_pan_label and len(pans) >= 2:
            if not employer_pan:
                employer_pan = pans[0]
            if not employee_pan:
                employee_pan = pans[-1]

        if not employer_tan and tans and re.search(
            r"\bTAN\s+of\s+the\s+Deductor\b|\bEmployer\s+TAN\b|"
            r"\bDeductor\s+TAN\b",
            text, re.I
        ):
            employer_tan = tans[0]


        assessment_year = self._first_match([
            r"\bAssessment\s+Year\s*[:\-]?\s*(20\d{2}\s*[-/]\s*\d{2,4})",
        ], text) or self._year_value(text)

        financial_year = self._first_match([
            r"\bFinancial\s+Year\s*[:\-]?\s*(20\d{2}\s*[-/]\s*\d{2,4})",
            r"\bF\.?\s*Y\.?\s*[:\-]?\s*(20\d{2}\s*[-/]\s*\d{2,4})",
        ], text)

        employment_period = self._first_match([
            r"\bPeriod\s+with\s+the\s+Employer\s*[:\-]?\s*"
            r"((?:From\s+)?\d{1,2}[-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*[-/ ]\d{4}\s*(?:to|-)\s*\d{1,2}[-/ ]"
            r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]\d{4})",
        ], text)

        if not employment_period:
            employment_period = self._first_match([
                r"\b(From\s+\d{1,2}[-/ ]\w{3,9}[-/ ]\d{4}\s+To\s+"
                r"\d{1,2}[-/ ]\w{3,9}[-/ ]\d{4})",
            ], text)

        # Financial rows are matched by their numbered labels. Specific
        # patterns prevent the standard deduction from becoming gross salary.
        salary_17_1 = self._label_amount(text, [
            r"Salary\s+as\s+per\s+provisions?.{0,35}section\s*17\s*\(\s*1\s*\)",
            r"\bSalary\s+under\s+section\s*17\s*\(\s*1\s*\)",
        ])

        perquisites = self._label_amount(text, [
            r"Value\s+of\s+perquisites.{0,35}section\s*17\s*\(\s*2\s*\)",
        ])

                # Handle OCR that splits the perquisites label across several lines.
        if perquisites is None:
            for index, line in enumerate(lines):
                if not re.search(r"\bValue\s+of\s+perquisites\b", line, re.I):
                    continue

                for candidate in lines[index + 1:index + 5]:
                    if re.search(
                        r"\bProfits?\s+in\s+lieu\s+of\s+salary\b|"
                        r"^\s*\(\s*[cd]\s*\)",
                        candidate,
                        re.I,
                    ):
                        break

                    values = self._numeric_line_values(candidate)
                    if values:
                        perquisites = values[-1]
                        break

                break

        profits_in_lieu = self._label_amount(text, [
            r"Profits?\s+in\s+lieu\s+of\s+salary.{0,35}section\s*17\s*\(\s*3\s*\)",
        ])

        gross_salary = self._label_amount(text, [
            r"\(\s*d\s*\)\s*Total\b",
            r"\bGross\s+Salary\s+Total\b",
            r"\bTotal\s+Gross\s+Salary\b",
        ])

        if gross_salary is None:
            gross_salary = self._label_amount(
                text,
                [r"\bGross\s+Salary\b"],
                exclude_patterns=[
                    r"salary\s+as\s+per\s+provisions",
                    r"standard\s+deduction",
                    r"basic\s+salary",
                ],
            )

        other_employer_salary = self._label_amount(text, [
            r"Reported\s+total\s+amount\s+of\s+salary\s+received\s+from\s+other",
            r"Salary\s+received\s+from\s+other\s+employer",
        ])

        travel_exemption = self._label_amount(text, [
            r"Travel\s+concession\s+or\s+assistance\s+under\s+section\s*10\s*\(\s*5\s*\)",
        ])
        gratuity_exemption = self._label_amount(text, [
            r"Death-cum-retirement\s+gratuity\s+under\s+section\s*10\s*\(\s*10\s*\)",
        ])
        pension_exemption = self._label_amount(text, [
            r"Commuted\s+value\s+of\s+pension\s+under\s+section\s*10\s*\(\s*10A\s*\)",
        ])
        leave_encashment_exemption = self._label_amount(text, [
            r"Cash\s+equivalent\s+of\s+leave\s+salary\s+encashment",
        ])
        hra_exemption = self._label_amount(text, [
            r"House\s+rent\s+allowance\s+under\s+section\s*10\s*\(\s*13A\s*\)",
            r"\bHRA\s+exemption\b",
        ])
        other_exemption = self._label_amount(text, [
            r"Total\s+amount\s+of\s+any\s+other\s+exemption\s+under\s+section\s*10",
        ])
        total_exemptions = self._label_amount(text, [
            r"Total\s+amount\s+of\s+exemption\s+claimed\s+under\s+section\s*10",
            r"\bTotal\s+exemptions?\b",
        ])

        income_from_salary = self._label_amount(text, [
            r"Income\s+chargeable\s+under\s+the\s+head\s*[\"']?Salaries",
            r"\bIncome\s+from\s+Salary\b",
        ])

        total_salary_current_employer = self._label_amount(text, [
            r"Total\s+amount\s+of\s+salary\s+received\s+from\s+current\s+employer",
        ])

        standard_deduction = self._label_amount(text, [
            r"Standard\s+deduction\s+under\s+section\s*16",
        ])
        entertainment_allowance = self._label_amount(text, [
            r"Entertainment\s+allowance\s+under\s+section\s*16",
        ])
        professional_tax = self._label_amount(text, [
            r"Tax\s+on\s+employment\s+under\s+section\s*16",
            r"\bProfessional\s+tax\b",
        ])
        total_section16_deductions = self._label_amount(text, [
            r"Total\s+amount\s+of\s+deductions\s+under\s+section\s*16",
        ])

        house_property_income = self._label_amount(text, [
            r"Income\s*\(or\s*admissible\s*loss\)\s*from\s*house\s*property",
        ])
        other_sources_income = self._label_amount(text, [
            r"Income\s+under\s+the\s+head\s+Other\s+Sources",
        ])
        total_other_income = self._label_amount(text, [
            r"Total\s+amount\s+of\s+other\s+income\s+reported\s+by\s+the\s+employee",
        ])
        gross_total_income = self._label_amount(text, [
            r"\bGross\s+total\s+income\b",
        ])

        section_80c = self._label_amount(text, [
            r"Total\s+deduction\s+under\s+section\s*80C\s*,?\s*80CCC",
            r"Deduction\s+in\s+respect\s+of\s+life\s+insurance\s+premia",
            r"\bSection\s*80C\b",
        ])
        section_80ccc = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+contribution\s+to\s+certain\s+pension\s+funds",
        ])
        section_80ccd1 = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+contribution\s+by\s+taxpayer\s+to\s+pension\s+scheme",
        ])
        section_80ccd1b = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+amount\s+paid/deposited\s+to\s+notified\s+pension",
        ])
        section_80ccd2 = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+contribution\s+by\s+Employer\s+to\s+pension",
        ])
        section_80d = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+health\s+insurance\s+premia\s+under\s+section\s*80D",
        ])
        section_80e = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+interest\s+on\s+loan\s+taken\s+for\s+higher\s+education",
        ])
        section_80g = self._label_amount(text, [
            r"Total\s+deduction\s+in\s+respect\s+of\s+donations",
        ])
        section_80tta = self._label_amount(text, [
            r"Deduction\s+in\s+respect\s+of\s+interest\s+on\s+deposits\s+in\s+savings\s+account",
        ])
        other_chapter_via = self._label_amount(text, [
            r"Total\s+of\s+amount\s+deductible\s+under\s+any\s+other\s+provision",
        ])
        total_chapter_via = self._label_amount(text, [
            r"Aggregate\s+of\s+deductible\s+amount\s+under\s+Chapter\s*VI-A",
            r"Total\s+deductions\s+under\s+Chapter\s*VI-A",
        ])

        taxable_income = self._label_amount(text, [
            r"Total\s+taxable\s+income",
        ])
        total_tax = self._label_amount(text, [
            r"Tax\s+on\s+total\s+income",
        ])
        rebate_87a = self._label_amount(text, [
            r"Rebate\s+under\s+section\s*87A",
        ])
        surcharge = self._label_amount(text, [
            r"Surcharge",
        ], exclude_patterns=[
            r"verification",
        ])
        cess = self._label_amount(text, [
            r"Health\s+and\s+education\s+cess",
        ])
        tax_payable = self._label_amount(text, [
            r"\bTax\s+payable\b",
        ], exclude_patterns=[
            r"net\s+tax\s+payable",
        ])
        relief_89 = self._label_amount(text, [
            r"Relief\s+under\s+section\s*89",
        ])
        net_tax_payable = self._label_amount(text, [
            r"\bNet\s+tax\s+payable\b",
        ])

        # TDS is not equivalent to "Tax on total income" or "Net tax payable".
        # Only populate it if a TDS-specific label exists in the OCR text.
        tds = self._label_amount(text, [
            r"\bTax\s+deducted\s+at\s+source\b",
            r"\bTDS\s+(?:deducted|amount|paid)\b",
            r"\bTotal\s+TDS\b",
        ])

        place = self._first_match([
            r"\bPlace\s*[:\-]\s*([A-Za-z][A-Za-z .'-]{1,60})",
        ], text)
        issue_date = self._first_match([
            r"\bDate\s*[:\-]\s*(\d{1,2}[-/ ](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/ ]\d{4})",
            r"\bDate\s*[:\-]\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})",
        ], text)

        # Keep legacy field names expected by the rest of the CAAI project.
        result = {
            "document_type": "form16",

            "employee_pan": employee_pan,
            "employee_name": details["employee_name"],
            "employee_address": details["employee_address"],
            "employer_name": details["employer_name"],
            "employer_address": details["employer_address"],
            "employer_pan": employer_pan,
            "employer_tan": employer_tan,

            "assessment_year": assessment_year,
            "financial_year": financial_year,
            "employment_period": employment_period,

            # Legacy field: basic_salary is used for Section 17(1) salary
            # when the document is a Form 16, not necessarily payroll basic pay.
            "basic_salary": salary_17_1,
            "gross_salary": gross_salary,
            "perquisites": perquisites,
            "profits_in_lieu_of_salary": profits_in_lieu,
            "other_employer_salary": other_employer_salary,

            "travel_exemption": travel_exemption,
            "gratuity_exemption": gratuity_exemption,
            "pension_exemption": pension_exemption,
            "leave_encashment_exemption": leave_encashment_exemption,
            "hra": hra_exemption,
            "other_exemption": other_exemption,
            "exemptions": total_exemptions,

            "total_salary_current_employer": total_salary_current_employer,
            "standard_deduction": standard_deduction,
            "entertainment_allowance": entertainment_allowance,
            "professional_tax": professional_tax,
            "total_section16_deductions": total_section16_deductions,
            "income_from_salary": income_from_salary,

            "house_property_income": house_property_income,
            "other_sources_income": other_sources_income,
            "total_other_income": total_other_income,
            "gross_total_income": gross_total_income,

            "section_80c": section_80c,
            "section_80ccc": section_80ccc,
            "section_80ccd1": section_80ccd1,
            "section_80ccd1b": section_80ccd1b,
            "section_80ccd2": section_80ccd2,
            "section_80d": section_80d,
            "section_80e": section_80e,
            "section_80g": section_80g,
            "section_80tta": section_80tta,
            "other_chapter_via": other_chapter_via,
            "total_deductions": total_chapter_via,

            "taxable_income": taxable_income,
            "total_tax": total_tax,
            "rebate_87a": rebate_87a,
            "surcharge": surcharge,
            "cess": cess,
            "tax_payable": tax_payable,
            "relief_89": relief_89,
            "net_tax_payable": net_tax_payable,
            "tds": tds,

            "issue_date": issue_date,
            "place": place,
        }

        # Retain compatibility for existing tax-engine field names.
        # Do not fabricate salary components that the document doesn't show.
        result["special_allowance"] = None

        return result

    # ---------------------------------------------------------
    # Salary slip
    # ---------------------------------------------------------


    def extract_salary_slip(self, text: str) -> Dict[str, Any]:
        text = self._clean(text)
        lines = text.splitlines()

        def extract_text(patterns):
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    return match.group(1).strip(" \t:-|")
            return None

        def extract_amount(label_patterns, split_tds=False):
            compiled = [re.compile(p, re.IGNORECASE) for p in label_patterns]

            for index, line in enumerate(lines):
                label_match = None

                for pattern in compiled:
                    label_match = pattern.search(line)
                    if label_match:
                        break

                if not label_match:
                    continue

                # First check whether the amount is on the same line as the label.
                trailing = line[label_match.end():].strip().lstrip(" :-|")
                values = self._numeric_line_values(trailing)

                if values:
                    return values[0]

                # Otherwise, look at the following lines for a standalone amount.
                candidates = []
                for next_index in range(index + 1, min(index + 4, len(lines))):
                    next_line = lines[next_index].strip()

                    if not next_line:
                        continue

                    # Stop at another labelled row, except for numeric-only lines.
                    numeric_values = self._numeric_line_values(next_line)

                    if numeric_values:
                        candidates.append((next_line, numeric_values[0]))
                        continue

                    # Ignore headings, but don't scan through another salary field.
                    if re.search(
                        r"\b(Basic|HRA|House Rent Allowance|Special Allowance|"
                        r"Gross Earnings|Gross Salary|Total Deductions|"
                        r"Net Pay|Net Salary|Provident Fund|Professional Tax|"
                        r"Income Tax|TDS|Employer NPS)\b",
                        next_line,
                        re.IGNORECASE,
                    ):
                        break

                    # Don't search past an unrelated descriptive line.
                    break

                if not candidates:
                    continue

                # OCR split 11,267.00 into two lines: "1" and "1,267.00".

                # OCR split 11,267.00 into two lines: "1" and "1,267.00".
                if split_tds and len(candidates) >= 2:
                    first_text = candidates[0][0].strip()
                    second_text = candidates[1][0].strip()

                    # Handle OCR splitting the leading digit from the amount.
                    if (
                        re.fullmatch(r"\d", first_text)
                        and re.fullmatch(r"\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?", second_text)
                    ):
                        combined = first_text + second_text.replace(",", "")
                        parsed = self._amount_value(combined)

                        if parsed is not None:
                            return parsed

                return candidates[0][1]

            return None

        return {
            "document_type": "salary-slip",

            "employee_name": extract_text([
                r"\bEmployee\s*:\s*(.+?)(?=\s+Code\s*:|$)",
                r"\bEmployee\s+Name\s*[:\-]\s*([^\n]+)",
                r"\bName\s*[:\-]\s*([^\n]+)",
            ]),

            "employee_id": extract_text([
                r"\bEmployee\s+(?:ID|Code)\s*[:\-]\s*([A-Za-z0-9/-]+)",
                r"\bCode\s*:\s*([A-Za-z0-9/-]+)",
            ]),

            "pan": extract_text([
                r"\bPAN\s*[:\-]?\s*(" + self.PAN_PATTERN + r")",
            ]),

            "employer_name": extract_text([
                r"\bEmployer\s*:\s*([^\n]+)",
                r"\bEmployer\s+Name\s*[:\-]\s*([^\n]+)",
                r"\bCompany\s+Name\s*[:\-]\s*([^\n]+)",
            ]),

            "salary_period": extract_text([
                r"\b(?:Salary\s+Month|Pay\s+Period|Period)\s*[:\-]\s*([^\n]+)",
                r"\bPAYSLIP\s*[\r\n]+\s*([A-Za-z]{3}-\d{4})",
            ]),

            "basic_salary": extract_amount([
                r"\bBasic\s+Salary\b",
                r"\bBasic\s+Pay\b",
                r"\bBasic\b",
            ]),

            "hra": extract_amount([
                r"\bHouse\s+Rent\s+Allowance\b",
                r"\bHRA\b",
            ]),

            "special_allowance": extract_amount([
                r"\bSpecial\s+Allowance\b",
            ]),

            "other_earnings": extract_amount([
                r"\bOther\s+Earnings\b",
                r"\bOther\s+Allowances\b",
            ]),

            "gross_salary": extract_amount([
                r"\bGross\s+(?:Salary|Earnings|Pay)\b",
            ]),

            "provident_fund": extract_amount([
                r"\b(?:Employee\s+)?Provident\s+Fund\b",
                r"\bEPF\b",
            ]),

            "professional_tax": extract_amount([
                r"\bProfessional\s+Tax\b",
            ]),

            "tds": extract_amount([
                r"\bTDS\b",
                r"\bIncome\s+Tax\s+Deducted\b",
                r"\bIncome\s+Tax\s*\(TDS\b",
            ], split_tds=True),

            "total_deductions": extract_amount([
                r"\bTotal\s+Deductions\b",
            ]),

            "net_salary": extract_amount([
                r"\bNet\s+(?:Salary|Pay)\b",
            ]),

            "employer_nps_contribution": extract_amount([
                r"\bEmployer\s+NPS\s+contribution\b",
                r"\bNPS\s+contribution\b",
            ]),
        }


    
    
    def extract_bank_statement(self, text: str) -> Dict[str, Any]:
        """Extract bank statement details while filtering repeated page headers."""

        original_text = self._clean(text)
        lines = original_text.splitlines()

        # Extract statement-level fields from the original OCR text.
        # This does not modify the text stored in the database.
        header_text = "\n".join(lines[:20])

        period_match = re.search(
            r"\b(?:ACCOUNT\s+STATEMENT\s+)?"
            r"(\d{1,2}[-/ ][A-Za-z]{3}[-/ ]\d{4})"
            r"\s+to\s+"
            r"(\d{1,2}[-/ ][A-Za-z]{3}[-/ ]\d{4})\b",
            header_text,
            re.IGNORECASE,
        )

        statement_period = (
            f"{period_match.group(1)} to {period_match.group(2)}"
            if period_match else self._first_match([
                r"\bStatement\s+Period\s*[:\-]\s*(.+)",
                r"\bPeriod\s*[:\-]\s*(.+)",
            ], original_text)
        )

        # Bank name is captured separately from IFSC and branch details.
        bank_name = self._first_match([
            r"(?m)^\s*(.+?)\s*\|\s*IFSC\b",
            r"(?m)^\s*(.+?)\s+IFSC\s+[A-Z0-9O]{11}\b",
            r"\bBank\s+Name\s*[:\-]\s*([^\n|]+)",
        ], header_text)

        if bank_name:
            bank_name = bank_name.strip(" |:-")

        # Extract IFSC from the header. Correct common OCR O/0 confusion
        # in the extracted field only; original_text remains untouched.
        ifsc = None
        ifsc_match = re.search(
            r"\bIFSC\s*[:\-]?\s*([A-Z0-9]{11})\b",
            original_text,
            re.IGNORECASE,
        )

        if ifsc_match:
            candidate = ifsc_match.group(1).upper()

            # IFSC structure: 4 letters, one zero, then 6 alphanumeric chars.
            candidate = candidate[:4] + "0" + candidate[5:].replace("O", "0")

            if re.fullmatch(r"[A-Z]{4}0[A-Z0-9]{6}", candidate):
                ifsc = candidate

        # Header may contain: Aarav Deshmukh | A/c 000000123456 | Opening balance...
        account_holder = self._first_match([
            # Name appears on the line immediately before the account number.
            r"(?m)^\s*([A-Za-z][A-Za-z .'-]{2,60})\s*\n\s*A[lI]?c\b",
            r"(?m)^\s*([A-Za-z][A-Za-z .'-]{2,60})\s*\n\s*A\s*/\s*C\b",

            # Explicit labels used by other bank statement formats.
            r"\bAccount\s+Holder(?:\s+Name)?\s*[:\-]\s*([^\n|]+)",
            r"\bCustomer\s+Name\s*[:\-]\s*([^\n|]+)",
        ], text)

        account_number = self._first_match([
            r"\bA[lI]?c\b\s*[:#\-]?\s*([Xx*0-9OoIl -]{4,30})",
            r"\bA\s*/\s*C(?:\s*(?:No\.?|Number))?\s*[:#\-]?\s*([Xx*0-9OoIl -]{4,30})",
            r"\bAccount\s+(?:No\.?|Number)\s*[:#\-]?\s*([Xx*0-9OoIl -]{4,30})",
        ], text)

        if account_holder:
            account_holder = account_holder.strip(" \t|:-")

        if account_number:
            account_number = account_number.strip(" \t-:")
            account_number = re.split(
                r"\s+(?:Opening\s+Balance|IFSC|Branch)\b",
                account_number,
                maxsplit=1,
                flags=re.IGNORECASE,
            )[0].strip()
        opening_balance = self._label_amount(
            original_text, [r"\bOpening\s+Balance\b"]
        )
        closing_balance = self._label_amount(
            original_text,
            [r"\bClosing\s+Balance\b", r"\bEnding\s+Balance\b"],
        )
        total_deposits_label = self._label_amount(
            original_text, [r"\bTotal\s+Deposits\b", r"\bTotal\s+Credits\b"]
        )
        total_withdrawals_label = self._label_amount(
            original_text, [r"\bTotal\s+Withdrawals\b", r"\bTotal\s+Debits\b"]
        )

        # Recognize transaction dates.
        date_pattern = re.compile(
            r"^\s*(\d{1,2}[-/ ](?:[A-Za-z]{3}|\d{1,2})[-/ ]\d{2,4})\s*$"
            r"|^\s*(\d{4}-\d{2}-\d{2})\s*$"
        )

        # Remove recurring sample/document headers from transaction text.
        # These patterns are applied only to local parsing copies.
        header_noise = re.compile(
            r"SAMPLE\s+SYNTHETIC\s+TEST\s+DATA\s+NOT\s+A\s+VALID\s+DOCUMENT.*$",
            re.IGNORECASE,
        )

        cleaned_lines = []
        for line in lines:
            line = re.sub(
                r"\bSAMPLE\s+SYNTHETIC\s+TEST\s+DATA\s+NOT\s+A\s+VALID\s+DOCUMENT\b",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()

            if not line:
             continue

            # Skip repeated page headings and column headings.
            upper = line.upper()
            if "ACCOUNT STATEMENT" in upper:
                continue
            if "TEST BRANCH" in upper and "IFSC" in upper:
                continue
            if upper in {
                "DATE",
                "NARRATION",
                "DEBIT",
                "CREDIT",
                "BALANCE",
            }:
                continue
            if re.fullmatch(
                r"(DATE\s+)?NARRATION\s+(DEBIT\s+)?CREDIT\s+BALANCE",
                upper,
            ):
                continue

            # Remove repeated account/header fragments if OCR joined them
            # to another line. Do not alter original_text or stored OCR.
            line = re.sub(
                r"\bSample Bank of Testland\b.*$",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            if not line:
                continue

            # Opening balance belongs to the statement header, not a transaction.
            if re.search(r"\bOpening\s+Balance\b", line, re.IGNORECASE):
                continue

            cleaned_lines.append(line)

        # Split the cleaned text into date-led transaction groups.
        groups = []
        current = None

        for line in cleaned_lines:
            match = date_pattern.match(line)
            if match:
                if current:
                    groups.append(current)
                current = {
                    "date": (match.group(1) or match.group(2)).strip(),
                    "lines": [],
                }
            elif current:
                current["lines"].append(line)

        if current:
            groups.append(current)

        transactions = []
        previous_balance = opening_balance

        credit_terms = re.compile(
            r"\b(SALARY|INTEREST CREDIT|CREDIT|DEPOSIT|REFUND|CASHBACK|"
            r"DIVIDEND|NEFT IN|IMPS IN|RTGS IN)\b",
            re.IGNORECASE,
        )

        debit_terms = re.compile(
            r"\b(DEBIT|WITHDRAWAL|ATM|RENT|SIP|PURCHASE|SHOPPING|"
            r"GROCERY|UTILITIES|FUEL|FOOD DELIVERY|PAYMENT|TRANSFER OUT)\b",
            re.IGNORECASE,
        )

        amount_only_pattern = re.compile(
            r"^[\s₹+\-()]*"
            r"(?:INR\s*)?"
            r"\d[\d,]*(?:\.\d{1,2})?"
            r"[\s)]*$",
            re.IGNORECASE,
        )

        for group in groups:
            narration_parts = []
            numeric_values = []

            for line in group["lines"]:
                if amount_only_pattern.fullmatch(line):
                    matches = re.findall(
                        r"(?<![A-Za-z])\-?\d[\d,]*(?:\.\d{1,2})?",
                        line,
                    )
                    for value in matches:
                        parsed = self._amount_value(value)
                        if parsed is not None:
                            numeric_values.append(parsed)
                else:
                    # Ignore leftover table headings and repeated header fragments.
                    if re.search(
                        r"\b(IFSC|BRANCH|ACCOUNT HOLDER|ACCOUNT NUMBER)\b",
                        line,
                        re.IGNORECASE,
                    ):
                        continue
                    narration_parts.append(line)

            narration = " ".join(narration_parts).strip()
            if not narration or not numeric_values:
                continue

            debit = None
            credit = None
            balance = None

            if len(numeric_values) >= 2:
                # Typical OCR layout: transaction amount followed by running balance.
                stated_amount = abs(numeric_values[-2])
                balance = numeric_values[-1]

                if previous_balance is not None:
                    change = balance - previous_balance

                    # Running balance determines direction when it is available.
                    if change > 0:
                        credit = stated_amount
                    elif change < 0:
                        debit = stated_amount
                    else:
                        # No balance change: use narration only as a fallback.
                        if credit_terms.search(narration):
                            credit = stated_amount
                        elif debit_terms.search(narration):
                            debit = stated_amount
                else:
                    if credit_terms.search(narration):
                        credit = stated_amount
                    elif debit_terms.search(narration):
                        debit = stated_amount

            else:
                # A repeated page header may have removed the running balance.
                # Use the single remaining amount only when narration gives a
                # recognizable direction; otherwise do not invent a transaction.
                stated_amount = abs(numeric_values[0])

                if credit_terms.search(narration):
                    credit = stated_amount
                elif debit_terms.search(narration):
                    debit = stated_amount
                else:
                    continue

                if previous_balance is not None:
                    if credit is not None:
                        balance = previous_balance + credit
                    else:
                        balance = previous_balance - debit

            transactions.append({
                "date": group["date"],
                "narration": narration,
                "debit": debit,
                "credit": credit,
                "balance": balance,
            })

            if balance is not None:
                previous_balance = balance

        # Derive totals from parsed transactions, not from contaminated header
        # numbers or differences against an incorrectly parsed opening balance.
        calculated_deposits = sum(
            tx["credit"] or 0 for tx in transactions
        )
        calculated_withdrawals = sum(
            tx["debit"] or 0 for tx in transactions
        )

        if transactions and transactions[-1]["balance"] is not None:
            closing_balance = transactions[-1]["balance"]

        return {
            "document_type": "bank-statement",
            "account_holder": account_holder,
            "account_number": account_number,
            "bank_name": bank_name,
            "ifsc": ifsc,
            "statement_period": statement_period,
            "opening_balance": opening_balance,
            "closing_balance": closing_balance,
            "total_deposits": (
                calculated_deposits
                if transactions else total_deposits_label
            ),
            "total_withdrawals": (
                calculated_withdrawals
                if transactions else total_withdrawals_label
            ),
            "transactions": transactions,
        }



    
    def extract_investment_proof(self, text: str) -> Dict[str, Any]:
        text = self._clean(text)

        def extract_first(patterns):
            return self._first_match(patterns, text)

        def extract_amount(patterns):
            return self._label_amount(text, patterns)

        # Identify the statement types present in the OCR text.
        has_nps = bool(re.search(
            r"\bNPS\s+TIER\s*[-I1]?\s*STATEMENT\b|"
            r"\bTotal\s+employer\s+contribution\b",
            text,
            re.IGNORECASE,
        ))

        has_mutual_fund = bool(re.search(
            r"\bMUTUAL\s+FUND\s+SIP\s+STATEMENT\b|"
            r"\bTotal\s+invested\b",
            text,
            re.IGNORECASE,
        ))

        # Extract the investor/subscriber name.
        investor_name = extract_first([
            r"\bInvestor\s+Name\s*[:\-]\s*([^\n]+)",
            r"\bName\s+of\s+Investor\s*[:\-]\s*([^\n]+)",
            r"\bEmployee\s+Name\s*[:\-]\s*([^\n]+)",
            r"\bSubscriber\s*[:\-]\s*([^\n]+)",
            r"\bInvestor\s*[:\-]\s*([^\n]+)",
        ])

        # Detect investment types.
        investment_types = []

        if has_nps:
            investment_types.append("NPS Tier-I")

        if has_mutual_fund:
            investment_types.append("Mutual Fund SIP")

        if not investment_types:
            detected_type = extract_first([
                r"\bInvestment\s+Type\s*[:\-]\s*([^\n]+)",
                r"\bPolicy\s+Type\s*[:\-]\s*([^\n]+)",
                r"\bInstrument\s*[:\-]\s*([^\n]+)",
            ])

            if detected_type:
                investment_types.append(detected_type)

        # Extract individual statement totals separately.
        employer_nps_contribution = (
            extract_amount([
                r"\bTotal\s+employer\s+contribution"
                r"\s*\(?\s*8[O0]CCD\s*\(\s*2\s*\)\s*\)?",
                r"\bTotal\s+employer\s+contribution\b",
            ])
            if has_nps else None
        )

        mutual_fund_invested = (
            extract_amount([
                r"\bTotal\s+invested\b",
            ])
            if has_mutual_fund else None
        )

        # Do not merge totals from different investment types.
        if has_nps and not has_mutual_fund:
            investment_amount = employer_nps_contribution
        elif has_mutual_fund and not has_nps:
            investment_amount = mutual_fund_invested
        else:
            investment_amount = None

        # An investment amount alone does not prove tax eligibility.
        eligible_deduction = extract_amount([
            r"\bEligible\s+Deduction\b",
            r"\bDeduction\s+Eligible\b",
            r"\bDeduction\s+under\s+section\s*80C\b",
            r"\bDeduction\s+under\s+section\s*80D\b",
        ])

        # Check for an explicit statement that the investment
        # has not been claimed under a deduction.
        not_claimed = bool(re.search(
            r"\bnot\s+claimed\s+under\s+any\s+deduction\b",
            text,
            re.IGNORECASE,
        ))

        return {
            "document_type": "investment-proof",
            "investor_name": investor_name,
            "investor_pan": extract_first([
                r"\bPAN\s*[:\-]?\s*(" + self.PAN_PATTERN + r")",
            ]),
            "investment_type": (
                " + ".join(investment_types)
                if investment_types else None
            ),
            "investment_amount": investment_amount,
            "eligible_deduction": (
                0 if not_claimed else eligible_deduction
            ),
            "financial_year": extract_first([
                r"\bFinancial\s+Year\s*[:\-]?\s*"
                r"(20\d{2}\s*[-/]\s*\d{2,4})",
                r"\bFY\s+(20\d{2}\s*[-/]\s*\d{2,4})",
            ]) or self._year_value(text),
            "issue_date": self._date(text),

            # Additional fields for the tax engine.
            "employer_nps_contribution": employer_nps_contribution,
            "mutual_fund_invested": mutual_fund_invested,
            "deduction_claim_status": (
                "not_claimed" if not_claimed else "not_confirmed"
            ),
        }
