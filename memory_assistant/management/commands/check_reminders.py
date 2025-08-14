from django.core.management.base import BaseCommand
from memory_assistant.smart_reminder_service import SmartReminderService

class Command(BaseCommand):
    help = 'Check and trigger smart reminders'

    def handle(self, *args, **options):
        reminder_service = SmartReminderService()
        
        self.stdout.write('Checking for triggered reminders...')
        
        triggered_reminders = reminder_service.check_and_trigger_reminders()
        
        if triggered_reminders:
            self.stdout.write(
                self.style.SUCCESS(f'Triggered {len(triggered_reminders)} reminder(s)')
            )
            for item in triggered_reminders:
                self.stdout.write(
                    f'  - {item["reminder"].memory.content[:50]}... '
                    f'({item["trigger"].trigger_reason})'
                )
        else:
            self.stdout.write(self.style.WARNING('No reminders triggered'))

