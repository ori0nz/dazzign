# Backend Development Rules

## Technology Stack
- **Package Manager**: uv
- **Python Version**: 3.12
- **Framework**: FastAPI
- **Development Server**: Uvicorn
- **Database**: PostgreSQL 17.4
- **Schema Validation**: Pydantic
- **ORM**: SQLAlchemy

## Project Structure
```
/
├── app/
│   ├── main.py                # FastAPI app entry point
│   ├── config.py              # Configuration settings
│   ├── models/                # Database models
│   │   └── image_node.py      # ImageNode model
│   ├── schemas/               # Pydantic schemas
│   │   ├── __init__.py        # Re-exports all schema models
│   │   ├── image_base.py      # Base schemas (ImageNodeBase, ImageNodeCreate, ImageNode)
│   │   ├── image_schemas.py   # Image generation schemas
│   │   ├── node_schemas.py    # Node-related schemas
│   │   ├── text_schemas.py    # Text-related schemas
│   │   └── design_attributes.py # PC case design attributes schema
│   ├── api/                   # API routes
│   │   └── endpoints/
│   │       ├── node_endpoints.py   # Node/DB retrieval endpoints
│   │       ├── image_endpoints.py  # Image generation endpoints
│   │       └── text_endpoints.py   # Text-to-image endpoints
│   ├── db/                    # Database utilities
│   │   ├── session.py         # DB session setup
│   │   └── init_db.py         # DB initialization
│   └── services/              # Business logic
│       ├── __init__.py            # Service exports
│       ├── facade_service.py      # Service facade (for backward compatibility)
│       ├── node_service.py        # Node management service
│       ├── image_generation_service.py # Image generation service
│       └── text_service.py        # Text processing service
├── scripts/                   # Utility scripts
│   └── reset_db.py            # DB reset script
├── tests/                     # Test files
├── .env                       # Environment variables
├── .env.example               # Example environment variables
├── requirements.txt           # Project dependencies
├── docker-compose.yml         # Docker setup
├── Dockerfile.postgres        # PostgreSQL Docker image definition
└── README.md                  # Project documentation
```

## Coding Guidelines
1. Use async/await for database operations and external API calls
2. Follow PEP 8 for code style
3. Use type hints throughout the code
4. Write docstrings for all functions and classes
5. Implement proper error handling with appropriate HTTP status codes
6. Use dependency injection for database sessions
7. Split schema definitions into logical groups for better organization
8. Maintain separation of concerns: node, image, and text operations

## Database Guidelines
1. Use SQLAlchemy as ORM
2. Implement database migrations
3. Use transactions for operations that modify multiple records
4. Store image data as base64 in the database initially, plan for file storage later

## API Design
1. Endpoints are organized by responsibility:
   - **Node endpoints** (prefix: `/node`):
     - GET `/node/:id` - Get single image details
     - GET `/node/:id/lineage` - Get image ancestry and descendants
     - GET `/node/root` - List all root images
   - **Image endpoints** (prefix: `/image`):
     - POST `/image/generate` - Generate new image from prompt
   - **Text endpoints** (prefix: `/text`):
     - POST `/text/text-to-image` - Convert free-form text to structured attributes
2. Use proper request validation with Pydantic models
3. Implement pagination for list endpoints
4. Return appropriate HTTP status codes

## Deployment
1. Use Docker for containerization
2. Use custom Dockerfile for PostgreSQL 17.4
3. Configure Uvicorn for production
4. Set up proper environment variable handling
5. Implement health check endpoint 