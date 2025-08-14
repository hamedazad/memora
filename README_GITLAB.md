# Memora - AI-Powered Memory Assistant

[![Version](https://img.shields.io/badge/version-4.1.0--release-blue.svg)](https://gitlab.com/yourusername/memora)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🧠 Overview

Memora is an intelligent memory management system that uses AI to help you capture, organize, and recall your most important memories. With voice input, smart search, and AI-powered insights, Memora transforms how you manage personal and professional information.

## ✨ Features

### 🎯 Core Features
- **Voice Memory Creation** - Create memories hands-free with natural voice commands
- **AI-Powered Insights** - Get intelligent suggestions and automatic categorization
- **Smart Search** - Find memories instantly with natural language queries
- **Smart Reminders** - Never miss important tasks with intelligent notifications
- **Social Sharing** - Share memories with friends, family, or team members
- **Privacy First** - Enterprise-grade security with full control over your data

### 🎨 Modern UI/UX
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile
- **Modern Interface** - Clean, intuitive design with smooth animations
- **Fast Performance** - Optimized for quick loading and smooth interactions
- **Accessibility** - WCAG compliant with keyboard navigation support

### 🤖 AI Capabilities
- **Natural Language Processing** - Understand context and intent
- **Automatic Categorization** - Smart tagging and organization
- **Personalized Recommendations** - Learn from your usage patterns
- **Voice Recognition** - High-accuracy speech-to-text conversion

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- PostgreSQL 12 or higher
- OpenAI API key (for AI features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://gitlab.com/yourusername/memora.git
   cd memora
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open http://localhost:8000 in your browser
   - Register a new account or use the admin credentials

## 📁 Project Structure

```
memora/
├── memora_project/          # Django project settings
├── memory_assistant/        # Main application
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   ├── migrations/        # Database migrations
│   └── management/        # Custom management commands
├── media/                 # User-uploaded files
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── README.md            # This file
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/memora

# OpenAI API (for AI features)
OPENAI_API_KEY=your-openai-api-key

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database**
   ```sql
   CREATE DATABASE memora;
   CREATE USER memora_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE memora TO memora_user;
   ```

## 🎯 Usage

### Creating Memories

1. **Voice Input**: Click the microphone icon and speak naturally
2. **Text Input**: Type your memory in the text area
3. **Smart Categorization**: AI automatically tags and categorizes your memory
4. **Save**: Your memory is stored with intelligent metadata

### Searching Memories

1. **Natural Language**: Ask questions like "What did I discuss with John last week?"
2. **Keywords**: Search by tags, categories, or specific words
3. **Date Filters**: Filter by date ranges or specific periods
4. **Smart Suggestions**: Get AI-powered search suggestions

### Managing Reminders

1. **Automatic Detection**: AI identifies time-sensitive information
2. **Smart Scheduling**: Intelligent reminder timing based on context
3. **Custom Reminders**: Set manual reminders for important events
4. **Notification Management**: Control how and when you receive notifications

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Add tests** for new functionality
5. **Commit your changes**
   ```bash
   git commit -m "Add: description of your changes"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Merge Request**

### Development Guidelines

- Follow PEP 8 Python style guidelines
- Write comprehensive tests
- Update documentation for new features
- Ensure all tests pass before submitting

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test memory_assistant

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 📦 Deployment

### Production Setup

1. **Set up production environment**
   ```bash
   export DEBUG=False
   export ALLOWED_HOSTS=your-domain.com
   ```

2. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

3. **Set up web server** (Nginx + Gunicorn recommended)
   ```bash
   pip install gunicorn
   gunicorn memora_project.wsgi:application
   ```

4. **Configure SSL** for secure connections

### Docker Deployment

```bash
# Build the image
docker build -t memora .

# Run the container
docker run -p 8000:8000 memora
```

## 📊 Performance

- **Page Load Time**: < 2 seconds
- **Search Response**: < 500ms
- **Voice Processing**: < 3 seconds
- **Database Queries**: Optimized with proper indexing

## 🔒 Security

- **Data Encryption**: All sensitive data is encrypted at rest
- **Authentication**: Secure user authentication with password hashing
- **Authorization**: Role-based access control
- **Input Validation**: Comprehensive input sanitization
- **CSRF Protection**: Built-in Django CSRF protection

## 📈 Monitoring

- **Application Metrics**: Performance monitoring and logging
- **Error Tracking**: Comprehensive error reporting
- **User Analytics**: Usage statistics and insights
- **Health Checks**: Automated system health monitoring

## 🆘 Support

### Getting Help

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and feature requests via GitLab Issues
- **Discussions**: Join community discussions in GitLab Discussions
- **Email**: Contact support at support@memora.com

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and credentials are correct
2. **API Keys**: Verify OpenAI API key is valid and has sufficient credits
3. **Static Files**: Run `collectstatic` if static files aren't loading
4. **Migrations**: Run `migrate` if database schema is outdated

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT API
- **Django** for the excellent web framework
- **Bootstrap** for the responsive UI components
- **Bootstrap Icons** for the beautiful icons
- **All contributors** who have helped improve Memora

## 📞 Contact

- **Project Maintainer**: [Your Name](mailto:your.email@example.com)
- **Project Website**: https://memora.com
- **GitLab Repository**: https://gitlab.com/yourusername/memora

---

**Made with ❤️ by the Memora Team**

*Version 4.1.0-release - Modernized login and registration pages with improved design, performance, and user experience*
