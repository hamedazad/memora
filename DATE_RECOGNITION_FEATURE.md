# Date Recognition Feature

## Overview

The Memora AI Assistant now includes intelligent date recognition that automatically extracts and schedules dates from natural language text. This feature allows users to create time-sensitive memories without manually specifying dates.

## Features

### Automatic Date Extraction
The system can recognize and extract dates from various natural language formats:

#### Time-based References
- **Today**: "appointment today", "call tonight", "meeting this evening"
- **Tomorrow**: "meeting tomorrow", "deadline tomorrow morning"
- **Yesterday**: "completed task yesterday"

#### Relative Time References
- **Days**: "in 3 days", "5 days from now"
- **Weeks**: "next week", "in 2 weeks", "meeting this Friday"
- **Months**: "next month", "in 3 months"
- **Years**: "next year", "in 2 years"

#### Exact Dates
- **Formats**: "December 25th", "2024-01-15", "12/25/2024"
- **Day of Week**: "next Monday", "this Friday"

### Smart Scheduling
- **Today's Memories**: Automatically displayed prominently on the dashboard
- **Overdue Memories**: Highlighted with warning indicators
- **Upcoming Memories**: Shown in chronological order
- **Date-based Filtering**: Filter memories by date categories

### Visual Indicators
- **Today**: Green badges and borders
- **Overdue**: Yellow/orange warning indicators
- **Upcoming**: Blue information badges
- **Unscheduled**: No special indicators

## Technical Implementation

### Date Recognition Service
Located in `memory_assistant/date_recognition_service.py`:

```python
class DateRecognitionService:
    def extract_date_from_text(self, text: str) -> Optional[date]
    def analyze_text_for_date_context(self, text: str) -> Dict[str, Any]
```

### Database Schema
Added `scheduled_date` field to the Memory model:

```python
scheduled_date = models.DateField(null=True, blank=True, 
                                help_text="Date when this memory should be displayed or acted upon")
```

### Model Properties
The Memory model includes helpful properties:

- `is_scheduled`: Check if memory has a scheduled date
- `is_due_today`: Check if scheduled for today
- `is_overdue`: Check if scheduled date is in the past
- `is_upcoming`: Check if scheduled for the future

## Usage Examples

### Creating Memories with Dates

#### Text Input
```
"I have a doctor appointment tomorrow at 2 PM"
```
**Result**: Memory scheduled for tomorrow

#### Voice Input
```
"Call my father tonight"
```
**Result**: Memory scheduled for today

#### Quick Add
```
"Submit quarterly report by Friday"
```
**Result**: Memory scheduled for this Friday

### Dashboard Organization

The dashboard now shows memories in priority order:

1. **Today's Scheduled Memories** (Green section)
2. **Overdue Memories** (Yellow warning section)
3. **Upcoming Memories** (Blue section, next 7 days)
4. **Recent Unscheduled Memories** (Standard section)

### Filtering and Search

Users can filter memories by:
- **Today**: Show only today's scheduled memories
- **Overdue**: Show overdue memories
- **Upcoming**: Show future scheduled memories
- **Scheduled**: Show all memories with dates
- **Unscheduled**: Show memories without dates

## AI Integration

The date recognition is integrated with the existing AI processing:

1. **Content Analysis**: AI analyzes memory content for date context
2. **Date Extraction**: Date recognition service extracts dates
3. **Smart Categorization**: AI categorizes memories as reminders when dates are detected
4. **Importance Adjustment**: Time-sensitive memories may get higher importance scores

## Supported Date Patterns

### Natural Language
- "today", "tonight", "this evening"
- "tomorrow", "tomorrow morning"
- "next week", "next month", "next year"
- "in 3 days", "in 2 weeks"
- "this Friday", "next Monday"

### Exact Dates
- "December 25th, 2024"
- "2024-01-15"
- "12/25/2024"
- "Jan 15, 2024"

### Relative References
- "by Friday" (next Friday)
- "next Monday" (next Monday)
- "this weekend" (upcoming weekend)

## Benefits

1. **Automatic Scheduling**: No manual date entry required
2. **Natural Language**: Users can write naturally
3. **Smart Organization**: Memories are automatically organized by date
4. **Visual Clarity**: Clear indicators for different date states
5. **AI Enhancement**: Integrated with existing AI categorization
6. **Flexible Input**: Works with text, voice, and quick add

## Future Enhancements

Potential improvements for future versions:

1. **Time Recognition**: Extract specific times (2 PM, 14:00)
2. **Recurring Dates**: "every Monday", "monthly meeting"
3. **Date Ranges**: "between Monday and Friday"
4. **Holiday Recognition**: "Christmas", "New Year's"
5. **Timezone Support**: Handle different timezones
6. **Calendar Integration**: Sync with external calendars

## Configuration

The date recognition service requires:
- `python-dateutil==2.8.2` (for advanced date parsing)
- No additional API keys required
- Works offline without internet connection

## Testing

The feature has been thoroughly tested with various date formats and edge cases. The system correctly handles:
- Natural language date references
- Exact date formats
- Relative time expressions
- Edge cases and invalid inputs
- Timezone considerations 