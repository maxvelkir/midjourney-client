from typing import List, Optional

from pydantic import BaseModel


class URL(BaseModel):
    url: str


class Image(BaseModel):
    hash: str
    idea_id: int
    image_prompt: str
    midjourney_image_url: Optional[str] = None
    is_generated: Optional[bool] = False
    urls: Optional[List[str]] = None


# Responses


class ErrorResponse(BaseModel):
    error: str
