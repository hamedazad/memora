# Search Functionality Guide

**Version:** 1.0.0  
**Last Updated:** 2025-01-12  
**Status:** ✅ IMPLEMENTED

---

## 📋 Overview

The Memora API now provides a **unified search endpoint** that supports **4 different search modes** to match the mobile app's requirements:

1. **Fast Search** - Traditional keyword-based search (default)
2. **Semantic Search** - AI-powered meaning-based search
3. **Hybrid Search** - Combines semantic + keyword with weighted scoring
4. **Comprehensive Search** - Searches across all fields

---

## 🎯 Unified Search Endpoint

### Base Endpoint
```
GET /api/v1/memories/search/
```

### Authentication
- **Required:** JWT Bearer token
- **Header:** `Authorization: Bearer <access_token>`

---

## 📊 Search Modes

### 1. Fast Search (Default)

**Best for:** Quick keyword-based searches, basic queries

**Mode Parameter:** `mode=fast` or omit (default)

**How it works:**
- Searches in: content, summary, tags
- Uses database `ILIKE` for case-insensitive matching
- Fastest performance
- Order by: created_at (newest first)

**Example Request:**
```http
GET /api/v1/memories/search/?q=meeting&mode=fast
Authorization: Bearer <token>
```

**Example Response:**
```json
{
  "results": [
    {
      "id": 123,
      "content": "Team meeting notes...",
      "memory_type": "work",
      "importance": 7,
      "created_at": "2025-01-12T10:00:00Z",
      ...
    }
  ],
  "total": 15,
  "query": "meeting",
  "mode": "fast",
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

---

### 2. Semantic Search

**Best for:** AI-powered searches, finding by meaning, conceptual queries

**Mode Parameter:** `mode=semantic`

**How it works:**
- Uses AI/embeddings to understand query meaning
- Searches by semantic similarity, not just keywords
- Searches in: content, summary, ai_reasoning, tags
- Falls back to enhanced keyword search if AI unavailable
- Order by: importance, then created_at

**Example Request:**
```http
GET /api/v1/memories/search/?q=important+work+deadlines&mode=semantic
Authorization: Bearer <token>
```

**Use Cases:**
- "memories about health and wellness"
- "ideas related to business growth"
- "reminders for family events"

**Fallback Behavior:**
- If OpenAI API unavailable, uses enhanced keyword matching
- Breaks query into words and searches across all fields
- Still provides good results without AI

---

### 3. Hybrid Search

**Best for:** Best of both worlds, most accurate results

**Mode Parameter:** `mode=hybrid`

**Additional Parameters:**
- `semantic_weight` - Weight for semantic score (default: 0.7)
- `keyword_weight` - Weight for keyword score (default: 0.3)

**How it works:**
1. Performs both semantic and keyword search
2. Calculates weighted score for each result
3. Combines and ranks by final score
4. Returns best matches from both methods

**Example Request:**
```http
GET /api/v1/memories/search/?q=project+planning&mode=hybrid&semantic_weight=0.6&keyword_weight=0.4
Authorization: Bearer <token>
```

**Example Response:**
```json
{
  "results": [...],
  "total": 25,
  "query": "project planning",
  "mode": "hybrid",
  "weights": {
    "semantic": 0.6,
    "keyword": 0.4
  },
  "pagination": {...}
}
```

**Scoring Formula:**
```
final_score = (semantic_score × semantic_weight) + (keyword_score × keyword_weight)
```

---

### 4. Comprehensive Search

**Best for:** Thorough searches, finding everything related to a topic

**Mode Parameter:** `mode=comprehensive`

**How it works:**
- Searches in ALL fields:
  - content
  - summary
  - tags
  - ai_reasoning
  - memory_type
- Most thorough but potentially slower
- Order by: importance, then created_at
- Returns distinct results

**Example Request:**
```http
GET /api/v1/memories/search/?q=travel&mode=comprehensive
Authorization: Bearer <token>
```

**Use Cases:**
- When you want to find EVERYTHING related to a topic
- When you're not sure what field the information is in
- When you want maximum recall

---

## 🔍 Query Parameters Reference

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `q` | string | Search query (min 2 chars) | `q=meeting` |

### Optional Parameters

| Parameter | Type | Default | Description | Example |
|-----------|------|---------|-------------|---------|
| `mode` | string | `fast` | Search mode: `fast`, `semantic`, `hybrid`, `comprehensive` | `mode=semantic` |
| `page` | integer | `1` | Page number for pagination | `page=2` |
| `page_size` | integer | `20` | Results per page (max 100) | `page_size=50` |
| `memory_type` | string | none | Filter by memory type | `memory_type=work` |
| `importance_min` | integer | none | Minimum importance (1-10) | `importance_min=7` |
| `importance_max` | integer | none | Maximum importance (1-10) | `importance_max=9` |
| `date_from` | string | none | Start date (YYYY-MM-DD) | `date_from=2025-01-01` |
| `date_to` | string | none | End date (YYYY-MM-DD) | `date_to=2025-01-31` |
| `delivery_type` | string | none | Filter by delivery type | `delivery_type=scheduled` |
| `semantic_weight` | float | `0.7` | Hybrid mode: semantic weight | `semantic_weight=0.6` |
| `keyword_weight` | float | `0.3` | Hybrid mode: keyword weight | `keyword_weight=0.4` |

---

## 🎨 Complete Example Requests

### Basic Fast Search
```bash
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=project" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Semantic Search with Filters
```bash
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=important+deadlines&mode=semantic&memory_type=work&importance_min=8" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Hybrid Search with Custom Weights
```bash
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=team+collaboration&mode=hybrid&semantic_weight=0.8&keyword_weight=0.2&page_size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Comprehensive Search with Date Filter
```bash
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=travel&mode=comprehensive&date_from=2025-01-01&date_to=2025-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Paginated Search
```bash
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=meeting&page=2&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 Search Suggestions Endpoint

Get search suggestions based on user's history and content.

### Endpoint
```
GET /api/v1/search/suggestions/
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string (optional) | Partial query for autocomplete |
| `limit` | integer (optional) | Max suggestions (default: 10, max: 20) |

### Example: Recent Searches
```bash
curl -X GET "http://localhost:8000/api/v1/search/suggestions/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "suggestions": [
    "project deadlines",
    "team meeting",
    "vacation plans"
  ],
  "type": "recent"
}
```

### Example: Autocomplete
```bash
curl -X GET "http://localhost:8000/api/v1/search/suggestions/?q=proj" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "suggestions": [
    "project",
    "project-management",
    "project-ideas",
    "work"
  ],
  "type": "autocomplete",
  "query": "proj"
}
```

---

## 📱 Mobile App Integration

The unified search endpoint is **fully compatible** with the mobile app's search implementation.

### Flutter/Dart Example
```dart
// Fast search
final fastResults = await apiService.fastSearchMemories(
  query: 'meeting',
  memoryType: 'work',
  importanceMin: 7,
);

// Semantic search
final semanticResults = await apiService.semanticSearchMemories(
  query: 'important project deadlines',
  page: 1,
);

// Hybrid search
final hybridResults = await apiService.hybridSearchMemories(
  query: 'team collaboration',
  semanticWeight: 0.7,
  keywordWeight: 0.3,
);
```

### Mobile App Constants
Ensure these constants are set in `app_constants.dart`:
```dart
static const String searchEndpoint = '/memories/search/';
static const String semanticSearchEndpoint = '/search/semantic';  // Legacy
static const String searchSuggestionsEndpoint = '/search/suggestions/';
```

---

## 🚀 Performance Considerations

### Fast Search
- ⚡ **Fastest** - Direct database query
- 📊 **Scalability:** Excellent (uses indexes)
- 🎯 **Best for:** Real-time search, mobile apps
- 💾 **Caching:** Recommended for frequent queries

### Semantic Search
- 🐌 **Slower** - AI processing required
- 📊 **Scalability:** Moderate (API rate limits)
- 🎯 **Best for:** Complex queries, meaning-based search
- 💾 **Caching:** Strongly recommended

### Hybrid Search
- ⚖️ **Medium** - Combines both methods
- 📊 **Scalability:** Good (runs searches in sequence)
- 🎯 **Best for:** Best accuracy, important searches
- 💾 **Caching:** Recommended for common queries

### Comprehensive Search
- 🐌 **Slower** - Searches all fields
- 📊 **Scalability:** Moderate (complex query)
- 🎯 **Best for:** Thorough searches, admin
- 💾 **Caching:** Highly recommended

---

## 🔮 Future Enhancements

Consider implementing these for even better search:

### 1. Elasticsearch Integration
```python
# Install: pip install elasticsearch elasticsearch-dsl
from elasticsearch import Elasticsearch

class ElasticsearchService:
    def search(self, query, filters):
        # Full-text search with relevance scoring
        # Faceted search
        # Fuzzy matching
        # Autocomplete
        pass
```

**Benefits:**
- 10-100x faster for large datasets
- Better relevance scoring
- Advanced features (fuzzy matching, facets, aggregations)
- Real-time indexing

**Setup:**
```bash
# Docker
docker run -d -p 9200:9200 elasticsearch:8.11.0

# Configure in settings.py
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
```

### 2. Algolia Integration
```python
# Install: pip install algoliasearch
from algoliasearch.search_client import SearchClient

client = SearchClient.create('APP_ID', 'API_KEY')
index = client.init_index('memories')

# Search
results = index.search('query')
```

**Benefits:**
- Hosted solution (no infrastructure)
- Typo tolerance
- Instant search (as-you-type)
- Analytics dashboard
- Geo-search support

**Pricing:**
- Free tier: 10K records, 100K operations/month
- Pro: $0.40/1K records/month

### 3. Vector Embeddings
```python
# Using OpenAI embeddings
from openai import OpenAI

client = OpenAI()

# Generate embedding
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Your search query"
)

embedding = response.data[0].embedding

# Search by similarity
similar_memories = Memory.objects.filter(
    embedding__cosine_similarity__gte=0.8
)
```

**Benefits:**
- True semantic understanding
- Cross-lingual search
- Conceptual similarity
- Better than keyword matching

**Cost:**
- $0.020 per 1M tokens (text-embedding-3-small)
- ~$0.002 per 1K searches

---

## 🧪 Testing Search Functionality

### Backend Tests
```bash
cd c:\memora_core

# Test unified search
python manage.py test memory_assistant.tests.test_unified_search

# Test all search modes
python manage.py test memory_assistant.tests.test_search_modes
```

### Mobile App Tests
```bash
cd c:\memora_mobile\memora_phone

# Test search endpoint integration
flutter test test/integration/search_integration_test.dart
```

### Manual Testing with cURL

```bash
# Set your token
TOKEN="your_jwt_token_here"

# Test fast search
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=test&mode=fast" \
  -H "Authorization: Bearer $TOKEN"

# Test semantic search
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=important+work&mode=semantic" \
  -H "Authorization: Bearer $TOKEN"

# Test hybrid search
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=meeting&mode=hybrid" \
  -H "Authorization: Bearer $TOKEN"

# Test with filters
curl -X GET "http://localhost:8000/api/v1/memories/search/?q=project&memory_type=work&importance_min=7" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Response Format

### Success Response (200 OK)
```json
{
  "results": [
    {
      "id": 123,
      "user": {...},
      "content": "Memory content...",
      "summary": "Summary...",
      "tags": ["tag1", "tag2"],
      "importance": 7,
      "memory_type": "work",
      "created_at": "2025-01-12T10:00:00Z",
      "updated_at": "2025-01-12T10:00:00Z",
      ...
    }
  ],
  "total": 25,
  "query": "search query",
  "mode": "fast",
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 2,
    "has_next": true,
    "has_previous": false
  }
}
```

### Error Responses

**400 Bad Request** - Invalid parameters
```json
{
  "error": "Search query (q) is required"
}
```

**401 Unauthorized** - Missing or invalid token
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**500 Internal Server Error** - Server error
```json
{
  "error": "Search failed: [error details]"
}
```

---

## 🎓 Best Practices

### 1. Choose the Right Mode

| Use Case | Recommended Mode |
|----------|------------------|
| Quick search, mobile app | Fast |
| Natural language queries | Semantic |
| Maximum accuracy | Hybrid |
| Find everything | Comprehensive |

### 2. Use Filters Effectively
```
?q=meeting&memory_type=work&importance_min=8&date_from=2025-01-01
```

### 3. Implement Pagination
```
?q=project&page=1&page_size=20
```

### 4. Cache Results
- Cache search results for 5-10 minutes
- Use query + filters as cache key
- Invalidate on new memory creation

### 5. Debounce User Input
```dart
// Wait 500ms after user stops typing
Timer? _debounce;

void onSearchChanged(String query) {
  _debounce?.cancel();
  _debounce = Timer(Duration(milliseconds: 500), () {
    performSearch(query);
  });
}
```

---

## 📚 Related Documentation

- **API Endpoint Mapping:** `API_ENDPOINT_MAPPING.md`
- **API Versioning:** `API_VERSIONING_STRATEGY.md`
- **Swagger UI:** http://localhost:8000/api/docs/
- **Mobile App:** `memora_phone/lib/services/api_service.dart`

---

## ✅ Summary

**Status:** ✅ Unified search endpoint implemented

**Supported Modes:**
- ✅ Fast Search (keyword-based)
- ✅ Semantic Search (AI-powered)
- ✅ Hybrid Search (combined)
- ✅ Comprehensive Search (all fields)

**Features:**
- ✅ Full filtering support (type, importance, dates)
- ✅ Pagination
- ✅ Search suggestions
- ✅ Mobile app compatible
- ✅ Backward compatible with legacy endpoints

**Next Steps:**
1. Test the endpoint with various queries
2. Update mobile app to use unified endpoint
3. Consider Elasticsearch for production
4. Monitor search performance and optimize

---

**Questions?** Check the Swagger docs or test with the examples above!






























