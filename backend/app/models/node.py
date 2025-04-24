from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Node(Base):
    """
    Node model representing a single generated or edited
    """
    __tablename__ = "nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    is_root = Column(Boolean, nullable=False, default=False)
    parent_id = Column(Integer, ForeignKey("nodes.id"), nullable=True, index=True)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    spec_json = Column(JSONB, nullable=True)
    request_params = Column(JSONB, nullable=True)
    image_base64 = Column(Text, nullable=True)
    image_path = Column(Text, nullable=True)
    action_type = Column(String(20), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    parent = relationship("Node", remote_side=[id], back_populates="children")
    children = relationship("Node", back_populates="parent") 