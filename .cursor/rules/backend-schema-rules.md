# FastAPI Schema Design Guidelines for AI Agent Code

## Directory Structure

```
schemas/
├── common/
│   └── base.py           # Cross-functional base models
├── code_completion/
│   ├── base.py           # Base models for code completion feature
│   ├── requests.py       # Request schemas for API endpoints
│   ├── responses.py      # Response schemas for API endpoints
│   └── domain.py         # Domain models for service layer
└── other_features/
    ├── base.py
    ├── requests.py
    ├── responses.py
    └── domain.py
```

## Schema Design Principles

### 1. Base Models

Define base models that can be inherited by both request/response schemas and domain models.

```python
# schemas/code_completion/base.py
from pydantic import BaseModel, Field
from typing import Optional, List

class CompletionBase(BaseModel):
    """Base class for code completion schemas"""
    code_snippet: str = Field(..., description="Code snippet for completion")
    language: str = Field(..., description="Programming language")
    context: Optional[str] = Field(None, description="Additional context for completion")
```

### 2. Request Schemas (API Layer)

Request schemas should focus on validation rules and API documentation.

```python
# schemas/code_completion/requests.py
from .base import CompletionBase
from pydantic import Field, validator
from typing import Optional, List

class GenerateCompletionRequest(CompletionBase):
    max_tokens: int = Field(50, description="Maximum number of tokens to generate")
    temperature: float = Field(0.7, description="Sampling temperature")
    
    @validator('temperature')
    def validate_temperature(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Temperature must be between 0 and 1')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code_snippet": "def calculate_sum(a, b):\n    ",
                "language": "python",
                "context": "This function adds two numbers",
                "max_tokens": 30,
                "temperature": 0.5
            }
        }

class RefineCompletionRequest(CompletionBase):
    previous_completion: str = Field(..., description="Previous completion to refine")
    feedback: str = Field(..., description="User feedback for refinement")
    
    class Config:
        schema_extra = {
            "example": {
                "code_snippet": "def calculate_sum(a, b):\n    return a + b",
                "language": "python",
                "context": "This function adds two numbers",
                "previous_completion": "return a + b",
                "feedback": "Add type hints"
            }
        }
```

### 3. Domain Models (Service Layer)

Domain models represent the business entities and contain business logic constraints.

```python
# schemas/code_completion/domain.py
from .base import CompletionBase
from typing import Optional, List, Dict
from pydantic import Field

class CompletionCreate(CompletionBase):
    max_tokens: int = 50
    temperature: float = 0.7
    user_id: str
    session_id: Optional[str] = None
    model_parameters: Optional[Dict] = None
    
class CompletionRefine(CompletionBase):
    previous_completion: str
    feedback: str
    user_id: str
    session_id: Optional[str] = None
```

### 4. Response Schemas

Response schemas define what's returned to the client.

```python
# schemas/code_completion/responses.py
from .base import CompletionBase
from typing import List, Optional
from datetime import datetime
from pydantic import Field

class CompletionResponse(BaseModel):
    completion: str = Field(..., description="Generated code completion")
    language: str
    created_at: datetime
    tokens_used: int
    model_used: str
    alternatives: Optional[List[str]] = None
    
class CompletionHistoryResponse(BaseModel):
    items: List[CompletionResponse]
    count: int = Field(..., description="Total number of completions")
```

## Usage Guidelines

### In API Routes (Endpoints)

```python
from schemas.code_completion.requests import GenerateCompletionRequest
from schemas.code_completion.domain import CompletionCreate
from fastapi import Depends, HTTPException

@router.post("/completions/generate/", response_model=CompletionResponse)
def generate_completion(
    completion_data: GenerateCompletionRequest,
    current_user = Depends(get_current_user)
):
    # Convert API schema to domain model
    completion_create = CompletionCreate(
        **completion_data.dict(),
        user_id=current_user.id
    )
    return completion_service.generate(completion_create)
```

### In Service Layer

```python
from schemas.code_completion.domain import CompletionCreate, CompletionRefine

def generate(completion_data: CompletionCreate) -> CompletionResponse:
    # Service uses domain models
    # Business logic here
    return repository.create_completion(completion_data)
```

## Best Practices

1. **Single Responsibility**: Each schema class should have a single purpose
2. **Inheritance over Composition**: Use inheritance to reduce code duplication
3. **Separation of Concerns**: Keep API validation separate from business logic
4. **Documentation**: Include examples and descriptions in request schemas
5. **Validation**: Put API-specific validation in request schemas
6. **Business Rules**: Put business logic validation in domain models
7. **Type Safety**: Use proper type annotations throughout all schemas

By following these guidelines, your AI code agent backend will maintain a clean separation between API concerns and business logic, allowing each layer to evolve independently while minimizing code duplication.