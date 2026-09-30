from datetime import datetime
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ObservabilityService:
    """Tracks queries, responses, and system metrics for observability."""
    
    def __init__(self, mem0_api_key: str = ""):
        self.mem0_client = None
        self._query_log = []
        
        if mem0_api_key:
            try:
                from mem0 import MemoryClient
                self.mem0_client = MemoryClient(api_key=mem0_api_key)
                logger.info("Mem0 observability client initialized")
            except ImportError:
                logger.warning("mem0ai package not installed, falling back to local logging")
            except Exception as e:
                logger.warning(f"Failed to initialize Mem0 client: {e}")
    
    def log_query(self, query: str, answer: str, sources: list, latency_ms: float, user_id: str = "default"):
        """Log a query-answer pair for observability."""
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "answer_length": len(answer),
            "sources_count": len(sources),
            "latency_ms": round(latency_ms, 2),
            "user_id": user_id
        }
        self._query_log.append(entry)
        logger.info(f"Query logged: {query[:50]}... | latency={latency_ms:.0f}ms | sources={len(sources)}")
        
        # Store in Mem0 if available
        if self.mem0_client:
            try:
                self.mem0_client.add(
                    f"User asked: {query}\nAnswer: {answer[:200]}",
                    user_id=user_id,
                    metadata={"type": "query_log", "latency_ms": latency_ms}
                )
            except Exception as e:
                logger.warning(f"Failed to log to Mem0: {e}")
    
    def get_stats(self) -> dict:
        """Get observability statistics."""
        if not self._query_log:
            return {"total_queries": 0, "avg_latency_ms": 0, "avg_sources": 0}
        
        total = len(self._query_log)
        avg_latency = sum(e["latency_ms"] for e in self._query_log) / total
        avg_sources = sum(e["sources_count"] for e in self._query_log) / total
        
        return {
            "total_queries": total,
            "avg_latency_ms": round(avg_latency, 2),
            "avg_sources": round(avg_sources, 2),
            "recent_queries": self._query_log[-10:]
        }
