from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.sql import func
from ..database import Base

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment_text = Column(String, nullable=False)
    uploader_id = Column(String, index=True, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    # Analysis results - will be populated in later phases
    sentiment = Column(String, nullable=True) # e.g., "positive", "negative", "neutral"
    category = Column(String, nullable=True) # e.g., "lecture_content", "materials", "operations", "other"
    is_critical = Column(Boolean, default=False)
    importance_score = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Comment(id={self.id}, text='{self.comment_text[:30]}...')>"
