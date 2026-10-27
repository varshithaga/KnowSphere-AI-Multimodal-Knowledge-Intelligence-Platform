import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi import File as FormFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import File, FileStatus, User
from app.schemas import FileResponse

router = APIRouter(prefix="/files", tags=["Files"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed extensions → the file_type we store in the database
ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".pptx": "pptx",
    ".txt": "txt",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".webp": "image",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
    ".mp4": "video",
    ".mkv": "video",
    ".mov": "video",
}


# ---------- Upload a file ----------
@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
def upload_file(
    file: UploadFile = FormFile(...),
    user_id: int = Form(...),                  # TEMPORARY: will come from JWT later
    description: str | None = Form(None),
    db: Session = Depends(get_db),
):
    # 1. Check the user exists
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

    # 2. Check the extension is allowed
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{extension}' not allowed",
        )

    # 3. Detect the file type
    file_type = ALLOWED_EXTENSIONS[extension]

    # 4. Save the file with a unique name
    unique_name = f"{uuid.uuid4().hex}_{file.filename}"
    save_path = UPLOAD_DIR / unique_name

    with save_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 5. Create the database row
    new_file = File(
        uploaded_by=user.id,
        file_name=file.filename,
        file_path=save_path.as_posix(),
        file_type=file_type,
        description=description,
        status=FileStatus.pending,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file


# ---------- List one user's files ----------
@router.get("/", response_model=list[FileResponse])
def list_files(user_id: int, db: Session = Depends(get_db)):
    return (
        db.query(File)
        .filter(File.uploaded_by == user_id)
        .order_by(File.created_at.desc())
        .all()
    )


# ---------- Get one file ----------
@router.get("/{file_id}", response_model=FileResponse)
def get_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.get(File, file_id)
    if not db_file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="File not found")
    return db_file


# ---------- Delete a file ----------
@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(file_id: int, db: Session = Depends(get_db)):
    db_file = db.get(File, file_id)
    if not db_file:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="File not found")

    # Delete from disk (no error if it's already gone)
    Path(db_file.file_path).unlink(missing_ok=True)

    # Delete from database (chunks are removed automatically by CASCADE)
    db.delete(db_file)
    db.commit()