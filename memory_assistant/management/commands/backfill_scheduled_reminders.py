from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from memory_assistant.models import Memory
from memory_assistant.smart_reminder_service import SmartReminderService
from django.utils import timezone

class Command(BaseCommand):
    help = 'Backfill existing scheduled memories with proper smart reminders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to process (optional, processes all users if not specified)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Starting Scheduled Memory Reminder Backfill...')
        )
        
        # Get users to process
        if options['user']:
            try:
                users = [User.objects.get(username=options['user'])]
                self.stdout.write(f"Processing user: {options['user']}")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"User '{options['user']}' not found")
                )
                return
        else:
            users = User.objects.filter(is_active=True)
            self.stdout.write(f"Processing {users.count()} users")
        
        reminder_service = SmartReminderService()
        total_processed = 0
        total_created = 0
        
        for user in users:
            self.stdout.write(f"\n👤 Processing user: {user.username}")
            
            # Find scheduled memories for this user
            scheduled_memories = Memory.objects.filter(
                user=user,
                delivery_date__isnull=False,
                is_archived=False
            ).order_by('created_at')
            
            user_processed = 0
            user_created = 0
            
            for memory in scheduled_memories:
                user_processed += 1
                total_processed += 1
                
                self.stdout.write(
                    f"  📅 Memory {memory.id}: {memory.content[:50]}... "
                    f"(due: {memory.delivery_date.strftime('%Y-%m-%d %H:%M')})"
                )
                
                if options['dry_run']:
                    # Check if reminder already exists
                    existing_reminder = memory.smart_reminders.filter(
                        reminder_type='time_based'
                    ).first()
                    
                    if existing_reminder:
                        self.stdout.write(
                            self.style.WARNING("    ⚠️  Reminder already exists")
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS("    ✅ Would create reminder")
                        )
                        user_created += 1
                        total_created += 1
                else:
                    # Create or update reminder
                    try:
                        reminder = reminder_service.create_scheduled_memory_reminder(memory, user)
                        if reminder:
                            self.stdout.write(
                                self.style.SUCCESS(f"    ✅ Created reminder for {reminder.next_trigger.strftime('%Y-%m-%d %H:%M')}")
                            )
                            user_created += 1
                            total_created += 1
                        else:
                            self.stdout.write(
                                self.style.WARNING("    ⚠️  No reminder created (past due date)")
                            )
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f"    ❌ Error creating reminder: {e}")
                        )
            
            self.stdout.write(
                f"  📊 User {user.username}: {user_processed} memories processed, "
                f"{user_created} reminders created"
            )
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(
            self.style.SUCCESS(f"🎉 Backfill Complete!")
        )
        self.stdout.write(f"📊 Total memories processed: {total_processed}")
        self.stdout.write(f"✅ Total reminders created: {total_created}")
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING("🔍 This was a dry run - no changes were made")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("✨ Scheduled memories now have proper smart reminders!")
            )
