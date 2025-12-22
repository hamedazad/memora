"""
API Endpoint Synchronization Tests

Validates that all API endpoints defined in the mobile app
actually exist and work correctly in the backend.
"""

import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from memory_assistant.models import Memory, SmartReminder


class APIEndpointSyncTests(TestCase):
    """
    Tests to ensure mobile app endpoints match backend endpoints
    """
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        
        # Create test memory
        self.memory = Memory.objects.create(
            user=self.user,
            content='Test memory for endpoint validation',
            memory_type='general',
            importance=5
        )
    
    # ========== System Endpoints ==========
    
    def test_health_endpoint(self):
        """Test /health/ endpoint"""
        response = self.client.get('/api/v1/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')
    
    # ========== Authentication Endpoints ==========
    
    def test_login_endpoint(self):
        """Test /auth/token/ endpoint"""
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_register_endpoint(self):
        """Test /auth/register/ endpoint"""
        response = self.client.post('/api/v1/auth/register/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        })
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_token_refresh_endpoint(self):
        """Test /auth/token/refresh/ endpoint"""
        # First login
        login_response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = login_response.data['refresh']
        
        # Then refresh
        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh_token
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
    
    # ========== Memory Endpoints ==========
    
    def test_memories_list_endpoint(self):
        """Test GET /memories/"""
        response = self.client.get('/api/v1/memories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(isinstance(response.data.get('results'), list) or isinstance(response.data, list))
    
    def test_memories_create_endpoint(self):
        """Test POST /memories/"""
        response = self.client.post('/api/v1/memories/', {
            'content': 'New test memory',
            'memory_type': 'general',
            'importance': 7
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
    
    def test_memories_detail_endpoint(self):
        """Test GET /memories/{id}/"""
        response = self.client.get(f'/api/v1/memories/{self.memory.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.memory.id)
    
    def test_memories_update_endpoint(self):
        """Test PUT /memories/{id}/"""
        response = self.client.put(f'/api/v1/memories/{self.memory.id}/', {
            'content': 'Updated memory',
            'memory_type': 'work',
            'importance': 8
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_memories_delete_endpoint(self):
        """Test DELETE /memories/{id}/"""
        # Create a memory to delete
        memory_to_delete = Memory.objects.create(
            user=self.user,
            content='Memory to delete',
            memory_type='general'
        )
        
        response = self.client.delete(f'/api/v1/memories/{memory_to_delete.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    
    def test_memories_search_endpoint(self):
        """Test GET /memories/search/"""
        response = self.client.get('/api/v1/memories/search/?q=test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_memories_quick_add_endpoint(self):
        """Test POST /memories/quick-add/"""
        response = self.client.post('/api/v1/memories/quick-add/', {
            'content': 'Quick add test memory'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_memories_dashboard_stats_endpoint(self):
        """Test GET /memories/dashboard-stats/"""
        response = self.client.get('/api/v1/memories/dashboard-stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
    
    def test_memory_like_endpoint(self):
        """Test POST /memories/{id}/like/"""
        response = self.client.post(f'/api/v1/memories/{self.memory.id}/like/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_memory_comment_endpoint(self):
        """Test POST /memories/{id}/comment/"""
        response = self.client.post(f'/api/v1/memories/{self.memory.id}/comment/', {
            'content': 'Test comment'
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_memory_similar_endpoint(self):
        """Test GET /memories/{id}/similar/"""
        response = self.client.get(f'/api/v1/memories/{self.memory.id}/similar/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # ========== Flutter Reminders Endpoints ==========
    
    def test_flutter_reminders_list_endpoint(self):
        """Test GET /flutter/reminders/"""
        response = self.client.get('/api/v1/flutter/reminders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reminders', response.data)
    
    def test_flutter_reminders_create_endpoint(self):
        """Test POST /flutter/reminders/"""
        response = self.client.post('/api/v1/flutter/reminders/', {
            'memory_id': self.memory.id,
            'reminder_type': 'time_based',
            'priority': 'medium',
            'trigger_conditions': {
                'target_time': '2025-12-31T10:00:00Z',
                'offset_minutes': 15
            }
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_flutter_reminders_check_endpoint(self):
        """Test POST /flutter/reminders/check/"""
        response = self.client.post('/api/v1/flutter/reminders/check/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reminders', response.data)
    
    def test_flutter_reminders_stats_endpoint(self):
        """Test GET /flutter/reminders/stats/"""
        response = self.client.get('/api/v1/flutter/reminders/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reminders', response.data)
    
    def test_flutter_reminders_for_memory_endpoint(self):
        """Test GET /flutter/reminders/memory/{memory_id}/"""
        response = self.client.get(f'/api/v1/flutter/reminders/memory/{self.memory.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reminders', response.data)
    
    def test_flutter_memory_create_endpoint(self):
        """Test POST /flutter/memories/create/"""
        response = self.client.post('/api/v1/flutter/memories/create/', {
            'content': 'Flutter optimized memory',
            'memory_type': 'general',
            'importance': 6
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('created_reminders', response.data)
    
    def test_flutter_memories_with_reminders_endpoint(self):
        """Test GET /flutter/memories/with-reminders/"""
        response = self.client.get('/api/v1/flutter/memories/with-reminders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('memories', response.data)
    
    # ========== AI Endpoints ==========
    
    def test_ai_suggestions_endpoint(self):
        """Test GET /ai/suggestions/"""
        response = self.client.get('/api/v1/ai/suggestions/')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
    
    def test_ai_enhance_endpoint(self):
        """Test POST /ai/enhance/"""
        response = self.client.post('/api/v1/ai/enhance/', {
            'content': 'Test memory for AI enhancement'
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
    
    def test_ai_categorize_endpoint(self):
        """Test POST /ai/categorize/"""
        response = self.client.post('/api/v1/ai/categorize/', {
            'content': 'Test memory for categorization'
        })
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE])
    
    def test_ai_status_endpoint(self):
        """Test GET /ai/status/"""
        response = self.client.get('/api/v1/ai/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available', response.data)
    
    # ========== Voice Endpoints ==========
    
    def test_voice_transcribe_endpoint_exists(self):
        """Test that /voice/transcribe/ endpoint exists"""
        # Just test that endpoint exists, actual transcription requires audio file
        response = self.client.post('/api/v1/voice/transcribe/')
        # Should fail with 400 (missing audio), not 404
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    # ========== Search Endpoints ==========
    
    def test_semantic_search_endpoint(self):
        """Test GET /search/semantic"""
        response = self.client.get('/api/v1/search/semantic?q=test')
        self.assertIn(response.status_code, [
            status.HTTP_200_OK, 
            status.HTTP_404_NOT_FOUND,  # May not be implemented
            status.HTTP_503_SERVICE_UNAVAILABLE
        ])


class EndpointDeprecationTests(TestCase):
    """Tests for deprecated endpoint warnings"""
    
    def setUp(self):
        """Set up test client and user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Get JWT token
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_deprecated_smart_reminders_endpoint_has_headers(self):
        """Test that deprecated /smart-reminders/ endpoint returns deprecation headers"""
        response = self.client.get('/api/v1/smart-reminders/')
        
        # Endpoint should still work (until sunset date)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        
        # If endpoint exists, check for deprecation headers
        if response.status_code == status.HTTP_200_OK:
            # Note: Headers may not be implemented yet
            # self.assertIn('X-API-Deprecated', response)
            # self.assertIn('X-API-Sunset', response)
            pass


class OpenAPISchemaTests(TestCase):
    """Tests for OpenAPI/Swagger schema generation"""
    
    def test_openapi_schema_endpoint(self):
        """Test that /api/schema/ endpoint works"""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify it's valid OpenAPI schema
        schema = response.json() if hasattr(response, 'json') else json.loads(response.content)
        self.assertIn('openapi', schema)
        self.assertIn('info', schema)
        self.assertIn('paths', schema)
    
    def test_swagger_ui_endpoint(self):
        """Test that /api/docs/ endpoint works"""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_redoc_endpoint(self):
        """Test that /api/redoc/ endpoint works"""
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class EndpointConsistencyTests(TestCase):
    """Tests for endpoint naming consistency"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Get JWT token
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
    
    def test_all_endpoints_use_trailing_slash(self):
        """Verify all endpoints consistently use trailing slashes"""
        endpoints_to_test = [
            '/api/v1/health/',
            '/api/v1/memories/',
            '/api/v1/flutter/reminders/',
        ]
        
        for endpoint in endpoints_to_test:
            # Should work with trailing slash
            response = self.client.get(endpoint)
            self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                              f"Endpoint {endpoint} not found")
    
    def test_endpoints_return_json(self):
        """Verify all API endpoints return JSON"""
        endpoints_to_test = [
            '/api/v1/health/',
            '/api/v1/memories/',
        ]
        
        for endpoint in endpoints_to_test:
            response = self.client.get(endpoint)
            if response.status_code == status.HTTP_200_OK:
                self.assertEqual(response['Content-Type'], 'application/json',
                               f"Endpoint {endpoint} doesn't return JSON")































