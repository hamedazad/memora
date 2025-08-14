from django.core.management.base import BaseCommand
from memory_assistant.models import Memory, SmartReminder
from memory_assistant.smart_reminder_service import SmartReminderService

class Command(BaseCommand):
    help = 'Create smart reminders for existing memories with time-based content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to process reminders for (optional)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating reminders',
        )

    def handle(self, *args, **options):
        reminder_service = SmartReminderService()
        
        # Get memories to process
        memories = Memory.objects.filter(is_archived=False)
        if options['user']:
            memories = memories.filter(user__username=options['user'])
        
        self.stdout.write(f'Processing {memories.count()} memories...')
        
        total_reminders_created = 0
        memories_with_reminders = 0
        
        for memory in memories:
            # Skip if memory already has smart reminders
            if memory.smart_reminders.exists():
                continue
            
            # Analyze memory for reminders
            suggestions = reminder_service.analyze_memory_for_reminders(memory)
            time_based_suggestions = [s for s in suggestions if s['type'] == 'time_based']
            
            if time_based_suggestions:
                memories_with_reminders += 1
                self.stdout.write(f'  Memory {memory.id}: "{memory.content[:50]}..."')
                
                for suggestion in time_based_suggestions:
                    self.stdout.write(f'    - {suggestion["description"]} ({suggestion["type"]})')
                    
                    if not options['dry_run']:
                        try:
                            reminder_service.create_smart_reminder(memory, memory.user, suggestion)
                            total_reminders_created += 1
                            self.stdout.write(f'      ✓ Created reminder')
                        except Exception as e:
                            self.stdout.write(f'      ✗ Error: {e}')
                    else:
                        total_reminders_created += 1
                        self.stdout.write(f'      (Would create reminder)')
        
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'DRY RUN: Would create {total_reminders_created} reminders for {memories_with_reminders} memories'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created {total_reminders_created} reminders for {memories_with_reminders} memories'
                )
            )

