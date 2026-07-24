"""
text_cleaner.py
---------------

Cleans raw OCR text before NLP processing.

Responsibilities
----------------
- Remove extra spaces
- Remove duplicate blank lines
- Normalize currency symbols
- Remove OCR artifacts
- Join broken lines
- Standardize text formatting

Author: CAAI Team
"""

import re


class TextCleaner:
    """
    Cleans OCR output to improve entity extraction.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Remove multiple spaces
    # ---------------------------------------------------------
    def remove_extra_spaces(self, text):
        """
        Converts multiple spaces into a single space.
        """
        return re.sub(r"[ \t]+", " ", text)

    # ---------------------------------------------------------
    # Remove blank lines
    # ---------------------------------------------------------
    def remove_blank_lines(self, text):
        """
        Removes duplicate empty lines.
        """
        lines = []

        for line in text.splitlines():

            line = line.strip()

            if line:
                lines.append(line)

        return "\n".join(lines)

    # ---------------------------------------------------------
    # Normalize currency
    # ---------------------------------------------------------
    def normalize_currency(self, text):
        """
        Converts OCR variations of Rs into a standard format.
        """
        text = re.sub(r"Rs\.\s*\n\s*", "Rs. ", text)

        replacements = {
            "Rs_": "Rs.",
            "Rs ": "Rs. ",
            "RS.": "Rs.",
            "rs.": "Rs.",
            "₹ ": "₹"
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    # ---------------------------------------------------------
    # Remove unwanted OCR symbols
    # ---------------------------------------------------------
    def remove_artifacts(self, text):
        """
        Removes unwanted OCR symbols.
        """

        text = text.replace("|", "")
        text = text.replace("_", "")
        text = text.replace("`", "")
        text = text.replace("~", "")

        return text

    # ---------------------------------------------------------
    # Join broken lines
    # ---------------------------------------------------------
    def join_broken_lines(self, text):
     """
     Join only words that were accidentally split by OCR.
     Preserve real line breaks.
     """

     lines = text.splitlines()
     cleaned = []

     i = 0

     while i < len(lines):

        line = lines[i].strip()

        # Join only if current line is a single word
        # and next line is also a single word.
        if (
            i < len(lines) - 1
            and len(line.split()) == 1
            and len(lines[i + 1].split()) == 1
        ):
            cleaned.append(line + " " + lines[i + 1].strip())
            i += 2
        else:
            cleaned.append(line)
            i += 1

     return "\n".join(cleaned)

    # ---------------------------------------------------------
    # Normalize punctuation
    # ---------------------------------------------------------
    def normalize_punctuation(self, text):
        """
        Removes repeated punctuation.
        """

        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r",{2,}", ",", text)

        return text
#-----------------------------------------------------------
#    normalize dates 
#-----------------------------------------------------------
    def normalize_dates(self, text):
     """
      Normalize date formats.
     """

     text = re.sub(
        r"(\d{1,2})\s*[-/.]\s*([A-Za-z]{3,9})\s*[-/.]\s*(\d{4})",
        r"\1-\2-\3",
        text,
     )

     return text
    
#-----------------------------------------------------------
#  normalize PAN numbers
#----------------------------------------------------------=

    def normalize_pan(self, text):
     """
       Normalize PAN numbers.
     """

     pattern = r"([A-Z]{5})\s*([0-9]{4})\s*([A-Z])"

     return re.sub(pattern, r"\1\2\3", text)
    
    def normalize_ifsc(self, text):
     """
     Normalize IFSC codes.
     """

     pattern = r"([A-Z]{4})\s*([0-9]{7})"

     return re.sub(pattern, r"\1\2", text)

    def fix_common_ocr_errors(self, text):
     """
     Fix common OCR mistakes.
     """

     replacements = {
        "uls": "u/s",
        "Secion": "Section",
        "Employec": "Employee",
        "Employcr": "Employer",
        "Taxablc": "Taxable",
    }

     for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

     return text

    def normalize_amounts(self, text):
     """
    Normalize amount formatting.
     """

     text = re.sub(r"Rs\.\s*\n\s*", "Rs. ", text)

     text = re.sub(r"₹\s+", "₹", text)

     return text

    # ---------------------------------------------------------
    # Final cleaning pipeline
    # ---------------------------------------------------------
    def clean(self, text):

     text = self.remove_extra_spaces(text)

     text = self.remove_blank_lines(text)

     text = self.normalize_currency(text)

     text = self.remove_artifacts(text)

     text = self.normalize_amounts(text)

     text = self.normalize_dates(text)

     text = self.normalize_pan(text)

     text = self.normalize_ifsc(text)

     text = self.fix_common_ocr_errors(text)

     text = self.normalize_punctuation(text)

     return text.strip()