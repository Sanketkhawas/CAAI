import os

from google import genai
from google.genai import types


class LLMInterface:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise Exception("Gemini API Key not found.")

        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt):

        print("\n==============================")
        print(">>> USING NEW LLM INTERFACE <<<")
        print("==============================")
        print("Model : gemini-2.5-flash")
        print("Prompt :", prompt[:150])

        try:

            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1024
                )
            )

            print("\nGemini Response Received\n")

            return response.text

        except Exception as e:

            print("\nGemini ERROR:")
            print(type(e))
            print(e)

            return f"Error: {e}"