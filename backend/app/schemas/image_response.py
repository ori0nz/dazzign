from pydantic import BaseModel, Field
from typing import List
from app.schemas.image_base import ImageNode
from app.schemas.design_attributes import PCCaseAttributes

# Schema for text-to-image response
class TextToImageResponse(BaseModel):
    prompt: str
    attributes: PCCaseAttributes
    structured_prompt: str

# Schema for lineage response
class ImageLineage(BaseModel):
    ancestors: List[ImageNode] = Field(default_factory=list)
    descendants: List[ImageNode] = Field(default_factory=list)
    
# Schema for root images response
class RootImages(BaseModel):
    images: List[ImageNode] = Field(default_factory=list)
    total: int
    page: int
    page_size: int 