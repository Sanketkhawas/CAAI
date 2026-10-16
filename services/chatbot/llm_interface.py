
"""
LLM Interface
-------------
Handles communication with the Google Gemini API.
"""

import logging
import os

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class LLMInterface:
    MODEL_NAME = "gemini-3.5-flash-lite"

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "Gemini API key is not configured. "
                "Set the GEMINI_API_KEY environment variable."
            )

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt):
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("The AI prompt cannot be empty.")

        try:
            response = self.client.models.generate_content(
                model=self.MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=1024,
                ),
            )

            answer = response.text

            if not isinstance(answer, str) or not answer.strip():
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return answer.strip()

        except Exception:
            logger.exception("Gemini response generation failed")
            raise
