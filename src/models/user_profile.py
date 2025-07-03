from pydantic import BaseModel
from typing import List, Dict

class UserProfile(BaseModel):
    user_id: str
    professional_interests: List[str]
    personal_interests: List[str]
    expertise_level: Dict[str, int]  # e.g., {"python": 8, "machine_learning": 6}
    preferred_content_types: List[str] # e.g., "article", "video", "tutorial"
    ignored_topics: List[str]
