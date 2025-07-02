#!/usr/bin/env python3
"""
Lightweight Embeddings for AWS Free Tier
Uses TF-IDF instead of transformer models to avoid heavy dependencies
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os
from typing import List, Union

class LightweightEmbeddings:
    """
    Lightweight embedding class using TF-IDF
    Designed for AWS Free Tier with minimal memory footprint
    """

    def __init__(self, max_features: int = 5000, cache_dir: str = "/app/data/embeddings_cache"):
        """
        Initialize lightweight embeddings

        Args:
            max_features: Maximum number of TF-IDF features
            cache_dir: Directory to cache the vectorizer
        """
        self.max_features = max_features
        self.cache_dir = cache_dir
        self.vectorizer = None
        self.is_fitted = False

        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        self.vectorizer_path = os.path.join(cache_dir, "tfidf_vectorizer.pkl")

        # Try to load existing vectorizer
        self._load_vectorizer()

    def _load_vectorizer(self):
        """Load existing vectorizer from cache"""
        try:
            if os.path.exists(self.vectorizer_path):
                with open(self.vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                    self.is_fitted = True
                print("✅ Loaded cached TF-IDF vectorizer")
        except Exception as e:
            print(f"⚠️ Could not load cached vectorizer: {e}")
            self._create_vectorizer()

    def _create_vectorizer(self):
        """Create new TF-IDF vectorizer"""
        self.vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            stop_words='english',
            lowercase=True,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,
            max_df=0.95
        )
        self.is_fitted = False
        print("✅ Created new TF-IDF vectorizer")

    def _save_vectorizer(self):
        """Save vectorizer to cache"""
        try:
            with open(self.vectorizer_path, 'wb') as f:
                pickle.dump(self.vectorizer, f)
            print("✅ Saved TF-IDF vectorizer to cache")
        except Exception as e:
            print(f"⚠️ Could not save vectorizer: {e}")

    def fit(self, documents: List[str]):
        """
        Fit the vectorizer on documents

        Args:
            documents: List of text documents
        """
        if not self.is_fitted:
            print(f"🔧 Fitting TF-IDF on {len(documents)} documents...")
            self.vectorizer.fit(documents)
            self.is_fitted = True
            self._save_vectorizer()
            print("✅ TF-IDF vectorizer fitted and cached")

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Create embeddings for documents

        Args:
            documents: List of text documents

        Returns:
            numpy array of embeddings
        """
        if not self.is_fitted:
            self.fit(documents)

        embeddings = self.vectorizer.transform(documents)
        return embeddings.toarray()

    def embed_query(self, query: str) -> np.ndarray:
        """
        Create embedding for a single query

        Args:
            query: Query text

        Returns:
            numpy array embedding
        """
        if not self.is_fitted:
            raise ValueError("Vectorizer not fitted. Call fit() or embed_documents() first.")

        embedding = self.vectorizer.transform([query])
        return embedding.toarray()[0]

    def similarity(self, query_embedding: np.ndarray, doc_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between query and documents

        Args:
            query_embedding: Query embedding
            doc_embeddings: Document embeddings

        Returns:
            Array of similarity scores
        """
        query_embedding = query_embedding.reshape(1, -1)
        similarities = cosine_similarity(query_embedding, doc_embeddings)
        return similarities[0]

    def get_stats(self) -> dict:
        """Get vectorizer statistics"""
        if not self.is_fitted:
            return {"status": "not_fitted"}

        return {
            "status": "fitted",
            "vocabulary_size": len(self.vectorizer.vocabulary_),
            "max_features": self.max_features,
            "feature_names_count": len(self.vectorizer.get_feature_names_out())
        }

# Global instance for AWS Free Tier
lightweight_embeddings = LightweightEmbeddings()

def get_lightweight_embeddings() -> LightweightEmbeddings:
    """Get the global lightweight embeddings instance"""
    return lightweight_embeddings
