# controller/chat_controller.py
from flask import Blueprint, request, jsonify
from service.chat_service import ChatGPTService

chat_bp = Blueprint('chat', __name__)

chat_service = ChatGPTService(api_key="OPENAI_API_KEY")

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Question is required"}), 400

    question = data['question']
    answer = chat_service.ask_chatgpt(question)
    return jsonify({"question": question, "answer": answer})
