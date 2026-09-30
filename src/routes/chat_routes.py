from flask import Blueprint, request, jsonify, current_app
from src.models.schemas import QueryRequest, QueryResponse, SourceDocument
from src.utils.logger import get_logger
from src.utils.query_validator import QueryValidator
import time
from pydantic import ValidationError

logger = get_logger(__name__)

chat_bp = Blueprint("chat_bp", __name__, url_prefix="/api/chat")

@chat_bp.route("/query", methods=["POST"])
def query():
    try:
        data = request.json or {}
        req = QueryRequest(**data)
        
        is_valid, msg = QueryValidator.validate(req.question)
        if not is_valid:
            return jsonify({"error": msg}), 400
        
        transformed_question = QueryValidator.transform(req.question)
        
        start_time = time.time()
        
        llm_service = current_app.config["llm_service"]
        result = llm_service.query(transformed_question, req.chat_history)
        
        latency_ms = (time.time() - start_time) * 1000
        
        sources = []
        for doc in result.get("source_documents", []):
            sources.append(SourceDocument(
                content=doc.page_content,
                source=doc.metadata.get("source", "unknown"),
                chunk_index=doc.metadata.get("chunk_index")
            ))
            
        resp = QueryResponse(
            answer=result["answer"],
            sources=sources,
            query=transformed_question
        )
        
        observability = current_app.config.get("observability")
        if observability:
            observability.log_query(
                query=transformed_question,
                answer=result["answer"],
                sources=sources,
                latency_ms=latency_ms
            )
            
        return jsonify(resp.model_dump(mode='json')), 200
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400
    except Exception as e:
        logger.error(f"Query endpoint failed: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/reset", methods=["POST"])
def reset():
    try:
        llm_service = current_app.config["llm_service"]
        llm_service.reset_memory()
        return jsonify({"status": "success", "message": "Memory reset"}), 200
    except Exception as e:
        logger.error(f"Reset memory failed: {e}")
        return jsonify({"error": str(e)}), 500

@chat_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy"}), 200
