from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from services.chatbot.chatbot_engine import ChatbotEngine

chatbot = Blueprint("chatbot", __name__)


@chatbot.route("/chat", methods=["POST"])
@login_required
def chat():

    data = request.get_json()

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "Question is required."
        }), 400

    answer = ChatbotEngine.chat(
        current_user.id,
        question
    )

    return jsonify({
        "answer": answer
    })