from flask import Blueprint, request, jsonify, current_app
from src.utils.logger import get_logger

logger = get_logger(__name__)

document_bp = Blueprint("document_bp", __name__, url_prefix="/api/documents")

@document_bp.route("/upload", methods=["POST"])
def upload_document():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    try:
        content = file.read()
        s3_service = current_app.config["s3_service"]
        doc_processor = current_app.config["doc_processor"]
        vector_store = current_app.config["vector_store"]
        
        s3_key = s3_service.upload_file(content, file.filename)
        docs = doc_processor.process_file(content, file.filename)
        chunks_added = vector_store.add_documents(docs)
        
        return jsonify({
            "status": "success",
            "message": f"Successfully uploaded and processed {file.filename}",
            "filename": file.filename,
            "chunks_added": chunks_added
        }), 201
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route("/list", methods=["GET"])
def list_documents():
    try:
        s3_service = current_app.config["s3_service"]
        files = s3_service.list_files()
        return jsonify({"documents": files}), 200
    except Exception as e:
        logger.error(f"List documents failed: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route("/<filename>", methods=["DELETE"])
def delete_document(filename):
    try:
        s3_service = current_app.config["s3_service"]
        vector_store = current_app.config["vector_store"]
        
        s3_service.delete_file(filename)
        vector_store.delete_document(filename)
        
        return jsonify({"status": "success", "message": f"Deleted {filename}"}), 200
    except Exception as e:
        logger.error(f"Delete document failed: {e}")
        return jsonify({"error": str(e)}), 500

@document_bp.route("/stats", methods=["GET"])
def get_stats():
    try:
        vector_store = current_app.config["vector_store"]
        stats = vector_store.get_collection_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Get stats failed: {e}")
        return jsonify({"error": str(e)}), 500
