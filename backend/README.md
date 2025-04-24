# Dazzign Backend

A FastAPI backend for generating and managing PC case designs.

## 🧩 System Overview

Users can generate PC case design images through text descriptions, with designs stored in a tree structure to maintain the lineage relationships between images.

## 🛠️ Tech Stack

- **Package Manager**: uv
- **Python**: 3.12
- **Framework**: FastAPI
- **Database**: PostgreSQL 17.4
- **ORM**: SQLAlchemy
- **Schema Validation**: Pydantic

## 🚀 Getting Started

### Prerequisites

- Python 3.12
- Docker and Docker Compose
- uv package manager

### Setup Database

#### Using Docker Compose (Recommended)

The easiest way to set up PostgreSQL 17.4 is using Docker Compose:

1. Make sure you have Docker and Docker Compose installed
2. Create a `.env` file from the included `.env` example (or use as is)
3. Run the following command to build and start the container:

```bash
# Navigate to the backend directory
cd backend

# Create virtual environment with Python 3.12
uv venv --python python3.12
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -r requirements.txt

# Build and start PostgreSQL service (in background)
docker-compose up -d

# Run the application
uvicorn app.main:app --reload
```

This will:
- Build a custom PostgreSQL 17.4 image
- Start a container named `dazzign-db` 
- Set up the environment using variables from .env
- Mount a volume for data persistence

Additional Docker Compose commands:

```bash
# View container logs
docker-compose logs -f

# Stop the containers
docker-compose down

# Stop the containers and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Rebuild the container if you change Dockerfile.postgres
docker-compose up -d --build
```

### Volume Storage Location

The Docker Compose file defines a named volume `dazzign_postgres_data` that stores PostgreSQL data. The actual location of this volume depends on your Docker installation:

- **Linux**: `/var/lib/docker/volumes/[project_directory_name]_dazzign_postgres_data/_data`
- **macOS**: `~/Library/Containers/com.docker.docker/Data/vms/...`
- **Windows**: `\\wsl$\docker-desktop-data\version-pack-data\community\docker\volumes\[project_directory_name]_dazzign_postgres_data\_data`

You don't need to rename this volume. Docker automatically prefixes volume names with the project directory name. If you want to use a specific local directory instead of a Docker-managed volume, you can modify the volumes section in docker-compose.yml:

```yaml
volumes:
  - /path/to/local/data:/var/lib/postgresql/data
```

#### Building PostgreSQL Container Manually

If you prefer to build and run the PostgreSQL container manually:

1. Build the PostgreSQL image:
```bash
docker build -f Dockerfile.postgres -t dazzign-postgres .
```

2. Run the container:
```bash
docker run -d \
  --name dazzign-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres_secure_password \
  -e POSTGRES_DB=dazzign \
  -p 5432:5432 \
  -v dazzign_postgres_data:/var/lib/postgresql/data \
  dazzign-postgres
```

### Application Setup

1. Set up a virtual environment with uv:
   ```bash
   uv venv --python python3.12
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Make sure the PostgreSQL database is running

4. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access the API documentation at http://localhost:8000/docs

### Database Management

To reset the database:
```bash
python -m scripts.reset_db
```

## 📡 API Endpoints

The API is divided into three main areas:

### Node Endpoints (prefix: `/node`)
- **GET** `/node/{image_id}` - Get a single image by ID
- **GET** `/node/{image_id}/lineage` - Get ancestry and descendants of an image
- **GET** `/node/root/list` - List all root images (with no parent)

### Image Generation Endpoints (prefix: `/image_gen`)
- **POST** `/image_gen/generate` - Generate a new image based on prompt

### Text Generation Endpoints (prefix: `/text_gen`)
- **POST** `/text_gen/text-to-image` - Convert free-form text to structured attributes

## 📁 Project Structure

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
│   │       ├── node_endpoints.py      # Node/DB retrieval endpoints
│   │       ├── image_gen_endpoints.py # Image generation endpoints
│   │       └── text_gen_endpoints.py  # Text-to-image endpoints
│   ├── db/                    # Database utilities
│   │   ├── session.py         # DB session setup
│   │   └── init_db.py         # DB initialization
│   └── services/              # Business logic
│       ├── __init__.py            # Service exports
│       ├── facade_service.py      # Service facade (for backward compatibility)
│       ├── node_service.py        # Node management service
│       ├── image_gen_service.py   # Image generation service
│       └── text_gen_service.py    # Text processing service
├── scripts/                   # Utility scripts
│   └── reset_db.py            # DB reset script
├── tests/                     # Test files
├── Dockerfile.postgres        # PostgreSQL Docker image definition
├── docker-compose.yml         # Docker setup
├── requirements.txt           # Project dependencies
├── .env                       # Environment variables
└── .env.example               # Example environment variables
```

## 📋 Feature Overview

### Node Management
- Database storage and retrieval of image nodes
- Hierarchical structure with parent-child relationships
- Lineage tracking for image evolution

### Image Generation
- Generate PC case design images from text prompts
- Maintain relationship between generated images
- Root image listing for easy navigation

### Text Processing
- Extract structured attributes from free-form text descriptions:
  - Color: Primary and accent colors
  - Style: Overall design style (Minimalist, Futuristic, etc.)
  - Shape: Silhouette or contour
  - Material: Main construction materials
  - Ventilation: Cooling and airflow features
  - Lighting: Illumination elements
  - Features: Additional functionality

### Database and Development
- PostgreSQL 17.4 for robust data storage
- FastAPI for high-performance API
- Docker containerization for easy deployment 