
"""
Response Generator
------------------
Generates AI responses and propagates failures
to the Flask route for proper error handling.
"""

import logging

from services.chatbot.llm_interface import LLMInterface

logger = logging.getLogger(__name__)


class ResponseGenerator:

    @staticmethod
    def generate(prompt):
        llm = LLMInterface()
        answer = llm.generate(prompt)

        if not answer or not answer.strip():
            raise RuntimeError(
                "The AI assistant returned an empty response."
            )

        return answer.strip()
