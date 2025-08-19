# Memora Core - AI-Powered Memory Assistant

**Version 4.2.0** - Mobile app API support, REST API endpoints, JWT authentication, and production deployment

A comprehensive Django-based memory management system featuring advanced AI-powered categorization, intelligent search, voice input, personalized insights, and mobile app support.

## 🚀 Features

### 🧠 AI-Powered Memory Management
- **Smart Categorization**: AI automatically recognizes memory types (Work, Personal, Learning, Idea, Reminder, General)
- **Intelligent Summarization**: AI generates concise summaries of your memories
- **Automatic Tagging**: AI creates relevant tags for easy organization
- **Importance Scoring**: AI assesses and suggests importance levels (1-10)
- **Reasoning Display**: See why AI categorized your memory the way it did

### 🔍 Enhanced Search & Filter
- **Comprehensive Search**: Search across content, summary, tags, and AI reasoning
- **AI Semantic Search**: Find memories using natural language understanding
- **Advanced Filtering**: Filter by type, importance, and date
- **Multiple Sorting**: Sort by newest, oldest, importance, or type
- **Smart Suggestions**: Get relevant suggestions when no exact matches found

### 🎤 Voice Features
- **Voice Input**: Create memories using speech-to-text
- **Voice Search**: Search memories using voice commands
- **Voice Reading**: Have memories read aloud to you
- **Audio Categorization**: AI categorizes voice-transcribed memories

### 📱 Mobile App Support
- **REST API**: Complete RESTful API for mobile app development
- **JWT Authentication**: Secure token-based authentication
- **Mobile-Optimized**: API endpoints designed for mobile apps
- **Real-time Sync**: Synchronize data across devices
- **Push Notifications**: Ready for mobile notifications

### 🔐 User Management
- **User Registration**: Secure account creation
- **Authentication**: Login/logout functionality with JWT support
- **User-Specific Data**: Each user's memories are private and secure
- **Social Features**: Share memories with friends and organizations

### 🛠 Technical Features
- **Django Framework**: Robust web framework with admin interface
- **PostgreSQL Support**: Scalable database with advanced features
- **OpenAI Integration**: Advanced AI capabilities via OpenAI API
- **Responsive Design**: Works on desktop, tablet, and mobile
- **RESTful API**: Clean API design for mobile app integration
- **Cost Monitoring**: Track API usage and costs
- **Production Ready**: Deployment configuration for cloud platforms

## 📱 Mobile App API

### Authentication Endpoints
```
POST /api/v1/auth/token/          # Login and get JWT token
POST /api/v1/auth/token/refresh/  # Refresh JWT token
POST /api/v1/auth/token/verify/   # Verify JWT token
```

### Memory Management
```
GET    /api/v1/memories/                    # List memories
POST   /api/v1/memories/                    # Create memory
GET    /api/v1/memories/{id}/               # Get memory details
PUT    /api/v1/memories/{id}/               # Update memory
DELETE /api/v1/memories/{id}/               # Delete memory
POST   /api/v1/memories/quick-add/          # Quick add memory
```

### Search & Discovery
```
GET /api/v1/memories/search/                # Search memories
GET /api/v1/memories/dashboard-stats/       # Dashboard statistics
```

### AI Features
```
GET  /api/v1/ai/suggestions/                # AI memory suggestions
POST /api/v1/ai/enhance-memory/             # Enhance memory with AI
```

## 🛠 Tech Stack

### Core Framework
- **Django**: 5.2.4 - Robust web framework
- **Python**: 3.8+ - Programming language
- **PostgreSQL**: 12+ - Primary database
- **SQLite**: 3.35+ - Development database

### API & Authentication
- **Django REST Framework**: 3.16.1 - REST API framework
- **JWT Authentication**: Secure token-based auth
- **CORS Support**: Cross-origin resource sharing
- **Rate Limiting**: API usage protection

### AI & Machine Learning
- **OpenAI GPT-3.5-turbo**: Advanced language model for AI features
- **OpenAI API**: Integration for memory categorization and analysis
- **Natural Language Processing**: Semantic search and text analysis

### Voice Processing
- **SpeechRecognition**: Speech-to-text conversion
- **pyttsx3**: Text-to-speech synthesis
- **PyAudio**: Audio processing and microphone access

### Frontend & UI
- **Bootstrap 5**: Modern responsive UI framework
- **Bootstrap Icons**: Icon library
- **HTML5/CSS3**: Modern web standards
- **JavaScript**: Interactive functionality

### Database & ORM
- **Django ORM**: Object-relational mapping
- **Django Migrations**: Database schema management
- **JSON Fields**: Flexible data storage for tags and metadata

### Development & Deployment
- **Git**: Version control
- **Docker**: Containerization (optional)
- **Virtual Environment**: Python dependency isolation
- **Environment Variables**: Secure configuration management
- **Production Settings**: Optimized for cloud deployment

## 📋 Prerequisites

### Development Environment
- **Python**: 3.8 or later
- **pip**: Python package installer
- **Git**: Version control system
- **PostgreSQL**: 12 or later (for production)
- **SQLite**: 3.35 or later (for development)

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet Connection**: Required for OpenAI API access

### API Requirements
- **OpenAI API Key**: Required for AI features
- **Google Speech Recognition**: Free tier available for voice features 