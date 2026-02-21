import json
import time
import uuid
from collections.abc import AsyncGenerator
from datetime import date, datetime

from openai import AsyncOpenAI
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.analytics import DailyAnalytics
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatChunkEvent, SourceCitation
from app.services import search_service, security_service

openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def get_conversation_context(
    db: AsyncSession, conversation_id: uuid.UUID
) -> list[dict]:
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(settings.CONVERSATION_MEMORY_LIMIT)
    )
    messages = list(reversed(result.scalars().all()))

    # Check if there's a summary
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()

    context = []
    if conversation and conversation.summary:
        context.append(
            {
                "role": "system",
                "content": f"Summary of earlier conversation: {conversation.summary}",
            }
        )

    for msg in messages:
        context.append({"role": msg.role, "content": msg.content})

    return context


async def summarize_older_messages(
    db: AsyncSession, conversation_id: uuid.UUID
) -> None:
    # Get message count
    count_result = await db.execute(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
    )
    total = count_result.scalar() or 0

    if total <= settings.CONVERSATION_MEMORY_LIMIT:
        return

    # Get older messages
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .limit(total - settings.CONVERSATION_MEMORY_LIMIT)
    )
    older_messages = result.scalars().all()

    if not older_messages:
        return

    # Build text to summarize
    text_parts = []
    for msg in older_messages:
        text_parts.append(f"{msg.role}: {msg.content}")
    text_to_summarize = "\n".join(text_parts)

    # Summarize with GPT
    response = await openai_client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Summarize the following conversation concisely, preserving key facts, decisions, and context.",
            },
            {"role": "user", "content": text_to_summarize},
        ],
        max_tokens=500,
    )

    summary = response.choices[0].message.content

    # Update conversation summary
    conv_result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = conv_result.scalar_one_or_none()
    if conversation:
        conversation.summary = summary
        await db.flush()


async def stream_chat_response(
    db: AsyncSession,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    message: str,
    conversation_id: uuid.UUID | None = None,
) -> AsyncGenerator[str, None]:
    start_time = time.time()

    # Security check
    if security_service.detect_injection(message):
        event = ChatChunkEvent(
            type="error", content="Your message was flagged as potentially harmful."
        )
        yield f"data: {event.model_dump_json()}\n\n"
        return

    sanitized_message = security_service.sanitize_input(message)

    # Create or retrieve conversation
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation is None:
            event = ChatChunkEvent(type="error", content="Conversation not found.")
            yield f"data: {event.model_dump_json()}\n\n"
            return
    else:
        conversation = Conversation(
            id=uuid.uuid4(),
            user_id=user_id,
            workspace_id=workspace_id,
            title=sanitized_message[:50] + ("..." if len(sanitized_message) > 50 else ""),
        )
        db.add(conversation)
        await db.flush()

    # Save user message
    user_msg = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        role="user",
        content=sanitized_message,
        token_count=len(sanitized_message.split()),
    )
    db.add(user_msg)
    conversation.message_count += 1
    await db.flush()

    # Send conversation_id to frontend
    event = ChatChunkEvent(type="conversation_id", conversation_id=conversation.id)
    yield f"data: {event.model_dump_json()}\n\n"

    # Search for relevant chunks
    search_results = await search_service.hybrid_search(
        db, sanitized_message, workspace_id
    )

    # Send sources
    sources = [
        SourceCitation(
            chunk_id=r.chunk_id,
            document_name=r.document_name,
            page_number=r.page_number,
            text_snippet=r.text_snippet,
            relevance_score=r.relevance_score,
        )
        for r in search_results
    ]
    event = ChatChunkEvent(type="sources", sources=sources)
    yield f"data: {event.model_dump_json()}\n\n"

    # Build context
    context_parts = []
    for r in search_results:
        page_info = f", Page {r.page_number}" if r.page_number else ""
        context_parts.append(
            f"[Source: {r.document_name}{page_info}]\n{r.text_snippet}"
        )
    context_text = "\n---\n".join(context_parts)

    system_prompt = f"""You are DocuMind, an AI assistant that answers questions based on the provided documents.
Use ONLY the following context to answer. If the answer is not in the context, say so.
Always cite your sources using [Source: document_name, Page X] format.

Context:
---
{context_text}
---"""

    # Get conversation history
    conversation_context = await get_conversation_context(db, conversation.id)

    # Build messages for OpenAI
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_context)

    # Stream from OpenAI
    full_response = ""
    prompt_tokens = 0
    completion_tokens = 0

    try:
        stream = await openai_client.chat.completions.create(
            model=settings.CHAT_MODEL,
            messages=messages,
            stream=True,
            max_tokens=2000,
            stream_options={"include_usage": True},
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                event = ChatChunkEvent(type="token", content=token)
                yield f"data: {event.model_dump_json()}\n\n"

            if chunk.usage:
                prompt_tokens = chunk.usage.prompt_tokens
                completion_tokens = chunk.usage.completion_tokens

    except Exception as e:
        event = ChatChunkEvent(type="error", content=str(e))
        yield f"data: {event.model_dump_json()}\n\n"
        return

    # Done event
    event = ChatChunkEvent(type="done")
    yield f"data: {event.model_dump_json()}\n\n"

    # Calculate latency
    latency_ms = int((time.time() - start_time) * 1000)

    # Save assistant message
    sources_data = [s.model_dump(mode="json") for s in sources]
    assistant_msg = Message(
        id=uuid.uuid4(),
        conversation_id=conversation.id,
        role="assistant",
        content=full_response,
        token_count=completion_tokens or len(full_response.split()),
        sources=sources_data,
        latency_ms=latency_ms,
    )
    db.add(assistant_msg)
    conversation.message_count += 1
    conversation.updated_at = datetime.utcnow()
    await db.flush()

    # Update analytics
    today = date.today()
    analytics_result = await db.execute(
        select(DailyAnalytics).where(
            DailyAnalytics.workspace_id == workspace_id,
            DailyAnalytics.date == today,
        )
    )
    analytics = analytics_result.scalar_one_or_none()

    if analytics is None:
        analytics = DailyAnalytics(
            workspace_id=workspace_id,
            date=today,
            total_queries=1,
            total_tokens_prompt=prompt_tokens,
            total_tokens_completion=completion_tokens,
            average_latency_ms=float(latency_ms),
            query_texts=[sanitized_message],
        )
        db.add(analytics)
    else:
        prev_total = analytics.total_queries
        analytics.total_queries += 1
        analytics.total_tokens_prompt += prompt_tokens
        analytics.total_tokens_completion += completion_tokens
        analytics.average_latency_ms = (
            analytics.average_latency_ms * prev_total + latency_ms
        ) / analytics.total_queries
        if analytics.query_texts is None:
            analytics.query_texts = [sanitized_message]
        else:
            analytics.query_texts = analytics.query_texts + [sanitized_message]

    await db.flush()

    # Trigger summarization if needed (fire and forget)
    if conversation.message_count > settings.CONVERSATION_MEMORY_LIMIT * 2:
        try:
            await summarize_older_messages(db, conversation.id)
        except Exception:
            pass  # Non-critical
