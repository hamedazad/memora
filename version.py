"""
Version information for Memora Memory Assistant
"""

__version__ = "3.3.0"
__version_info__ = (3, 3, 0)

# Version history
VERSION_HISTORY = [
    "1.0.0 - Initial release with voice memory creation and search functionality",
    "1.1.0 - Added AI-powered personalized recommendations and insights",
    "1.2.0 - Added user registration system and authentication features",
    "2.0.0 - Added PostgreSQL support and enhanced AI features",
    "2.1.0 - Fixed database constraints and integrated OpenAI API key",
    "3.0.0 - Major release with advanced AI features and improved database architecture",
    "3.1.0 - Enhanced AI memory type recognition and improved search/filter functionality",
    "3.2.0 - Major search improvements: enhanced natural language processing, fixed QuerySet errors, improved voice search, and better date recognition",
    "3.3.0 - Enhanced AI Suggestions with contextual fallbacks, clickable dashboard cards, and improved JSON parsing for better user experience",
]

def get_version():
    """Get the current version string"""
    return __version__

def get_version_info():
    """Get the current version as a tuple"""
    return __version_info__

def get_version_history():
    """Get the version history"""
    return VERSION_HISTORY 