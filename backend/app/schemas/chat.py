from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import ChatMessageSender


# ---------- Chat sessions ----------
class ChatSessionCreate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)


class ChatSessionResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Asking a question ----------
class ChatQuestion(BaseModel):
    session_id: int
    question: str = Field(min_length=1, max_length=1000)


# ---------- Messages ----------
class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    sender: ChatMessageSender
    message: str
    model_name: str | None = None
    response_time_ms: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------- Citations (built in the router from citations + chunks + files) ----------
class CitationResponse(BaseModel):
    chunk_id: int
    score: float
    rank: int
    file_name: str
    page_number: int | None = None
    start_time: float | None = None
    content: str


# ---------- Nested responses ----------
class ChatAnswerResponse(BaseModel):
    question: ChatMessageResponse
    answer: ChatMessageResponse
    citations: list[CitationResponse] = []


class ChatSessionDetail(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: list[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)