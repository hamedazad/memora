import speech_recognition as sr
import pyttsx3
from typing import Tuple, Dict, Any
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        
        # Configure text-to-speech engine
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
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
    
    def listen_for_speech(self, timeout: int = 5) -> Tuple[bool, str]:
        if not self.voice_available or self.microphone is None:
            return False, "Voice input not available. PyAudio is required for microphone access."
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                return True, text
        except Exception as e:
            return False, f"Error: {e}"
    
    def speak_text(self, text: str) -> bool:
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            return False
    
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

voice_service = VoiceService() 