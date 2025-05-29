from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from typing import Dict, Any
from ..services.csv_service import csv_service

router = APIRouter(prefix="/csv", tags=["csv"])


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a CSV file"""
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
