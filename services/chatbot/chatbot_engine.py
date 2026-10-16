
"""
Chatbot Engine
--------------
Coordinates intent detection, user context,
prompt construction, AI generation, and chat history.
"""

import logging

from database.database import db
from database.models import ChatHistory
from services.chatbot.intent_classifier import detect_intent
from services.chatbot.context_manager import ContextManager
from services.chatbot.prompt_builder import PromptBuilder
from services.chatbot.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class ChatbotEngine:

    @staticmethod
    def chat(user_id, question):
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Please enter a valid question.")

        question = question.strip()

        # 1. Detect intent
        intent = detect_intent(question)

        # 2. Fetch context belonging to this user
        context = ContextManager.get_context(user_id)

        # 3. Build the AI prompt
        prompt = PromptBuilder.build(
            question,
            intent,
            context,
        )

        # 4. Generate the answer
        # Errors propagate to the Flask route.
        answer = ResponseGenerator.generate(prompt)

        # 5. Save only successful answers
        history = ChatHistory(
            user_id=user_id,
            question=question,
            answer=answer,
        )

        try:
            db.session.add(history)
            db.session.commit()
        except Exception:
            db.session.rollback()
            logger.exception("Failed to save chatbot history")
            raise

        return answer
