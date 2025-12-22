"""
AI Response Caching Service

Caches AI responses to reduce OpenAI API costs and improve response times.
Implements TTL-based caching with automatic cleanup.
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import pickle


class AICacheService:
    """
    Cache AI responses to reduce API costs and improve performance
    """
    
    def __init__(self, cache_dir='ai_cache'):
        """
        Initialize cache service
        
        Args:
            cache_dir: Directory to store cache files (default: 'ai_cache')
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # TTL settings (in hours)
        self.ttl_settings = {
            'categorize': 24 * 7,  # 7 days - content categorization rarely changes
            'summarize': 24 * 7,   # 7 days - summaries are stable
            'tags': 24 * 7,        # 7 days - tags are stable
            'enhance': 24,         # 1 day - enhancements might be refined
            'suggestions': 1,      # 1 hour - suggestions should be fresh
            'semantic_search': 4,  # 4 hours - search results should be reasonably fresh
        }
        
        # Cost tracking
        self.cost_savings = {
            'total_saved': 0.0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
        
        self._load_cost_savings()
    
    def _generate_cache_key(self, operation: str, content: str, params: Optional[Dict] = None) -> str:
        """
        Generate unique cache key for an operation
        
        Args:
            operation: Type of AI operation (categorize, summarize, etc.)
            content: The content being processed
            params: Additional parameters that affect the result
            
        Returns:
            Unique cache key as hex string
        """
        # Create a string that uniquely identifies this request
        cache_input = f"{operation}:{content}"
        
        if params:
            # Sort params to ensure consistent key generation
            sorted_params = sorted(params.items())
            cache_input += f":{json.dumps(sorted_params)}"
        
        # Generate hash
        return hashlib.sha256(cache_input.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _load_cost_savings(self):
        """Load cost savings data from file"""
        cost_file = self.cache_dir / 'cost_savings.json'
        if cost_file.exists():
            try:
                with open(cost_file, 'r') as f:
                    self.cost_savings = json.load(f)
            except Exception:
                pass
    
    def _save_cost_savings(self):
        """Save cost savings data to file"""
        cost_file = self.cache_dir / 'cost_savings.json'
        try:
            with open(cost_file, 'w') as f:
                json.dump(self.cost_savings, f)
        except Exception:
            pass
    
    def get(self, operation: str, content: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached AI response if available and not expired
        
        Args:
            operation: Type of AI operation
            content: The content being processed
            params: Additional parameters
            
        Returns:
            Cached response dict or None if cache miss
        """
        cache_key = self._generate_cache_key(operation, content, params)
        cache_path = self._get_cache_path(cache_key)
        
        # Check if cache file exists
        if not cache_path.exists():
            self.cost_savings['cache_misses'] += 1
            return None
        
        try:
            # Load cache file
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Check if expired
            ttl_hours = self.ttl_settings.get(operation, 24)
            expiry_time = cached_data['timestamp'] + timedelta(hours=ttl_hours)
            
            if datetime.now() > expiry_time:
                # Cache expired, delete file
                cache_path.unlink()
                self.cost_savings['cache_misses'] += 1
                return None
            
            # Cache hit!
            self.cost_savings['cache_hits'] += 1
            
            # Estimate cost saved (assuming ~500 tokens per request)
            cost_per_request = 0.0015 * 0.5  # $0.0015 per 1K tokens × 0.5K tokens
            self.cost_savings['total_saved'] += cost_per_request
            
            self._save_cost_savings()
            
            return cached_data['response']
            
        except Exception as e:
            print(f"Error loading cache: {e}")
            self.cost_savings['cache_misses'] += 1
            return None
    
    def set(self, operation: str, content: str, response: Dict[str, Any], params: Optional[Dict] = None):
        """
        Cache an AI response
        
        Args:
            operation: Type of AI operation
            content: The content that was processed
            response: The AI response to cache
            params: Additional parameters used
        """
        cache_key = self._generate_cache_key(operation, content, params)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Prepare cache data
            cache_data = {
                'timestamp': datetime.now(),
                'operation': operation,
                'response': response,
                'content_hash': hashlib.md5(content.encode()).hexdigest()[:8]
            }
            
            # Save to file
            with open(cache_path, 'wb') as f:
                pickle.dump(cache_data, f)
                
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def clear_expired(self):
        """Clear all expired cache entries"""
        cleared_count = 0
        
        for cache_file in self.cache_dir.glob('*.cache'):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # Determine operation type from filename or default TTL
                operation = cached_data.get('operation', 'default')
                ttl_hours = self.ttl_settings.get(operation, 24)
                expiry_time = cached_data['timestamp'] + timedelta(hours=ttl_hours)
                
                if datetime.now() > expiry_time:
                    cache_file.unlink()
                    cleared_count += 1
                    
            except Exception:
                # If we can't read it, delete it
                cache_file.unlink()
                cleared_count += 1
        
        return cleared_count
    
    def clear_all(self):
        """Clear all cache entries"""
        cleared_count = 0
        
        for cache_file in self.cache_dir.glob('*.cache'):
            cache_file.unlink()
            cleared_count += 1
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics
        
        Returns:
            Dict with cache statistics
        """
        # Count cache files
        cache_files = list(self.cache_dir.glob('*.cache'))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        # Calculate cache hit rate
        total_requests = self.cost_savings['cache_hits'] + self.cost_savings['cache_misses']
        hit_rate = (self.cost_savings['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_entries': len(cache_files),
            'cache_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_hits': self.cost_savings['cache_hits'],
            'cache_misses': self.cost_savings['cache_misses'],
            'hit_rate_percent': round(hit_rate, 1),
            'total_cost_saved': round(self.cost_savings['total_saved'], 4),
            'ttl_settings': self.ttl_settings,
        }
    
    def get_cached_count_by_operation(self) -> Dict[str, int]:
        """Get count of cached items by operation type"""
        counts = {}
        
        for cache_file in self.cache_dir.glob('*.cache'):
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                operation = cached_data.get('operation', 'unknown')
                counts[operation] = counts.get(operation, 0) + 1
            except Exception:
                pass
        
        return counts


# Singleton instance
_cache_service = None

def get_cache_service() -> AICacheService:
    """Get singleton cache service instance"""
    global _cache_service
    if _cache_service is None:
        _cache_service = AICacheService()
    return _cache_service




























