"""
RAG Chatbot Module

Combines retrieval and generation to answer questions about the textbook.
Uses OpenAI GPT-4 to generate answers based on retrieved context.
"""

from typing import Dict, List, Optional

from openai import OpenAI

from app.config import settings
from app.rag.retrieval import (
    format_context_for_prompt,
    get_unique_sources,
    search_similar_chunks,
)

# Initialize OpenAI client using settings
client = OpenAI(api_key=settings.openai_api_key)

# Model configuration
CHAT_MODEL = settings.openai_model
MAX_TOKENS = 800
TEMPERATURE = 0.7


class ChatbotResponse:
    """Represents a chatbot response with answer and sources."""

    def __init__(self, answer: str, sources: List[Dict], context_used: str):
        self.answer = answer
        self.sources = sources
        self.context_used = context_used

    def to_dict(self) -> Dict:
        """Convert to dictionary for API responses."""
        return {
            "answer": self.answer,
            "sources": self.sources,
            "context_preview": self.context_used[:200] + "..."
            if len(self.context_used) > 200
            else self.context_used,
        }


def build_system_prompt() -> str:
    """
    Build the system prompt that defines the chatbot's behavior.

    Returns:
        System prompt string
    """
    return """You are an expert teaching assistant for the "Physical AI & Humanoid Robotics" course.

Your role is to help students understand robotics concepts by answering their questions based on the textbook content.

Guidelines:
1. **Answer based on provided context**: Use the textbook excerpts provided to answer questions
2. **Be clear and educational**: Explain concepts thoroughly but concisely
3. **Use examples**: Include code examples or concrete scenarios when relevant
4. **Cite sources**: Reference which section of the textbook you're using
5. **Admit uncertainty**: If the context doesn't contain the answer, say so clearly
6. **Encourage learning**: Suggest related topics the student might explore

Tone: Friendly, knowledgeable, patient - like a helpful TA in office hours."""


def generate_answer(
    question: str, selected_text: Optional[str] = None, top_k: int = 5
) -> ChatbotResponse:
    """
    Generate an answer to the user's question using RAG.

    Workflow:
    1. Search for relevant textbook chunks
    2. Format context from search results
    3. Build prompt with question and context
    4. Call GPT-4 to generate answer
    5. Return answer with sources

    Args:
        question: User's question
        selected_text: Optional text selected by user (for "Ask about this" feature)
        top_k: Number of relevant chunks to retrieve

    Returns:
        ChatbotResponse with answer and sources

    Raises:
        Exception: If answer generation fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    try:
        # 1. Retrieve relevant chunks
        if selected_text:
            # If user selected text, search for similar content to provide more context
            search_query = (
                f"{question} {selected_text[:200]}"  # Combine question with selection
            )
        else:
            search_query = question

        search_results = search_similar_chunks(search_query, top_k=top_k)

        # 2. Format context
        context = format_context_for_prompt(search_results)

        # Add selected text to context if provided
        if selected_text:
            context = f"[User selected text]\n{selected_text}\n\n{context}"

        # 3. Build messages for GPT-4
        messages = [
            {"role": "system", "content": build_system_prompt()},
            {
                "role": "user",
                "content": f"""Based on the following textbook content, please answer this question:

Question: {question}

Textbook Content:
{context}

Please provide a clear, educational answer based on this content. If the content doesn't fully answer the question, explain what information is available and what might be missing.""",
            },
        ]

        # 4. Generate answer with GPT-4
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
        )

        answer = response.choices[0].message.content.strip()

        # 5. Extract sources
        sources = get_unique_sources(search_results)

        # 6. Create response object
        return ChatbotResponse(answer=answer, sources=sources, context_used=context)

    except Exception as e:
        print(f"Error generating answer: {e}")
        raise


def get_conversation_response(
    question: str,
    conversation_history: Optional[List[Dict]] = None,
    selected_text: Optional[str] = None,
) -> ChatbotResponse:
    """
    Generate answer with conversation history support.

    Args:
        question: Current question
        conversation_history: Previous messages [{"role": "user"|"assistant", "content": "..."}]
        selected_text: Optional selected text

    Returns:
        ChatbotResponse object
    """
    if conversation_history and len(conversation_history) > 0:
        # Build context-aware query using previous messages
        recent_context = " ".join(
            [
                msg["content"]
                for msg in conversation_history[-4:]  # Last 2 exchanges
                if msg["role"] == "user"
            ]
        )
        enhanced_query = f"{recent_context} {question}"

        return generate_answer(enhanced_query, selected_text=selected_text)
    else:
        return generate_answer(question, selected_text=selected_text)


# Example usage
if __name__ == "__main__":
    # Test questions
    test_questions = [
        "What is a ROS 2 node and how do I create one?",
        "Explain the difference between topics and services",
        "How do I use Isaac Sim for synthetic data generation?",
    ]

    for question in test_questions:
        print(f"\n{'=' * 70}")
        print(f"Q: {question}")
        print("=" * 70)

        try:
            response = generate_answer(question, top_k=3)

            print(f"\nA: {response.answer}")

            print(f"\n📚 Sources ({len(response.sources)}):")
            for i, source in enumerate(response.sources, 1):
                print(f"  {i}. {source['section']} ({source['file']})")

        except Exception as e:
            print(f"Error: {e}")
