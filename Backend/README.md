# README for DreamTeller Backend

## Overview

This is the backend for DreamTeller, an AI-powered story and illustration generator. It provides API endpoints for:

- Generating complete stories with images based on user prompts
- Regenerating individual scenes or images
- Fetching and managing previously created stories

## Technology Stack

- **Framework**: FastAPI
- **AI Text Generation**: OpenAI GPT API
- **AI Image Generation**: Replicate/Stability AI Diffusion API
- **Data Validation**: Pydantic
- **Async HTTP Client**: HTTPX

## Getting Started

### Prerequisites

- Python 3.8 or higher
- API keys for OpenAI and Stability AI (or Replicate)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/dreamteller.git
cd dreamteller/backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

5. Edit the `.env` file with your API keys and settings

### Running the Server

Start the development server:

```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:5000`

### API Documentation

FastAPI automatically generates interactive documentation:

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## API Endpoints

### Story Endpoints

- `POST /api/stories/generate` - Generate a new story

  - Request body: StoryPrompt model with idea, genre, tone, etc.
  - Returns: Complete Story with title and scenes

- `POST /api/stories/regenerate-text` - Regenerate text for a specific scene

  - Request body: RegenerateTextRequest with prompt, current text, and scene index
  - Returns: New text for the scene

- `GET /api/stories` - Get all stories

  - Returns: Array of Story objects

- `GET /api/stories/{story_id}` - Get a specific story

  - Returns: Story object

- `DELETE /api/stories/{story_id}` - Delete a story
  - Returns: Success message

### Image Endpoints

- `POST /api/images/generate` - Generate an image
  - Request body: ImageGenerationRequest with prompt and optional parameters
  - Returns: URL to the generated image

## Project Structure

- `app.py` - Main FastAPI application
- `config.py` - Configuration and environment variables
- `models/` - Pydantic data models
  - `story.py` - Story-related data models
  - `image.py` - Image-related data models
- `routes/` - API route handlers
  - `story_routes.py` - Story generation endpoints
  - `image_routes.py` - Image generation endpoints
- `services/` - Business logic
  - `openai_service.py` - OpenAI integration for story generation
  - `diffusion_service.py` - Image generation service
- `utils/` - Helper utilities
  - `prompt_engineering.py` - Prompt crafting for AI models
  - `error_handling.py` - Error handling decorators and utilities

## Notes for Production Deployment

1. Use a proper database (PostgreSQL, MongoDB) instead of in-memory storage
2. Add authentication and rate limiting
3. Set up proper logging and monitoring
4. Use environment-specific configuration
5. Implement a CDN for serving generated images
6. Set up CI/CD pipelines for testing and deployment

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Submit a pull request
