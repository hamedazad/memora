#!/usr/bin/env python3
"""
Test script for multilingual TTS functionality
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memora_project.settings')
django.setup()

from memory_assistant.voice_service import MultilingualVoiceService

def test_multilingual_tts():
    """Test the multilingual TTS functionality"""
    print("🧪 Testing Multilingual TTS Implementation")
    print("=" * 50)
    
    # Initialize the voice service
    voice_service = MultilingualVoiceService()
    
    print(f"✅ pyttsx3 available: {voice_service.pyttsx3_available}")
    print(f"✅ Voice input available: {voice_service.voice_available}")
    print(f"✅ AI available: {voice_service.ai_available}")
    
    # Test language detection
    test_texts = {
        'en': 'Hello, this is a test message in English.',
        'es': 'Hola, este es un mensaje de prueba en español.',
        'fr': 'Bonjour, ceci est un message de test en français.',
        'de': 'Hallo, dies ist eine Testnachricht auf Deutsch.',
        'ar': 'مرحبا، هذه رسالة اختبار باللغة العربية.',
        'fa': 'سلام، این یک پیام آزمایشی به فارسی است.',
        'zh': '你好，这是一条中文测试消息。',
        'ru': 'Привет, это тестовое сообщение на русском языке.',
        'ja': 'こんにちは、これは日本語のテストメッセージです。'
    }
    
    print("\n🔍 Testing Language Detection:")
    print("-" * 30)
    
    for lang_code, text in test_texts.items():
        detected = voice_service.detect_language(text)
        status = "✅" if detected == lang_code else "❌"
        print(f"{status} {lang_code.upper()}: '{text[:30]}...' -> Detected: {detected}")
    
    # Test TTS for each language
    print("\n🔊 Testing Text-to-Speech:")
    print("-" * 30)
    
    for lang_code, text in test_texts.items():
        print(f"Testing TTS for {lang_code.upper()}...")
        
        # Test pyttsx3 first
        success_pyttsx3 = voice_service.speak_text(text, lang_code)
        print(f"  pyttsx3: {'✅' if success_pyttsx3 else '❌'}")
        
        # Test gTTS fallback
        success_gtts = voice_service.speak_with_gtts(text, lang_code)
        print(f"  gTTS: {'✅' if success_gtts else '❌'}")
        
        # Test combined approach
        success_combined = voice_service.speak_text_multilingual(text, lang_code)
        print(f"  Combined: {'✅' if success_combined else '❌'}")
        print()
    
    print("🎉 Multilingual TTS Test Complete!")
    print("\n📋 Summary:")
    print(f"- pyttsx3 (offline): {'✅ Available' if voice_service.pyttsx3_available else '❌ Not available'}")
    print(f"- gTTS (online): {'✅ Available' if 'gtts' in sys.modules else '❌ Not installed'}")
    print(f"- Language detection: {'✅ Available' if voice_service.ai_available else '❌ Not available'}")
    
    print("\n💡 To install missing dependencies:")
    print("pip install gtts pygame")

if __name__ == "__main__":
    test_multilingual_tts()
