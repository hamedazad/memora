"""
Utility functions for timezone handling in Memora
Ensures memories are saved in user's local timezone
"""
import pytz
from django.utils import timezone
from datetime import datetime


# Country to timezone mapping for registration
COUNTRY_TIMEZONE_MAP = {
    'US': 'America/New_York',
    'CA': 'America/Toronto',
    'MX': 'America/Mexico_City',
    'GB': 'Europe/London',
    'IE': 'Europe/Dublin',
    'FR': 'Europe/Paris',
    'DE': 'Europe/Berlin',
    'IT': 'Europe/Rome',
    'ES': 'Europe/Madrid',
    'PT': 'Europe/Lisbon',
    'NL': 'Europe/Amsterdam',
    'BE': 'Europe/Brussels',
    'CH': 'Europe/Zurich',
    'AT': 'Europe/Vienna',
    'SE': 'Europe/Stockholm',
    'NO': 'Europe/Oslo',
    'DK': 'Europe/Copenhagen',
    'FI': 'Europe/Helsinki',
    'PL': 'Europe/Warsaw',
    'CZ': 'Europe/Prague',
    'HU': 'Europe/Budapest',
    'RO': 'Europe/Bucharest',
    'BG': 'Europe/Sofia',
    'GR': 'Europe/Athens',
    'TR': 'Europe/Istanbul',
    'RU': 'Europe/Moscow',
    'UA': 'Europe/Kiev',
    'JP': 'Asia/Tokyo',
    'CN': 'Asia/Shanghai',
    'KR': 'Asia/Seoul',
    'IN': 'Asia/Kolkata',
    'TH': 'Asia/Bangkok',
    'VN': 'Asia/Ho_Chi_Minh',
    'SG': 'Asia/Singapore',
    'MY': 'Asia/Kuala_Lumpur',
    'ID': 'Asia/Jakarta',
    'PH': 'Asia/Manila',
    'PK': 'Asia/Karachi',
    'BD': 'Asia/Dhaka',
    'IR': 'Asia/Tehran',
    'IQ': 'Asia/Baghdad',
    'SA': 'Asia/Riyadh',
    'AE': 'Asia/Dubai',
    'IL': 'Asia/Jerusalem',
    'AU': 'Australia/Sydney',
    'NZ': 'Pacific/Auckland',
    'FJ': 'Pacific/Fiji',
    'BR': 'America/Sao_Paulo',
    'AR': 'America/Argentina/Buenos_Aires',
    'CL': 'America/Santiago',
    'CO': 'America/Bogota',
    'PE': 'America/Lima',
    'VE': 'America/Caracas',
    'ZA': 'Africa/Johannesburg',
    'EG': 'Africa/Cairo',
    'NG': 'Africa/Lagos',
    'KE': 'Africa/Nairobi',
    'ET': 'Africa/Addis_Ababa',
}


def get_country_choices():
    """
    Returns a list of (country_code, country_name) tuples for form choices
    """
    countries = [
        ('', 'Select your country'),
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('MX', 'Mexico'),
        ('GB', 'United Kingdom'),
        ('IE', 'Ireland'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('PT', 'Portugal'),
        ('NL', 'Netherlands'),
        ('BE', 'Belgium'),
        ('CH', 'Switzerland'),
        ('AT', 'Austria'),
        ('SE', 'Sweden'),
        ('NO', 'Norway'),
        ('DK', 'Denmark'),
        ('FI', 'Finland'),
        ('PL', 'Poland'),
        ('CZ', 'Czech Republic'),
        ('HU', 'Hungary'),
        ('RO', 'Romania'),
        ('BG', 'Bulgaria'),
        ('GR', 'Greece'),
        ('TR', 'Turkey'),
        ('RU', 'Russia'),
        ('UA', 'Ukraine'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('KR', 'South Korea'),
        ('IN', 'India'),
        ('TH', 'Thailand'),
        ('VN', 'Vietnam'),
        ('SG', 'Singapore'),
        ('MY', 'Malaysia'),
        ('ID', 'Indonesia'),
        ('PH', 'Philippines'),
        ('PK', 'Pakistan'),
        ('BD', 'Bangladesh'),
        ('IR', 'Iran'),
        ('IQ', 'Iraq'),
        ('SA', 'Saudi Arabia'),
        ('AE', 'United Arab Emirates'),
        ('IL', 'Israel'),
        ('AU', 'Australia'),
        ('NZ', 'New Zealand'),
        ('FJ', 'Fiji'),
        ('BR', 'Brazil'),
        ('AR', 'Argentina'),
        ('CL', 'Chile'),
        ('CO', 'Colombia'),
        ('PE', 'Peru'),
        ('VE', 'Venezuela'),
        ('ZA', 'South Africa'),
        ('EG', 'Egypt'),
        ('NG', 'Nigeria'),
        ('KE', 'Kenya'),
        ('ET', 'Ethiopia'),
    ]
    return countries


def get_timezone_for_country(country_code):
    """
    Get the timezone string for a given country code
    Returns UTC if country code is not found
    """
    return COUNTRY_TIMEZONE_MAP.get(country_code, 'UTC')


def get_user_timezone(user):
    """
    Get the user's timezone from their profile
    Returns a pytz timezone object
    """
    try:
        if hasattr(user, 'profile') and user.profile:
            tz_name = user.profile.user_timezone
            return pytz.timezone(tz_name)
    except:
        pass
    
    # Default to UTC if no profile timezone
    return pytz.UTC


def get_current_time_in_user_timezone(user):
    """
    Get the current time in the user's local timezone
    This is what should be saved as created_at for memories
    """
    user_tz = get_user_timezone(user)
    
    # Get current UTC time
    utc_now = datetime.now(pytz.UTC)
    
    # Convert to user's timezone
    local_time = utc_now.astimezone(user_tz)
    
    return local_time


def convert_to_user_timezone(dt, user):
    """
    Convert any datetime to user's timezone
    """
    if dt is None:
        return None
    
    user_tz = get_user_timezone(user)
    
    # Make sure datetime is timezone-aware
    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = pytz.UTC.localize(dt)
    
    return dt.astimezone(user_tz)


def naive_datetime_in_user_timezone(user):
    """
    Get current time in user's timezone as a naive datetime
    (without timezone info - for storage in database with USE_TZ=False)
    """
    user_tz = get_user_timezone(user)
    utc_now = datetime.now(pytz.UTC)
    local_time = utc_now.astimezone(user_tz)
    
    # Return as naive datetime (remove timezone info)
    return local_time.replace(tzinfo=None)
