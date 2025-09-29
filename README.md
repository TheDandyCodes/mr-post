# Mr. Post

AI Solution that helps users to writing posts about any idea

## Architecture

This is a multi-microservice system built with Python and uv for dependency management:

### Services

1. **Frontend Service** (Port 8000)
   - Built with FastHTML and DaisyUI
   - User interface for creating and managing posts
   - Handles authentication and user preferences

2. **Agents Service** (Port 8002)
   - Multi-agent system with Writer and Reviewer agents
   - Writer agent: Generates content from user ideas
   - Reviewer agent: Reviews and improves generated content
   - Uses OpenAI API (with demo fallback)

3. **Storage Service** (Port 8001)
   - User management and authentication
   - Post storage and session management
   - SQLite database for development
   - RESTful API for data operations

## Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd mr-post

# Start all services with Docker Compose
docker-compose up --build

# Access the application
open http://localhost:8000
```

### Local Development

```bash
# Install dependencies
uv sync

# Run all services locally
python scripts/dev.py

# Or run individual services:
python -m services.storage.main    # Port 8001
python -m services.agents.main     # Port 8002  
python -m services.frontend.main   # Port 8000
```

## Features

### User Management
- User registration and authentication
- Session management with JWT tokens
- User preferences for writing style, tone, and length

### AI-Powered Writing
- **Writer Agent**: Transforms user ideas into structured posts
- **Reviewer Agent**: Provides feedback and improvements
- Customizable writing preferences (style, tone, audience, length)
- Real-time processing status updates

### User Interface
- Modern, responsive design with DaisyUI
- Real-time updates during AI processing
- Post management dashboard
- Preferences configuration
- Copy/download functionality for completed posts

## Configuration

### Environment Variables

```bash
# Optional: OpenAI API key for enhanced AI capabilities
OPENAI_API_KEY=your_openai_api_key

# Service URLs (for Docker deployment)
STORAGE_SERVICE_URL=http://storage:8001
AGENTS_SERVICE_URL=http://agents:8002

# Database
DATABASE_URL=sqlite:///./mr_post.db
```

### Development Setup

```bash
# Install UV package manager
pip install uv

# Clone and setup
git clone <repository-url>
cd mr-post
uv sync

# Create data directory
mkdir -p data

# Run development server
python scripts/dev.py
```

## API Documentation

When running locally, API documentation is available at:
- Storage API: http://localhost:8001/docs
- Agents API: http://localhost:8002/docs

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: FastHTML, DaisyUI, Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production ready)
- **AI/ML**: OpenAI API integration
- **Development**: uv for dependency management
- **Deployment**: Docker and Docker Compose

## Project Structure

```
mr-post/
├── services/
│   ├── frontend/          # FastHTML frontend service
│   ├── agents/            # Multi-agent AI system
│   └── storage/           # Data and user management
├── docker/                # Docker configurations
├── scripts/               # Development scripts
├── src/mr_post/          # Main package
├── data/                 # Local database storage
├── docker-compose.yml    # Multi-service orchestration
└── pyproject.toml        # Dependencies and configuration
```

## Contributing

This project uses:
- Python 3.12+
- uv for dependency management
- Black for code formatting
- Ruff for linting

```bash
# Format code
uv run black .

# Lint code
uv run ruff check .

# Run tests
uv run pytest
```

## License

This project is open source and available under the MIT License.
