"""
RAG Agent for retrieval from GST rules documents.
"""
import os
from pathlib import Path
from typing import List, Optional
import logging
import chromadb
from chromadb.config import Settings
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..utils.llm import llm

logger = logging.getLogger(__name__)


class RAGAgent:
    """RAG agent for querying GST rules and regulations."""
    
    def __init__(self, 
                 vector_store_path: str = "./data/vector_store",
                 documents_path: str = "./data/gst_rules"):
        """
        Initialize RAG agent with ChromaDB.
        
        Args:
            vector_store_path: Path to persist vector database
            documents_path: Path to source documents folder
        """
        self.vector_store_path = Path(vector_store_path)
        self.documents_path = Path(documents_path)
        self.collection_name = "gst_rules"
        
        # Ensure directories exist
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.documents_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(self.vector_store_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = None
        self._initialize_collection()
        
        logger.info("RAG Agent initialized")
    
    def _initialize_collection(self):
        """Initialize or load existing ChromaDB collection."""
        try:
            # Try to get existing collection
            self.collection = self.client.get_collection(name=self.collection_name)
            count = self.collection.count()
            logger.info(f"Loaded existing collection with {count} documents")
        except Exception:
            # Collection doesn't exist, create it
            logger.info("Creating new collection...")
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "GST Rules and Regulations"}
            )
            
            # Auto-ingest documents if available
            if self._has_documents():
                logger.info("Found documents in gst_rules folder. Ingesting...")
                self.ingest_documents()
            else:
                logger.warning("No documents found in gst_rules folder. Collection is empty.")
    
    def _has_documents(self) -> bool:
        """Check if documents exist in the documents folder."""
        pdf_files = list(self.documents_path.glob("*.pdf"))
        txt_files = list(self.documents_path.glob("*.txt"))
        return len(pdf_files) + len(txt_files) > 0
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from a PDF file."""
        try:
            reader = PdfReader(str(pdf_path))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Failed to extract PDF {pdf_path}: {e}")
            return ""
    
    def ingest_documents(self):
        """
        Ingest all documents from the documents folder into ChromaDB.
        """
        documents = []
        metadatas = []
        ids = []
        
        # Process PDF files
        for pdf_file in self.documents_path.glob("*.pdf"):
            logger.info(f"Processing PDF: {pdf_file.name}")
            text = self._extract_text_from_pdf(pdf_file)
            
            if text.strip():
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50,
                    length_function=len
                )
                chunks = text_splitter.split_text(text)
                
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "source": pdf_file.name,
                        "type": "pdf",
                        "chunk": i
                    })
                    ids.append(f"{pdf_file.stem}_chunk_{i}")
        
        # Process text files
        for txt_file in self.documents_path.glob("*.txt"):
            logger.info(f"Processing text file: {txt_file.name}")
            text = txt_file.read_text(encoding='utf-8')
            
            if text.strip():
                # Split text into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500,
                    chunk_overlap=50,
                    length_function=len
                )
                chunks = text_splitter.split_text(text)
                
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "source": txt_file.name,
                        "type": "txt",
                        "chunk": i
                    })
                    ids.append(f"{txt_file.stem}_chunk_{i}")
        
        # Add to ChromaDB with embeddings
        if documents:
            logger.info(f"Adding {len(documents)} chunks to vector store...")
            
            # Generate embeddings using Gemini
            embeddings = []
            for doc in documents:
                embedding = llm.generate_embedding(doc)
                embeddings.append(embedding)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully ingested {len(documents)} document chunks")
        else:
            logger.warning("No documents to ingest")
    
    def retrieve_context(self, query: str, k: int = 5) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: User query
            k: Number of top results to retrieve
            
        Returns:
            Combined context from relevant documents
        """
        if self.collection.count() == 0:
            logger.warning("Vector store is empty. Cannot retrieve context.")
            return ""
        
        try:
            # Generate query embedding
            query_embedding = llm.generate_embedding(query)
            
            # Query ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            
            # Combine results
            if results and results['documents'] and results['documents'][0]:
                context_chunks = results['documents'][0]
                context = "\n\n".join([f"[Source: {results['metadatas'][0][i]['source']}]\n{chunk}" 
                                      for i, chunk in enumerate(context_chunks)])
                
                logger.debug(f"Retrieved {len(context_chunks)} relevant chunks")
                return context
            else:
                logger.warning("No relevant context found")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to retrieve context: {e}")
            return ""


# Global RAG agent instance
rag_agent = RAGAgent()
