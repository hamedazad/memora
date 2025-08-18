import speech_recognition as sr
import pyttsx3
from typing import Tuple, Dict, Any, Optional
import json
import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class MultilingualVoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # Initialize pyttsx3 for offline TTS
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('volume', 0.9)
            self.available_voices = self.engine.getProperty('voices')
            self.pyttsx3_available = True
        except Exception as e:
            print(f"pyttsx3 initialization failed: {e}")
            self.engine = None
            self.available_voices = []
            self.pyttsx3_available = False
        
        # Language to voice mapping for pyttsx3
        self.language_voice_map = self._create_language_voice_map()
        
        # Initialize OpenAI client for categorization
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key and api_key != 'your_openai_api_key_here':
            try:
                self.openai_client = OpenAI(api_key=api_key)
                self.ai_available = True
            except Exception:
                self.openai_client = None
                self.ai_available = False
        else:
            self.openai_client = None
            self.ai_available = False
        
        # Initialize microphone only if PyAudio is available
        try:
            self.microphone = sr.Microphone()
            self.voice_available = True
        except Exception:
            self.microphone = None
            self.voice_available = False
    
    def _create_language_voice_map(self) -> Dict[str, str]:
        """Create mapping of language codes to available pyttsx3 voices"""
        language_map = {}
        
        if not self.pyttsx3_available:
            return language_map
        
        # Common language patterns in voice names
        language_patterns = {
            'en': ['english', 'en-us', 'en-gb', 'us', 'uk'],
            'es': ['spanish', 'es-es', 'es-mx'],
            'fr': ['french', 'fr-fr', 'fr-ca'],
            'de': ['german', 'de-de', 'de-at'],
            'ar': ['arabic', 'ar-sa', 'ar-eg'],
            'fa': ['persian', 'farsi', 'fa-ir'],
            'zh': ['chinese', 'zh-cn', 'zh-tw'],
            'ru': ['russian', 'ru-ru'],
            'ja': ['japanese', 'ja-jp']
        }
        
        for voice in self.available_voices:
            voice_name = voice.name.lower()
            voice_id = voice.id
            
            for lang_code, patterns in language_patterns.items():
                for pattern in patterns:
                    if pattern in voice_name:
                        language_map[lang_code] = voice_id
                        break
                if lang_code in language_map:
                    break
        
        return language_map
    
    def listen_for_speech(self, timeout: int = 5, language: str = 'en') -> Tuple[bool, str]:
        """Listen for speech with language-specific recognition"""
        if not self.voice_available or self.microphone is None:
            return False, "Voice input not available. PyAudio is required for microphone access."
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Try language-specific recognition first
                try:
                    text = self.recognizer.recognize_google(audio, language=self._get_google_language_code(language))
                    return True, text
                except:
                    # Fallback to default recognition
                    text = self.recognizer.recognize_google(audio)
                    return True, text
        except Exception as e:
            return False, f"Error: {e}"
    
    def _get_google_language_code(self, language: str) -> str:
        """Convert our language codes to Google Speech Recognition codes"""
        google_codes = {
            'en': 'en-US',
            'es': 'es-ES',
            'fr': 'fr-FR',
            'de': 'de-DE',
            'ar': 'ar-SA',
            'fa': 'fa-IR',
            'zh': 'zh-CN',
            'ru': 'ru-RU',
            'ja': 'ja-JP'
        }
        return google_codes.get(language, 'en-US')
    
    def speak_text(self, text: str) -> bool:
        """Speak text using pyttsx3 (offline)"""
        if not self.pyttsx3_available or not self.engine:
            return False
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 speech error: {e}")
            return False
    
    def speak_with_gtts(self, text: str, language: str) -> bool:
        """Speak text using gTTS (online, more languages)"""
        try:
            from gtts import gTTS
            import pygame
            
            # Create temporary audio file
            tts = gTTS(text=text, lang=language)
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            tts.save(temp_file.name)
            
            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file.name)
            pygame.mixer.music.play()
            
            # Wait for audio to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Clean up
            pygame.mixer.quit()
            os.unlink(temp_file.name)
            return True
            
        except ImportError:
            print("gTTS or pygame not installed. Install with: pip install gtts pygame")
            return False
        except Exception as e:
            print(f"gTTS speech error: {e}")
            return False
    

    
    def speak_memory(self, memory) -> bool:
        """Speak memory content"""
        text_to_speak = f"Memory: {memory.content}"
        if memory.summary:
            text_to_speak += f" Summary: {memory.summary}"
        
        return self.speak_text(text_to_speak)
    

    
    def categorize_audio_memory(self, audio_text: str) -> Dict[str, Any]:
        """Categorize audio-transcribed memory content using enhanced AI."""
        if not self.ai_available or not self.openai_client:
            return {
                "category": "general",
                "confidence": 50,
                "tags": ["general"],
                "summary": f"Audio memory about: {audio_text[:100]}...",
                "importance": 5
            }
        
        # Try to use the enhanced AI service first
        try:
            from .ai_services import get_ai_service
            ai_service = get_ai_service()
            result = ai_service.categorize_audio_memory(audio_text)
            return result
        except Exception as e:
            print(f"Enhanced AI service failed, falling back to basic categorization: {e}")
        
        # Fallback to basic categorization
        try:
            prompt = f"""
            This is a transcribed audio memory. Analyze and categorize it with high precision into one of these categories:

            CATEGORY DEFINITIONS:
            - work: Professional tasks, meetings, projects, career-related items, business activities, job responsibilities, workplace events, professional development, work deadlines, team activities, client interactions, business ideas, work-related learning
            - personal: Family, friends, hobbies, personal life, relationships, social events, personal celebrations, family activities, personal interests, social gatherings, personal goals, lifestyle choices, personal experiences
            - learning: Education, skills, courses, knowledge acquisition, academic activities, training sessions, reading notes, study materials, educational goals, skill development, research, tutorials, workshops, certifications
            - idea: Creative thoughts, innovations, concepts, brainstorming, creative projects, inventions, artistic ideas, business concepts, problem-solving ideas, innovative solutions, creative inspiration, design ideas
            - reminder: Tasks, to-dos, appointments, deadlines, scheduled events, time-sensitive activities, future plans, calendar events, action items, follow-ups, time management, planning activities
            - general: Everything else that doesn't fit the above categories

            ANALYSIS INSTRUCTIONS:
            1. Look for specific keywords and context clues in the audio transcription
            2. Consider the intent and purpose of the spoken memory
            3. Identify the primary focus of the content
            4. Consider temporal aspects (past events vs future plans)
            5. Evaluate the emotional and practical significance
            6. Account for potential transcription errors or unclear speech

            Audio transcription: {audio_text}

            Provide a detailed analysis in JSON format:
            {{
                "category": "work|personal|learning|idea|reminder|general",
                "confidence": 0-100,
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
                "summary": "1-2 sentence summary",
                "importance": 1-10,
                "reasoning": "Brief explanation of why this category was chosen"
            }}
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert AI memory analyst specializing in audio transcriptions. You excel at identifying the primary purpose and context of spoken memories, even with potential transcription errors. Be precise, consistent, and provide well-reasoned categorizations."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Ensure the category is valid
            valid_categories = ['work', 'personal', 'learning', 'idea', 'reminder', 'general']
            if result.get('category') not in valid_categories:
                result['category'] = 'general'
            
            # Ensure importance is within range
            importance = result.get('importance', 5)
            if not isinstance(importance, int) or importance < 1 or importance > 10:
                result['importance'] = 5
            
            return result
        except Exception as e:
            print(f"Error in categorize_audio_memory: {e}")
            return {
                "category": "general",
                "confidence": 50,
                "tags": ["general"],
                "summary": f"Audio memory about: {audio_text[:100]}...",
                "importance": 5,
                "reasoning": "Fallback categorization due to processing error"
            }

# Create global instance
voice_service = MultilingualVoiceService() 