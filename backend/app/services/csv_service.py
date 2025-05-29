import pandas as pd
import io
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException


class CSVService:
    def __init__(self):
        self.csv_data: pd.DataFrame = pd.DataFrame()
        self.filename: str = ""
    
    async def upload_csv(self, file: UploadFile) -> Dict[str, Any]:
        """Upload and parse CSV file"""
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV")
        
        try:
            # Read the file content
            content = await file.read()
            
            # Parse CSV using pandas
            csv_string = content.decode('utf-8')
            self.csv_data = pd.read_csv(io.StringIO(csv_string))
            self.filename = file.filename
            
            return {
                "filename": self.filename,
                "total_rows": len(self.csv_data),
                "columns": list(self.csv_data.columns),
                "message": "CSV uploaded successfully"
            }
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")
    
    def get_paginated_data(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated CSV data"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No CSV data available. Please upload a CSV file first.")
        
        # Calculate pagination
        total_rows = len(self.csv_data)
        total_pages = (total_rows + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            raise HTTPException(status_code=400, detail=f"Page must be between 1 and {total_pages}")
        
        # Get the data for the current page
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = self.csv_data.iloc[start_idx:end_idx]
        
        # Convert to list of dictionaries for JSON serialization
        data = page_data.to_dict('records')
        
        return {
            "filename": self.filename,
            "data": data,
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_rows": total_rows,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "columns": list(self.csv_data.columns)
        }
    
    def get_csv_info(self) -> Dict[str, Any]:
        """Get basic information about the uploaded CSV"""
        if self.csv_data.empty:
            return {
                "has_data": False,
                "message": "No CSV data available"
            }
        
        return {
            "has_data": True,
            "filename": self.filename,
            "total_rows": len(self.csv_data),
            "columns": list(self.csv_data.columns),
            "sample_data": self.csv_data.head(3).to_dict('records')
        }


# Global instance to store CSV data in memory
csv_service = CSVService()
