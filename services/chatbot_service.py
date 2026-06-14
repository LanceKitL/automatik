"""
NVIDIA LangChain chatbot service for AutoMatik.
Uses ChatNVIDIA with Minimax-M3 via langchain_nvidia_ai_endpoints.
"""

from threading import Lock
from pathlib import Path

from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from conn import run_query

API_KEY = "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"

MAX_HISTORY = 4
MAX_TOKENS = 384

# In-memory cache
_cache = {}
_cache_lock = Lock()
CACHE_MAX = 100

# Load system context
_context_path = Path(__file__).resolve().parent.parent / "SYSTEM_CONTEXT.md"
_infos_path = Path(__file__).resolve().parent.parent / "SYSTEM_INFOS.md"
SYSTEM_CONTEXT = _context_path.read_text(encoding="utf-8") if _context_path.exists() else ""
SYSTEM_INFOS = _infos_path.read_text(encoding="utf-8") if _infos_path.exists() else ""

SYSTEM_PROMPT = f"""You are AutoBot, a helpful assistant for AutoMatik, a car dealership in the Philippines.

You can ONLY answer questions about these topics:
- Vehicles: brands, models, pricing, availability, features, specs
- Financing: loans, monthly amortization, interest rates, down payment, terms
- Test drives: scheduling, requirements (valid driver's license, 18+)
- Reservations: how to reserve, ₱5,000 reservation fee
- Service bookings: maintenance, repair, warranty claims
- Warranty: coverage, claims process
- Dealership: location, hours, contact
- System: how the AutoMatik software works, its features, capabilities, database, and business logic
- Privacy Policy and Terms & Conditions
- FAQs about the dealership and system

{SYSTEM_CONTEXT}

{SYSTEM_INFOS}

If the question is OUTSIDE these dealership topics, politely respond:
"I'm AutoBot — I can only assist with dealership-related questions. Please contact us at info@automatik.com for other inquiries."

Always be concise, friendly, and professional. Use Philippine Peso (₱) for prices.
When suggesting actions, you can reference the website: /vehicles, /loan-calculator, /contact.
Use information from the system context above to answer questions about how the system works."""

client = ChatNVIDIA(
    model="moonshotai/kimi-k2.6",
    api_key=API_KEY,
    temperature=0.7,
    top_p=0.95,
    max_tokens=MAX_TOKENS,
)


def format_messages(history, user_message):
    """Build LangChain message list from conversation history (trimmed to last MAX_HISTORY messages)."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    recent = (history or [])[-MAX_HISTORY:]
    for msg in recent:
        role = msg.get("role", "")
        text = msg.get("text", "")
        if role == "user":
            messages.append(HumanMessage(content=text))
        elif role == "bot":
            messages.append(AIMessage(content=text))
    messages.append(HumanMessage(content=user_message))
    return messages


def handle_tool_call(tool_name, tool_args):
    """Execute a tool/function and return the result as a string."""
    if tool_name == "get_available_brands":
        rows = run_query("SELECT DISTINCT brand FROM vehicles WHERE status = 'available' ORDER BY brand", fetch="all")
        brands = [r["brand"] for r in rows]
        return f"Available brands: {', '.join(brands)}." if brands else "No vehicles currently available."

    if tool_name == "get_business_hours":
        return "We are open Monday – Saturday, 8:00 AM – 6:00 PM. Closed on Sundays."

    if tool_name == "get_contact_info":
        return "Call us at +63 (2) 8123 4567 or email info@automatik.com. Visit us at 123 AutoMall Drive, Makati City."

    return "I'm not sure about that. Please contact the dealership directly."


def _get_cache_key(user_message, history):
    """Generate a cache key from the user message and recent history."""
    recent = (history or [])[-2:]
    ctx = "|".join(f"{m.get('role','')}:{m.get('text','')}" for m in recent)
    return f"{ctx}|user:{user_message}".lower().strip()


def ask(user_message, history=None):
    """
    Send a user message to the chatbot and return the response.
    Uses caching for identical questions within the same conversation context.
    """
    cache_key = _get_cache_key(user_message, history)

    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    try:
        messages = format_messages(history, user_message)
        response = client.invoke(messages)

        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                tool_result = handle_tool_call(tc["name"], tc.get("args", {}))
                messages.append(AIMessage(content="", tool_calls=[tc]))
                messages.append(ToolMessage(content=tool_result, tool_call_id=tc["id"]))
            response = client.invoke(messages)

        result = response.content.strip() if response.content else "I'm not sure about that. Please contact our team for assistance."

        with _cache_lock:
            if len(_cache) >= CACHE_MAX:
                _cache.clear()
            _cache[cache_key] = result

        return result

    except Exception as e:
        return f"I encountered an error. Please try again or contact support. ({str(e)})"
