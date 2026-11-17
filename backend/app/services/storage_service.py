import io
import os
import uuid
from datetime import datetime, timezone
from typing import Tuple
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
import pypdf
import docx

from app.core.config import settings
from app.models.candidate import Resume

# Magic byte signatures
PDF_MAGIC_BYTES = b"%PDF-"
DOCX_MAGIC_BYTES = b"PK\x03\x04"

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream"  # Some browsers send generic octet-stream for docx
}

def scan_malware(file_bytes: bytes) -> bool:
    """
    Malware scanner hook (ClamAV / security API placeholder).
    Returns True if clean, False if flagged.
    """
    # Verify no embedded malicious script tags or suspicious execution prefixes
    suspicious_signatures = [b"<script", b"javascript:", b"cmd.exe", b"/bin/sh", b"powershell"]
    for sig in suspicious_signatures:
        if sig in file_bytes[:4096].lower():
            return False
    return True

def validate_magic_and_structure(file_bytes: bytes, filename: str) -> str:
    """
    Validates magic bytes and structural integrity of PDF/DOCX.
    Raises HTTPException on validation failure.
    Returns normalized MIME type.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension '{ext}'. Only .pdf and .docx are allowed."
        )

    if ext == ".pdf":
        if not file_bytes.startswith(PDF_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File header does not match valid PDF magic bytes (%PDF-)."
            )
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            if reader.is_encrypted:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Encrypted or password-protected PDF files are not allowed."
                )
            if len(reader.pages) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The provided PDF document is empty."
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse PDF document or file is corrupted: {str(e)}"
            )
        return "application/pdf"

    elif ext == ".docx":
        if not file_bytes.startswith(DOCX_MAGIC_BYTES):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File header does not match valid DOCX magic bytes (PK\\x03\\x04)."
            )
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            # Test document accessibility
            _ = len(doc.paragraphs)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse DOCX document or file is corrupted: {str(e)}"
            )
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid document format.")

async def check_storage_quota(db: AsyncSession, new_file_size: int) -> None:
    """
    Enforces the 950 MB total DB storage safety threshold.
    """
    query = select(func.coalesce(func.sum(Resume.file_size_bytes), 0))
    result = await db.execute(query)
    current_total_bytes = result.scalar_one()

    if (current_total_bytes + new_file_size) > settings.MAX_TOTAL_STORAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
            detail="Storage quota threshold exceeded (950 MB limit reached). Please contact platform administrator."
        )

class StorageService:
    @staticmethod
    async def upload_resume(
        file: UploadFile,
        candidate_id: int,
        db: AsyncSession
    ) -> Resume:
        # 1. Read file bytes
        file_bytes = await file.read()
        file_size = len(file_bytes)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file uploaded. Please upload a valid resume."
            )

        # 2. Strict size check (2 MB ceiling)
        if file_size > settings.MAX_RESUME_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of 2 MB (received {file_size / (1024 * 1024):.2f} MB)."
            )

        # 3. Check cumulative storage quota (950 MB ceiling)
        await check_storage_quota(db, file_size)

        # 4. Validate magic bytes and structural parse
        original_filename = file.filename or "resume.pdf"
        mime_type = validate_magic_and_structure(file_bytes, original_filename)

        # 5. Malware Scan Hook
        if not scan_malware(file_bytes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security scan rejected the file. Potential malicious content detected."
            )

        # 6. Generate unique pathname: resumes/{year}/{month}/{uuid4()}.{ext}
        now = datetime.now(timezone.utc)
        ext = os.path.splitext(original_filename)[1].lower()
        unique_id = str(uuid.uuid4())
        blob_pathname = f"resumes/{now.year}/{now.month:02d}/{unique_id}{ext}"

        # 7. Upload to Vercel Blob (or local storage fallback if token not configured)
        blob_url = None
        if settings.BLOB_READ_WRITE_TOKEN:
            try:
                import requests
                # Vercel Blob Put API
                url = f"https://blob.vercel-storage.com/{blob_pathname}"
                headers = {
                    "Authorization": f"Bearer {settings.BLOB_READ_WRITE_TOKEN}",
                    "x-api-version": "7",
                    "x-access": "private"
                }
                res = requests.put(url, headers=headers, data=file_bytes, timeout=30)
                if res.status_code in (200, 201):
                    blob_data = res.json()
                    blob_url = blob_data.get("url")
                else:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"Vercel Blob upload failed with status {res.status_code}: {res.text}"
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to communicate with Vercel Blob storage: {str(e)}"
                )
        else:
            # Local secure fallback directory
            local_dir = os.path.join(os.getcwd(), "uploads", f"{now.year}", f"{now.month:02d}")
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, f"{unique_id}{ext}")
            with open(local_path, "wb") as f:
                f.write(file_bytes)
            blob_url = f"/uploads/{now.year}/{now.month:02d}/{unique_id}{ext}"

        # 8. Check if candidate already has default resume
        existing_resumes = await db.execute(
            select(Resume).where(Resume.candidate_id == candidate_id)
        )
        is_first = len(existing_resumes.scalars().all()) == 0

        # 9. Save metadata in DB
        resume = Resume(
            candidate_id=candidate_id,
            original_filename=original_filename,
            blob_pathname=blob_pathname,
            blob_url=blob_url,
            file_size_bytes=file_size,
            mime_type=mime_type,
            is_default=is_first,
            is_scanned_safe=True
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        return resume

    @staticmethod
    async def delete_resume(resume_id: int, candidate_id: int, db: AsyncSession) -> bool:
        stmt = select(Resume).where(
            Resume.id == resume_id,
            Resume.candidate_id == candidate_id
        )
        res = await db.execute(stmt)
        resume = res.scalar_one_or_none()
        if not resume:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume record not found.")

        # 1. Delete from Vercel Blob if token available
        if settings.BLOB_READ_WRITE_TOKEN and resume.blob_url:
            try:
                import requests
                headers = {
                    "Authorization": f"Bearer {settings.BLOB_READ_WRITE_TOKEN}",
                    "x-api-version": "7"
                }
                # Vercel Blob Delete API
                del_url = "https://blob.vercel-storage.com/delete"
                requests.post(del_url, json={"urls": [resume.blob_url]}, headers=headers, timeout=15)
            except Exception as e:
                # Log but continue to ensure database cleanliness
                pass

        # 2. Delete from DB
        await db.delete(resume)
        await db.commit()
        return True
