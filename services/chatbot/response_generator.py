from services.chatbot.llm_interface import LLMInterface


class ResponseGenerator:

    @staticmethod
    def generate(prompt):
        try:
            llm = LLMInterface()
            return llm.generate(prompt)

        except Exception as e:
            return f"Error: {str(e)}"