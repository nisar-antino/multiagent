"""
Gemini LLM initialization and wrapper using LangChain.
"""
import os
from typing import Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.utils.security import rate_limiter

logger = logging.getLogger(__name__)


class GeminiLLM:
    """Wrapper for LLM (Google Gemini or OpenRouter) with rate limiting."""
    
    _instance: Optional['GeminiLLM'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Check for OpenRouter configuration first
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # 1. Initialize LLM (The "Brain")
        if openrouter_key:
            model_name = os.getenv('OPENROUTER_MODEL', 'google/gemini-2.0-flash-001')
            logger.info(f"Using OpenRouter LLM: {model_name}")
            
            self.model = ChatOpenAI(
                model=model_name,
                openai_api_key=openrouter_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=0.1
            )
        elif google_api_key:
            logger.info("Using Google Gemini Direct API")
            self.model = ChatGoogleGenerativeAI(
                model="gemini-flash-latest",
                google_api_key=google_api_key,
                temperature=0.1,
                max_tokens=2048,
                convert_system_message_to_human=True
            )
        else:
             raise ValueError("No API Key found! Please set OPENROUTER_API_KEY or GOOGLE_API_KEY in .env")

        # 2. Initialize Embeddings (The "Memory")
        try:
            if openrouter_key:
                logger.info("Using OpenRouter for Embeddings (via OpenAI-compatible endpoint)")
                # Standard model usually supported by OpenRouter's forwarding
                # Ensure the provider supports this or use a generic one if routed
                emb_model = "text-embedding-3-small" 
                self.embeddings = OpenAIEmbeddings(
                    model=emb_model,
                    openai_api_key=openrouter_key,
                    openai_api_base="https://openrouter.ai/api/v1"
                )
                self.embeddings.embed_query("test")
                
            elif google_api_key:
                # User suggested model for deprecated text-embedding-004
                model_name = "models/gemini-embedding-001"
                logger.info(f"Using Google Embeddings: {model_name}")
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=model_name,
                    google_api_key=google_api_key
                )
                self.embeddings.embed_query("test")
            else:
                raise ValueError("No API key available for embeddings")
                
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
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
