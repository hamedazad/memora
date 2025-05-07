# 🧠 Memora

"Speak It. Save It. Recall It."

Memora is an AI-powered memory assistant built with Django + OpenAI. It helps users record important facts using natural language and retrieve them later using questions.

---

## ✨ Features

- 🔐 Token-based user authentication (login)
- 📝 Save structured memories from free-form input
- 🤖 Ask natural questions to retrieve saved info
- 🧠 OpenAI-powered memory parsing
- 🎤 Voice input + speech reply via Web API
- 📦 REST API (chat + login)

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/hamedazad/memora.git
cd memora

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file and add your OpenAI key
echo OPENAI_API_KEY=sk-... > .env

# Run the app
python manage.py runserver
