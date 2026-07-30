"""
Chatbot Engine
--------------
Main controller of the AI Tax Assistant.
"""
from database.database import db
from database.models import ChatHistory
from services.chatbot.intent_classifier import detect_intent
from services.chatbot.context_manager import ContextManager
from services.chatbot.prompt_builder import PromptBuilder
from services.chatbot.response_generator import ResponseGenerator


class ChatbotEngine:

    @staticmethod
    def chat(user_id, question):

        # Step 1 - Detect user intent
        intent = detect_intent(question)

        # Step 2 - Fetch user context
        context = ContextManager.get_context(user_id)

        # Step 3 - Build prompt
        prompt = PromptBuilder.build(
            question,
            intent,
            context
        )

        # Step 4 - Generate response
        answer = ResponseGenerator.generate(prompt)

        history = ChatHistory(

            user_id=user_id,

            question=question,

            answer=answer

        )

        db.session.add(history)

        db.session.commit()

        return answer