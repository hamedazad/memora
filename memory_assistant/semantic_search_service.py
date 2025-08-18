"""
Semantic Search Service for Memory Assistant

This module provides semantic search functionality using OpenAI embeddings
to find memories by meaning, not just keywords.
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
from openai import OpenAI
from django.conf import settings
from django.db.models import Q
from dotenv import load_dotenv
import pickle
import hashlib

from .models import Memory

load_dotenv()


class SemanticSearchService:
    """
    Semantic search service using OpenAI embeddings for finding memories by meaning.
    """
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            try:
                self.client = OpenAI(api_key=api_key)
                self.embedding_model = "text-embedding-ada-002"
                self._available = True
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self._available = False
        else:
            self._available = False
    
    def is_available(self) -> bool:
        """Check if OpenAI API is available"""
        return self._available
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a given text using OpenAI's text-embedding-ada-002 model.
        
        Args:
            text: The text to generate embedding for
            
        Returns:
            List of floats representing the embedding, or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            # Clean and truncate text if too long (OpenAI has limits)
            cleaned_text = text.strip()
            if len(cleaned_text) > 8000:  # OpenAI limit is 8192 tokens, roughly 8000 chars
                cleaned_text = cleaned_text[:8000]
            
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=cleaned_text
            )
            
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity score between 0 and 1
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def prepare_memory_text(self, memory: Memory) -> str:
        """
        Prepare memory text for embedding generation by combining all relevant fields.
        
        Args:
            memory: Memory object
            
        Returns:
            Combined text string for embedding
        """
        text_parts = []
        
        # Main content
        if memory.content:
            text_parts.append(memory.content)
        
        # Summary
        if memory.summary:
            text_parts.append(f"Summary: {memory.summary}")
        
        # Tags
        if memory.tags:
            tags_text = ", ".join(memory.tags)
            text_parts.append(f"Tags: {tags_text}")
        
        # Memory type
        text_parts.append(f"Type: {memory.get_memory_type_display()}")
        
        # AI reasoning
        if memory.ai_reasoning:
            text_parts.append(f"Context: {memory.ai_reasoning}")
        
        # Delivery date info
        if memory.delivery_date:
            text_parts.append(f"Scheduled for: {memory.delivery_date.strftime('%Y-%m-%d %H:%M')}")
        
        return " | ".join(text_parts)
    
    def semantic_search(self, query: str, memories: List[Memory], top_k: int = 10, 
                       similarity_threshold: float = 0.3) -> List[Tuple[Memory, float]]:
        """
        Perform semantic search on memories using embeddings.
        
        Args:
            query: Search query
            memories: List of memories to search through
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score to include in results
            
        Returns:
            List of tuples (memory, similarity_score) sorted by similarity
        """
        if not self.is_available() or not memories:
            return []
        
        # Generate embedding for the query
        query_embedding = self.generate_embedding(query)
        if not query_embedding:
            return []
        
        # Calculate similarities for all memories
        memory_similarities = []
        
        for memory in memories:
            # Prepare memory text for embedding
            memory_text = self.prepare_memory_text(memory)
            
            # Generate embedding for memory
            memory_embedding = self.generate_embedding(memory_text)
            
            if memory_embedding:
                # Calculate similarity
                similarity = self.cosine_similarity(query_embedding, memory_embedding)
                
                # Only include if above threshold
                if similarity >= similarity_threshold:
                    memory_similarities.append((memory, similarity))
        
        # Sort by similarity (highest first) and return top_k results
        memory_similarities.sort(key=lambda x: x[1], reverse=True)
        return memory_similarities[:top_k]
    
    def hybrid_search(self, query: str, memories: List[Memory], top_k: int = 10,
                     semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> List[Tuple[Memory, float]]:
        """
        Perform hybrid search combining semantic and keyword matching.
        
        Args:
            query: Search query
            memories: List of memories to search through
            top_k: Number of top results to return
            semantic_weight: Weight for semantic similarity (0-1)
            keyword_weight: Weight for keyword matching (0-1)
            
        Returns:
            List of tuples (memory, combined_score) sorted by score
        """
        if not memories:
            return []
        
        # Get semantic search results
        semantic_results = {}
        if self.is_available():
            semantic_matches = self.semantic_search(query, memories, top_k=len(memories))
            for memory, score in semantic_matches:
                semantic_results[memory.id] = score
        
        # Get keyword search results
        keyword_results = {}
        query_lower = query.lower()
        query_words = query_lower.split()
        
        for memory in memories:
            memory_text = self.prepare_memory_text(memory).lower()
            
            # Calculate keyword score based on word matches
            word_matches = sum(1 for word in query_words if word in memory_text)
            keyword_score = word_matches / len(query_words) if query_words else 0
            
            if keyword_score > 0:
                keyword_results[memory.id] = keyword_score
        
        # Combine scores
        combined_results = {}
        all_memory_ids = set(semantic_results.keys()) | set(keyword_results.keys())
        
        for memory_id in all_memory_ids:
            semantic_score = semantic_results.get(memory_id, 0)
            keyword_score = keyword_results.get(memory_id, 0)
            
            # Normalize scores to 0-1 range
            combined_score = (semantic_score * semantic_weight) + (keyword_score * keyword_weight)
            combined_results[memory_id] = combined_score
        
        # Sort by combined score and return top results
        sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)
        
        # Convert back to memory objects
        memory_dict = {memory.id: memory for memory in memories}
        final_results = []
        
        for memory_id, score in sorted_results[:top_k]:
            if memory_id in memory_dict:
                final_results.append((memory_dict[memory_id], score))
        
        return final_results
    
    def find_similar_memories(self, memory: Memory, memories: List[Memory], 
                            top_k: int = 5, similarity_threshold: float = 0.5) -> List[Tuple[Memory, float]]:
        """
        Find memories similar to a given memory.
        
        Args:
            memory: Reference memory
            memories: List of memories to search through (excluding the reference memory)
            top_k: Number of similar memories to return
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of tuples (similar_memory, similarity_score)
        """
        if not self.is_available():
            return []
        
        # Exclude the reference memory from search
        other_memories = [m for m in memories if m.id != memory.id]
        if not other_memories:
            return []
        
        # Prepare reference memory text
        reference_text = self.prepare_memory_text(memory)
        reference_embedding = self.generate_embedding(reference_text)
        
        if not reference_embedding:
            return []
        
        # Find similar memories
        similar_memories = []
        
        for other_memory in other_memories:
            other_text = self.prepare_memory_text(other_memory)
            other_embedding = self.generate_embedding(other_text)
            
            if other_embedding:
                similarity = self.cosine_similarity(reference_embedding, other_embedding)
                if similarity >= similarity_threshold:
                    similar_memories.append((other_memory, similarity))
        
        # Sort by similarity and return top results
        similar_memories.sort(key=lambda x: x[1], reverse=True)
        return similar_memories[:top_k]
    
    def get_search_suggestions(self, query: str, memories: List[Memory], top_k: int = 5) -> List[str]:
        """
        Generate search suggestions based on the query and existing memories.
        
        Args:
            query: Current search query
            memories: List of memories to analyze
            top_k: Number of suggestions to return
            
        Returns:
            List of suggested search terms
        """
        if not self.is_available() or not memories:
            return []
        
        # Extract common themes from memories
        all_tags = []
        all_content = []
        
        for memory in memories:
            if memory.tags:
                all_tags.extend(memory.tags)
            if memory.content:
                all_content.append(memory.content[:100])  # First 100 chars
        
        # Find most common tags
        tag_counts = defaultdict(int)
        for tag in all_tags:
            tag_counts[tag.lower()] += 1
        
        # Generate suggestions based on query and common themes
        suggestions = []
        
        # Add query-related suggestions
        query_words = query.lower().split()
        for word in query_words:
            if len(word) >= 3:
                suggestions.append(f"Find memories about {word}")
        
        # Add tag-based suggestions
        common_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        for tag, count in common_tags:
            if tag not in query.lower():
                suggestions.append(f"Search for '{tag}'")
        
        # Add type-based suggestions
        memory_types = ['work', 'personal', 'learning', 'idea', 'reminder']
        for memory_type in memory_types:
            if memory_type not in query.lower():
                suggestions.append(f"Show {memory_type} memories")
        
        return suggestions[:top_k]
    
    def analyze_search_intent(self, query: str) -> Dict[str, Any]:
        """
        Analyze the search query to understand user intent.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with intent analysis
        """
        intent = {
            'query_type': 'general',
            'date_references': [],
            'memory_types': [],
            'keywords': [],
            'is_question': False,
            'sentiment': 'neutral'
        }
        
        query_lower = query.lower()
        
        # Check for date references
        date_keywords = {
            'today': 'today',
            'tonight': 'today',
            'tomorrow': 'tomorrow',
            'yesterday': 'yesterday',
            'this week': 'this_week',
            'next week': 'next_week',
            'this month': 'this_month',
            'next month': 'next_month'
        }
        
        for keyword, date_type in date_keywords.items():
            if keyword in query_lower:
                intent['date_references'].append(date_type)
                intent['query_type'] = 'time_based'
        
        # Check for memory type references
        type_keywords = {
            'work': 'work',
            'job': 'work',
            'meeting': 'work',
            'personal': 'personal',
            'family': 'personal',
            'friend': 'personal',
            'learning': 'learning',
            'study': 'learning',
            'course': 'learning',
            'idea': 'idea',
            'creative': 'idea',
            'reminder': 'reminder',
            'task': 'reminder',
            'todo': 'reminder'
        }
        
        for keyword, memory_type in type_keywords.items():
            if keyword in query_lower:
                intent['memory_types'].append(memory_type)
        
        # Check if it's a question
        question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which']
        intent['is_question'] = any(word in query_lower for word in question_words)
        
        # Extract keywords (words longer than 3 characters)
        words = query_lower.split()
        intent['keywords'] = [word for word in words if len(word) > 3]
        
        return intent
