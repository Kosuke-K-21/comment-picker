from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CommentBase(BaseModel):
    comment_text: str
    uploader_id: Optional[str] = None # Optional: ID of the person who uploaded

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    uploaded_at: datetime
    sentiment: Optional[str] = None # e.g., "positive", "negative", "neutral"
    category: Optional[str] = None # e.g., "lecture_content", "materials", "operations", "other"
    is_critical: Optional[bool] = False
    importance_score: Optional[float] = None

    class Config:
        orm_mode = True # For SQLAlchemy compatibility, will be renamed to from_attributes in Pydantic v2

class CommentUploadResponse(BaseModel):
    message: str
    total_comments_received: int
    # successful_imports: int # Could add more detail later
    # failed_imports: int      # Could add more detail later
