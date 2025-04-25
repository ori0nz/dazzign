from pydantic import BaseModel
from typing import Optional, List

# Schema for structured design attributes
class PCCaseAttributes(BaseModel):
    color: Optional[List[str]] = None
    style: Optional[List[str]] = None
    shape: Optional[List[str]] = None
    material: Optional[List[str]] = None
    ventilation: Optional[List[str]] = None
    lighting: Optional[List[str]] = None
    features: Optional[List[str]] = None 