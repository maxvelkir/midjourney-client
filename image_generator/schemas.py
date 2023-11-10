from typing import List, Optional

from pydantic import BaseModel


class URL(BaseModel):
    url: str


class GenImage(BaseModel):
    product_id: int
    hash: str
    image_prompt: str
    midjourney_image_url: Optional[str] = None
    is_generated: Optional[bool] = False
    urls: Optional[List[str]] = None


# Responses


class ErrorResponse(BaseModel):
    error: str
