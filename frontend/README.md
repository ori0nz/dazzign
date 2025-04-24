# ImageFlow - Image Generation and Management System

A React-based web application for AI image generation with version control and lineage tracking capabilities.

## Project Structure

```
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── image/           # Image-related components
│   │   ├── lineage/         # Lineage tree visualization
│   │   ├── prompt/          # Prompt input components
│   │   └── ui/              # Basic UI components
│   ├── pages/               # Page components
│   ├── services/            # API and business logic
│   ├── models/              # TypeScript types/interfaces
│   └── data/                # Mock data and constants
├── public/                  # Static assets
└── api/                     # Python backend API
    ├── main.py             # FastAPI application
    ├── models/             # Database models
    └── routers/            # API route handlers
```

## API Integration Guide

### 1. Backend Setup

Create a new `api` directory and install FastAPI:

```bash
mkdir api
cd api
pip install fastapi uvicorn sqlalchemy python-dotenv
```

### 2. API Structure

Create the following files in the `api` directory:

```python
# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers here
from routers import images

app.include_router(images.router, prefix="/api")
```

```python
# api/models/image.py
from sqlalchemy import Boolean, Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class ImageNode(Base):
    __tablename__ = "image_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    is_root = Column(Boolean, nullable=False)
    parent_id = Column(Integer, ForeignKey("image_nodes.id"), nullable=True)
    prompt = Column(String, nullable=False)
    negative_prompt = Column(String)
    spec_json = Column(JSON, nullable=False)
    request_params = Column(JSON, nullable=False)
    image_path = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

```python
# api/routers/images.py
from fastapi import APIRouter, HTTPException
from typing import List
from models.image import ImageNode

router = APIRouter()

@router.get("/images/{image_id}")
async def get_image(image_id: int):
    # Implementation here
    pass

@router.post("/images/generate")
async def generate_image(prompt: str, spec_json: dict, parent_id: int = None):
    # Implementation here
    pass

@router.get("/images/{image_id}/lineage")
async def get_image_lineage(image_id: int):
    # Implementation here
    pass
```

### 3. Frontend Integration

Update the image service to use the API: