"""
GOVs-AI Memory Store
JSON-file-backed persistent memory per user for the AI agent.
Stores extracted profile fields, conversation summaries, and scheme interests.
"""

import json
import os
from typing import Optional
from datetime import datetime, timezone

MEMORY_DIR = "./memory_store"
os.makedirs(MEMORY_DIR, exist_ok=True)


class MemoryStore:
    """Persistent memory store for user conversation context."""

    @staticmethod
    def _get_path(user_id: int) -> str:
        return os.path.join(MEMORY_DIR, f"user_{user_id}.json")

    @staticmethod
    def load(user_id: int) -> dict:
        """Load user memory from disk. Returns empty structure if not found."""
        path = MemoryStore._get_path(user_id)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "user_id": user_id,
            "extracted_profile": {},
            "conversation_summaries": [],
            "topics_discussed": [],
            "schemes_interested": [],
            "schemes_recommended": [],
            "preferences": [],
            "last_interaction": None,
            "interaction_count": 0,
        }

    @staticmethod
    def save(user_id: int, memory: dict) -> None:
        """Persist user memory to disk."""
        memory["last_interaction"] = datetime.now(timezone.utc).isoformat()
        memory["interaction_count"] = memory.get("interaction_count", 0) + 1

        path = MemoryStore._get_path(user_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

    @staticmethod
    def update_from_conversation(user_id: int, summary: dict) -> dict:
        """Update memory with extracted information from a conversation turn."""
        memory = MemoryStore.load(user_id)

        # Merge extracted profile fields
        if "extracted_profile_fields" in summary:
            memory["extracted_profile"].update(summary["extracted_profile_fields"])

        # Append topics
        if "topics_discussed" in summary:
            existing = set(memory["topics_discussed"])
            for topic in summary["topics_discussed"]:
                if topic not in existing:
                    memory["topics_discussed"].append(topic)

        # Append recommendations
        if "schemes_recommended" in summary:
            existing = set(memory["schemes_recommended"])
            for scheme in summary["schemes_recommended"]:
                if scheme not in existing:
                    memory["schemes_recommended"].append(scheme)

        # Append preferences
        if "user_preferences" in summary:
            existing = set(memory["preferences"])
            for pref in summary["user_preferences"]:
                if pref not in existing:
                    memory["preferences"].append(pref)

        # Store conversation summary (keep last 10)
        if "follow_up_needed" in summary:
            memory["conversation_summaries"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "summary": summary.get("follow_up_needed", ""),
                "topics": summary.get("topics_discussed", []),
            })
            memory["conversation_summaries"] = memory["conversation_summaries"][-10:]

        MemoryStore.save(user_id, memory)
        return memory

    @staticmethod
    def get_summary(user_id: int) -> str:
        """Get a human-readable memory summary for prompt injection."""
        memory = MemoryStore.load(user_id)

        if memory["interaction_count"] == 0:
            return "New user — no previous interactions."

        parts = []
        if memory["extracted_profile"]:
            profile_str = ", ".join(f"{k}: {v}" for k, v in memory["extracted_profile"].items())
            parts.append(f"Known profile: {profile_str}")

        if memory["schemes_recommended"]:
            parts.append(f"Previously recommended: {', '.join(memory['schemes_recommended'][-5:])}")

        if memory["topics_discussed"]:
            parts.append(f"Topics discussed: {', '.join(memory['topics_discussed'][-5:])}")

        if memory["preferences"]:
            parts.append(f"Preferences: {', '.join(memory['preferences'][-3:])}")

        if memory["last_interaction"]:
            parts.append(f"Last interaction: {memory['last_interaction']}")

        return " | ".join(parts) if parts else "Returning user, but minimal history."

    @staticmethod
    def clear(user_id: int) -> None:
        """Clear user memory (for testing/demo reset)."""
        path = MemoryStore._get_path(user_id)
        if os.path.exists(path):
            os.remove(path)
