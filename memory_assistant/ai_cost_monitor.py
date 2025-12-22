"""
AI Cost Monitoring and Usage Limits

Tracks OpenAI API usage, enforces limits, and provides cost analytics.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path
from collections import defaultdict


class AICostMonitor:
    """
    Monitor AI API usage and enforce cost limits
    """
    
    def __init__(self, data_dir='ai_usage_data'):
        """Initialize cost monitor"""
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Cost per 1K tokens (as of 2025)
        self.costs = {
            'gpt-3.5-turbo': 0.0015,        # Input: $0.0005, Output: $0.0015
            'gpt-4': 0.03,                   # Input: $0.01, Output: $0.03
            'text-embedding-3-small': 0.00002,  # $0.02 per 1M tokens
            'text-embedding-ada-002': 0.0001,   # $0.10 per 1M tokens
        }
        
        # Usage limits (per day)
        self.limits = {
            'max_daily_cost': 10.0,          # $10 per day
            'max_daily_requests': 10000,      # 10K requests per day
            'max_hourly_requests': 500,       # 500 requests per hour
            'max_user_daily_requests': 100,   # 100 requests per user per day
        }
        
        # Load usage data
        self.usage_file = self.data_dir / 'usage.json'
        self.load_usage()
    
    def load_usage(self):
        """Load usage data from file"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r') as f:
                    self.usage = json.load(f)
            except Exception:
                self.usage = self._init_usage_structure()
        else:
            self.usage = self._init_usage_structure()
    
    def _init_usage_structure(self) -> Dict:
        """Initialize usage data structure"""
        return {
            'daily': {},
            'hourly': {},
            'by_user': {},
            'by_operation': {},
            'total_cost': 0.0,
            'total_requests': 0,
        }
    
    def save_usage(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving usage data: {e}")
    
    def record_request(
        self,
        operation: str,
        tokens_used: int,
        user_id: Optional[int] = None,
        model: str = 'gpt-3.5-turbo',
        success: bool = True
    ) -> Dict[str, Any]:
        """
        Record an AI API request
        
        Args:
            operation: Type of operation (categorize, summarize, etc.)
            tokens_used: Number of tokens used
            user_id: User ID if available
            model: AI model used
            success: Whether request succeeded
            
        Returns:
            Dict with recording details and limit status
        """
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_hour = now.strftime('%Y-%m-%d-%H')
        
        # Calculate cost
        cost = (tokens_used / 1000) * self.costs.get(model, 0.0015)
        
        # Initialize structures if needed
        if today not in self.usage['daily']:
            self.usage['daily'][today] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0,
                'operations': {}
            }
        
        if current_hour not in self.usage['hourly']:
            self.usage['hourly'][current_hour] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0
            }
        
        if user_id:
            user_key = f"{user_id}:{today}"
            if user_key not in self.usage['by_user']:
                self.usage['by_user'][user_key] = {
                    'requests': 0,
                    'tokens': 0,
                    'cost': 0.0
                }
        
        if operation not in self.usage['by_operation']:
            self.usage['by_operation'][operation] = {
                'requests': 0,
                'tokens': 0,
                'cost': 0.0,
                'cache_hits': 0,
                'cache_misses': 0
            }
        
        # Update counters
        self.usage['daily'][today]['requests'] += 1
        self.usage['daily'][today]['tokens'] += tokens_used
        self.usage['daily'][today]['cost'] += cost
        
        if operation not in self.usage['daily'][today]['operations']:
            self.usage['daily'][today]['operations'][operation] = 0
        self.usage['daily'][today]['operations'][operation] += 1
        
        self.usage['hourly'][current_hour]['requests'] += 1
        self.usage['hourly'][current_hour]['tokens'] += tokens_used
        self.usage['hourly'][current_hour]['cost'] += cost
        
        if user_id:
            user_key = f"{user_id}:{today}"
            self.usage['by_user'][user_key]['requests'] += 1
            self.usage['by_user'][user_key]['tokens'] += tokens_used
            self.usage['by_user'][user_key]['cost'] += cost
        
        self.usage['by_operation'][operation]['requests'] += 1
        self.usage['by_operation'][operation]['tokens'] += tokens_used
        self.usage['by_operation'][operation]['cost'] += cost
        if not success:
            self.usage['by_operation'][operation]['cache_misses'] += 1
        
        self.usage['total_cost'] += cost
        self.usage['total_requests'] += 1
        
        # Save usage data
        self.save_usage()
        
        # Check limits
        return {
            'recorded': True,
            'cost': cost,
            'tokens': tokens_used,
            'daily_cost': self.usage['daily'][today]['cost'],
            'daily_requests': self.usage['daily'][today]['requests'],
            'hourly_requests': self.usage['hourly'][current_hour]['requests'],
            'limits': self.check_limits(user_id)
        }
    
    def record_cache_hit(self, operation: str, estimated_tokens: int = 500):
        """Record a cache hit (saved API call)"""
        if operation in self.usage['by_operation']:
            self.usage['by_operation'][operation]['cache_hits'] += 1
        
        # Estimate cost saved
        cost_saved = (estimated_tokens / 1000) * 0.0015
        self.usage['total_cost'] -= cost_saved  # Negative cost = savings
        
        self.save_usage()
    
    def check_limits(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Check if any limits are exceeded
        
        Args:
            user_id: User ID to check user-specific limits
            
        Returns:
            Dict with limit status
        """
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        current_hour = now.strftime('%Y-%m-%d-%H')
        
        daily_data = self.usage['daily'].get(today, {'requests': 0, 'cost': 0.0})
        hourly_data = self.usage['hourly'].get(current_hour, {'requests': 0})
        
        limits_status = {
            'daily_cost_ok': daily_data['cost'] < self.limits['max_daily_cost'],
            'daily_requests_ok': daily_data['requests'] < self.limits['max_daily_requests'],
            'hourly_requests_ok': hourly_data['requests'] < self.limits['max_hourly_requests'],
            'user_requests_ok': True,
            'can_proceed': True,
        }
        
        # Check user-specific limits
        if user_id:
            user_key = f"{user_id}:{today}"
            user_data = self.usage['by_user'].get(user_key, {'requests': 0})
            limits_status['user_requests_ok'] = user_data['requests'] < self.limits['max_user_daily_requests']
        
        # Overall status
        limits_status['can_proceed'] = all([
            limits_status['daily_cost_ok'],
            limits_status['daily_requests_ok'],
            limits_status['hourly_requests_ok'],
            limits_status['user_requests_ok']
        ])
        
        # Add current usage
        limits_status['current_usage'] = {
            'daily_cost': daily_data['cost'],
            'daily_requests': daily_data['requests'],
            'hourly_requests': hourly_data['requests'],
        }
        
        # Add limits for reference
        limits_status['limits'] = self.limits
        
        return limits_status
    
    def get_daily_stats(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific day"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        return self.usage['daily'].get(date, {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'operations': {}
        })
    
    def get_operation_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for a specific operation type"""
        return self.usage['by_operation'].get(operation, {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        })
    
    def get_user_stats(self, user_id: int, date: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for a specific user"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        user_key = f"{user_id}:{date}"
        return self.usage['by_user'].get(user_key, {
            'requests': 0,
            'tokens': 0,
            'cost': 0.0
        })
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        now = datetime.now()
        today = now.strftime('%Y-%m-%d')
        
        # Get today's data
        today_data = self.get_daily_stats(today)
        
        # Get last 7 days
        last_7_days = []
        for i in range(7):
            date = (now - timedelta(days=i)).strftime('%Y-%m-%d')
            day_data = self.get_daily_stats(date)
            last_7_days.append({
                'date': date,
                'requests': day_data.get('requests', 0),
                'cost': day_data.get('cost', 0.0)
            })
        
        return {
            'today': today_data,
            'last_7_days': last_7_days,
            'total_lifetime_cost': self.usage.get('total_cost', 0.0),
            'total_lifetime_requests': self.usage.get('total_requests', 0),
            'operations_breakdown': self.usage.get('by_operation', {}),
            'limits': self.limits
        }
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Remove usage data older than specified days"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
        
        # Clean daily data
        old_dates = [date for date in self.usage['daily'].keys() if date < cutoff_date]
        for date in old_dates:
            del self.usage['daily'][date]
        
        # Clean hourly data
        old_hours = [hour for hour in self.usage['hourly'].keys() if hour[:10] < cutoff_date]
        for hour in old_hours:
            del self.usage['hourly'][hour]
        
        # Clean user data
        old_user_keys = [key for key in self.usage['by_user'].keys() if key.split(':')[1] < cutoff_date]
        for key in old_user_keys:
            del self.usage['by_user'][key]
        
        self.save_usage()
        
        return len(old_dates) + len(old_hours) + len(old_user_keys)


# Singleton instance
_cost_monitor = None

def get_cost_monitor() -> AICostMonitor:
    """Get singleton cost monitor instance"""
    global _cost_monitor
    if _cost_monitor is None:
        _cost_monitor = AICostMonitor()
    return _cost_monitor




























