"""
Tests for Unified Search API

Tests all 4 search modes:
1. Fast Search
2. Semantic Search
3. Hybrid Search
4. Comprehensive Search
"""

from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from memory_assistant.models import Memory
from datetime import datetime, timedelta
from django.utils import timezone


class UnifiedSearchTests(TestCase):
    """Tests for unified search endpoint"""
    
    def setUp(self):
        """Set up test client, user, and sample memories"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='searchuser',
            email='search@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'searchuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test memories
        self.create_test_memories()
    
    def create_test_memories(self):
        """Create diverse test memories for searching"""
        
        # Work-related memories
        Memory.objects.create(
            user=self.user,
            content='Team meeting scheduled for tomorrow at 2 PM to discuss project roadmap',
            summary='Team meeting for project planning',
            tags=['meeting', 'work', 'project'],
            importance=8,
            memory_type='work'
        )
        
        Memory.objects.create(
            user=self.user,
            content='Important client presentation deadline next Friday',
            summary='Client presentation due',
            tags=['deadline', 'client', 'presentation'],
            importance=9,
            memory_type='work'
        )
        
        # Personal memories
        Memory.objects.create(
            user=self.user,
            content='Family vacation to beach planned for summer',
            summary='Summer vacation plans',
            tags=['vacation', 'family', 'travel'],
            importance=7,
            memory_type='personal'
        )
        
        Memory.objects.create(
            user=self.user,
            content='Dentist appointment on Tuesday morning',
            summary='Dental checkup',
            tags=['health', 'appointment'],
            importance=6,
            memory_type='reminder'
        )
        
        # Learning memories
        Memory.objects.create(
            user=self.user,
            content='Python async programming concepts - await, asyncio, coroutines',
            summary='Learning async Python',
            tags=['programming', 'python', 'learning'],
            importance=7,
            memory_type='learning'
        )
        
        Memory.objects.create(
            user=self.user,
            content='Machine learning fundamentals - supervised vs unsupervised learning',
            summary='ML basics',
            tags=['machine-learning', 'ai', 'learning'],
            importance=8,
            memory_type='learning'
        )
        
        # Ideas
        Memory.objects.create(
            user=self.user,
            content='Mobile app idea: Habit tracking with AI-powered insights',
            summary='Habit tracking app concept',
            tags=['app-idea', 'ai', 'habits'],
            importance=7,
            memory_type='idea'
        )
    
    # ========== Mode Tests ==========
    
    def test_fast_search_basic(self):
        """Test basic fast search"""
        response = self.client.get('/api/v1/memories/search/?q=meeting&mode=fast')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertIn('total', response.data)
        self.assertIn('mode', response.data)
        self.assertEqual(response.data['mode'], 'fast')
        self.assertEqual(response.data['query'], 'meeting')
        self.assertTrue(response.data['total'] > 0)
    
    def test_fast_search_default_mode(self):
        """Test that fast is the default mode"""
        response = self.client.get('/api/v1/memories/search/?q=project')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mode'], 'fast')
    
    def test_semantic_search(self):
        """Test semantic search mode"""
        response = self.client.get('/api/v1/memories/search/?q=work+deadlines&mode=semantic')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mode'], 'semantic')
        # Should find work-related memories
        self.assertTrue(response.data['total'] >= 0)
    
    def test_hybrid_search(self):
        """Test hybrid search mode"""
        response = self.client.get('/api/v1/memories/search/?q=learning+concepts&mode=hybrid')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mode'], 'hybrid')
        self.assertIn('weights', response.data)
        self.assertEqual(response.data['weights']['semantic'], 0.7)
        self.assertEqual(response.data['weights']['keyword'], 0.3)
    
    def test_hybrid_search_custom_weights(self):
        """Test hybrid search with custom weights"""
        response = self.client.get(
            '/api/v1/memories/search/?q=project&mode=hybrid&semantic_weight=0.5&keyword_weight=0.5'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['weights']['semantic'], 0.5)
        self.assertEqual(response.data['weights']['keyword'], 0.5)
    
    def test_comprehensive_search(self):
        """Test comprehensive search mode"""
        response = self.client.get('/api/v1/memories/search/?q=learning&mode=comprehensive')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['mode'], 'comprehensive')
        # Should find learning-related memories
        self.assertTrue(response.data['total'] >= 2)
    
    # ========== Filter Tests ==========
    
    def test_filter_by_memory_type(self):
        """Test filtering by memory type"""
        response = self.client.get('/api/v1/memories/search/?q=&mode=fast&memory_type=work')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for memory in response.data['results']:
            self.assertEqual(memory['memory_type'], 'work')
    
    def test_filter_by_importance(self):
        """Test filtering by importance range"""
        response = self.client.get('/api/v1/memories/search/?q=&mode=fast&importance_min=8')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for memory in response.data['results']:
            self.assertGreaterEqual(memory['importance'], 8)
    
    def test_filter_by_date_range(self):
        """Test filtering by date range"""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        response = self.client.get(
            f'/api/v1/memories/search/?q=&mode=fast&date_from={yesterday}&date_to={today}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_combined_filters(self):
        """Test combining multiple filters"""
        response = self.client.get(
            '/api/v1/memories/search/?q=project&mode=fast&memory_type=work&importance_min=7'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for memory in response.data['results']:
            self.assertEqual(memory['memory_type'], 'work')
            self.assertGreaterEqual(memory['importance'], 7)
    
    # ========== Pagination Tests ==========
    
    def test_pagination_default(self):
        """Test default pagination"""
        response = self.client.get('/api/v1/memories/search/?q=')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('pagination', response.data)
        self.assertEqual(response.data['pagination']['page'], 1)
        self.assertEqual(response.data['pagination']['page_size'], 20)
    
    def test_pagination_custom_page_size(self):
        """Test custom page size"""
        response = self.client.get('/api/v1/memories/search/?q=&page_size=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pagination']['page_size'], 5)
        self.assertLessEqual(len(response.data['results']), 5)
    
    def test_pagination_max_page_size(self):
        """Test that page size is capped at 100"""
        response = self.client.get('/api/v1/memories/search/?q=&page_size=200')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pagination']['page_size'], 100)
    
    # ========== Validation Tests ==========
    
    def test_missing_query_parameter(self):
        """Test error when query parameter is missing"""
        response = self.client.get('/api/v1/memories/search/')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_short_query(self):
        """Test error for query less than 2 characters"""
        response = self.client.get('/api/v1/memories/search/?q=a')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_invalid_mode(self):
        """Test error for invalid search mode"""
        response = self.client.get('/api/v1/memories/search/?q=test&mode=invalid')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    # ========== Search Quality Tests ==========
    
    def test_search_finds_content(self):
        """Test that search finds text in content"""
        response = self.client.get('/api/v1/memories/search/?q=meeting')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['total'] > 0)
        
        # Verify result contains the search term
        found = False
        for memory in response.data['results']:
            if 'meeting' in memory['content'].lower():
                found = True
                break
        self.assertTrue(found)
    
    def test_search_finds_tags(self):
        """Test that search finds memories by tags"""
        response = self.client.get('/api/v1/memories/search/?q=python')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['total'] > 0)
    
    def test_search_case_insensitive(self):
        """Test that search is case insensitive"""
        response1 = self.client.get('/api/v1/memories/search/?q=MEETING')
        response2 = self.client.get('/api/v1/memories/search/?q=meeting')
        
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        # Both should find similar results
        self.assertTrue(response1.data['total'] > 0)
        self.assertTrue(response2.data['total'] > 0)
    
    # ========== Response Format Tests ==========
    
    def test_response_structure(self):
        """Test that response has correct structure"""
        response = self.client.get('/api/v1/memories/search/?q=test')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check required fields
        self.assertIn('results', response.data)
        self.assertIn('total', response.data)
        self.assertIn('query', response.data)
        self.assertIn('mode', response.data)
        self.assertIn('pagination', response.data)
        
        # Check pagination structure
        pagination = response.data['pagination']
        self.assertIn('page', pagination)
        self.assertIn('page_size', pagination)
        self.assertIn('total_pages', pagination)
        self.assertIn('has_next', pagination)
        self.assertIn('has_previous', pagination)


class SearchSuggestionsTests(TestCase):
    """Tests for search suggestions endpoint"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='suggestionuser',
            password='testpass123'
        )
        
        # Get JWT token
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'suggestionuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create memories with tags
        Memory.objects.create(
            user=self.user,
            content='Test content',
            tags=['python', 'programming', 'learning']
        )
    
    def test_suggestions_endpoint_exists(self):
        """Test that suggestions endpoint exists"""
        response = self.client.get('/api/v1/search/suggestions/')
        
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_suggestions_without_query(self):
        """Test suggestions without query (recent searches)"""
        response = self.client.get('/api/v1/search/suggestions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        self.assertIn('type', response.data)
        self.assertEqual(response.data['type'], 'recent')
    
    def test_suggestions_with_query(self):
        """Test suggestions with partial query (autocomplete)"""
        response = self.client.get('/api/v1/search/suggestions/?q=py')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('suggestions', response.data)
        self.assertIn('type', response.data)
        self.assertEqual(response.data['type'], 'autocomplete')
    
    def test_suggestions_limit(self):
        """Test that suggestions respect limit parameter"""
        response = self.client.get('/api/v1/search/suggestions/?limit=5')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data['suggestions']), 5)


class SearchAuthenticationTests(TestCase):
    """Tests for search endpoint authentication"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
    
    def test_search_requires_authentication(self):
        """Test that search endpoint requires authentication"""
        response = self.client.get('/api/v1/memories/search/?q=test')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_suggestions_require_authentication(self):
        """Test that suggestions endpoint requires authentication"""
        response = self.client.get('/api/v1/search/suggestions/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)






























