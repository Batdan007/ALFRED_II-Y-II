#!/usr/bin/env python3
"""
Alfred Vector Knowledge Base - ChromaDB Integration
Provides semantic search and storage for crawled content
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import logging
from datetime import datetime


class VectorKnowledgeBase:
    """
    Vector database for storing and searching crawled content
    Uses ChromaDB for local persistent storage
    """

    def __init__(self, data_dir: str = "alfred_data", collection_name: str = "alfred_knowledge"):
        """
        Initialize vector knowledge base

        Args:
            data_dir: Directory for ChromaDB storage
            collection_name: Name of the collection
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = collection_name

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.data_dir / "chroma_db"),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # Initialize embedding model (lightweight, runs locally)
        logging.info("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        # Model info: 384 dimensions, 22M parameters, fast on CPU

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Alfred's web crawl knowledge base"}
        )

        logging.info(f"Vector knowledge base initialized: {collection_name}")

    def add_document(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the knowledge base

        Args:
            text: Document text content
            metadata: Optional metadata (url, title, source, etc.)
            doc_id: Optional custom document ID

        Returns:
            Document ID
        """
        if not text or not text.strip():
            raise ValueError("Document text cannot be empty")

        # Generate ID if not provided
        if not doc_id:
            doc_id = f"doc_{datetime.now().timestamp()}"

        # Prepare metadata
        meta = metadata or {}
        meta['added_at'] = datetime.now().isoformat()
        meta['char_count'] = len(text)

        # Generate embedding
        embedding = self.embedding_model.encode(text).tolist()

        # Add to ChromaDB
        self.collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[meta],
            ids=[doc_id]
        )

        logging.info(f"Added document {doc_id} ({len(text)} chars)")
        return doc_id

    def add_documents_batch(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add multiple documents in batch (faster)

        Args:
            texts: List of document texts
            metadatas: Optional list of metadata dicts
            ids: Optional list of document IDs

        Returns:
            List of document IDs
        """
        if not texts:
            return []

        # Generate IDs if not provided
        if not ids:
            timestamp = datetime.now().timestamp()
            ids = [f"doc_{timestamp}_{i}" for i in range(len(texts))]

        # Prepare metadatas
        if not metadatas:
            metadatas = [{}] * len(texts)

        for i, meta in enumerate(metadatas):
            meta['added_at'] = datetime.now().isoformat()
            meta['char_count'] = len(texts[i])

        # Generate embeddings in batch (much faster)
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True).tolist()

        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )

        logging.info(f"Added {len(texts)} documents in batch")
        return ids

    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        include_distances: bool = True
    ) -> Dict[str, Any]:
        """
        Semantic search for relevant documents

        Args:
            query: Search query
            n_results: Number of results to return
            where: Optional metadata filter (e.g., {"source": "wikipedia"})
            include_distances: Include similarity distances

        Returns:
            Search results with documents, metadatas, distances
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()

        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=['documents', 'metadatas', 'distances']
        )

        # Format results
        formatted = {
            'query': query,
            'n_results': len(results['ids'][0]) if results['ids'] else 0,
            'results': []
        }

        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                result = {
                    'id': results['ids'][0][i],
                    'text': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                }

                if include_distances and results.get('distances'):
                    # Convert distance to similarity score (0-1, higher is better)
                    distance = results['distances'][0][i]
                    similarity = 1.0 / (1.0 + distance)
                    result['similarity'] = similarity
                    result['distance'] = distance

                formatted['results'].append(result)

        logging.info(f"Search '{query}': {formatted['n_results']} results")
        return formatted

    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific document by ID

        Args:
            doc_id: Document ID

        Returns:
            Document data or None if not found
        """
        results = self.collection.get(
            ids=[doc_id],
            include=['documents', 'metadatas', 'embeddings']
        )

        if results['ids']:
            return {
                'id': results['ids'][0],
                'text': results['documents'][0],
                'metadata': results['metadatas'][0],
                'embedding': results['embeddings'][0] if results.get('embeddings') else None
            }
        return None

    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            self.collection.delete(ids=[doc_id])
            logging.info(f"Deleted document {doc_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete {doc_id}: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        count = self.collection.count()

        return {
            'collection': self.collection_name,
            'total_documents': count,
            'embedding_model': 'all-MiniLM-L6-v2',
            'embedding_dimensions': 384,
            'storage_path': str(self.data_dir / "chroma_db")
        }

    def clear(self) -> None:
        """Clear all documents from the collection"""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"description": "Alfred's web crawl knowledge base"}
        )
        logging.warning(f"Cleared all documents from {self.collection_name}")


class DocumentChunker:
    """
    Chunks large documents into smaller pieces for better retrieval
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize chunker

        Args:
            chunk_size: Target size of each chunk in characters
            chunk_overlap: Overlap between chunks for context
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Chunk text into overlapping segments

        Args:
            text: Text to chunk
            metadata: Metadata to include with each chunk

        Returns:
            List of chunks with text and metadata
        """
        if not text:
            return []

        chunks = []
        start = 0
        chunk_num = 0

        while start < len(text):
            # Extract chunk
            end = start + self.chunk_size
            chunk_text = text[start:end]

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for sep in ['. ', '.\n', '! ', '?\n', '? ']:
                    last_sep = chunk_text.rfind(sep)
                    if last_sep > self.chunk_size * 0.7:  # At least 70% of chunk_size
                        chunk_text = chunk_text[:last_sep + 1]
                        break

            # Create chunk metadata
            chunk_meta = metadata.copy() if metadata else {}
            chunk_meta.update({
                'chunk_num': chunk_num,
                'chunk_start': start,
                'chunk_end': start + len(chunk_text),
                'chunk_size': len(chunk_text)
            })

            chunks.append({
                'text': chunk_text.strip(),
                'metadata': chunk_meta
            })

            # Move to next chunk with overlap
            advance = max(1, len(chunk_text) - self.chunk_overlap)  # Always advance at least 1 char
            start = start + advance
            chunk_num += 1

            # Prevent infinite loop - if we're near the end, stop
            if start >= len(text) - 1:
                break

        logging.info(f"Chunked text into {len(chunks)} pieces")
        return chunks

    def chunk_documents(
        self,
        documents: List[Dict[str, Any]],
        text_key: str = 'text',
        metadata_key: str = 'metadata'
    ) -> List[Dict[str, Any]]:
        """
        Chunk multiple documents

        Args:
            documents: List of documents with text and metadata
            text_key: Key for text in document dict
            metadata_key: Key for metadata in document dict

        Returns:
            List of chunked documents
        """
        all_chunks = []

        for doc in documents:
            text = doc.get(text_key, '')
            metadata = doc.get(metadata_key, {})

            chunks = self.chunk_text(text, metadata)
            all_chunks.extend(chunks)

        return all_chunks


# Convenience functions
def create_knowledge_base(data_dir: str = "alfred_data", collection: str = "alfred_knowledge") -> VectorKnowledgeBase:
    """Create a new knowledge base instance"""
    return VectorKnowledgeBase(data_dir, collection)


def chunk_large_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Quick text chunking"""
    chunker = DocumentChunker(chunk_size=chunk_size)
    chunks = chunker.chunk_text(text)
    return [c['text'] for c in chunks]


if __name__ == "__main__":
    # Test the vector knowledge base
    print("=" * 80)
    print("Testing Alfred Vector Knowledge Base")
    print("=" * 80)
    print()

    # Create knowledge base
    kb = create_knowledge_base()
    print(f"Knowledge base created: {kb.get_stats()}")
    print()

    # Add test documents
    print("Adding test documents...")
    kb.add_document(
        "Python is a high-level programming language known for its simplicity and readability.",
        metadata={"source": "test", "topic": "programming"}
    )

    kb.add_document(
        "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
        metadata={"source": "test", "topic": "AI"}
    )

    kb.add_document(
        "ChromaDB is a vector database designed for AI applications and semantic search.",
        metadata={"source": "test", "topic": "database"}
    )
    print(f"Added 3 documents. Total: {kb.get_stats()['total_documents']}")
    print()

    # Search
    print("Searching for 'artificial intelligence'...")
    results = kb.search("artificial intelligence", n_results=2)
    for i, result in enumerate(results['results'], 1):
        print(f"{i}. (similarity: {result['similarity']:.3f})")
        print(f"   {result['text'][:100]}...")
        print()

    # Test chunking
    print("Testing document chunking...")
    chunker = DocumentChunker(chunk_size=50, chunk_overlap=10)
    long_text = "This is a test document. " * 20
    chunks = chunker.chunk_text(long_text, metadata={"test": "chunking"})
    print(f"Chunked {len(long_text)} chars into {len(chunks)} pieces")
    print()

    print("=" * 80)
    print("Vector Knowledge Base Test Complete!")
    print("=" * 80)
