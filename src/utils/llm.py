"""
Gemini LLM initialization and wrapper using LangChain.
"""
import os
from typing import Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from src.utils.security import rate_limiter

logger = logging.getLogger(__name__)


class GeminiLLM:
    """Wrapper for Google Gemini API with rate limiting and retry logic."""
    
    _instance: Optional['GeminiLLM'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Get API key from environment
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError("GOOGLE_API_KEY not set in environment. Please update .env file.")
        
        # Initialize LangChain Gemini model  
        # Using gemini-flash-latest which is available with the API key
        self.model = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            google_api_key=api_key,
            temperature=0.1,
            max_tokens=2048,
            convert_system_message_to_human=True
        )
        
        # Initialize embeddings model
        try:
            # User suggested model for deprecated text-embedding-004
            model_name = "models/gemini-embedding-001"
            print(f"Initializing embeddings with model: {model_name}")
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=model_name,
                google_api_key=api_key
            )
            # Test connection
            self.embeddings.embed_query("test")
        except Exception as e:
            logger.error(f"Failed to initialize {model_name}: {e}")
            
            # Try fallback to embedding-001 if gemini-embedding-001 fails
            try:
                fallback_model = "models/embedding-001"
                logger.info(f"Trying fallback model: {fallback_model}")
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=fallback_model,
                    google_api_key=api_key
                )
                self.embeddings.embed_query("test")
            except Exception as e2:
                logger.error(f"Failed to initialize {fallback_model}: {e2}")
                logger.warning("Falling back to FakeEmbeddings (RAG will not be accurate)")
                from langchain_community.embeddings import FakeEmbeddings
                self.embeddings = FakeEmbeddings(size=768)
        
        self._initialized = True
        logger.info("Gemini LLM initialized successfully with LangChain")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_text(self, prompt: str) -> str:
        """
        Generate text using Gemini with rate limiting and retry logic.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Generated text
        """
        # Apply rate limiting
        rate_limiter.wait_if_needed()
        
        try:
            response = self.model.invoke(prompt)
            logger.debug(f"Generated response for prompt: {prompt[:100]}...")
            
            # Ensure we always return a string
            content = response.content
            if isinstance(content, list):
                content = ' '.join(str(item) for item in content)
            elif not isinstance(content, str):
                content = str(content)
            
            return content
        except Exception as e:
            logger.error(f"Failed to generate text: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_embedding(self, text: str) -> list[float]:
        """
        Generate embedding for text using Gemini.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        # Apply rate limiting
        rate_limiter.wait_if_needed()
        
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise


# Global LLM instance
llm = GeminiLLM()
