
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.schemas.node.base import NodeBase
class GenerateImageResponse(NodeBase):
    id: int