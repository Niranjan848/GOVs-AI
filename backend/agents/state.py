"""
GOVs-AI Agent State
TypedDict state schema for the LangGraph workflow.
"""

from typing import TypedDict, Optional, List, Any
from langgraph.graph import MessagesState


class AgentState(TypedDict):
    """Complete state flowing through the LangGraph agent workflow."""

    # ── Conversation ─────────────────────────────────────────────
    messages: list  # Chat message history (HumanMessage / AIMessage)
    current_input: str  # The latest user message
    current_intent: str  # Classified intent: query | eligibility | compare | general | greeting

    # ── User Context ─────────────────────────────────────────────
    user_id: int
    user_profile: dict  # Profile fields from DB
    memory: dict  # Persisted conversation memory

    # ── Information Gathering ────────────────────────────────────
    missing_fields: list  # Profile fields still needed for eligibility
    questions_asked: int  # Counter to prevent infinite question loops
    max_questions: int  # Maximum questions before proceeding (default: 3)

    # ── RAG & Retrieval ──────────────────────────────────────────
    retrieved_docs: list  # Document chunks from FAISS
    search_query: str  # Reformulated search query

    # ── Eligibility & Recommendations ────────────────────────────
    eligible_schemes: list  # Schemes the user qualifies for
    ranked_schemes: list  # Sorted by relevance/score
    eligibility_reasoning: list  # Per-scheme reasoning

    # ── Output ───────────────────────────────────────────────────
    response: str  # Final response to user
    checklist: Optional[list]  # Document checklist (if applicable)
    schemes_metadata: Optional[list]  # Scheme cards for frontend rendering


def create_initial_state(user_input: str, user_id: int, profile: dict, memory: dict) -> AgentState:
    """Create a fresh agent state for a new invocation."""
    return AgentState(
        messages=[],
        current_input=user_input,
        current_intent="",
        user_id=user_id,
        user_profile=profile,
        memory=memory,
        missing_fields=[],
        questions_asked=0,
        max_questions=3,
        retrieved_docs=[],
        search_query="",
        eligible_schemes=[],
        ranked_schemes=[],
        eligibility_reasoning=[],
        response="",
        checklist=None,
        schemes_metadata=None,
    )
