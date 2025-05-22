from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd
import io
from typing import List

from ..database import get_db
from ..schemas.comment_schemas import Comment, CommentCreate, CommentUploadResponse
from ..models.comment_models import Comment as DBComment # Alias to avoid name collision
from ..services.comment_analysis_service import comment_analysis_service

router = APIRouter()

@router.post("/upload-csv/", response_model=CommentUploadResponse)
async def upload_comments_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only CSV files are allowed."
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Validate required columns
        required_columns = ["comment_text"] # Assuming 'comment_text' is the primary column
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns in CSV. Expected: {', '.join(required_columns)}"
            )

        comments_to_create = []
        for index, row in df.iterrows():
            comment_data = CommentCreate(
                comment_text=row["comment_text"],
                uploader_id=row["uploader_id"] if "uploader_id" in row else None
            )
            comments_to_create.append(comment_data)

        # Save comments to database and analyze
        total_comments_received = 0
        for comment_data in comments_to_create:
            analysis_results = comment_analysis_service.analyze_comment(comment_data.comment_text)
            
            db_comment = DBComment( # Use the aliased DBComment
                comment_text=comment_data.comment_text,
                uploader_id=comment_data.uploader_id,
                sentiment=analysis_results.get("sentiment"),
                category=analysis_results.get("category")
            )
            db.add(db_comment)
            total_comments_received += 1
        db.commit()

        return CommentUploadResponse( # Use the directly imported CommentUploadResponse
            message=f"Successfully uploaded {total_comments_received} comments.",
            total_comments_received=total_comments_received
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process CSV file: {e}"
        )

@router.get("/", response_model=List[Comment])
def get_all_comments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    comments = db.query(DBComment).offset(skip).limit(limit).all() # Use the aliased DBComment
    return comments
