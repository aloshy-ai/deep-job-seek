"""Vector database search utilities"""
from qdrant_client import QdrantClient
from fastembed import TextEmbedding
from ..config import QDRANT_URL, QDRANT_COLLECTION_NAME, SEARCH_LIMIT


class VectorSearchClient:
    """Client for vector database operations"""
    
    def __init__(self, url=None, collection_name=None):
        self.url = url or QDRANT_URL
        self.collection_name = collection_name or QDRANT_COLLECTION_NAME
        self.client = QdrantClient(url=self.url)
        self._embedding_model = None
    
    @property
    def embedding_model(self):
        """Lazy-loaded embedding model"""
        if self._embedding_model is None:
            self._embedding_model = TextEmbedding()
        return self._embedding_model
    
    def generate_embedding(self, text):
        """
        Generate embedding for text.
        
        Args:
            text (str): Text to embed
            
        Returns:
            list: Embedding vector
        """
        return list(self.embedding_model.embed([text]))[0].tolist()
    
    def search(self, query_text, limit=None):
        """
        Search for similar content using vector similarity.
        
        Args:
            query_text (str): Query text
            limit (int): Maximum number of results
            
        Returns:
            list: Search results from Qdrant
        """
        query_embedding = self.generate_embedding(query_text)
        
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit or SEARCH_LIMIT
        )
    
    def search_with_filter(self, query_text, filter_conditions=None, limit=None):
        """
        Search with additional filter conditions.
        
        Args:
            query_text (str): Query text
            filter_conditions (dict): Qdrant filter conditions
            limit (int): Maximum number of results
            
        Returns:
            list: Filtered search results
        """
        query_embedding = self.generate_embedding(query_text)
        
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=filter_conditions,
            limit=limit or SEARCH_LIMIT
        )


# Global client instance
_search_client = None

def get_search_client():
    """Get the global vector search client instance"""
    global _search_client
    if _search_client is None:
        _search_client = VectorSearchClient()
    return _search_client


def search_resume_content(query_text, limit=None):
    """
    Convenience function to search resume content.
    
    Args:
        query_text (str): Query text
        limit (int): Maximum number of results
        
    Returns:
        list: Search results
    """
    client = get_search_client()
    return client.search(query_text, limit)