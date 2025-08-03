from django.core.management.base import BaseCommand
from memory_assistant.models import Memory
from django.db.models import Q


class Command(BaseCommand):
    help = 'Check memories in database and test search functionality'

    def handle(self, *args, **options):
        # Get all memories
        memories = Memory.objects.all()
        
        self.stdout.write(f"Total memories in database: {memories.count()}")
        
        if memories.count() > 0:
            self.stdout.write("\nRecent memories:")
            for memory in memories[:5]:
                self.stdout.write(f"- ID: {memory.id}, Content: {memory.content[:50]}...")
                if memory.summary:
                    self.stdout.write(f"  Summary: {memory.summary[:50]}...")
        
        # Test search functionality
        test_queries = ["club", "tonight", "what should I do", "remember"]
        
        self.stdout.write("\nTesting search functionality:")
        for query in test_queries:
            results = Memory.objects.filter(
                Q(content__icontains=query) |
                Q(summary__icontains=query)
            )
            self.stdout.write(f"Query '{query}': {results.count()} results")
            if results.count() > 0:
                for result in results[:3]:
                    self.stdout.write(f"  - {result.content[:50]}...")
        
        # Test the specific query that's failing
        specific_query = "what should I do tonight"
        results = Memory.objects.filter(
            Q(content__icontains=specific_query) |
            Q(summary__icontains=specific_query)
        )
        self.stdout.write(f"\nSpecific query '{specific_query}': {results.count()} results")
        
        # Try partial matches
        partial_results = Memory.objects.filter(
            Q(content__icontains="tonight") |
            Q(summary__icontains="tonight")
        )
        self.stdout.write(f"Partial query 'tonight': {partial_results.count()} results")
        if partial_results.count() > 0:
            for result in partial_results:
                self.stdout.write(f"  - {result.content[:100]}...") 