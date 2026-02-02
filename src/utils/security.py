"""
Security utilities for SQL validation and rate limiting.
"""
import time
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
from typing import Optional
import logging
import threading

logger = logging.getLogger(__name__)


class SQLValidator:
    """Validates SQL queries to ensure read-only operations."""
    
    # Allowed SQL statement types
    ALLOWED_TYPES = {'SELECT'}
    
    # Dangerous keywords that should never appear
    DANGEROUS_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'TRUNCATE', 'REPLACE', 'MERGE', 'GRANT', 'REVOKE',
        'EXEC', 'EXECUTE', 'CALL', 'LOAD', 'INTO OUTFILE', 'INTO DUMPFILE'
    }
    
    @staticmethod
    def validate_query(query: str) -> tuple[bool, Optional[str]]:
        """
        Validate that a SQL query is safe (read-only).
        
        Args:
            query: SQL query string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Empty query"
        
        # Parse the SQL query
        try:
            parsed = sqlparse.parse(query)
        except Exception as e:
            return False, f"Failed to parse SQL: {str(e)}"
        
        if not parsed:
            return False, "No valid SQL statement found"
        
        # Check for multiple statements (semicolon injection)
        if len(parsed) > 1:
            return False, "Multiple SQL statements not allowed"
        
        statement: Statement = parsed[0]
        
        # Check statement type
        stmt_type = statement.get_type()
        if stmt_type not in SQLValidator.ALLOWED_TYPES:
            return False, f"Only SELECT queries allowed. Found: {stmt_type}"
        
        # Check for dangerous keywords in the entire query
        query_upper = query.upper()
        for keyword in SQLValidator.DANGEROUS_KEYWORDS:
            if keyword in query_upper:
                return False, f"Dangerous keyword detected: {keyword}"
        
        logger.debug(f"SQL query validated successfully: {query[:100]}...")
        return True, None


class RateLimiter:
    """Token bucket rate limiter for API calls."""
    
    def __init__(self, max_requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests_per_minute: Maximum number of requests allowed per minute
        """
        self.max_requests = max_requests_per_minute
        self.tokens = max_requests_per_minute
        self.last_update = time.time()
        self.lock = threading.Lock()
        
        logger.info(f"Rate limiter initialized: {max_requests_per_minute} requests/minute")
    
    def _refill_tokens(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        time_passed = now - self.last_update
        
        # Refill tokens: (time_passed / 60 seconds) * max_requests
        tokens_to_add = (time_passed / 60.0) * self.max_requests
        self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
        self.last_update = now
    
    def allow_request(self) -> bool:
        """
        Check if a request is allowed under rate limit.
        
        Returns:
            bool: True if request is allowed, False otherwise
        """
        with self.lock:
            self._refill_tokens()
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                logger.warning("Rate limit exceeded")
                return False
    
    def wait_if_needed(self):
        """Block until a request can be made (waiting for rate limit)."""
        while not self.allow_request():
            time.sleep(0.1)  # Wait 100ms before trying again


# Global rate limiter instance
import os
MAX_REQUESTS = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
rate_limiter = RateLimiter(max_requests_per_minute=MAX_REQUESTS)
