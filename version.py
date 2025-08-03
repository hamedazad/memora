"""
Version information for Memora Memory Assistant
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)

# Version history
VERSION_HISTORY = [
    "1.0.0 - Initial release with voice memory creation and search functionality",
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