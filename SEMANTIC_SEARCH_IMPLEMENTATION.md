# Semantic Search Implementation Guide

## Overview

This document explains the implementation of semantic search functionality in Memora Memory Assistant, which allows users to find memories by meaning rather than just keywords.

## 🎯 What is Semantic Search?

Semantic search goes beyond traditional keyword matching to understand the **meaning** and **context** of your search queries. Instead of just looking for exact word matches, it uses AI to understand:

- **Conceptual relationships** (e.g., "meeting" finds "team discussion", "brainstorming session")
- **Synonyms and related terms** (e.g., "family" finds "mom", "dinner with loved ones")
- **Context and intent** (e.g., "work stuff" finds professional memories, meetings, projects)
- **Semantic similarity** (e.g., "AI technology" finds machine learning, algorithms, embeddings)

## 🏗️ Architecture

### Core Components

1. **SemanticSearchService** (`semantic_search_service.py`)
   - Main service class handling all semantic search operations
   - Uses OpenAI's text-embedding-ada-002 model for generating embeddings
   - Implements cosine similarity for comparing memory vectors

2. **Enhanced Search View** (`views.py`)
   - Updated search_memories view to integrate semantic search
   - Supports multiple search types: hybrid, semantic, keyword
   - Provides fallback to traditional search when AI is unavailable

3. **Updated Templates** (`search_results.html`)
   - Enhanced UI showing similarity scores
   - Search intent analysis display
   - Search suggestions and recommendations

## 🔧 Technical Implementation

### 1. Embedding Generation

```python
def generate_embedding(self, text: str) -> Optional[List[float]]:
    """Generate embedding for a given text using OpenAI's text-embedding-ada-002 model."""
    if not self.is_available():
        return None
    
    try:
        # Clean and truncate text if too long
        cleaned_text = text.strip()
        if len(cleaned_text) > 8000:
            cleaned_text = cleaned_text[:8000]
        
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=cleaned_text
        )
        
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None
```

### 2. Memory Text Preparation

The system combines all relevant memory fields to create comprehensive embeddings:

```python
def prepare_memory_text(self, memory: Memory) -> str:
    """Prepare memory text for embedding generation."""
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
```

### 3. Semantic Similarity Calculation

```python
def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
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
```

## 🚀 Search Types

### 1. Pure Semantic Search

Finds memories based purely on semantic similarity:

```python
def semantic_search(self, query: str, memories: List[Memory], top_k: int = 10, 
                   similarity_threshold: float = 0.3) -> List[Tuple[Memory, float]]:
    """Perform semantic search on memories using embeddings."""
    # Generate embedding for the query
    query_embedding = self.generate_embedding(query)
    
    # Calculate similarities for all memories
    memory_similarities = []
    for memory in memories:
        memory_text = self.prepare_memory_text(memory)
        memory_embedding = self.generate_embedding(memory_text)
        
        if memory_embedding:
            similarity = self.cosine_similarity(query_embedding, memory_embedding)
            if similarity >= similarity_threshold:
                memory_similarities.append((memory, similarity))
    
    # Sort by similarity and return top results
    memory_similarities.sort(key=lambda x: x[1], reverse=True)
    return memory_similarities[:top_k]
```

### 2. Hybrid Search

Combines semantic and keyword matching for optimal results:

```python
def hybrid_search(self, query: str, memories: List[Memory], top_k: int = 10,
                 semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> List[Tuple[Memory, float]]:
    """Perform hybrid search combining semantic and keyword matching."""
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
        combined_score = (semantic_score * semantic_weight) + (keyword_score * keyword_weight)
        combined_results[memory_id] = combined_score
    
    # Sort and return results
    sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)
    return [(memory_dict[memory_id], score) for memory_id, score in sorted_results[:top_k]]
```

## 🧠 Advanced Features

### 1. Search Intent Analysis

Analyzes user queries to understand their intent:

```python
def analyze_search_intent(self, query: str) -> Dict[str, Any]:
    """Analyze the search query to understand user intent."""
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
        'next week': 'next_week'
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
        'learning': 'learning',
        'study': 'learning',
        'idea': 'idea',
        'creative': 'idea',
        'reminder': 'reminder',
        'task': 'reminder'
    }
    
    for keyword, memory_type in type_keywords.items():
        if keyword in query_lower:
            intent['memory_types'].append(memory_type)
    
    # Check if it's a question
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'which']
    intent['is_question'] = any(word in query_lower for word in question_words)
    
    return intent
```

### 2. Search Suggestions

Generates intelligent search suggestions based on existing memories:

```python
def get_search_suggestions(self, query: str, memories: List[Memory], top_k: int = 5) -> List[str]:
    """Generate search suggestions based on the query and existing memories."""
    # Extract common themes from memories
    all_tags = []
    for memory in memories:
        if memory.tags:
            all_tags.extend(memory.tags)
    
    # Find most common tags
    tag_counts = defaultdict(int)
    for tag in all_tags:
        tag_counts[tag.lower()] += 1
    
    # Generate suggestions
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
    
    return suggestions[:top_k]
```

### 3. Similar Memories Discovery

Finds memories similar to a given memory:

```python
def find_similar_memories(self, memory: Memory, memories: List[Memory], 
                         top_k: int = 5, similarity_threshold: float = 0.5) -> List[Tuple[Memory, float]]:
    """Find memories similar to a given memory."""
    # Exclude the reference memory from search
    other_memories = [m for m in memories if m.id != memory.id]
    
    # Prepare reference memory text
    reference_text = self.prepare_memory_text(memory)
    reference_embedding = self.generate_embedding(reference_text)
    
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
```

## 🎨 User Interface Features

### 1. Search Type Selection

Users can choose between different search types:

- **Hybrid (Recommended)**: Combines semantic understanding with keyword matching
- **Semantic Only**: Pure semantic search using AI embeddings
- **Keyword Only**: Traditional keyword-based search

### 2. Similarity Score Display

Search results show similarity scores when using semantic search:

```
[0.85] WORK: Had a great meeting with the development team...
[0.72] LEARNING: Learned about machine learning algorithms...
[0.68] IDEA: Got an idea for a new productivity app...
```

### 3. Search Intent Analysis

The UI displays analysis of the user's search intent:

```
🔍 Search Intent Analysis:
  📊 Time-based search
  📊 Question detected  
  📊 Memory types: work
  📊 Keywords: meeting, team
```

### 4. Search Suggestions

Intelligent suggestions help users refine their searches:

```
💡 Search Suggestions:
  💭 Find memories about "meeting"
  💭 Search for "development"
  💭 Show work memories
  💭 Search for "AI"
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for semantic search
OPENAI_API_KEY=your_openai_api_key_here
```

### Dependencies

```txt
openai==1.98.0
numpy==1.24.3
scikit-learn==1.3.0
```

## 🧪 Testing

### Test Script

Run the test script to verify semantic search functionality:

```bash
python test_semantic_search.py
```

This script will:
1. Create test memories with different themes
2. Test semantic search with various queries
3. Test hybrid search functionality
4. Test search suggestions and intent analysis
5. Test similar memories discovery

### Example Test Queries

```python
test_queries = [
    "artificial intelligence and machine learning",
    "family time and personal activities", 
    "work meetings and team collaboration",
    "health and medical appointments",
    "creative ideas and innovation",
    "outdoor activities and nature",
    "technology and software development"
]
```

## 📊 Performance Considerations

### 1. Embedding Generation

- **Cost**: Each embedding generation costs ~$0.0001 per 1K tokens
- **Speed**: Embedding generation takes ~100-500ms per request
- **Caching**: Consider implementing embedding caching for frequently accessed memories

### 2. Similarity Calculation

- **Complexity**: O(n) where n is the number of memories
- **Optimization**: For large datasets, consider:
  - Pre-computing embeddings
  - Using approximate nearest neighbor search
  - Implementing vector databases (Pinecone, Weaviate, etc.)

### 3. Fallback Strategy

The system gracefully falls back to traditional search when:
- OpenAI API is unavailable
- Embedding generation fails
- No semantic results are found above threshold

## 🚀 Future Enhancements

### 1. Vector Database Integration

Consider integrating with vector databases for better performance:

```python
# Example with Pinecone
import pinecone

pinecone.init(api_key="your-pinecone-key", environment="us-west1-gcp")
index = pinecone.Index("memories")

# Store embeddings
index.upsert(vectors=[(memory_id, embedding, metadata)])

# Search
results = index.query(vector=query_embedding, top_k=10)
```

### 2. Embedding Caching

Implement caching to reduce API calls:

```python
import redis
import pickle

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_embedding(text: str) -> Optional[List[float]]:
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cached = redis_client.get(f"embedding:{text_hash}")
    return pickle.loads(cached) if cached else None

def cache_embedding(text: str, embedding: List[float]):
    text_hash = hashlib.md5(text.encode()).hexdigest()
    redis_client.setex(f"embedding:{text_hash}", 3600, pickle.dumps(embedding))
```

### 3. Multi-language Support

Extend semantic search to support multiple languages:

```python
def detect_language(text: str) -> str:
    """Detect the language of the text."""
    # Use language detection library
    from langdetect import detect
    return detect(text)

def get_language_specific_embedding(text: str, language: str) -> List[float]:
    """Get embedding optimized for specific language."""
    # Use language-specific embedding models
    if language == 'es':
        model = "text-embedding-ada-002"  # OpenAI supports multiple languages
    return generate_embedding(text)
```

### 4. Contextual Search

Implement context-aware search based on user behavior:

```python
def contextual_search(query: str, user_context: Dict) -> List[Memory]:
    """Search with user context awareness."""
    # Consider recent searches
    # Consider user preferences
    # Consider time of day, day of week
    # Consider current projects or tasks
    pass
```

## 🎯 Benefits

### For Users

1. **Natural Language Queries**: Search using everyday language
2. **Conceptual Understanding**: Find related memories even without exact keywords
3. **Better Discovery**: Discover memories you might have forgotten about
4. **Intelligent Suggestions**: Get helpful search recommendations
5. **Context Awareness**: Search understands your intent and context

### For Developers

1. **Scalable Architecture**: Easy to extend and modify
2. **Fallback Support**: Graceful degradation when AI is unavailable
3. **Performance Optimized**: Efficient similarity calculations
4. **Modular Design**: Clean separation of concerns
5. **Comprehensive Testing**: Thorough test coverage

## 🔍 Example Use Cases

### 1. Finding Work Memories

**Query**: "meetings and team stuff"
**Finds**: 
- Team brainstorming sessions
- Development team meetings
- Project discussions
- Collaboration activities

### 2. Finding Personal Memories

**Query**: "family time"
**Finds**:
- Dinner with family
- Vacation plans
- Family activities
- Personal celebrations

### 3. Finding Learning Content

**Query**: "AI and technology"
**Finds**:
- Machine learning courses
- Technology articles
- Programming concepts
- Algorithm studies

### 4. Finding Ideas

**Query**: "creative thoughts"
**Finds**:
- App ideas
- Innovation concepts
- Creative projects
- Problem-solving ideas

## 📝 Conclusion

The semantic search implementation provides a powerful, AI-driven search experience that goes far beyond traditional keyword matching. By understanding the meaning and context of user queries, it helps users discover relevant memories more effectively and naturally.

The modular architecture makes it easy to extend and improve the functionality, while the comprehensive fallback strategy ensures the system remains usable even when AI services are unavailable.
