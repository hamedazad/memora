# Like and Comment Functionality for Shared Memories

## Overview

The Memora application now supports like and comment functionality for shared memories, allowing authenticated users to interact with memories shared with them based on their permissions. **Note: Like and comment interactions are only available for memories shared with the user, not for the user's own memories.**

## Features

### 1. Like/Reaction System
- **Multiple Reaction Types**: Users can react with 6 different emotions:
  - 👍 Like
  - ❤️ Love
  - 😂 Funny
  - 😮 Wow
  - 😢 Sad
  - 😠 Angry

- **Toggle Functionality**: Users can change their reaction or remove it entirely
- **Real-time Updates**: Like counts update instantly via AJAX
- **Visual Feedback**: Active reactions are highlighted with colored buttons

### 2. Comment System
- **Add Comments**: Users can add comments to memories they have permission to view
- **Comment Display**: Comments show user avatars, usernames, and timestamps
- **Form Validation**: Comments are validated for content and length
- **Real-time Count**: Comment counts update automatically

## Authentication and Permissions

### Memory Access Control
Users can only like and comment on memories they have permission to view based on:

1. **Memory Owner**: Always has full access
2. **Privacy Settings**:
   - **Private**: Only the owner can view
   - **Friends**: Only friends of the owner can view
   - **Organization**: Only organization members can view
   - **Public**: Anyone can view

3. **Direct Sharing**: Users can view memories specifically shared with them

### Permission Checks
- `memory.can_be_viewed_by(user)`: Checks if user can view the memory
- `memory.allow_likes`: Checks if likes are enabled for the memory
- `memory.allow_comments`: Checks if comments are enabled for the memory

## Implementation Details

### Models
- **MemoryLike**: Stores user reactions with reaction types
- **MemoryComment**: Stores user comments with timestamps
- **Memory**: Has `allow_likes` and `allow_comments` boolean fields

### Views
- **`toggle_like`**: Handles AJAX requests for like/reaction toggling
- **`add_comment`**: Handles comment submission via POST

### URLs
- `/memora/social/like/<memory_id>/`: Toggle like/reaction
- `/memora/social/comment/<memory_id>/`: Add comment

### Templates
- **Memory Detail**: Shows like buttons, comment form, and interaction history
- **Shared Memories**: Shows like/comment counts for shared memories

## User Experience

### For Memory Owners
- Can enable/disable likes and comments when creating/editing memories
- Receive notifications when others like or comment on their memories
- Can see all interactions on their memories
- **Note: Memory owners cannot like or comment on their own memories**

### For Shared Memory Viewers
- Can react to memories they have permission to view
- Can add comments if comments are enabled
- See real-time updates of interaction counts
- Get visual feedback for their own interactions

## Security Features

1. **CSRF Protection**: All forms and AJAX requests include CSRF tokens
2. **Permission Validation**: Server-side checks ensure users can only interact with accessible memories
3. **Input Validation**: Comments are validated for content and length
4. **Rate Limiting**: Built-in protection against spam interactions

## Technical Implementation

### JavaScript Features
- **AJAX Requests**: Real-time like/reaction updates without page refresh
- **Dynamic UI Updates**: Button states and counts update instantly
- **Error Handling**: User-friendly error messages for failed requests
- **Responsive Design**: Works on desktop and mobile devices

### Database Design
- **Efficient Queries**: Optimized for quick like/comment counts
- **Indexing**: Proper indexing on memory and user foreign keys
- **Cascade Deletion**: Comments and likes are removed when memories are deleted

## Usage Examples

### Enabling Interactions
When creating a memory, users can check:
- "Allow Comments" - Enables comment functionality
- "Allow Likes/Reactions" - Enables like/reaction functionality

### Reacting to Memories
1. Navigate to a shared memory (not your own)
2. Click on any reaction button (Like, Love, Funny, etc.)
3. The reaction is applied instantly
4. Click the same button again to remove the reaction
5. Click a different button to change the reaction

### Adding Comments
1. Navigate to a shared memory with comments enabled (not your own)
2. Scroll to the comments section
3. Type a comment in the text area
4. Click "Post Comment"
5. The comment appears immediately in the comments list

## Future Enhancements

Potential improvements could include:
- **Comment Editing**: Allow users to edit their own comments
- **Comment Replies**: Nested comment threads
- **Reaction Analytics**: Show reaction breakdowns
- **Notification Preferences**: Customize notification settings
- **Moderation Tools**: Flag inappropriate content
- **Rich Text Comments**: Support for formatting and media in comments
