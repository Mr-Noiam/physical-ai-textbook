"""
Chatbot API Endpoint

Provides HTTP API for the RAG-powered textbook chatbot.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

from app.rag.chatbot import generate_answer, get_conversation_response
from app.db.models import ChatMessage, User
from app.db.neon import get_db
from app.auth.dependencies import get_current_user_optional
from sqlalchemy.orm import Session


# Create API router
router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])


# Request/Response models
class AskQuestionRequest(BaseModel):
    """Request body for asking a question."""
    question: str = Field(..., min_length=1, max_length=1000, description="User's question")
    selected_text: Optional[str] = Field(None, max_length=5000, description="Text selected by user (optional)")
    conversation_history: Optional[List[Dict]] = Field(None, description="Previous messages in conversation")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is a ROS 2 node?",
                "selected_text": None,
                "conversation_history": None
            }
        }


class SourceReference(BaseModel):
    """A source reference from the textbook."""
    file: str
    section: str
    url: str


class AskQuestionResponse(BaseModel):
    """Response from chatbot."""
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceReference] = Field(..., description="List of source references")
    conversation_id: Optional[int] = Field(None, description="ID of saved conversation (if user is logged in)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "A ROS 2 node is a fundamental building block...",
                "sources": [
                    {
                        "file": "module-1-ros2/week2-fundamentals.md",
                        "section": "Week 2: ROS 2 Fundamentals - Nodes",
                        "url": "/docs/module-1-ros2/week2-fundamentals"
                    }
                ],
                "conversation_id": 123,
                "timestamp": "2025-01-10T12:00:00"
            }
        }


@router.post("/ask", response_model=AskQuestionResponse)
async def ask_question(
    request: AskQuestionRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Ask a question to the RAG chatbot.

    This endpoint:
    1. Retrieves relevant textbook content using vector search
    2. Generates an answer using GPT-4
    3. Returns the answer with source references
    4. Optionally saves the conversation to database (if user is authenticated)

    Args:
        request: Question request with optional selected text and conversation history
        db: Database session (injected)
        current_user: Optional authenticated user (injected)

    Returns:
        Answer with sources and optional conversation ID

    Raises:
        HTTPException: If answer generation fails
    """
    try:
        # Generate answer using RAG
        if request.conversation_history:
            chatbot_response = get_conversation_response(
                question=request.question,
                conversation_history=request.conversation_history,
                selected_text=request.selected_text
            )
        else:
            chatbot_response = generate_answer(
                question=request.question,
                selected_text=request.selected_text
            )

        # Convert sources to Pydantic models
        sources = [
            SourceReference(**source)
            for source in chatbot_response.sources
        ]

        # Save conversation to database if user is logged in
        conversation_id = None
        if current_user:
            try:
                # Save chat message with both question and answer
                chat_message = ChatMessage(
                    user_id=current_user.id,
                    question=request.question,
                    answer=chatbot_response.answer,
                    context=chatbot_response.context_used[:1000],  # Save first 1000 chars of context
                    selected_text=request.selected_text
                )
                db.add(chat_message)
                db.commit()
                db.refresh(chat_message)

                conversation_id = str(chat_message.id)

            except Exception as e:
                db.rollback()
                print(f"Error saving conversation: {e}")
                # Don't fail the request if saving fails

        # Return response
        return AskQuestionResponse(
            answer=chatbot_response.answer,
            sources=sources,
            conversation_id=conversation_id
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"Error in ask_question endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate answer. Please try again."
        )


@router.get("/history/{user_id}", response_model=List[Dict])
async def get_conversation_history(
    user_id: int,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get conversation history for a user.

    Args:
        user_id: User ID
        limit: Maximum number of messages to return (default 20)
        db: Database session (injected)

    Returns:
        List of conversation messages

    Raises:
        HTTPException: If retrieval fails
    """
    try:
        messages = db.query(ChatMessage)\
            .filter(ChatMessage.user_id == user_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(limit)\
            .all()

        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "selected_text": msg.selected_text,
                "created_at": msg.created_at.isoformat()
            }
            for msg in reversed(messages)  # Reverse to show oldest first
        ]

    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversation history"
        )


@router.delete("/history/{user_id}")
async def clear_conversation_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Clear conversation history for a user.

    Args:
        user_id: User ID
        db: Database session (injected)

    Returns:
        Success message

    Raises:
        HTTPException: If deletion fails
    """
    try:
        deleted_count = db.query(ChatMessage)\
            .filter(ChatMessage.user_id == user_id)\
            .delete()

        db.commit()

        return {
            "message": f"Deleted {deleted_count} messages",
            "deleted_count": deleted_count
        }

    except Exception as e:
        db.rollback()
        print(f"Error clearing conversation history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear conversation history"
        )


# Health check endpoint
@router.get("/health")
async def health_check():
    """Check if chatbot API is running."""
    return {
        "status": "healthy",
        "service": "chatbot",
        "version": "1.0.0"
    }
