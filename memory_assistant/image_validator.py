"""
Image Upload Validator

Validates image uploads for size, type, dimensions, and content.
Ensures secure and appropriate image uploads.
"""

import os
from typing import Dict, Any, Tuple
from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile


class ImageUploadValidator:
    """
    Validates image uploads with comprehensive checks
    """
    
    # Configuration
    MAX_FILE_SIZE_MB = 10  # 10 MB
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    ALLOWED_MIME_TYPES = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
    ]
    
    MAX_DIMENSIONS = (4096, 4096)  # Max width x height
    MIN_DIMENSIONS = (10, 10)      # Min width x height
    
    @classmethod
    def validate_image(cls, image_file: UploadedFile) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate uploaded image file
        
        Args:
            image_file: Django UploadedFile object
            
        Returns:
            Tuple of (is_valid, error_message, metadata)
        """
        try:
            # Validation 1: File size
            if image_file.size > cls.MAX_FILE_SIZE_BYTES:
                size_mb = image_file.size / (1024 * 1024)
                return False, f'Image too large: {size_mb:.2f}MB. Maximum size: {cls.MAX_FILE_SIZE_MB}MB', {}
            
            if image_file.size == 0:
                return False, 'Image file is empty', {}
            
            # Validation 2: File extension
            file_ext = cls._get_file_extension(image_file.name).lower()
            if file_ext not in cls.ALLOWED_EXTENSIONS:
                return False, f'Invalid file type: .{file_ext}. Allowed: {", ".join(cls.ALLOWED_EXTENSIONS)}', {}
            
            # Validation 3: MIME type
            content_type = image_file.content_type
            if content_type and content_type not in cls.ALLOWED_MIME_TYPES:
                return False, f'Invalid MIME type: {content_type}. Allowed image types only.', {}
            
            # Validation 4: Image content (can it be opened?)
            try:
                img = Image.open(image_file)
                img.verify()  # Verify it's a valid image
                
                # Re-open for size check (verify() closes the image)
                image_file.seek(0)
                img = Image.open(image_file)
                width, height = img.size
                format_name = img.format
                mode = img.mode
                
                # Reset file pointer for later use
                image_file.seek(0)
                
            except Exception as e:
                return False, f'Invalid or corrupted image file: {str(e)}', {}
            
            # Validation 5: Dimensions
            if width > cls.MAX_DIMENSIONS[0] or height > cls.MAX_DIMENSIONS[1]:
                return False, f'Image dimensions too large: {width}x{height}px. Maximum: {cls.MAX_DIMENSIONS[0]}x{cls.MAX_DIMENSIONS[1]}px', {}
            
            if width < cls.MIN_DIMENSIONS[0] or height < cls.MIN_DIMENSIONS[1]:
                return False, f'Image dimensions too small: {width}x{height}px. Minimum: {cls.MIN_DIMENSIONS[0]}x{cls.MIN_DIMENSIONS[1]}px', {}
            
            # All validations passed
            metadata = {
                'width': width,
                'height': height,
                'format': format_name,
                'mode': mode,
                'size_bytes': image_file.size,
                'size_mb': round(image_file.size / (1024 * 1024), 2),
                'size_kb': round(image_file.size / 1024, 2),
                'extension': file_ext,
                'mime_type': content_type,
                'filename': image_file.name,
            }
            
            return True, 'Image validation passed', metadata
            
        except Exception as e:
            return False, f'Validation error: {str(e)}', {}
    
    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """Extract file extension from filename"""
        return filename.rsplit('.', 1)[-1] if '.' in filename else ''
    
    @classmethod
    def get_validation_rules(cls) -> Dict[str, Any]:
        """
        Get validation rules for API documentation
        
        Returns:
            Dict with all validation rules
        """
        return {
            'max_file_size_mb': cls.MAX_FILE_SIZE_MB,
            'max_file_size_bytes': cls.MAX_FILE_SIZE_BYTES,
            'allowed_extensions': cls.ALLOWED_EXTENSIONS,
            'allowed_mime_types': cls.ALLOWED_MIME_TYPES,
            'max_dimensions': {
                'width': cls.MAX_DIMENSIONS[0],
                'height': cls.MAX_DIMENSIONS[1]
            },
            'min_dimensions': {
                'width': cls.MIN_DIMENSIONS[0],
                'height': cls.MIN_DIMENSIONS[1]
            },
        }
    
    @classmethod
    def validate_django_field(cls, image_file):
        """
        Django model field validator
        
        Use in model field definition:
        image = models.ImageField(validators=[ImageUploadValidator.validate_django_field])
        """
        is_valid, error_message, metadata = cls.validate_image(image_file)
        
        if not is_valid:
            raise ValidationError(error_message)




























