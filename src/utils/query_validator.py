import re
from src.utils.logger import get_logger

logger = get_logger(__name__)


class QueryValidator:
    """Validates and transforms user queries before processing."""
    
    # Words that indicate non-knowledge queries
    BLOCKED_PATTERNS = [
        r"\b(hack|exploit|inject|drop\s+table)\b",
    ]
    
    @staticmethod
    def validate(query: str) -> tuple[bool, str]:
        """Validate a query string. Returns (is_valid, message)."""
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        query = query.strip()
        
        if len(query) < 3:
            return False, "Query is too short (minimum 3 characters)"
        
        if len(query) > 1000:
            return False, "Query is too long (maximum 1000 characters)"
        
        # Check for blocked patterns
        for pattern in QueryValidator.BLOCKED_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Blocked query matching pattern: {pattern}")
                return False, "Query contains disallowed content"
        
        return True, "Valid"
    
    @staticmethod
    def transform(query: str) -> str:
        """Clean and transform a query for better retrieval."""
        # Strip extra whitespace
        query = " ".join(query.split())
        # Remove trailing punctuation repetition
        query = re.sub(r'([?!.]){2,}', r'\1', query)
        return query.strip()
