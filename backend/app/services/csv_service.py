import pandas as pd
import io
import random
from typing import List, Dict, Any
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse


class CSVService:
    def __init__(self):
        self.csv_data: pd.DataFrame = pd.DataFrame()
        self.filename: str = ""
        self.analyzed: bool = False
    
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
            self.analyzed = False
            
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
            "sample_data": self.csv_data.head(3).to_dict('records'),
            "analyzed": self.analyzed
        }
    
    def analyze_comments(self) -> Dict[str, Any]:
        """Analyze comments using LLM (currently using random values)"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No CSV data available. Please upload a CSV file first.")
        
        if self.analyzed:
            return {
                "message": "CSV has already been analyzed",
                "total_rows": len(self.csv_data),
                "analyzed": True
            }
        
        try:
            # Check if required columns exist
            required_columns = ['コメントID', '受講生ID', 'コメント']
            missing_columns = [col for col in required_columns if col not in self.csv_data.columns]
            
            if missing_columns:
                # Try alternative column names
                alt_mapping = {
                    'コメントID': ['comment_id', 'id', 'Comment ID'],
                    '受講生ID': ['student_id', 'user_id', 'Student ID'],
                    'コメント': ['comment', 'comments', 'Comment']
                }
                
                for missing_col in missing_columns:
                    found = False
                    for alt_col in alt_mapping.get(missing_col, []):
                        if alt_col in self.csv_data.columns:
                            self.csv_data = self.csv_data.rename(columns={alt_col: missing_col})
                            found = True
                            break
                    if not found:
                        raise HTTPException(
                            status_code=400, 
                            detail=f"Required column '{missing_col}' not found. Expected columns: {required_columns}"
                        )
            
            # Add analysis columns with random values (placeholder for LLM)
            sentiment_options = ['ポジティブ', '中立', 'ネガティブ']
            category_options = ['講義内容', '講義資料', '運営', 'その他']
            importance_options = ['高', '中', '低']
            commonality_options = ['高', '中', '低']
            
            self.csv_data['感情'] = [random.choice(sentiment_options) for _ in range(len(self.csv_data))]
            self.csv_data['カテゴリ'] = [random.choice(category_options) for _ in range(len(self.csv_data))]
            self.csv_data['重要性'] = [random.choice(importance_options) for _ in range(len(self.csv_data))]
            self.csv_data['共通性'] = [random.choice(commonality_options) for _ in range(len(self.csv_data))]
            
            self.analyzed = True
            
            # Check for dangerous comments (ネガティブ + 重要性高)
            dangerous_comments = self.csv_data[
                (self.csv_data['感情'] == 'ネガティブ') & 
                (self.csv_data['重要性'] == '高')
            ]
            
            dangerous_list = []
            if not dangerous_comments.empty:
                for _, row in dangerous_comments.iterrows():
                    comment_id = row.get('コメントID', row.get('comment_id', row.get('id', 'N/A')))
                    comment_text = row.get('コメント', row.get('comment', row.get('comments', 'N/A')))
                    dangerous_list.append({
                        "id": str(comment_id),
                        "comment": str(comment_text)
                    })
            
            return {
                "message": "CSV analysis completed successfully",
                "total_rows": len(self.csv_data),
                "analyzed": True,
                "new_columns": ['感情', 'カテゴリ', '重要性', '共通性'],
                "dangerous_comments": dangerous_list
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error during analysis: {str(e)}")
    
    def download_analyzed_csv(self) -> StreamingResponse:
        """Download the analyzed CSV file"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No CSV data available. Please upload a CSV file first.")
        
        if not self.analyzed:
            raise HTTPException(status_code=400, detail="CSV has not been analyzed yet. Please analyze the CSV first.")
        
        try:
            # Convert DataFrame to CSV string
            csv_buffer = io.StringIO()
            self.csv_data.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_content = csv_buffer.getvalue()
            
            # Create a BytesIO object for the response
            csv_bytes = io.BytesIO(csv_content.encode('utf-8'))
            
            # Generate filename with timestamp
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"analyzed_{self.filename.replace('.csv', '')}_{timestamp}.csv"
            
            return StreamingResponse(
                io.BytesIO(csv_content.encode('utf-8')),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating CSV download: {str(e)}")
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """Get analysis statistics for visualization"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No CSV data available. Please upload a CSV file first.")
        
        if not self.analyzed:
            raise HTTPException(status_code=400, detail="CSV has not been analyzed yet. Please analyze the CSV first.")
        
        try:
            # Category statistics
            category_counts = self.csv_data['カテゴリ'].value_counts().to_dict()
            total_comments = len(self.csv_data)
            
            category_stats = []
            for category, count in category_counts.items():
                percentage = round((count / total_comments) * 100, 1)
                category_stats.append({
                    "category": category,
                    "count": int(count),
                    "percentage": percentage
                })
            
            # Sentiment statistics overall
            sentiment_counts = self.csv_data['感情'].value_counts().to_dict()
            overall_sentiment = {
                "positive": sentiment_counts.get('ポジティブ', 0),
                "neutral": sentiment_counts.get('中立', 0),
                "negative": sentiment_counts.get('ネガティブ', 0),
                "positive_percentage": round((sentiment_counts.get('ポジティブ', 0) / total_comments) * 100, 1),
                "neutral_percentage": round((sentiment_counts.get('中立', 0) / total_comments) * 100, 1),
                "negative_percentage": round((sentiment_counts.get('ネガティブ', 0) / total_comments) * 100, 1)
            }
            
            # Sentiment statistics by category
            category_sentiment_stats = []
            for category in category_counts.keys():
                category_data = self.csv_data[self.csv_data['カテゴリ'] == category]
                category_sentiment_counts = category_data['感情'].value_counts().to_dict()
                category_total = len(category_data)
                
                positive_count = category_sentiment_counts.get('ポジティブ', 0)
                neutral_count = category_sentiment_counts.get('中立', 0)
                negative_count = category_sentiment_counts.get('ネガティブ', 0)
                
                category_sentiment_stats.append({
                    "category": category,
                    "positive": int(positive_count),
                    "neutral": int(neutral_count),
                    "negative": int(negative_count),
                    "positive_percentage": round((positive_count / category_total) * 100, 1) if category_total > 0 else 0,
                    "neutral_percentage": round((neutral_count / category_total) * 100, 1) if category_total > 0 else 0,
                    "negative_percentage": round((negative_count / category_total) * 100, 1) if category_total > 0 else 0,
                    "total": category_total
                })
            
            return {
                "total_comments": total_comments,
                "category_statistics": category_stats,
                "overall_sentiment": overall_sentiment,
                "category_sentiment_statistics": category_sentiment_stats
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating statistics: {str(e)}")
    
    def get_top_comments(self, max_count: int = 5) -> Dict[str, Any]:
        """Get top comments based on commonality and importance score"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No CSV data available. Please upload a CSV file first.")
        
        if not self.analyzed:
            raise HTTPException(status_code=400, detail="CSV has not been analyzed yet. Please analyze the CSV first.")
        
        try:
            # Convert importance and commonality to numeric scores
            importance_map = {'高': 3, '中': 2, '低': 1}
            commonality_map = {'高': 3, '中': 2, '低': 1}
            
            # Calculate score for each comment
            df_with_score = self.csv_data.copy()
            df_with_score['importance_score'] = df_with_score['重要性'].map(importance_map)
            df_with_score['commonality_score'] = df_with_score['共通性'].map(commonality_map)
            df_with_score['total_score'] = df_with_score['importance_score'] * df_with_score['commonality_score']
            
            # Get overall top comments
            overall_top = df_with_score.nlargest(max_count, 'total_score')
            overall_comments = []
            for _, row in overall_top.iterrows():
                comment_id = row.get('コメントID', row.get('comment_id', row.get('id', 'N/A')))
                comment_text = row.get('コメント', row.get('comment', row.get('comments', 'N/A')))
                overall_comments.append({
                    "id": str(comment_id),
                    "comment": str(comment_text),
                    "category": row['カテゴリ'],
                    "sentiment": row['感情'],
                    "importance": row['重要性'],
                    "commonality": row['共通性'],
                    "score": int(row['total_score'])
                })
            
            # Get top comments by category
            category_top_comments = {}
            categories = df_with_score['カテゴリ'].unique()
            
            for category in categories:
                category_data = df_with_score[df_with_score['カテゴリ'] == category]
                category_top = category_data.nlargest(max_count, 'total_score')
                
                category_comments = []
                for _, row in category_top.iterrows():
                    comment_id = row.get('コメントID', row.get('comment_id', row.get('id', 'N/A')))
                    comment_text = row.get('コメント', row.get('comment', row.get('comments', 'N/A')))
                    category_comments.append({
                        "id": str(comment_id),
                        "comment": str(comment_text),
                        "category": row['カテゴリ'],
                        "sentiment": row['感情'],
                        "importance": row['重要性'],
                        "commonality": row['共通性'],
                        "score": int(row['total_score'])
                    })
                
                category_top_comments[category] = category_comments
            
            return {
                "max_count": max_count,
                "overall_top_comments": overall_comments,
                "category_top_comments": category_top_comments
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating top comments: {str(e)}")


# Global instance to store CSV data in memory
csv_service = CSVService()
