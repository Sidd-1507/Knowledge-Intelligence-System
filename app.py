import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv

from src.config.settings import get_settings
from src.services.s3_storage import S3StorageService
from src.services.document_processor import DocumentProcessor
from src.services.vector_store import VectorStoreService
from src.services.llm_service import LLMService
from src.routes.document_routes import document_bp
from src.routes.chat_routes import chat_bp
from src.utils.logger import get_logger
from src.utils.observability import ObservabilityService

load_dotenv()

logger = get_logger(__name__)


def create_app() -> Flask:
    """Application factory."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )
    CORS(app)
    
    # Load settings
    settings = get_settings()
    
    # Configure upload size
    app.config["MAX_CONTENT_LENGTH"] = settings.max_upload_size_mb * 1024 * 1024
    
    # Initialize services
    s3_service = S3StorageService(settings)
    doc_processor = DocumentProcessor(settings)
    vector_store = VectorStoreService(settings)
    llm_service = LLMService(settings, vector_store)
    observability = ObservabilityService(settings.mem0_api_key)
    
    # Store services in app config for access in routes
    app.config["s3_service"] = s3_service
    app.config["doc_processor"] = doc_processor
    app.config["vector_store"] = vector_store
    app.config["llm_service"] = llm_service
    app.config["observability"] = observability
    
    # Register blueprints
    app.register_blueprint(document_bp)
    app.register_blueprint(chat_bp)
    
    # Root route — serve UI
    @app.route("/")
    def index():
        return render_template("index.html")
    
    # Health check at root level too
    @app.route("/api/health")
    def health():
        stats = vector_store.get_collection_stats()
        return {
            "status": "healthy",
            "version": "1.0.0",
            "documents_count": len(vector_store.get_document_sources()),
            "vector_chunks_count": stats.get("total_chunks", 0)
        }
    
    logger.info("Knowledge Intelligence System initialized successfully")
    return app


app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    app.run(
        host=settings.flask_host,
        port=settings.flask_port,
        debug=settings.flask_debug
    )
