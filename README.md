# Memora Core - AI-Powered Memory Assistant

**Version 3.1.0** - Enhanced AI memory type recognition and improved search/filter functionality

A comprehensive Django-based memory management system featuring advanced AI-powered categorization, intelligent search, voice input, and personalized insights.

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

### 📊 Memory Organization
- **Memory Types**: Work, Personal, Learning, Idea, Reminder, General
- **Importance Levels**: 1-10 scale for priority management
- **Tag System**: AI-generated tags for easy categorization
- **Archive System**: Archive old memories while keeping them accessible

### 🔐 User Management
- **User Registration**: Secure account creation
- **Authentication**: Login/logout functionality
- **User-Specific Data**: Each user's memories are private and secure

### 🛠 Technical Features
- **Django Framework**: Robust web framework with admin interface
- **PostgreSQL Support**: Scalable database with advanced features
- **OpenAI Integration**: Advanced AI capabilities via OpenAI API
- **Responsive Design**: Works on desktop, tablet, and mobile
- **RESTful API**: Clean API design for future integrations

## 📱 Screenshots

*Screenshots will be added here*

## 🛠 Tech Stack

### Core Framework
- **Django**: 4.2.7 - Robust web framework
- **Python**: 3.8+ - Programming language
- **PostgreSQL**: 12+ - Primary database
- **SQLite**: 3.35+ - Development database

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

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/memora-core.git
cd memora-core
```

### 2. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env file with your settings
# Add your OpenAI API key
OPENAI_API_KEY=your_openai_api_key_here
```
### 5. Database Setup
```bash
# Run database migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Run the Application
```bash
# Start the development server
python manage.py runserver

# Access the application at http://127.0.0.1:8000/
```

### 7. Voice Features Setup (Optional)
```bash
# Install PyAudio for voice features
# On Windows:
pip install pyaudio

# On macOS:
brew install portaudio
pip install pyaudio

# On Linux:
sudo apt-get install python3-pyaudio
pip install pyaudio
```

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Start the Django development server
python manage.py runserver

# Access the application at http://127.0.0.1:8000/
# Admin interface at http://127.0.0.1:8000/admin/
```

### Production Deployment
```bash
# Collect static files
python manage.py collectstatic

# Run with production server (e.g., Gunicorn)
gunicorn memora_project.wsgi:application
```

## 🧪 Testing

### Run Test Suite
```bash
# Run all tests
python manage.py test

# Run specific test
python test_ai_memory_categorization.py
python test_search_filter.py
```

## 🆕 What's New in Version 3.1.0

### 🧠 Enhanced AI Memory Type Recognition
- **Advanced Categorization**: AI now provides detailed reasoning for memory categorization
- **Confidence Scores**: Each categorization includes a confidence level (0-100%)
- **Improved Accuracy**: Better recognition of memory types with more detailed prompts
- **Fallback System**: Multiple layers of AI services ensure reliability

### 🔍 Improved Search & Filter Functionality
- **Comprehensive Search**: Search across content, summary, tags, and AI reasoning
- **AI Semantic Search**: Find memories using natural language understanding
- **Advanced Filtering**: Filter by type, importance, and sort by various criteria
- **Smart Suggestions**: Get relevant suggestions when no exact matches found
- **Filter Summary**: Visual feedback showing current filter status

### 🎯 Key Improvements
- **Better User Experience**: Improved UI with clear visual feedback
- **Enhanced Performance**: More efficient search algorithms
- **Robust Error Handling**: Better fallback mechanisms
- **Comprehensive Testing**: Extensive test coverage for new features

## 📚 Documentation

- [AI Memory Categorization Guide](AI_MEMORY_CATEGORIZATION_GUIDE.md)
- [Search & Filter Improvements](SEARCH_FILTER_IMPROVEMENTS.md)
- [PostgreSQL Migration Guide](POSTGRESQL_MIGRATION.md)
- [Deployment Guide](DEPLOYMENT.md)

## 📁 Project Structure

```
memora-core/
├── memora_project/           # Django project settings
│   ├── settings.py          # Project configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI application
├── memory_assistant/        # Main Django app
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── urls.py              # App URL routing
│   ├── ai_services.py       # AI-powered services
│   ├── services.py          # ChatGPT integration
│   ├── voice_service.py     # Voice processing
│   ├── recommendation_service.py  # AI recommendations
│   ├── forms.py             # Django forms
│   ├── admin.py             # Admin interface
│   ├── templates/           # HTML templates
│   │   └── memory_assistant/
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── memory_list.html
│   │       ├── create_memory.html
│   │       └── search_results.html
│   └── migrations/          # Database migrations
├── requirements.txt         # Python dependencies
├── manage.py               # Django management script
├── env.example             # Environment variables template
├── version.py              # Version information
├── test_ai_memory_categorization.py  # AI test script
├── test_search_filter.py   # Search/filter test script
└── docs/                   # Documentation
    ├── AI_MEMORY_CATEGORIZATION_GUIDE.md
    ├── SEARCH_FILTER_IMPROVEMENTS.md
    └── POSTGRESQL_MIGRATION.md
```

## 🔧 Configuration

### Django Settings
Configure the application in `memora_project/settings.py`:

```python
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'memora_db',
        'USER': 'memora_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
```

### Environment Variables
Set up your environment variables in `.env`:

```env
# Django settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/memora_db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Voice features (optional)
ENABLE_VOICE_FEATURES=True
```

## 🔐 Security Features

- **User Authentication**: Secure login/logout system
- **CSRF Protection**: Built-in Django CSRF protection
- **SQL Injection Prevention**: Django ORM protection
- **XSS Protection**: Automatic HTML escaping
- **Secure Headers**: Django security middleware

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure production database
3. Set up static file serving
4. Configure HTTPS
5. Set up monitoring and logging

### Docker Deployment
```bash
# Build Docker image
docker build -t memora-core .

# Run container
docker run -p 8000:8000 memora-core
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
- Android-specific navigation patterns
- Background job processing
- Custom notification channels

### iOS
- iOS-specific UI patterns
- Face ID/Touch ID integration
- iOS notification handling
- Background app refresh

## 🐛 Troubleshooting

### Common Issues

1. **Metro bundler issues**:
```bash
npx react-native start --reset-cache
```

2. **iOS build issues**:
```bash
cd ios && pod install && cd ..
```

3. **Android build issues**:
```bash
cd android && ./gradlew clean && cd ..
```

4. **Permission issues**:
- Check device settings
- Reinstall the app
- Clear app data

### Debug Mode
Enable debug mode in development:
```bash
# Android
adb reverse tcp:8081 tcp:8081

# iOS
# Use Xcode debugger
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [Wiki](../../wiki)
- **Issues**: Report bugs on [GitHub Issues](../../issues)
- **Discussions**: Join the [GitHub Discussions](../../discussions)

## 🔄 Version History

- **v1.0.0**: Initial release with core features
- **v1.1.0**: Added voice search and biometric auth
- **v1.2.0**: Enhanced offline sync and notifications

## 📞 Contact

- **Email**: support@memora.app
- **Website**: https://memora.app
- **Twitter**: @memora_app

---

Made with ❤️ by the Memora Team 