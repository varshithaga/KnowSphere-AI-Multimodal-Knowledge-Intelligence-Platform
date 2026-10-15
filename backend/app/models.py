from datetime import datetime
import enum

from sqlalchemy import Boolean, DateTime, Integer, String, func,ForeignKey,Text,Enum,Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


# ---------- Table 1: users ----------
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # created_at = Column(DateTime, default=datetime.datetime.utcnow)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

class FileStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


    
class File(Base):
    __tablename__ ="files"

    id:Mapped[int] =mapped_column(Integer,primary_key=True,autoincrement=True)
    uploaded_by:Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    file_path:Mapped[str]=mapped_column(String(255))
    file_name: Mapped[str] =mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(50),nullable=False)
    description : Mapped[str |None]  =mapped_column(Text)
    status: Mapped[FileStatus] = mapped_column(
        Enum(FileStatus, name="file_status"), default=FileStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime,server_default=func.now())



class ChunkType(str, enum.Enum):
    text = "text"                    # normal text (PDF, DOCX, TXT...)
    ocr = "ocr"                      # text read from an image / scan
    image_caption = "image_caption"  # AI description of an image
    transcript = "transcript"        # speech-to-text from audio / video
    video_frame = "video_frame"      # AI description of a video frame



class Chunks(Base):
    __tablename__ ="chunks"

    id : Mapped[int] = mapped_column(Integer,primary_key=True,
                                     autoincrement=True)
    file_id : Mapped[int] = mapped_column(Integer,ForeignKey('files.id',ondelete='CASCADE'),nullable=False)
    chunk_type : Mapped[ChunkType] = mapped_column(Enum(ChunkType),nullable=False)
    chunk_index : Mapped[int] = mapped_column(Integer,nullable=False)
    content : Mapped[str] = mapped_column(Text,nullable=False)
    page_number : Mapped[int | None] = mapped_column(Integer)#for pdf,docx
    start_time : Mapped[float | None] = mapped_column(Float)#for video/audio
    end_time : Mapped[float | None] = mapped_column(Float)#for video/audio
    image_path : Mapped[str | None] = mapped_column(String(255))#for imageor video frame
    vector_id : Mapped[str | None] = mapped_column(String(255),unique=True)#for vector database in chromadb
    created_at : Mapped[datetime] = mapped_column(DateTime,server_default=func.now())


class ChatSessions(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class ChatMessageSender(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class ChatMessages(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_sessions.id", ondelete='CASCADE'), nullable=False)
    sender: Mapped[ChatMessageSender] = mapped_column(Enum(ChatMessageSender), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100))#assistant model name example: gpt-3.5-turbo, gpt-4, llama-2-13b-chat-hf
    response_time_ms: Mapped[int | None] = mapped_column(Integer)#assistant response time in milliseconds
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())



class Citation(Base):#it links an AI answer to the chunks it used
    __tablename__ = "citations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat_messages.id", ondelete='CASCADE'), nullable=False)
    chunk_id: Mapped[int] = mapped_column(Integer, ForeignKey("chunks.id", ondelete='CASCADE'), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)#similarity score between the chunk and the message
    rank: Mapped[int] = mapped_column(Integer, nullable=False)#RANK the order to display sources in: 1 = most relevant.