from django.core.management.base import BaseCommand
from memory_assistant.models import Memory, SmartReminder
from memory_assistant.smart_reminder_service import SmartReminderService
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Clean up smart reminders for memories about past events'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned up without actually doing it',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Only process memories for a specific user',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        user_filter = options['user']
        
        self.stdout.write("=== CLEANING UP OLD SMART REMINDERS ===")
        
        # Get memories to check
        memories = Memory.objects.all()
        if user_filter:
            memories = memories.filter(user__username=user_filter)
        
        reminder_service = SmartReminderService()
        total_memories = memories.count()
        past_events = 0
        reminders_removed = 0
        
        self.stdout.write(f"Checking {total_memories} memories...")
        
        for memory in memories:
            # Check if this memory is about a past event
            if reminder_service._is_past_event(memory):
                past_events += 1
                self.stdout.write(f"\n📅 Past event detected: {memory.content[:50]}...")
                self.stdout.write(f"   Created: {memory.created_at}")
                self.stdout.write(f"   User: {memory.user.username}")
                
                # Find and remove smart reminders for this memory
                old_reminders = SmartReminder.objects.filter(memory=memory)
                if old_reminders.exists():
                    self.stdout.write(f"   Found {old_reminders.count()} old reminder(s)")
                    
                    if not dry_run:
                        old_reminders.delete()
                        self.stdout.write(f"   ✅ Deleted {old_reminders.count()} reminder(s)")
                    else:
                        self.stdout.write(f"   🔍 Would delete {old_reminders.count()} reminder(s)")
                    
                    reminders_removed += old_reminders.count()
        
        self.stdout.write(f"\n=== SUMMARY ===")
        self.stdout.write(f"Total memories checked: {total_memories}")
        self.stdout.write(f"Past events found: {past_events}")
        self.stdout.write(f"Reminders removed: {reminders_removed}")
        
        if dry_run:
            self.stdout.write(f"\n🔍 This was a dry run. No changes were made.")
        else:
            self.stdout.write(f"\n✅ Cleanup completed!")

