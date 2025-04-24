from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas.node.base import NodeBase

# Schema for node request
class NodeRequest(NodeBase):
    id: int
    parent_id: Optional[int] = None
    image_base64: str
    image_path: Optional[str] = None
    request_params: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = {
        "from_attributes": True
    }

# Schema for node create request
class NodeCreateRequest(NodeBase):
    request_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "prompt": "A beautiful landscape",
                "negative_prompt": "blurry, low quality",
                "spec_json": {"width": 512, "height": 512},
                "action_type": "generate",
                "parent_id": 1,
                "request_params": {"seed": 42},
                "is_root": False,
                "image_base64": "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="
            }
        }
    }

# Schema for lineage request
class NodeLineageRequest(BaseModel):
    node_id: int = Field(..., description="ID of the node to get lineage for")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "node_id": 1
            }
        }
    }

# Schema for root request
class RootNodesRequest(BaseModel):
    page: int = Field(1, description="Page number")
    page_size: int = Field(10, description="Number of items per page")
    
    @validator('page')
    def validate_page(cls, v):
        if v < 1:
            raise ValueError('Page must be greater than 0')
        return v
        
    @validator('page_size')
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Page size must be between 1 and 100')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "page": 1,
                "page_size": 10
                }
            }      
        }
