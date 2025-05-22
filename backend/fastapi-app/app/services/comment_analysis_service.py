from .bedrock_service import bedrock_service
from typing import Dict, Any

class CommentAnalysisService:
    def __init__(self):
        self.bedrock = bedrock_service

    def analyze_sentiment(self, comment_text: str) -> str:
        prompt = f"""Human: Analyze the sentiment of the following comment. Respond with only "positive", "negative", or "neutral".

Comment: "{comment_text}"

Assistant:"""
        response = self.bedrock.invoke_model(prompt, max_tokens=10, temperature=0.1)
        return response.strip().lower()

    def classify_category(self, comment_text: str) -> str:
        categories = ["講義内容 (lecture_content)", "講義資料 (materials)", "運営 (operations)", "その他 (other)"]
        prompt = f"""Human: Classify the following comment into one of these categories: {', '.join(categories)}. Respond with only the category name in English (e.g., "lecture_content").

Comment: "{comment_text}"

Assistant:"""
        response = self.bedrock.invoke_model(prompt, max_tokens=20, temperature=0.1)
        # Simple parsing, might need more robust handling for unexpected responses
        for cat in categories:
            if cat.split(' ')[0].lower() in response.strip().lower():
                return cat.split(' ')[1].strip('()')
        return "other" # Default to other if classification fails

    def analyze_comment(self, comment_text: str) -> Dict[str, Any]:
        sentiment = self.analyze_sentiment(comment_text)
        category = self.classify_category(comment_text)
        return {
            "sentiment": sentiment,
            "category": category
        }

comment_analysis_service = CommentAnalysisService()
