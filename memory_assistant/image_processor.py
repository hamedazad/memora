"""
Image Processing Service

Handles image optimization, resizing, and thumbnail generation.
Reduces file sizes while maintaining quality.
"""

import os
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from typing import Tuple, Optional


class ImageProcessor:
    """
    Process images for optimal storage and display
    """
    
    # Target dimensions
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1920
    THUMBNAIL_WIDTH = 300
    THUMBNAIL_HEIGHT = 300
    
    # Quality settings
    JPEG_QUALITY = 85
    PNG_OPTIMIZE = True
    WEBP_QUALITY = 80
    
    @classmethod
    def optimize_image(cls, image_file: InMemoryUploadedFile) -> InMemoryUploadedFile:
        """
        Optimize image for storage
        
        - Resizes if too large
        - Adjusts quality for smaller file size
        - Converts to optimal format if needed
        
        Args:
            image_file: Uploaded image file
            
        Returns:
            Optimized image file
        """
        try:
            # Open image
            img = Image.open(image_file)
            original_format = img.format
            original_size = image_file.size
            width, height = img.size
            
            print(f"Processing image: {width}x{height}, {original_format}, {original_size/1024:.1f}KB")
            
            # Check if needs resizing
            needs_resize = width > cls.MAX_WIDTH or height > cls.MAX_HEIGHT
            
            if needs_resize:
                img = cls._resize_image(img, cls.MAX_WIDTH, cls.MAX_HEIGHT)
                width, height = img.size
                print(f"  Resized to: {width}x{height}")
            
            # Convert RGBA to RGB if saving as JPEG
            if img.mode == 'RGBA' and original_format in ['JPEG', 'JPG']:
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                # Paste using alpha channel as mask
                if len(img.split()) == 4:
                    rgb_img.paste(img, mask=img.split()[3])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Convert palette images to RGB
            if img.mode == 'P':
                img = img.convert('RGB')
            
            # Save optimized image
            output = BytesIO()
            save_format = original_format if original_format in ['JPEG', 'PNG', 'WEBP', 'GIF'] else 'JPEG'
            
            if save_format == 'JPEG':
                img.save(output, format='JPEG', quality=cls.JPEG_QUALITY, optimize=True)
            elif save_format == 'PNG':
                img.save(output, format='PNG', optimize=cls.PNG_OPTIMIZE)
            elif save_format == 'WEBP':
                img.save(output, format='WEBP', quality=cls.WEBP_QUALITY)
            elif save_format == 'GIF':
                img.save(output, format='GIF', optimize=True)
            else:
                img.save(output, format='JPEG', quality=cls.JPEG_QUALITY)
            
            output.seek(0)
            optimized_size = output.getbuffer().nbytes
            
            # Calculate compression ratio
            if original_size > 0:
                reduction = ((original_size - optimized_size) / original_size * 100)
                print(f"  Optimized: {optimized_size/1024:.1f}KB (-{reduction:.1f}%)")
            
            # Determine content type
            content_type_map = {
                'JPEG': 'image/jpeg',
                'PNG': 'image/png',
                'WEBP': 'image/webp',
                'GIF': 'image/gif',
            }
            content_type = content_type_map.get(save_format, 'image/jpeg')
            
            # Create new file object
            optimized_file = InMemoryUploadedFile(
                output,
                'ImageField',
                image_file.name,
                content_type,
                optimized_size,
                None
            )
            
            return optimized_file
            
        except Exception as e:
            print(f"⚠️  Image optimization failed: {e}")
            # Return original if optimization fails
            image_file.seek(0)
            return image_file
    
    @classmethod
    def _resize_image(cls, img: Image.Image, max_width: int, max_height: int) -> Image.Image:
        """
        Resize image maintaining aspect ratio
        
        Args:
            img: PIL Image object
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            Resized Image object
        """
        width, height = img.size
        
        # Calculate new dimensions
        aspect_ratio = width / height
        
        if width > max_width:
            width = max_width
            height = int(width / aspect_ratio)
        
        if height > max_height:
            height = max_height
            width = int(height * aspect_ratio)
        
        # Resize with high-quality resampling
        return img.resize((width, height), Image.Resampling.LANCZOS)
    
    @classmethod
    def generate_thumbnail(cls, image_file: InMemoryUploadedFile, 
                         width: int = None, height: int = None) -> Optional[InMemoryUploadedFile]:
        """
        Generate thumbnail from image
        
        Args:
            image_file: Uploaded image file
            width: Thumbnail width (default: 300)
            height: Thumbnail height (default: 300)
            
        Returns:
            Thumbnail image file or None if failed
        """
        width = width or cls.THUMBNAIL_WIDTH
        height = height or cls.THUMBNAIL_HEIGHT
        
        try:
            img = Image.open(image_file)
            
            # Create thumbnail (maintains aspect ratio)
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            output = BytesIO()
            
            # Convert to RGB if needed
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'A' in img.mode:
                    rgb_img.paste(img, mask=img.split()[-1])
                else:
                    rgb_img.paste(img)
                img = rgb_img
            
            # Save as JPEG for thumbnails (smaller size)
            img.save(output, format='JPEG', quality=cls.JPEG_QUALITY, optimize=True)
            output.seek(0)
            
            # Generate thumbnail filename
            name_parts = image_file.name.rsplit('.', 1)
            base_name = name_parts[0] if len(name_parts) > 1 else image_file.name
            thumbnail_name = f"{base_name}_thumb.jpg"
            
            thumbnail_file = InMemoryUploadedFile(
                output,
                'ImageField',
                thumbnail_name,
                'image/jpeg',
                output.getbuffer().nbytes,
                None
            )
            
            print(f"  Generated thumbnail: {thumbnail_file.size/1024:.1f}KB")
            
            return thumbnail_file
            
        except Exception as e:
            print(f"⚠️  Thumbnail generation failed: {e}")
            return None
