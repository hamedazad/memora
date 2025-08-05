# AI Memory Type Recognition Guide

## Overview

The Memora Core application now features enhanced AI-powered memory type recognition that automatically categorizes your memories based on their content. This system uses advanced natural language processing to understand the context and intent of your memories.

## How It Works

### 1. Automatic Categorization
When you create a memory (via text input or voice), the AI automatically analyzes the content and categorizes it into one of these types:

- **Work**: Professional tasks, meetings, projects, career-related items, business activities, job responsibilities, workplace events, professional development, work deadlines, team activities, client interactions, business ideas, work-related learning

- **Personal**: Family, friends, hobbies, personal life, relationships, social events, personal celebrations, family activities, personal interests, social gatherings, personal goals, lifestyle choices, personal experiences

- **Learning**: Education, skills, courses, knowledge acquisition, academic activities, training sessions, reading notes, study materials, educational goals, skill development, research, tutorials, workshops, certifications

- **Idea**: Creative thoughts, innovations, concepts, brainstorming, creative projects, inventions, artistic ideas, business concepts, problem-solving ideas, innovative solutions, creative inspiration, design ideas

- **Reminder**: Tasks, to-dos, appointments, deadlines, scheduled events, time-sensitive activities, future plans, calendar events, action items, follow-ups, time management, planning activities

- **General**: Everything else that doesn't fit the above categories

### 2. AI Analysis Features

The AI provides comprehensive analysis including:

- **Category**: The primary memory type
- **Confidence Score**: How certain the AI is about the categorization (0-100%)
- **Importance Level**: Suggested importance rating (1-10)
- **Tags**: Relevant keywords for easy searching
- **Summary**: Concise summary of the memory
- **Reasoning**: Explanation of why the AI chose that category

### 3. Fallback System

The system includes a robust fallback mechanism:
1. **Enhanced AI Service**: Primary categorization using advanced prompts
2. **ChatGPT Service**: Fallback if enhanced AI fails
3. **Default Values**: Final fallback with basic categorization

## Usage Examples

### Text Memory Creation
```
Content: "Meeting with the development team tomorrow at 2 PM to discuss the new feature implementation and project timeline."

AI Analysis:
- Category: work
- Confidence: 90%
- Importance: 8/10
- Tags: meeting, development team, new feature implementation, project timeline
- Reasoning: Contains work-related keywords and professional context
```

### Voice Memory Creation
```
Spoken: "Need to buy groceries: milk, bread, eggs, and vegetables. Also pick up the dry cleaning."

AI Analysis:
- Category: reminder
- Confidence: 90%
- Importance: 8/10
- Tags: groceries, shopping, dry cleaning
- Reasoning: Focuses on specific tasks to be completed in the future
```

## Technical Implementation

### Enhanced AI Service (`ai_services.py`)
- Uses detailed category definitions
- Implements advanced analysis instructions
- Provides confidence scores and reasoning
- Handles audio transcriptions with error tolerance

### ChatGPT Service (`services.py`)
- Fallback categorization system
- Maintains compatibility with existing features
- Provides basic categorization when enhanced AI is unavailable

### Voice Service (`voice_service.py`)
- Specialized audio memory categorization
- Accounts for transcription errors
- Optimized for spoken content analysis

## Testing

Run the test script to see the AI categorization in action:

```bash
python test_ai_memory_categorization.py
```

This will demonstrate:
- Various memory types and their categorization
- Confidence scores and reasoning
- Fallback system functionality
- Audio transcription handling

## Benefits

1. **Automatic Organization**: Memories are automatically sorted into logical categories
2. **Improved Search**: Better tagging and categorization enables more effective searching
3. **Time Saving**: No need to manually categorize memories
4. **Consistency**: AI provides consistent categorization across all memories
5. **Insights**: AI reasoning helps understand why memories were categorized as they were
6. **Flexibility**: Multiple fallback systems ensure reliability

## Configuration

The AI categorization requires:
- OpenAI API key configured in `.env` file
- Internet connection for API calls
- Proper Django environment setup

## Future Enhancements

Potential improvements include:
- Learning from user corrections
- Custom category definitions
- Multi-language support
- Offline categorization capabilities
- Integration with calendar and task management systems 