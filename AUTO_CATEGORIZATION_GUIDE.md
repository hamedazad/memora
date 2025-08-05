# 🤖 Auto-Categorization Guide for Memora

## Overview

Memora now features intelligent auto-categorization for both text and audio memories using AI. The system automatically categorizes your memories into meaningful categories to help you organize and find your information more effectively.

## Categories

The system categorizes memories into the following categories:

### 🏢 Work
- Professional tasks, meetings, projects
- Career-related items, deadlines
- Client interactions, team collaboration

### 👨‍👩‍👧‍👦 Personal
- Family, friends, relationships
- Hobbies, personal life events
- Social activities, personal achievements

### 🏥 Health
- Exercise, fitness routines
- Medical appointments, wellness
- Diet, mental health, self-care

### 💰 Finance
- Money management, expenses
- Investments, budgeting
- Financial planning, bills

### 📚 Learning
- Education, courses, skills
- Knowledge acquisition
- Training, certifications

### 💡 Idea
- Creative thoughts, innovations
- Concepts, brainstorming
- Inspirations, new ideas

### ⏰ Reminder
- Tasks, to-dos, appointments
- Deadlines, scheduled events
- Action items

### 📝 General
- Everything else that doesn't fit the above categories

## How It Works

### Text Memories
When you create a text memory:
1. Enter your memory content
2. The AI analyzes the content
3. Automatically assigns the most appropriate category
4. Generates relevant tags and summary
5. Suggests an importance level (1-10)

### Audio Memories
When you create an audio memory:
1. Speak your memory or provide transcribed text
2. The AI processes the audio content
3. Automatically categorizes based on context
4. Generates tags, summary, and importance level
5. Creates the memory with full categorization

## AI Confidence

The system provides a confidence score (0-100%) for each categorization:
- **90-100%**: High confidence in the category assignment
- **70-89%**: Good confidence with some uncertainty
- **50-69%**: Moderate confidence, may need review
- **Below 50%**: Low confidence, manual review recommended

## Benefits

1. **Automatic Organization**: No need to manually categorize every memory
2. **Consistent Categorization**: AI applies consistent logic across all memories
3. **Better Search**: Find memories by category more easily
4. **Insights**: Understand patterns in your memory types
5. **Time Saving**: Focus on content, not organization

## Manual Override

You can always:
- Change the category after creation
- Edit tags and summary
- Adjust importance levels
- The AI suggestions are just starting points

## Examples

### Work Memory
**Input**: "Meeting with marketing team tomorrow at 2 PM to discuss Q4 campaign"
**AI Output**:
- Category: Work
- Confidence: 90%
- Tags: ["meeting", "project", "deadline"]
- Summary: Meeting with the marketing team tomorrow at 2 PM to discuss Q4 campaign strategy

### Health Memory
**Input**: "Doctor appointment scheduled for next Tuesday at 3 PM for annual checkup"
**AI Output**:
- Category: Health
- Confidence: 90%
- Tags: ["medical appointment", "wellness", "reminder"]
- Summary: Upcoming doctor appointment for annual checkup scheduled for next Tuesday at 3 PM

### Finance Memory
**Input**: "Invested $1000 in the new tech stock portfolio, expecting good returns"
**AI Output**:
- Category: Finance
- Confidence: 90%
- Tags: ["investment", "portfolio", "financial planning"]
- Summary: Invested $1000 in the new tech stock portfolio for potential returns

## Technical Details

- Uses OpenAI GPT-3.5-turbo for intelligent categorization
- Processes both text and audio content
- Provides fallback categorization when AI is unavailable
- Integrates seamlessly with existing memory creation workflow
- Maintains backward compatibility with existing memories

## Getting Started

1. Create a new memory (text or voice)
2. The AI will automatically categorize it
3. Review the suggested category and tags
4. Edit if needed
5. Save your memory

The auto-categorization feature makes Memora more intelligent and user-friendly while maintaining full control over your data organization. 