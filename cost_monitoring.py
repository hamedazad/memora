#!/usr/bin/env python3
"""
Cost Monitoring for Memora Core
Track OpenAI API usage and costs
"""

import os
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CostMonitor:
    def __init__(self):
        self.usage_file = 'api_usage.json'
        self.costs = {
            'gpt-3.5-turbo': 0.0015,  # per 1K tokens
            'gpt-4': 0.03,            # per 1K tokens
            'database_operation': 0.0001,
            'server_processing': 0.0001,
        }
        self.load_usage()
    
    def load_usage(self):
        """Load usage data from file"""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r') as f:
                self.usage = json.load(f)
        else:
            self.usage = {
                'daily': defaultdict(lambda: {
                    'tokens_used': 0,
                    'api_calls': 0,
                    'operations': defaultdict(int)
                }),
                'monthly': defaultdict(lambda: {
                    'tokens_used': 0,
                    'api_calls': 0,
                    'operations': defaultdict(int)
                })
            }
    
    def save_usage(self):
        """Save usage data to file"""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)
    
    def track_operation(self, operation_type, tokens_used=0, model='gpt-3.5-turbo'):
        """Track an operation and its costs"""
        today = datetime.now().strftime('%Y-%m-%d')
        month = datetime.now().strftime('%Y-%m')
        
        # Update daily usage
        self.usage['daily'][today]['operations'][operation_type] += 1
        self.usage['daily'][today]['tokens_used'] += tokens_used
        self.usage['daily'][today]['api_calls'] += 1 if tokens_used > 0 else 0
        
        # Update monthly usage
        self.usage['monthly'][month]['operations'][operation_type] += 1
        self.usage['monthly'][month]['tokens_used'] += tokens_used
        self.usage['monthly'][month]['api_calls'] += 1 if tokens_used > 0 else 0
        
        self.save_usage()
        
        # Calculate cost
        cost = self.calculate_cost(tokens_used, model)
        logger.info(f"Operation: {operation_type}, Tokens: {tokens_used}, Cost: ${cost:.4f}")
        
        return cost
    
    def calculate_cost(self, tokens_used, model='gpt-3.5-turbo'):
        """Calculate cost for tokens used"""
        if tokens_used == 0:
            return 0.0002  # Basic operation cost
        
        # OpenAI API cost
        api_cost = (tokens_used / 1000) * self.costs[model]
        
        # Add basic operation cost
        total_cost = api_cost + 0.0002
        
        return total_cost
    
    def get_daily_report(self, date=None):
        """Get daily usage report"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        if date not in self.usage['daily']:
            return None
        
        daily = self.usage['daily'][date]
        total_cost = self.calculate_cost(daily['tokens_used'])
        
        return {
            'date': date,
            'operations': dict(daily['operations']),
            'tokens_used': daily['tokens_used'],
            'api_calls': daily['api_calls'],
            'total_cost': total_cost
        }
    
    def get_monthly_report(self, month=None):
        """Get monthly usage report"""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        if month not in self.usage['monthly']:
            return None
        
        monthly = self.usage['monthly'][month]
        total_cost = self.calculate_cost(monthly['tokens_used'])
        
        return {
            'month': month,
            'operations': dict(monthly['operations']),
            'tokens_used': monthly['tokens_used'],
            'api_calls': monthly['api_calls'],
            'total_cost': total_cost
        }
    
    def estimate_monthly_costs(self, users=100, memories_per_user=50, searches_per_user=200):
        """Estimate monthly costs based on usage patterns"""
        total_memories = users * memories_per_user
        total_searches = users * searches_per_user
        
        # Estimate AI usage (50% of memories use AI)
        ai_memories = total_memories * 0.5
        ai_searches = total_searches * 0.1  # 10% use semantic search
        
        # Calculate costs
        basic_memory_cost = (total_memories - ai_memories) * 0.0002
        ai_memory_cost = ai_memories * 0.0012
        basic_search_cost = (total_searches - ai_searches) * 0.0002
        ai_search_cost = ai_searches * 0.0040
        
        total_cost = basic_memory_cost + ai_memory_cost + basic_search_cost + ai_search_cost
        
        return {
            'users': users,
            'total_memories': total_memories,
            'total_searches': total_searches,
            'ai_memories': ai_memories,
            'ai_searches': ai_searches,
            'basic_memory_cost': basic_memory_cost,
            'ai_memory_cost': ai_memory_cost,
            'basic_search_cost': basic_search_cost,
            'ai_search_cost': ai_search_cost,
            'total_cost': total_cost
        }

# Usage examples
if __name__ == "__main__":
    monitor = CostMonitor()
    
    # Track some operations
    monitor.track_operation('memory_save_basic', tokens_used=0)
    monitor.track_operation('memory_save_ai', tokens_used=300)
    monitor.track_operation('search_basic', tokens_used=0)
    monitor.track_operation('search_semantic', tokens_used=800)
    
    # Get reports
    daily_report = monitor.get_daily_report()
    monthly_report = monitor.get_monthly_report()
    
    print("Daily Report:")
    print(json.dumps(daily_report, indent=2))
    
    print("\nMonthly Report:")
    print(json.dumps(monthly_report, indent=2))
    
    # Estimate costs
    estimate = monitor.estimate_monthly_costs(users=100)
    print("\nCost Estimate for 100 users:")
    print(json.dumps(estimate, indent=2))
