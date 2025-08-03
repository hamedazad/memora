"""
Version information for Memora Memory Assistant
"""

__version__ = "1.2.0"
__version_info__ = (1, 2, 0)

# Version history
VERSION_HISTORY = [
    "1.0.0 - Initial release with voice memory creation and search functionality",
    "1.1.0 - Added AI-powered personalized recommendations and insights",
    "1.2.0 - Added user registration system and authentication features",
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