from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import io
from ..services.csv_service import csv_service

router = APIRouter(prefix="/csv", tags=["csv"])


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a CSV or Excel file"""
    return await csv_service.upload_csv(file)


@router.get("/data")
async def get_csv_data(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of rows per page")
) -> Dict[str, Any]:
    """Get paginated CSV data"""
    return csv_service.get_paginated_data(page=page, page_size=page_size)


@router.get("/info")
async def get_csv_info() -> Dict[str, Any]:
    """Get information about the uploaded CSV"""
    return csv_service.get_csv_info()


@router.post("/analyze")
async def analyze_csv() -> Dict[str, Any]:
    """Analyze the uploaded CSV comments"""
    return await csv_service.analyze_comments()


@router.get("/download")
async def download_analyzed_csv():
    """Download the analyzed CSV file"""
    return csv_service.download_analyzed_csv()


@router.get("/statistics")
async def get_analysis_statistics() -> Dict[str, Any]:
    """Get analysis statistics for visualization"""
    return csv_service.get_analysis_statistics()


@router.get("/top-comments")
async def get_top_comments(
    max_count: int = Query(5, ge=1, le=10, description="Maximum number of top comments to return")
) -> Dict[str, Any]:
    """Get top comments based on importance and commonality score"""
    return csv_service.get_top_comments(max_count=max_count)


@router.post("/generate-report")
async def generate_comment_report() -> Dict[str, Any]:
    """Generate a comprehensive report from top 50 comments using Nova Pro"""
    return await csv_service.generate_comment_report()
