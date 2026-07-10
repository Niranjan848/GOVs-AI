"""
GOVs-AI Chat Routes
POST /api/chat — AI conversation endpoint
GET /api/history — chat history
GET /api/chat/{chat_id} — full conversation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database.connection import get_db
from database.models import User, Chat, Message
from api.auth import get_current_user
from agents.graph import run_agent
from utils.validators import (
    ChatMessageRequest, ChatResponse, MessageResponse, ChatListItem,
)

router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/chat", response_model=MessageResponse)
def send_message(
    request: ChatMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to the AI agent and get a response."""
    # Get or create chat
    if request.chat_id:
        chat = db.query(Chat).filter(
            Chat.id == request.chat_id,
            Chat.user_id == current_user.id,
        ).first()
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        # Create new chat with first message as title
        title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        chat = Chat(user_id=current_user.id, title=title)
        db.add(chat)
        db.flush()

    # Save user message
    user_msg = Message(
        chat_id=chat.id,
        role="user",
        content=request.message,
    )
    db.add(user_msg)
    db.flush()

    # Run AI agent
    try:
        result = run_agent(request.message, current_user.id)
    except Exception as e:
        result = {
            "response": "I apologize, but I encountered an error processing your request. Please try again.",
            "schemes_metadata": None,
            "checklist": None,
            "intent": "error",
        }

    # Save AI response
    ai_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=result["response"],
        metadata_json={
            "schemes": result.get("schemes_metadata"),
            "checklist": result.get("checklist"),
            "intent": result.get("intent"),
        },
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return MessageResponse.model_validate(ai_msg)


@router.get("/history", response_model=List[ChatListItem])
def get_chat_history(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's chat history with pagination."""
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for chat in chats:
        msg_count = db.query(func.count(Message.id)).filter(Message.chat_id == chat.id).scalar()
        last_msg = (
            db.query(Message)
            .filter(Message.chat_id == chat.id)
            .order_by(Message.created_at.desc())
            .first()
        )
        result.append(ChatListItem(
            id=chat.id,
            title=chat.title,
            created_at=chat.created_at,
            message_count=msg_count or 0,
            last_message_preview=last_msg.content[:100] if last_msg else "",
        ))

    return result


@router.get("/chat/{chat_id}", response_model=ChatResponse)
def get_chat(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full conversation by chat ID."""
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id,
    ).first()

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    return ChatResponse.model_validate(chat)
