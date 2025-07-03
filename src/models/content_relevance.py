from pydantic import BaseModel, Field
from typing import List

class ContentRelevance(BaseModel):
    relevance_score: int = Field(description="Relevance score from 0-100")
    relevance_categories: List[str] = Field(description="Categories of relevance")
    explanation: str = Field(description="Explanation of the relevance score")
    summary: str = Field(description="A concise summary of the content")
