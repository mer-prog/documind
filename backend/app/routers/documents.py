import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse, IngestResponse
from app.services import ingest_service

router = APIRouter()

ALLOWED_TYPES = {"md", "pdf", "docx"}
MAX_UPLOAD_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Count
    count_result = await db.execute(
        select(func.count(Document.id)).where(
            Document.workspace_id == current_user.workspace_id
        )
    )
    total = count_result.scalar() or 0

    # Fetch
    result = await db.execute(
        select(Document)
        .where(Document.workspace_id == current_user.workspace_id)
        .order_by(Document.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
    )


@router.post("/documents", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_TYPES)}",
        )

    # Read file with size limit
    file_bytes = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB} MB",
        )

    # Create document
    document = Document(
        id=uuid.uuid4(),
        workspace_id=current_user.workspace_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        file_type=ext,
        file_size=len(file_bytes),
        file_content=file_bytes,
        status="pending",
        content_hash=hashlib.sha256(file_bytes).hexdigest(),
    )
    db.add(document)
    await db.flush()

    return DocumentResponse.model_validate(document)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.workspace_id == current_user.workspace_id,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    await db.delete(document)
    await db.flush()


@router.post("/documents/{document_id}/ingest", response_model=IngestResponse)
async def ingest_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.workspace_id == current_user.workspace_id,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if document.file_content is None:
        raise HTTPException(status_code=400, detail="Document has no file content")

    chunk_count = await ingest_service.ingest_document(
        db, document.id, document.file_content, document.file_type
    )

    return IngestResponse(
        document_id=document.id,
        status=document.status,
        chunk_count=chunk_count,
    )
