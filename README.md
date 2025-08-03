# Memora Memory Assistant v1.0.0

A Django-based memory management application with advanced voice capabilities for creating, searching, and managing personal memories.

## 🚀 Features

- **Voice Memory Creation**: Create memories using voice input with browser-based speech recognition
- **Smart Search**: Advanced search with contextual filtering and relevance scoring
- **Voice Search**: Search memories using voice commands
- **Text-to-Speech**: Listen to your memories being read aloud
- **AI-Powered Summaries**: Automatic memory summarization using ChatGPT
- **Time-Aware Search**: Intelligent filtering based on time context (today, tomorrow, etc.)
- **Responsive Design**: Modern, mobile-friendly interface

## 📋 Requirements

- Python 3.8+
- Django 5.2+
- Modern web browser with Web Speech API support
- OpenAI API key (optional, for AI features)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/memora.git
   cd memora
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the project root:
   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   OPENAI_API_KEY=your-openai-api-key-here
   ```

5. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   Open your browser and go to `http://127.0.0.1:8000`

## 🎯 Usage

### Creating Memories
- Use the voice creation feature to speak your memories
- Or use the text input for manual entry
- Memories are automatically summarized and tagged

### Searching Memories
- Use the search bar for text-based searches
- Use voice search for hands-free memory retrieval
- Search results are ranked by relevance and recency

### Voice Features
- **Voice Creation**: Click the microphone button and speak clearly
- **Voice Search**: Use natural language queries like "what's my plan for today"
- **Text-to-Speech**: Click the speaker icon to hear memories read aloud

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key for security
- `DEBUG`: Set to False in production
- `OPENAI_API_KEY`: Required for AI-powered features

### Browser Compatibility
The voice features require a modern browser with Web Speech API support:
- Chrome 25+
- Firefox 44+
- Safari 14.1+
- Edge 79+

## 📦 Version History

### v1.0.0 (Current)
- Initial release
- Voice memory creation and search
- Advanced contextual search filtering
- Time-aware search capabilities
- AI-powered memory summarization
- Responsive web interface

## 🐛 Known Issues

- Voice features require HTTPS in production
- Some browsers may require microphone permissions
- Speech recognition accuracy varies by accent and environment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:
1. Check the browser console for errors
2. Ensure your browser supports Web Speech API
3. Verify microphone permissions are granted
4. Check the Django server logs for backend errors

## 🔮 Roadmap

- [ ] Mobile app development
- [ ] Offline voice processing
- [ ] Multi-language support
- [ ] Memory sharing features
- [ ] Advanced AI integrations
- [ ] Calendar integration

---

**Memora Memory Assistant v1.0.0** - Making memory management effortless and intuitive. 