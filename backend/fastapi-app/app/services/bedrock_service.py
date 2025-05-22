import boto3
import json
from botocore.exceptions import ClientError
from ..config import settings

class BedrockService:
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=settings.BEDROCK_REGION
        )
        self.model_id = settings.BEDROCK_MODEL_ID

    def invoke_model(self, prompt: str, max_tokens: int = 500, temperature: float = 0.5) -> str:
        body = json.dumps({
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": temperature,
        })

        try:
            response = self.client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept='application/json',
                contentType='application/json'
            )
            response_body = json.loads(response.get('body').read())
            return response_body.get('completion')
        except ClientError as e:
            print(f"Error invoking Bedrock model: {e}")
            raise

# Initialize the service
bedrock_service = BedrockService()
