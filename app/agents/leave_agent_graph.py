import os
from typing import TypedDict, Annotated, Sequence
import operator
from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from app.tools import leave_tools

# --- Agent State Definition (No changes here) ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_info: dict

# --- Setup Tools (No changes here) ---
tools = [
    leave_tools.create_leave_request,
    leave_tools.get_my_leave_requests,
    leave_tools.get_pending_supervisor_requests,
    leave_tools.get_pending_hr_requests,
    leave_tools.approve_or_reject_request
]
tool_map = {tool.name: tool for tool in tools}

# --- Graph Nodes ---
def call_model(state: AgentState):
    """Invokes the LLM to get the next step."""
    user_info = state.get("user_info", {})
    user_role = user_info.get('role', 'unknown')
    
    # --- FIX 1: Get the employee_id from the user_info ---
    # The user's own ID comes from the JWT token under the 'user_id' key
    employee_id = user_info.get('user_id') 
    
    supervisor_id = user_info.get('supervisor_id', None) if user_role == 'employee' else None
    
    # Format the system prompt with all necessary context
    system_prompt_with_context = system_prompt.format(
        user_role=user_role,
        supervisor_id=supervisor_id,
        employee_id=employee_id  # Pass the employee_id to the prompt
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_with_context),
        MessagesPlaceholder(variable_name="messages"),
    ])
    llm_with_tools = llm.bind_tools(tools)
    chain = prompt | llm_with_tools
    response = chain.invoke({"messages": state["messages"]})
    return {"messages": [response]}


def call_tool(state: AgentState):
    """Executes the tool chosen by the model. (No changes here)"""
    # ... (මෙම ශ්‍රිතයේ කිසිදු වෙනසක් නැත, පෙර පිළිතුරේ පරිදිම තබන්න) ...
    last_message = state["messages"][-1]
    tool_outputs = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call['name']
        tool_args = tool_call['args']
        if tool_name in tool_map:
            tool_to_call = tool_map[tool_name]
            print(f"--- Calling Tool: {tool_name} with args: {tool_args} ---")
            try:
                tool_output = tool_to_call.invoke(tool_args)
            except Exception as e:
                print(f"--- Error calling tool {tool_name}: {e} ---")
                tool_output = f"Error: {e}"
        else:
            tool_output = f"Error: Tool '{tool_name}' not found."
        tool_outputs.append(
            ToolMessage(content=str(tool_output), tool_call_id=tool_call['id'])
        )
    return {"messages": tool_outputs}

# --- Conditional Edge Logic (No changes here) ---
def should_continue(state: AgentState):
    # ... (මෙම ශ්‍රිතයේ කිසිදු වෙනසක් නැත) ...
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# --- Setup LLM and Prompt ---
llm = ChatGroq(model="qwen/qwen3-32b", temperature=0, groq_api_key=os.getenv("GROQ_API_KEY"))

# --- FIX 2: Update the system prompt with instructions for employee_id ---
system_prompt = """You are an expert HR assistant chatbot for a leave management system.
You must respond to the user in **Sinhala**. Be polite, professional, and helpful.

**GOLDEN RULE: Before calling any tool, you MUST first check the conversation history. If the information the user is asking for (like a rejection reason) is already available in a previous message, answer using that information directly. DO NOT call a tool again if you already have the answer.**

Your capabilities depend on the user's role, which is: **{user_role}**.

- If the user's role is 'employee':
  - Your main task is to help them create and view leave requests.
  - When you use `get_my_leave_requests` and find a rejected request, make sure to mention that the user can ask for the reason.
  # ... ( සේවකයාට අදාළ අනෙකුත් උපදෙස් පෙර පරිදිම තබන්න) ...
  - **CRITICAL INSTRUCTIONS FOR CREATING LEAVE:**
    - To create a leave request using `create_leave_request`, you absolutely need THREE pieces of information from the user: 1. The leave type. 2. The start date. 3. The end date.
    - **Follow this conversation flow exactly:**
        - **Step 1:** If the user makes a vague request, you MUST ask for the missing details.
        - **Step 2:** Do NOT call the `create_leave_request` tool until you have gathered all three pieces of information.
        - **Step 3:** Once you have the details, YOU MUST confirm them with the user one last time.
        - **Step 4:** Only after the user confirms, you are allowed to call the `create_leave_request` tool. For the tool arguments, you MUST use the following IDs which are provided to you:
            - Use **{employee_id}** for the `employee_id` argument.
            - Use **{supervisor_id}** for the `supervisor_id` argument.
            - Do NOT ask the user for these IDs.
  - You can also show an employee their own leave requests using `get_my_leave_requests`.

- If the user's role is 'supervisor' or 'hr':
  # ... (සුපවයිසර් සහ HR ට අදාළ උපදෙස් පෙර පරිදිම තබන්න) ...
  - You can show them pending leave requests using the appropriate tools.
  - **CRITICAL INSTRUCTIONS FOR APPROVING/REJECTING:**
    - When you use the `approve_or_reject_request` tool, the `request_id` argument **MUST** be the 24-character hexadecimal ObjectId of the leave request (e.g., '667b...'), **NOT** the employee's ID (e.g., 'EMP123').
    - You should find this specific `request_id` from the list of requests you previously showed the user in the conversation history. If a user says "approve Kamal's request", you must look back in the conversation to find the specific request ID associated with Kamal's pending request.
"""

# --- Define the Graph (No changes here) ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("action", call_tool)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")
agent_graph = workflow.compile()
print("✅ LangGraph agent compiled with FINAL ID handling.")