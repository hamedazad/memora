#!/usr/bin/env python
"""
Dashboard Performance Test Script
Measures loading time and identifies bottlenecks in the dashboard view.
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from django.contrib.auth.models import User
from memory_assistant.models import Memory, SharedMemory, Organization, OrganizationMembership
from memory_assistant.views import dashboard
from django.core.cache import cache
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

def create_test_data(user, num_memories=50, num_shared=10):
    """Create test data for performance testing"""
    print(f"Creating {num_memories} test memories...")
    
    # Create test memories
    memories = []
    for i in range(num_memories):
        memory = Memory.objects.create(
            user=user,
            content=f"Test memory {i+1}: This is a test memory for performance testing. It contains some content to make it realistic.",
            memory_type='reminder',
            importance=5 + (i % 5),
            summary=f"Test summary for memory {i+1}",
            tags=['test', f'tag{i}', 'performance']
        )
        memories.append(memory)
    
    # Create test organization
    org = Organization.objects.create(
        name="Test Organization",
        description="Test organization for performance testing",
        created_by=user
    )
    
    # Add user to organization
    OrganizationMembership.objects.create(
        user=user,
        organization=org,
        role='member',
        is_active=True
    )
    
    # Create shared memories
    print(f"Creating {num_shared} shared memories...")
    for i in range(num_shared):
        SharedMemory.objects.create(
            memory=memories[i],
            shared_by=user,
            shared_with_organization=org,
            share_type='organization',
            message=f"Shared memory {i+1}",
            is_active=True
        )
    
    print("Test data created successfully!")

def test_dashboard_performance():
    """Test dashboard loading performance"""
    print("🔍 Dashboard Performance Test")
    print("=" * 50)
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("Created test user: testuser (password: testpass123)")
    
    # Create test data if needed
    if Memory.objects.filter(user=user).count() < 10:
        create_test_data(user)
    
    # Clear cache
    cache.clear()
    print("Cache cleared")
    
    # Setup request factory
    factory = RequestFactory()
    
    # Test dashboard loading
    print("\n📊 Testing Dashboard Loading...")
    
    # Warm-up request (ignore first request)
    print("Warm-up request...")
    request = factory.get('/memora/dashboard/')
    request.user = user
    start_time = time.time()
    response = dashboard(request)
    warmup_time = time.time() - start_time
    print(f"Warm-up time: {warmup_time:.3f}s")
    
    # Multiple test requests
    times = []
    for i in range(5):
        print(f"Test request {i+1}...")
        request = factory.get('/memora/dashboard/')
        request.user = user
        start_time = time.time()
        response = dashboard(request)
        load_time = time.time() - start_time
        times.append(load_time)
        print(f"  Load time: {load_time:.3f}s")
        print(f"  Status code: {response.status_code if hasattr(response, 'status_code') else 'N/A'}")
        
        # Small delay between requests
        time.sleep(0.1)
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n📈 Performance Results:")
    print(f"  Average load time: {avg_time:.3f}s")
    print(f"  Minimum load time: {min_time:.3f}s")
    print(f"  Maximum load time: {max_time:.3f}s")
    
    # Performance assessment
    if avg_time < 1.0:
        print("✅ Performance: EXCELLENT")
    elif avg_time < 2.0:
        print("✅ Performance: GOOD")
    elif avg_time < 3.0:
        print("⚠️  Performance: ACCEPTABLE")
    else:
        print("❌ Performance: NEEDS IMPROVEMENT")
    
    # Database query analysis
    print(f"\n🗄️  Database Analysis:")
    from django.db import connection
    print(f"  Total queries: {len(connection.queries)}")
    
    # Group queries by type
    query_types = {}
    for query in connection.queries:
        query_type = query['sql'][:50]  # First 50 chars
        if query_type not in query_types:
            query_types[query_type] = 0
        query_types[query_type] += 1
    
    print(f"  Unique query types: {len(query_types)}")
    
    # Show slowest queries
    if connection.queries:
        slow_queries = sorted(connection.queries, key=lambda x: float(x['time']), reverse=True)[:5]
        print(f"\n🐌 Slowest queries:")
        for i, query in enumerate(slow_queries, 1):
            print(f"  {i}. {float(query['time']):.3f}s - {query['sql'][:100]}...")
    
    return avg_time

def test_cache_effectiveness():
    """Test cache effectiveness"""
    print(f"\n💾 Cache Effectiveness Test")
    print("=" * 50)
    
    factory = RequestFactory()
    user = User.objects.get(username='testuser')
    
    # First request (cache miss)
    print("First request (cache miss)...")
    request = factory.get('/memora/dashboard/')
    request.user = user
    start_time = time.time()
    response = dashboard(request)
    first_time = time.time() - start_time
    print(f"  Load time: {first_time:.3f}s")
    
    # Second request (cache hit)
    print("Second request (cache hit)...")
    request = factory.get('/memora/dashboard/')
    request.user = user
    start_time = time.time()
    response = dashboard(request)
    second_time = time.time() - start_time
    print(f"  Load time: {second_time:.3f}s")
    
    # Calculate cache effectiveness
    cache_improvement = ((first_time - second_time) / first_time) * 100
    print(f"  Cache improvement: {cache_improvement:.1f}%")
    
    if cache_improvement > 50:
        print("✅ Cache: HIGHLY EFFECTIVE")
    elif cache_improvement > 25:
        print("✅ Cache: EFFECTIVE")
    else:
        print("⚠️  Cache: NEEDS OPTIMIZATION")

def test_memory_count_scaling():
    """Test how performance scales with memory count"""
    print(f"\n📊 Memory Count Scaling Test")
    print("=" * 50)
    
    factory = RequestFactory()
    user = User.objects.get(username='testuser')
    
    # Test with different memory counts
    memory_counts = [10, 50, 100, 200]
    
    for count in memory_counts:
        # Create additional memories if needed
        current_count = Memory.objects.filter(user=user).count()
        if current_count < count:
            additional_needed = count - current_count
            print(f"Creating {additional_needed} additional memories...")
            for i in range(additional_needed):
                Memory.objects.create(
                    user=user,
                    content=f"Additional memory {i+1} for scaling test",
                    memory_type='reminder',
                    importance=5,
                    tags=['scaling', 'test']
                )
        
        # Clear cache and test
        cache.clear()
        request = factory.get('/memora/dashboard/')
        request.user = user
        start_time = time.time()
        response = dashboard(request)
        load_time = time.time() - start_time
        
        print(f"  {count} memories: {load_time:.3f}s")

if __name__ == "__main__":
    print("🚀 Starting Dashboard Performance Test")
    print(f"Time: {datetime.now()}")
    
    try:
        # Test basic performance
        avg_time = test_dashboard_performance()
        
        # Test cache effectiveness
        test_cache_effectiveness()
        
        # Test scaling
        test_memory_count_scaling()
        
        print(f"\n✅ Performance test completed successfully!")
        print(f"Average dashboard load time: {avg_time:.3f}s")
        
    except Exception as e:
        print(f"❌ Error during performance test: {e}")
        import traceback
        traceback.print_exc()
