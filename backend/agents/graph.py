"""
GOVs-AI LangGraph Agent Workflow
The core AI agent as a LangGraph StateGraph with conditional routing.
Demonstrates: Planning, Tool Usage, Memory Management, Autonomous Execution.
"""

import json
import logging
from typing import Literal

from agents.state import AgentState, create_initial_state
from agents.prompts import (
    SYSTEM_PERSONA, INTENT_CLASSIFICATION, MISSING_FIELDS_CHECK,
    QUESTION_GENERATION, ELIGIBILITY_REASONING, RESPONSE_GENERATION,
    CHECKLIST_GENERATION, GREETING_RESPONSE, CONVERSATION_SUMMARY,
    COMPARISON_PROMPT,
)
from agents.tools import (
    search_schemes_by_query, get_all_schemes, check_eligibility,
    get_user_profile_dict, generate_checklist_for_scheme, get_scheme_by_name,
)
from memory.store import MemoryStore
from config import settings

logger = logging.getLogger(__name__)


# ── LLM Abstraction ─────────────────────────────────────────────
def call_llm(prompt: str, system: str = SYSTEM_PERSONA) -> str:
    """Call Gemini API or return mock response."""
    if settings.should_use_mock:
        return _mock_llm_response(prompt)

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.3,
        )
        from langchain_core.messages import SystemMessage, HumanMessage
        response = llm.invoke([
            SystemMessage(content=system),
            HumanMessage(content=prompt),
        ])
        return response.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return _mock_llm_response(prompt)


def _mock_llm_response(prompt: str) -> str:
    """Generate intelligent mock responses for demo mode without API key."""
    prompt_lower = prompt.lower()

    # Intent classification
    if "classify" in prompt_lower or "intent" in prompt_lower or "category" in prompt_lower:
        if any(w in prompt_lower for w in ["hello", "hi", "namaste", "greet"]):
            return "greeting"
        if any(w in prompt_lower for w in ["compare", "difference", "vs", "versus"]):
            return "compare"
        if any(w in prompt_lower for w in ["eligible", "qualify", "can i get", "am i"]):
            return "eligibility"
        if any(w in prompt_lower for w in ["checklist", "documents", "papers"]):
            return "checklist"
        return "query"

    # Missing fields
    if "missing" in prompt_lower and "field" in prompt_lower:
        return "[]"

    # Question generation
    if "generate" in prompt_lower and "question" in prompt_lower:
        return "Could you tell me about your current occupation? For example, are you a farmer, student, business owner, or employed in the private/government sector?"

    # Greeting
    if "greet" in prompt_lower or "welcome" in prompt_lower:
        return "🙏 Namaste! Welcome to GOVs-AI — your AI-powered guide to government welfare schemes. I can help you discover schemes you're eligible for, explain benefits, and create application checklists. What would you like to know about?"

    # Default — scheme recommendation response
    return """Based on your profile, here are the government schemes you may be eligible for:

**1. 🌾 PM Kisan Samman Nidhi**
- **Benefit**: ₹6,000/year in 3 installments
- **Why you qualify**: You are a farmer with cultivable land
- **Eligibility Score**: 92%

**2. 💰 Pradhan Mantri Mudra Yojana (PMMY)**
- **Benefit**: Loans up to ₹10 lakh without collateral
- **Categories**: Shishu (up to ₹50K), Kishore (up to ₹5L), Tarun (up to ₹10L)
- **Eligibility Score**: 85%

**3. 🏥 Ayushman Bharat (PM-JAY)**
- **Benefit**: ₹5 lakh health coverage per family/year
- **Why you qualify**: Your income is within the eligible range
- **Eligibility Score**: 78%

Would you like me to:
- 📋 Generate a document checklist for any of these schemes?
- 🔍 Get detailed eligibility analysis?
- 📊 Compare any two schemes?"""


# ── Graph Nodes ──────────────────────────────────────────────────

def understand_goal(state: AgentState) -> AgentState:
    """Node 1: Classify the user's intent."""
    logger.info("🧠 Node: understand_goal")

    profile_summary = json.dumps({k: v for k, v in state["user_profile"].items() if v}, default=str)
    conversation_context = state["memory"].get("conversation_summaries", [])[-2:]

    prompt = INTENT_CLASSIFICATION.format(
        user_input=state["current_input"],
        profile_summary=profile_summary[:500],
        conversation_context=str(conversation_context)[:300],
    )
    intent = call_llm(prompt).strip().lower()

    valid_intents = {"greeting", "query", "eligibility", "compare", "checklist", "profile_update", "general"}
    if intent not in valid_intents:
        intent = "query"

    state["current_intent"] = intent
    logger.info(f"   Intent classified: {intent}")
    return state


def retrieve_memory(state: AgentState) -> AgentState:
    """Node 2: Load conversation memory for the user."""
    logger.info("🧠 Node: retrieve_memory")

    memory = MemoryStore.load(state["user_id"])
    state["memory"] = memory

    # Merge any memory-extracted profile fields into current profile
    if memory.get("extracted_profile"):
        for key, val in memory["extracted_profile"].items():
            if key in state["user_profile"] and not state["user_profile"].get(key):
                state["user_profile"][key] = val

    logger.info(f"   Memory loaded. Interaction count: {memory.get('interaction_count', 0)}")
    return state


def check_missing_fields(state: AgentState) -> AgentState:
    """Node 3: Determine what profile info is needed for the query."""
    logger.info("🧠 Node: check_missing_fields")

    if state["current_intent"] in ("greeting", "general"):
        state["missing_fields"] = []
        return state

    prompt = MISSING_FIELDS_CHECK.format(
        profile_json=json.dumps(state["user_profile"], default=str),
        user_input=state["current_input"],
        intent=state["current_intent"],
    )
    result = call_llm(prompt).strip()

    try:
        # Try to extract JSON array from response
        if "[" in result:
            start = result.index("[")
            end = result.rindex("]") + 1
            missing = json.loads(result[start:end])
        else:
            missing = []
    except (json.JSONDecodeError, ValueError):
        missing = []

    state["missing_fields"] = missing
    logger.info(f"   Missing fields: {missing}")
    return state


def ask_question(state: AgentState) -> AgentState:
    """Node 4: Generate a conversational question for missing info."""
    logger.info("🧠 Node: ask_question")

    if not state["missing_fields"]:
        return state

    field = state["missing_fields"][0]  # Ask about one field at a time
    conversation_context = state.get("response", "")

    prompt = QUESTION_GENERATION.format(
        field_name=field,
        user_input=state["current_input"],
        conversation_context=conversation_context[:300],
    )
    question = call_llm(prompt).strip()

    state["response"] = question
    state["questions_asked"] = state.get("questions_asked", 0) + 1
    return state


def retrieve_documents(state: AgentState) -> AgentState:
    """Node 5: Search FAISS vector store for relevant scheme documents."""
    logger.info("🧠 Node: retrieve_documents")

    # Build a rich search query from user input + profile context
    profile = state["user_profile"]
    search_parts = [state["current_input"]]

    if profile.get("occupation"):
        search_parts.append(f"for {profile['occupation']}")
    if profile.get("state"):
        search_parts.append(f"in {profile['state']}")
    if profile.get("category"):
        search_parts.append(f"{profile['category']} category")

    search_query = " ".join(search_parts)
    state["search_query"] = search_query

    results = search_schemes_by_query(search_query, top_k=settings.RETRIEVER_TOP_K)
    state["retrieved_docs"] = results
    logger.info(f"   Retrieved {len(results)} document chunks")
    return state


def reason_eligibility(state: AgentState) -> AgentState:
    """Node 6: Evaluate user eligibility against all schemes."""
    logger.info("🧠 Node: reason_eligibility")

    schemes = get_all_schemes()
    profile = state["user_profile"]

    eligible = []
    all_results = []

    for scheme in schemes:
        result = check_eligibility(profile, scheme)
        all_results.append(result)
        if result["eligible"]:
            result["scheme_data"] = scheme
            eligible.append(result)

    state["eligible_schemes"] = eligible
    state["eligibility_reasoning"] = all_results
    logger.info(f"   Found {len(eligible)} eligible schemes out of {len(schemes)}")
    return state


def rank_schemes(state: AgentState) -> AgentState:
    """Node 7: Sort eligible schemes by relevance score."""
    logger.info("🧠 Node: rank_schemes")

    eligible = state["eligible_schemes"]
    ranked = sorted(eligible, key=lambda x: x["score"], reverse=True)
    state["ranked_schemes"] = ranked[:10]  # Top 10

    # Generate metadata for frontend rendering
    schemes_metadata = []
    for r in state["ranked_schemes"]:
        scheme = r.get("scheme_data", {})
        schemes_metadata.append({
            "id": scheme.get("id"),
            "name": scheme.get("name", r["scheme_name"]),
            "category": scheme.get("category", ""),
            "benefits_amount": scheme.get("benefits_amount", ""),
            "score": r["score"],
            "reasoning": r["reasoning"],
        })

    state["schemes_metadata"] = schemes_metadata
    logger.info(f"   Ranked {len(ranked)} schemes")
    return state


def generate_response(state: AgentState) -> AgentState:
    """Node 8: Generate the final response to the user."""
    logger.info("🧠 Node: generate_response")

    intent = state["current_intent"]

    if intent == "greeting":
        is_returning = state["memory"].get("interaction_count", 0) > 0
        prompt = GREETING_RESPONSE.format(
            user_input=state["current_input"],
            user_name=state["user_profile"].get("name", "there"),
            is_returning=is_returning,
            memory_summary=MemoryStore.get_summary(state["user_id"]),
        )
        state["response"] = call_llm(prompt)
        return state

    if intent == "compare":
        schemes = get_all_schemes()[:5]
        prompt = COMPARISON_PROMPT.format(
            profile_json=json.dumps(state["user_profile"], default=str),
            user_input=state["current_input"],
            schemes_json=json.dumps(schemes[:3], default=str),
        )
        state["response"] = call_llm(prompt)
        return state

    # Standard query/eligibility response
    retrieved_context = "\n".join([
        f"[{d.get('source', 'unknown')}] {d.get('content', '')[:200]}"
        for d in state["retrieved_docs"][:3]
    ])

    eligible_str = json.dumps([
        {"name": s["scheme_name"], "score": s["score"], "reasoning": s["reasoning"]}
        for s in state["ranked_schemes"][:5]
    ], default=str)

    prompt = RESPONSE_GENERATION.format(
        user_input=state["current_input"],
        intent=intent,
        profile_summary=json.dumps({k: v for k, v in state["user_profile"].items() if v}, default=str)[:500],
        eligible_schemes=eligible_str,
        retrieved_context=retrieved_context[:1000],
        memory_summary=MemoryStore.get_summary(state["user_id"]),
    )
    state["response"] = call_llm(prompt)
    return state


def generate_checklist(state: AgentState) -> AgentState:
    """Node 9: Generate document checklists for top eligible schemes."""
    logger.info("🧠 Node: generate_checklist")

    if state["current_intent"] not in ("eligibility", "checklist") or not state["ranked_schemes"]:
        return state

    # Generate checklist for the top scheme
    top = state["ranked_schemes"][0]
    scheme_data = top.get("scheme_data", {})
    if scheme_data:
        checklist = generate_checklist_for_scheme(scheme_data, state["user_profile"])
        state["checklist"] = checklist
        logger.info(f"   Generated checklist for {scheme_data.get('name', 'unknown')}")

    return state


def store_memory(state: AgentState) -> AgentState:
    """Node 10: Persist conversation memory."""
    logger.info("🧠 Node: store_memory")

    summary = {
        "topics_discussed": [state["current_intent"]],
        "schemes_recommended": [s["scheme_name"] for s in state.get("ranked_schemes", [])[:3]],
        "user_preferences": [],
        "extracted_profile_fields": {},
        "follow_up_needed": "",
    }

    MemoryStore.update_from_conversation(state["user_id"], summary)
    logger.info("   Memory stored successfully")
    return state


# ── Routing Logic ────────────────────────────────────────────────

def should_ask_question(state: AgentState) -> Literal["ask_question", "retrieve_documents"]:
    """Conditional edge: ask for missing info or proceed to retrieval."""
    if (
        state["missing_fields"]
        and state["questions_asked"] < state["max_questions"]
        and state["current_intent"] not in ("greeting", "general")
    ):
        return "ask_question"
    return "retrieve_documents"


def should_skip_eligibility(state: AgentState) -> Literal["reason_eligibility", "generate_response"]:
    """Skip eligibility check for simple queries/greetings."""
    if state["current_intent"] in ("greeting", "general"):
        return "generate_response"
    return "reason_eligibility"


# ── Graph Builder ────────────────────────────────────────────────

def build_graph():
    """
    Build the LangGraph StateGraph.

    Flow:
    START → understand_goal → retrieve_memory → check_missing_fields
        → [conditional] → ask_question (if missing) → END (wait for user)
        → [conditional] → retrieve_documents → reason_eligibility → rank_schemes
        → generate_response → generate_checklist → store_memory → END
    """
    try:
        from langgraph.graph import StateGraph, END

        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("understand_goal", understand_goal)
        graph.add_node("retrieve_memory", retrieve_memory)
        graph.add_node("check_missing_fields", check_missing_fields)
        graph.add_node("ask_question", ask_question)
        graph.add_node("retrieve_documents", retrieve_documents)
        graph.add_node("reason_eligibility", reason_eligibility)
        graph.add_node("rank_schemes", rank_schemes)
        graph.add_node("generate_response", generate_response)
        graph.add_node("generate_checklist", generate_checklist)
        graph.add_node("store_memory", store_memory)

        # Define edges
        graph.set_entry_point("understand_goal")
        graph.add_edge("understand_goal", "retrieve_memory")
        graph.add_edge("retrieve_memory", "check_missing_fields")

        # Conditional: ask question or proceed
        graph.add_conditional_edges(
            "check_missing_fields",
            should_ask_question,
            {
                "ask_question": "ask_question",
                "retrieve_documents": "retrieve_documents",
            }
        )

        # If asking question, go to store memory and end
        graph.add_edge("ask_question", "store_memory")

        # Conditional: skip eligibility for greetings
        graph.add_conditional_edges(
            "retrieve_documents",
            should_skip_eligibility,
            {
                "reason_eligibility": "reason_eligibility",
                "generate_response": "generate_response",
            }
        )

        graph.add_edge("reason_eligibility", "rank_schemes")
        graph.add_edge("rank_schemes", "generate_response")
        graph.add_edge("generate_response", "generate_checklist")
        graph.add_edge("generate_checklist", "store_memory")
        graph.add_edge("store_memory", END)

        compiled = graph.compile()
        logger.info("✅ LangGraph agent compiled successfully")
        return compiled

    except ImportError:
        logger.warning("LangGraph not installed. Using fallback sequential agent.")
        return None


# ── Fallback Sequential Agent ───────────────────────────────────

def run_fallback_agent(state: AgentState) -> AgentState:
    """Run the agent workflow sequentially without LangGraph."""
    state = understand_goal(state)
    state = retrieve_memory(state)
    state = check_missing_fields(state)

    if state["missing_fields"] and state["questions_asked"] < state["max_questions"]:
        state = ask_question(state)
        state = store_memory(state)
        return state

    state = retrieve_documents(state)

    if state["current_intent"] not in ("greeting", "general"):
        state = reason_eligibility(state)
        state = rank_schemes(state)

    state = generate_response(state)
    state = generate_checklist(state)
    state = store_memory(state)
    return state


# ── Public API ───────────────────────────────────────────────────

_compiled_graph = None


def get_agent():
    """Get or build the compiled agent graph."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


def run_agent(user_input: str, user_id: int) -> dict:
    """
    Run the AI agent with a user message.
    Returns: {response, schemes_metadata, checklist, intent}
    """
    profile = get_user_profile_dict(user_id)
    memory = MemoryStore.load(user_id)

    state = create_initial_state(user_input, user_id, profile, memory)

    agent = get_agent()
    if agent:
        try:
            result = agent.invoke(state)
        except Exception as e:
            logger.error(f"LangGraph agent error: {e}")
            result = run_fallback_agent(state)
    else:
        result = run_fallback_agent(state)

    return {
        "response": result.get("response", "I'm sorry, I couldn't process that. Please try again."),
        "schemes_metadata": result.get("schemes_metadata"),
        "checklist": result.get("checklist"),
        "intent": result.get("current_intent", "general"),
    }
