import hashlib
import re
import uuid
from dataclasses import dataclass, field
from io import BytesIO
from typing import Optional

import tiktoken
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.services import embedding_service

tokenizer = tiktoken.get_encoding("cl100k_base")


@dataclass
class RawChunk:
    content: str
    heading: Optional[str] = None
    page_number: Optional[int] = None


@dataclass
class ProcessedChunk:
    content: str
    heading: Optional[str] = None
    page_number: Optional[int] = None
    token_count: int = 0
    chunk_index: int = 0


def parse_markdown(content: str) -> list[RawChunk]:
    chunks: list[RawChunk] = []
    # Split by headings
    sections = re.split(r"(?=^#{1,3}\s)", content, flags=re.MULTILINE)

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract heading
        heading_match = re.match(r"^(#{1,3})\s+(.+?)$", section, re.MULTILINE)
        heading = heading_match.group(2).strip() if heading_match else None

        # Get body (text after heading)
        if heading_match:
            body = section[heading_match.end() :].strip()
        else:
            body = section

        if not body:
            continue

        # Split by paragraphs
        paragraphs = re.split(r"\n\s*\n", body)
        for para in paragraphs:
            para = para.strip()
            if para:
                chunks.append(RawChunk(content=para, heading=heading))

    return chunks


def parse_pdf(file_bytes: bytes) -> list[RawChunk]:
    import fitz  # PyMuPDF

    chunks: list[RawChunk] = []
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        if not text.strip():
            continue

        paragraphs = re.split(r"\n\s*\n", text)
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 20:
                chunks.append(
                    RawChunk(content=para, page_number=page_num + 1)
                )

    doc.close()
    return chunks


def parse_docx(file_bytes: bytes) -> list[RawChunk]:
    from docx import Document as DocxDocument

    chunks: list[RawChunk] = []
    doc = DocxDocument(BytesIO(file_bytes))

    current_heading: str | None = None
    current_text: list[str] = []

    for para in doc.paragraphs:
        if para.style and para.style.name.startswith("Heading"):
            # Save accumulated text
            if current_text:
                text = "\n".join(current_text)
                if text.strip():
                    chunks.append(
                        RawChunk(content=text.strip(), heading=current_heading)
                    )
                current_text = []
            current_heading = para.text.strip()
        else:
            if para.text.strip():
                current_text.append(para.text.strip())

    # Remaining text
    if current_text:
        text = "\n".join(current_text)
        if text.strip():
            chunks.append(
                RawChunk(content=text.strip(), heading=current_heading)
            )

    return chunks


def count_tokens(text: str) -> int:
    return len(tokenizer.encode(text))


def chunk_text(raw_chunks: list[RawChunk]) -> list[ProcessedChunk]:
    processed: list[ProcessedChunk] = []
    chunk_index = 0
    previous_overlap_text = ""

    for raw in raw_chunks:
        tokens = count_tokens(raw.content)

        if tokens <= settings.CHUNK_SIZE:
            content = raw.content
            if previous_overlap_text:
                content = previous_overlap_text + " " + content
            processed.append(
                ProcessedChunk(
                    content=content,
                    heading=raw.heading,
                    page_number=raw.page_number,
                    token_count=count_tokens(content),
                    chunk_index=chunk_index,
                )
            )
            chunk_index += 1
            # Set overlap from end of this chunk
            words = raw.content.split()
            overlap_tokens = 0
            overlap_words = []
            for w in reversed(words):
                overlap_tokens += count_tokens(w)
                if overlap_tokens >= settings.CHUNK_OVERLAP:
                    break
                overlap_words.insert(0, w)
            previous_overlap_text = " ".join(overlap_words)
        else:
            # Split at sentence boundaries
            sentences = re.split(r"(?<=[.!?])\s+", raw.content)
            current_chunk: list[str] = []
            current_tokens = 0

            if previous_overlap_text:
                current_chunk.append(previous_overlap_text)
                current_tokens = count_tokens(previous_overlap_text)

            for sentence in sentences:
                sentence_tokens = count_tokens(sentence)
                if current_tokens + sentence_tokens > settings.CHUNK_SIZE and current_chunk:
                    chunk_content = " ".join(current_chunk)
                    processed.append(
                        ProcessedChunk(
                            content=chunk_content,
                            heading=raw.heading,
                            page_number=raw.page_number,
                            token_count=count_tokens(chunk_content),
                            chunk_index=chunk_index,
                        )
                    )
                    chunk_index += 1
                    # Overlap
                    words = chunk_content.split()
                    overlap_tokens = 0
                    overlap_words = []
                    for w in reversed(words):
                        overlap_tokens += count_tokens(w)
                        if overlap_tokens >= settings.CHUNK_OVERLAP:
                            break
                        overlap_words.insert(0, w)
                    current_chunk = overlap_words
                    current_tokens = count_tokens(" ".join(current_chunk))

                current_chunk.append(sentence)
                current_tokens += sentence_tokens

            if current_chunk:
                chunk_content = " ".join(current_chunk)
                processed.append(
                    ProcessedChunk(
                        content=chunk_content,
                        heading=raw.heading,
                        page_number=raw.page_number,
                        token_count=count_tokens(chunk_content),
                        chunk_index=chunk_index,
                    )
                )
                chunk_index += 1
                words = chunk_content.split()
                overlap_tokens = 0
                overlap_words = []
                for w in reversed(words):
                    overlap_tokens += count_tokens(w)
                    if overlap_tokens >= settings.CHUNK_OVERLAP:
                        break
                    overlap_words.insert(0, w)
                previous_overlap_text = " ".join(overlap_words)

    return processed


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    return await embedding_service.get_embeddings_batch(texts)


async def ingest_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    file_bytes: bytes,
    file_type: str,
) -> int:
    from sqlalchemy import select

    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise ValueError(f"Document {document_id} not found")

    try:
        # Update status
        document.status = "processing"
        await db.flush()

        # Parse based on file type
        if file_type == "md":
            raw_chunks = parse_markdown(file_bytes.decode("utf-8"))
        elif file_type == "pdf":
            raw_chunks = parse_pdf(file_bytes)
        elif file_type == "docx":
            raw_chunks = parse_docx(file_bytes)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        if not raw_chunks:
            document.status = "completed"
            document.chunk_count = 0
            return 0

        # Chunk
        processed_chunks = chunk_text(raw_chunks)

        # Generate embeddings
        texts = [c.content for c in processed_chunks]
        embeddings = await generate_embeddings(texts)

        # Bulk insert chunks
        chunk_objects = []
        for i, (pc, emb) in enumerate(zip(processed_chunks, embeddings)):
            chunk_objects.append(
                Chunk(
                    id=uuid.uuid4(),
                    document_id=document_id,
                    workspace_id=document.workspace_id,
                    content=pc.content,
                    token_count=pc.token_count,
                    page_number=pc.page_number,
                    heading=pc.heading,
                    chunk_index=pc.chunk_index,
                    embedding=emb,
                )
            )
        db.add_all(chunk_objects)

        # Update document
        document.status = "completed"
        document.chunk_count = len(chunk_objects)
        document.content_hash = hashlib.sha256(file_bytes).hexdigest()

        # Detect page count
        if file_type == "pdf":
            import fitz

            doc = fitz.open(stream=file_bytes, filetype="pdf")
            document.page_count = len(doc)
            doc.close()

        await db.flush()
        return len(chunk_objects)

    except Exception:
        document.status = "failed"
        await db.flush()
        raise
