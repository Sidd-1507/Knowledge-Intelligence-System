# Knowledge Intelligence System

![CI/CD](https://github.com/yourusername/knowledge-intelligence-system/actions/workflows/ci-cd.yml/badge.svg)
![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Description

The Knowledge Intelligence System is an advanced AI-powered application designed to manage, index, and query knowledge efficiently. By leveraging state-of-the-art language models and vector databases, this system enables intelligent semantic search and retrieval augmented generation (RAG) capabilities.

## Architecture

The system is built on a scalable microservices architecture:
- **Backend Framework**: Flask
- **LLM Integration**: LangChain & OpenAI
- **Vector Database**: ChromaDB
- **Storage**: AWS S3
- **Memory**: Mem0

## Features

- **Semantic Search**: Understands context and meaning behind queries.
- **RAG Capabilities**: Generates accurate and context-aware responses based on indexed knowledge.
- **Document Ingestion**: Supports uploading and processing multiple document formats (PDF, DOCX, etc.).
- **Memory Management**: Keeps track of conversation history and preferences via Mem0.

## Prerequisites

- Python 3.11+
- AWS Account (S3 access)
- OpenAI API Key

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/knowledge-intelligence-system.git
   cd knowledge-intelligence-system
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Copy the example environment file and update the configurations:
```bash
cp .env.example .env
```
Fill in the necessary keys (`OPENAI_API_KEY`, `AWS_ACCESS_KEY_ID`, etc.) in `.env`.

## Running the App

### Locally
```bash
flask run --host=0.0.0.0 --port=5000
```

### With Docker
```bash
docker-compose up --build
```

## API Endpoints

- `GET /api/health` - Health check
- *Other endpoints to be documented.*

## Project Structure

```
├── .github/workflows/   # CI/CD pipelines
├── src/                 # Application source code
│   ├── config/          # Configurations
│   ├── models/          # Data models
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── utils/           # Utility functions
├── tests/               # Unit and integration tests
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker compose configuration
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or new features.

## License

This project is licensed under the MIT License.
