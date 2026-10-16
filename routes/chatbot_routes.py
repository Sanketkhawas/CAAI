
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user

from services.chatbot.chatbot_engine import ChatbotEngine

chatbot = Blueprint("chatbot", __name__)


@chatbot.route("/assistant", methods=["GET"])
@login_required
def chat_page():
    return render_template("chatbot.html", user=current_user)


@chatbot.route("/chat", methods=["POST"])
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get("question")

    if not isinstance(question, str) or not question.strip():
        return jsonify({"error": "Please enter a question."}), 400

    try:
        answer = ChatbotEngine.chat(current_user.id, question.strip())
        return jsonify({"answer": answer})

    except Exception:
        current_app.logger.exception("Chatbot request failed")
        return jsonify({
            "error": "The AI assistant could not process your question. Please try again."
        }), 500
