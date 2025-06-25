from flask import Blueprint, request, jsonify
from app.utils.decorators import token_required
from app.agents.leave_agent_graph import agent_graph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/', methods=['POST'])
@token_required
def handle_chat(current_user):
    data = request.json
    user_message = data.get("message")
    history_from_frontend = data.get("history", [])

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    chat_history_messages = []
    # Start from the second message if the first is the initial greeting
    start_index = 1 if len(history_from_frontend) > 0 and history_from_frontend[0].get('role') == 'assistant' else 0
    for msg in history_from_frontend[start_index:]:
        if msg["role"] == "user":
            chat_history_messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history_messages.append(AIMessage(content=msg["content"]))
    
    chat_history_messages.append(HumanMessage(content=user_message))

    try:
        user_info_for_agent = current_user.copy()
        if current_user.get('role') == 'employee':
            from app.models.user import User
            user_data = User.find_by_username(current_user['username'])
            user_info_for_agent['supervisor_id'] = user_data.get('supervisor_id') if user_data else None

        response = agent_graph.invoke({
            "messages": chat_history_messages,
            "user_info": user_info_for_agent
        })
        
        ai_response = response['messages'][-1].content
        
        return jsonify({"response": ai_response})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An internal error occurred: {e}"}), 500