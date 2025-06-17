import pandas as pd
import io
import random
import os
import asyncio
import json
from typing import List, Dict, Any, Optional
from enum import Enum
from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.bedrock import BedrockConverseModel, BedrockModelSettings
import dotenv


# Load environment variables
dotenv.load_dotenv()


class SentimentEnum(str, Enum):
    POSITIVE = 'ポジティブ'
    NEUTRAL = '中立'
    NEGATIVE = 'ネガティブ'


class CategoryEnum(str, Enum):
    LECTURE_CONTENT = '講義内容'
    LECTURE_MATERIAL = '講義資料'
    OPERATION = '運営'
    OTHER = 'その他'


class ImportanceEnum(str, Enum):
    HIGH = '高'
    MEDIUM = '中'
    LOW = '低'


class CommonalityEnum(str, Enum):
    HIGH = '高'
    MEDIUM = '中'
    LOW = '低'


class EvalOutput(BaseModel):
    sentiment: SentimentEnum = Field(description="コメントに対する感情の分類")
    category: CategoryEnum = Field(description="コメントに対するカテゴリの分類")
    importance: ImportanceEnum = Field(description="コメントに対する重要度の分類")
    commonality: CommonalityEnum = Field(description="コメントに対する共通性の分類")


def generate_agent(
    model_id: str,
    output_type: Optional[BaseModel] = None,
    retries: int = 5,
    temperature: float = 0.2,
    max_tokens: int = 20000,
    timeout: int = 60,
) -> Agent:
    """Generate a Bedrock agent with specified settings"""
    model = BedrockConverseModel(model_name=model_id)

    model_settings = BedrockModelSettings(
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=timeout,
    )

    agent = Agent(
        model,
        retries=retries,
        output_type=output_type or str,
        model_settings=model_settings,
        system_prompt="""
        あなたは講義に関するフィードバックを分析するAIアシスタントです。
        以下のルールに従って、コメントを分類してください。
        1. コメントの感情を分類してください。
        2. コメントのカテゴリを分類してください。
        3. コメントの重要度を分類してください。
        4. コメントの共通性を分類してください。
        
        各分類は以下の選択肢から選んでください。
        
        感情: ポジティブ, 中立, ネガティブ
        カテゴリ: 講義内容, 講義資料, 運営, その他
        重要度: 高, 中, 低
        共通性: 高, 中, 低
        """
    )

    return agent


def calculate_cost(
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    think_tokens: Optional[int] = None,
) -> tuple[float, float, float]:
    """
    Calculate the total cost based on input, output, and think tokens.
    """
    if think_tokens is None:
        think_tokens = 0

    if "gemini-2.0-flash" in model_name:
        input_cost_per_mil_token = 0.15
        output_cost_per_mil_token = 0.60

    elif "gemini-2.5-flash" in model_name:
        input_cost_per_mil_token = 0.15
        if think_tokens == 0:
            output_cost_per_mil_token = 0.60
        else:
            output_cost_per_mil_token = 3.5
    
    elif "amazon.nova-lite-v1:0" in model_name:
        input_cost_per_mil_token = 0.00006 * 1000  # Convert to per million tokens
        output_cost_per_mil_token = 0.00024 * 1000  # Convert to per million tokens
    
    elif "amazon.nova-pro-v1:0" in model_name:
        input_cost_per_mil_token = 0.0008 * 1000
        output_cost_per_mil_token = 0.0032 * 1000

    else:
        raise ValueError(f"Unsupported model name: {model_name}")

    input_cost = input_tokens * input_cost_per_mil_token * 1e-6
    output_cost = output_tokens * output_cost_per_mil_token * 1e-6
    think_cost = think_tokens * output_cost_per_mil_token * 1e-6

    return input_cost, output_cost, think_cost


async def analyze_comment_with_llm(comment: str) -> Dict[str, Any]:
    """Analyze a single comment using Bedrock Nova-lite LLM"""
    try:
        await asyncio.sleep(0.5)  # Rate limiting
        
        model_id = "amazon.nova-lite-v1:0"
        agent = generate_agent(
            model_id=model_id,
            output_type=EvalOutput,
            retries=3,
            temperature=0.2,
            max_tokens=2000,
            timeout=60,
        )

        response = await agent.run([comment])
        output = response.output

        # Calculate cost
        input_tokens = response.usage().request_tokens
        output_tokens = response.usage().response_tokens
        total_tokens = response.usage().total_tokens
        think_tokens = total_tokens - input_tokens - output_tokens

        input_cost, output_cost, think_cost = calculate_cost(
            model_name=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            think_tokens=think_tokens,
        )
        total_cost = input_cost + output_cost + think_cost

        return {
            "sentiment": output.sentiment.value,
            "category": output.category.value,
            "importance": output.importance.value,
            "commonality": output.commonality.value,
            "total_cost": total_cost,
            "is_error": False,
        }
    except Exception as e:
        print(f"Error analyzing comment: {e}")
        return {
            "sentiment": None,
            "category": None,
            "importance": None,
            "commonality": None,
            "total_cost": 0.0,
            "is_error": True,
        }


class CSVService:
    def __init__(self):
        self.csv_data: pd.DataFrame = pd.DataFrame()
        self.filename: str = ""
        self.analyzed: bool = False
    
    async def upload_csv(self, file: UploadFile) -> Dict[str, Any]:
        """Upload and parse Excel/CSV file"""
        if file.filename is None:
            raise HTTPException(status_code=400, detail="No filename provided")
            
        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            raise HTTPException(status_code=400, detail="File must be a CSV or Excel file")
        
        try:
            # Read the file content
            content = await file.read()
            
            # Parse file using pandas
            if file.filename.endswith('.xlsx'):
                # Parse Excel file
                self.csv_data = pd.read_excel(io.BytesIO(content))
            else:
                # Parse CSV file
                csv_string = content.decode('utf-8')
                self.csv_data = pd.read_csv(io.StringIO(csv_string))
            
            self.filename = file.filename
            self.analyzed = False
            
            # Filter to show only comment columns
            comment_columns = [col for col in self.csv_data.columns if "必須" in col or "任意" in col]
            
            return {
                "filename": self.filename,
                "total_rows": len(self.csv_data),
                "columns": list(self.csv_data.columns),
                "comment_columns": comment_columns,
                "message": f"{'Excel' if file.filename.endswith('.xlsx') else 'CSV'} uploaded successfully"
            }
        
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error processing file: {str(e)}")
    
    def get_paginated_data(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """Get paginated data showing only comment columns"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
        
        # Get comment columns
        comment_columns = [col for col in self.csv_data.columns if "必須" in col or "任意" in col]
        
        # Include analysis columns if analyzed - put them at the beginning
        display_columns = []
        if self.analyzed:
            display_columns.extend(['感情', 'カテゴリ', '重要性', '共通性'])
        display_columns.extend(comment_columns)
        
        # Calculate pagination
        total_rows = len(self.csv_data)
        total_pages = (total_rows + page_size - 1) // page_size
        
        if page < 1 or page > total_pages:
            raise HTTPException(status_code=400, detail=f"Page must be between 1 and {total_pages}")
        
        # Get the data for the current page, only display columns
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = self.csv_data[display_columns].iloc[start_idx:end_idx]
        
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
            "columns": display_columns,
            "comment_columns": comment_columns
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
    
    async def analyze_comments(self) -> Dict[str, Any]:
        """Analyze comments using Bedrock Nova-lite LLM"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No CSV data available. Please upload a file first.")
        
        if self.analyzed:
            return {
                "message": "File has already been analyzed",
                "total_rows": len(self.csv_data),
                "analyzed": True
            }
        
        try:
            # Find comment columns - Excel has 6 comment columns
            comment_columns = [col for col in self.csv_data.columns if "必須" in col or "任意" in col]
            
            if not comment_columns:
                raise HTTPException(status_code=400, detail="No comment columns found. Expected columns with '必須' or '任意'")
            
            # Combine all comment columns into JSON format for each row
            comments = self.csv_data[comment_columns].apply(
                lambda row: json.dumps(row.dropna().to_dict(), ensure_ascii=False), axis=1
            ).tolist()
            
            # Create tasks for LLM analysis
            tasks = [analyze_comment_with_llm(comment) for comment in comments]
            
            # Process with semaphore for rate limiting
            semaphore = asyncio.Semaphore(500)  # Limit concurrent requests
            
            async def process_with_semaphore(task):
                async with semaphore:
                    return await task
            
            # Execute all tasks
            results = await asyncio.gather(*[process_with_semaphore(task) for task in tasks], return_exceptions=True)
            
            # Process results
            processed_results = []
            error_count = 0
            total_cost = 0.0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"Error processing comment {i}: {result}")
                    processed_results.append({
                        "sentiment": "中立",  # Default fallback
                        "category": "その他",
                        "importance": "中",
                        "commonality": "中",
                        "total_cost": 0.0,
                        "is_error": True,
                    })
                    error_count += 1
                else:
                    if result.get("is_error", False):
                        # Use fallback values for errors
                        processed_results.append({
                            "sentiment": "中立",
                            "category": "その他", 
                            "importance": "中",
                            "commonality": "中",
                            "total_cost": 0.0,
                            "is_error": True,
                        })
                        error_count += 1
                    else:
                        processed_results.append(result)
                        total_cost += result.get("total_cost", 0.0)
            
            # Add analysis columns to DataFrame
            self.csv_data['感情'] = [r['sentiment'] for r in processed_results]
            self.csv_data['カテゴリ'] = [r['category'] for r in processed_results]
            self.csv_data['重要性'] = [r['importance'] for r in processed_results]
            self.csv_data['共通性'] = [r['commonality'] for r in processed_results]
            
            self.analyzed = True
            
            # Check for dangerous comments (ネガティブ + 重要性高)
            dangerous_comments = self.csv_data[
                (self.csv_data['感情'] == 'ネガティブ') & 
                (self.csv_data['重要性'] == '高')
            ]
            
            dangerous_list = []
            if not dangerous_comments.empty:
                for _, row in dangerous_comments.iterrows():
                    # Use index as ID and combine comment columns
                    comment_id = row.name
                    comment_dict = row[comment_columns].dropna().to_dict()
                    comment_text = json.dumps(comment_dict, ensure_ascii=False)
                    dangerous_list.append({
                        "id": str(comment_id),
                        "comment": comment_text
                    })
            
            return {
                "message": "Analysis completed successfully",
                "total_rows": len(self.csv_data),
                "analyzed": True,
                "new_columns": ['感情', 'カテゴリ', '重要性', '共通性'],
                "dangerous_comments": dangerous_list,
                "error_rate": f"{error_count / len(self.csv_data):.2%}" if len(self.csv_data) > 0 else "0%",
                "comment_columns": comment_columns,
                "total_cost": round(total_cost, 4),
                "cost_display": f"${total_cost:.4f}"
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
            raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
        
        if not self.analyzed:
            raise HTTPException(status_code=400, detail="File has not been analyzed yet. Please analyze first.")
        
        try:
            # Find comment columns
            comment_columns = [col for col in self.csv_data.columns if "必須" in col or "任意" in col]
            
            if not comment_columns:
                raise HTTPException(status_code=400, detail="No comment columns found. Expected columns with '必須' or '任意'")
            
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
                # Use index as ID and combine comment columns
                comment_id = row.name
                comment_dict = row[comment_columns].dropna().to_dict()
                comment_text = json.dumps(comment_dict, ensure_ascii=False)
                overall_comments.append({
                    "id": str(comment_id),
                    "comment": comment_text,
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
                    # Use index as ID and combine comment columns
                    comment_id = row.name
                    comment_dict = row[comment_columns].dropna().to_dict()
                    comment_text = json.dumps(comment_dict, ensure_ascii=False)
                    category_comments.append({
                        "id": str(comment_id),
                        "comment": comment_text,
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


    async def generate_comment_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report from top 50 comments using Nova Pro"""
        if self.csv_data.empty:
            raise HTTPException(status_code=404, detail="No data available. Please upload a file first.")
        
        if not self.analyzed:
            raise HTTPException(status_code=400, detail="File has not been analyzed yet. Please analyze first.")
        
        try:
            # Find comment columns
            comment_columns = [col for col in self.csv_data.columns if "必須" in col or "任意" in col]
            
            if not comment_columns:
                raise HTTPException(status_code=400, detail="No comment columns found.")
            
            # Get top 50 comments based on importance and commonality score
            importance_map = {'高': 3, '中': 2, '低': 1}
            commonality_map = {'高': 3, '中': 2, '低': 1}
            
            df_with_score = self.csv_data.copy()
            df_with_score['importance_score'] = df_with_score['重要性'].map(importance_map)
            df_with_score['commonality_score'] = df_with_score['共通性'].map(commonality_map)
            df_with_score['total_score'] = df_with_score['importance_score'] * df_with_score['commonality_score']
            
            # Get top 50 comments
            top_50 = df_with_score.nlargest(50, 'total_score')
            
            # Prepare comments for analysis
            comments_for_analysis = []
            for _, row in top_50.iterrows():
                comment_dict = row[comment_columns].dropna().to_dict()
                comment_text = json.dumps(comment_dict, ensure_ascii=False)
                comments_for_analysis.append({
                    "comment": comment_text,
                    "sentiment": row['感情'],
                    "category": row['カテゴリ'],
                    "importance": row['重要性'],
                    "commonality": row['共通性']
                })
            
            # Separate positive and negative comments
            positive_comments = [c for c in comments_for_analysis if c['sentiment'] == 'ポジティブ']
            negative_comments = [c for c in comments_for_analysis if c['sentiment'] == 'ネガティブ']
            
            # Create prompt for Nova Pro
            prompt = f"""
以下は講義に関するフィードバックコメントのトップ50件です。これらのコメントを分析して、包括的なレポートを作成してください。

ポジティブなコメント（{len(positive_comments)}件）:
{chr(10).join([f"- {c['comment']}" for c in positive_comments[:25]])}

ネガティブなコメント（{len(negative_comments)}件）:
{chr(10).join([f"- {c['comment']}" for c in negative_comments[:25]])}

以下の形式でレポートを作成してください：

1. ポジティブな意見のまとめ：
受講者から評価されている点を具体的にまとめてください。共通するテーマや特に評価の高い要素を抽出し、講義の強みを明確にしてください。

2. ネガティブな意見のまとめ：
受講者が改善を求めている点を具体的にまとめてください。共通する課題や問題点を抽出し、優先度の高い改善項目を明確にしてください。

3. 総合的な洞察：
ポジティブとネガティブな意見を総合して、講義全体の評価と今後の改善方向性について洞察を提供してください。具体的な改善提案も含めてください。

各セクションは段落形式で、読みやすく構造化してください。
"""

            # Use Nova Pro for report generation
            model_id = "amazon.nova-pro-v1:0"
            agent = generate_agent(
                model_id=model_id,
                output_type=str,
                retries=3,
                temperature=0.3,
                max_tokens=4000,
                timeout=120,
            )

            response = await agent.run([prompt])
            report_text = response.output

            # Calculate cost
            input_tokens = response.usage().request_tokens
            output_tokens = response.usage().response_tokens
            total_tokens = response.usage().total_tokens
            think_tokens = total_tokens - input_tokens - output_tokens

            input_cost, output_cost, think_cost = calculate_cost(
                model_name=model_id,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                think_tokens=think_tokens,
            )
            total_cost = input_cost + output_cost + think_cost

            # Parse the report into sections
            sections = report_text.split('\n\n')
            
            positive_summary = ""
            negative_summary = ""
            overall_insights = ""
            
            current_section = ""
            for section in sections:
                if "ポジティブな意見" in section or "1." in section:
                    current_section = "positive"
                    positive_summary += section.replace("1. ポジティブな意見のまとめ：", "").strip() + "\n\n"
                elif "ネガティブな意見" in section or "2." in section:
                    current_section = "negative"
                    negative_summary += section.replace("2. ネガティブな意見のまとめ：", "").strip() + "\n\n"
                elif "総合的な洞察" in section or "3." in section:
                    current_section = "insights"
                    overall_insights += section.replace("3. 総合的な洞察：", "").strip() + "\n\n"
                else:
                    if current_section == "positive":
                        positive_summary += section + "\n\n"
                    elif current_section == "negative":
                        negative_summary += section + "\n\n"
                    elif current_section == "insights":
                        overall_insights += section + "\n\n"

            return {
                "positive_summary": positive_summary.strip(),
                "negative_summary": negative_summary.strip(),
                "overall_insights": overall_insights.strip(),
                "total_comments_analyzed": len(comments_for_analysis),
                "positive_count": len(positive_comments),
                "negative_count": len(negative_comments),
                "total_cost": round(total_cost, 4),
                "cost_display": f"${total_cost:.4f}",
                "model_used": "Amazon Nova Pro"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


# Global instance to store CSV data in memory
csv_service = CSVService()
