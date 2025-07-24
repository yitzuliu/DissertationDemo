"""
Image Preprocessing Utilities

This module provides a centralized set of image preprocessing functions
that can be used by different models and the backend server.
"""

import io
import cv2
import numpy as np
import logging
from PIL import Image, ImageEnhance, ImageFilter, ImageChops, ImageOps
from typing import Union, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

def convert_to_pil_image(image: Union[np.ndarray, Image.Image, bytes]) -> Image.Image:
    """Convert various image formats to PIL Image for consistent handling."""
    if isinstance(image, Image.Image):
        return image
    
    if isinstance(image, bytes):
        try:
            return Image.open(io.BytesIO(image))
        except Exception as e:
            logger.error(f"Error converting bytes to PIL image: {e}")
            raise TypeError(f"Invalid image bytes: {e}")
    
    if isinstance(image, np.ndarray):
        # Check if the array is in BGR format (common for OpenCV)
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(image)
    
    raise TypeError(f"Unsupported image type: {type(image)}")

def convert_to_cv2_image(image: Union[np.ndarray, Image.Image, bytes]) -> np.ndarray:
    """Convert various image formats to OpenCV (numpy array) format for consistent handling."""
    if isinstance(image, np.ndarray):
        # If already numpy array, ensure it's in BGR format for OpenCV if 3 channels
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume input is RGB, convert to BGR
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image
    
    if isinstance(image, bytes):
        # Convert bytes to numpy array
        nparr = np.frombuffer(image, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Returns BGR format
    
    if isinstance(image, Image.Image):
        # Convert PIL to numpy array (RGB)
        img_np = np.array(image)
        # Convert RGB to BGR for OpenCV
        if len(img_np.shape) == 3 and img_np.shape[2] == 3:
            return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        return img_np
    
    raise TypeError(f"Unsupported image type: {type(image)}")

def enhance_image_clahe(image: Union[np.ndarray, Image.Image, bytes]) -> Image.Image:
    """Enhance image using CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    cv_image = convert_to_cv2_image(image)
    
    try:
        # Convert to LAB color space
        lab = cv2.cvtColor(cv_image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # Apply CLAHE to L-channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        
        # Merge back and convert to BGR
        merged = cv2.merge([cl, a, b])
        enhanced_frame = cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)
        
        # Convert to PIL Image
        return Image.fromarray(cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2RGB))
    except Exception as e:
        logger.error(f"Error enhancing image with CLAHE: {str(e)}")
        return convert_to_pil_image(image)

def enhance_color_balance(
    image: Union[np.ndarray, Image.Image, bytes],
    method: str = 'lab',
    config: Optional[Dict] = None
) -> Image.Image:
    """Enhance image color balance."""
    if config is None:
        config = {}
        
    try:
        pil_image = convert_to_pil_image(image)
        
        if method == 'lab':
            # LAB color space enhancement
            enhancer = ImageEnhance.Color(pil_image)
            pil_image = enhancer.enhance(config.get('color_factor', 1.1))
            
        elif method == 'rgb':
            # RGB channel enhancement
            enhancer = ImageEnhance.Brightness(pil_image)
            pil_image = enhancer.enhance(config.get('brightness_factor', 1.0))
            
        elif method == 'auto_wb':
            # Auto white balance
            cv_image = convert_to_cv2_image(pil_image)
            result = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            result = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
            pil_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
            
        return pil_image
        
    except Exception as e:
        logger.error(f"Color balance enhancement failed: {e}")
        return convert_to_pil_image(image)

def smart_crop_and_resize(
    image: Union[np.ndarray, Image.Image, bytes],
    target_size: Tuple[int, int],
    min_size: int = 512,
    preserve_aspect_ratio: bool = True
) -> Image.Image:
    """Smart crop and resize image while maintaining important content."""
    try:
        pil_image = convert_to_pil_image(image)
        
        if preserve_aspect_ratio:
            # Calculate aspect ratio preserving resize
            ratio = min(target_size[0] / pil_image.width, target_size[1] / pil_image.height)
            new_size = (int(pil_image.width * ratio), int(pil_image.height * ratio))
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        else:
            # Direct resize
            pil_image = pil_image.resize(target_size, Image.Resampling.LANCZOS)
            
        return pil_image
        
    except Exception as e:
        logger.error(f"Smart crop and resize failed: {e}")
        return convert_to_pil_image(image)

def reduce_noise(
    image: Union[np.ndarray, Image.Image, bytes],
    method: str = 'bilateral',
    config: Optional[Dict] = None
) -> Image.Image:
    """
    Advanced noise reduction processing with multiple methods.
    
    Args:
        image: Input image
        method: Noise reduction method ('bilateral', 'nlm', 'gaussian')
        config: Noise reduction parameters
        
    Returns:
        Processed image
    """
    if config is None:
        config = {}
        
    try:
        # Convert to OpenCV format
        cv_image = convert_to_cv2_image(image)
        
        if method == 'bilateral':
            # Bilateral filtering, preserving edges while reducing noise
            d = config.get("diameter", 9)
            sigma_color = config.get("sigma_color", 75)
            sigma_space = config.get("sigma_space", 75)
            processed = cv2.bilateralFilter(cv_image, d, sigma_color, sigma_space)
            
        elif method == 'nlm':
            # Non-local means denoising
            h = config.get("h", 10)
            template_window = config.get("template_window", 7)
            search_window = config.get("search_window", 21)
            processed = cv2.fastNlMeansDenoisingColored(
                cv_image,
                None,
                h=h,
                hColor=h,
                templateWindowSize=template_window,
                searchWindowSize=search_window
            )
            
        elif method == 'gaussian':
            # Gaussian noise reduction
            kernel_size = config.get("kernel_size", (5, 5))
            sigma = config.get("sigma", 0)
            processed = cv2.GaussianBlur(cv_image, kernel_size, sigma)
            
        else:
            logger.warning(f"Unknown noise reduction method: {method}")
            return convert_to_pil_image(image)
            
        return convert_to_pil_image(processed)
        
    except Exception as e:
        logger.error(f"Noise reduction failed: {e}")
        return convert_to_pil_image(image)

def preprocess_for_llava_mlx(
    image: Union[np.ndarray, Image.Image, bytes],
    max_size: int = 1024,
    min_size: int = 224,
    quality: int = 95
) -> Image.Image:
    """
    Special preprocessing for LLaVA MLX to avoid axis remapping errors
    
    Args:
        image: Input image
        max_size: Maximum dimension size
        min_size: Minimum dimension size
        quality: JPEG quality for saving
        
    Returns:
        Preprocessed PIL image optimized for LLaVA MLX
    """
    try:
        # Convert to PIL image
        pil_image = convert_to_pil_image(image)
        
        # Ensure RGB format
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Get original size
        original_size = pil_image.size
        
        # Check and adjust size constraints
        width, height = pil_image.size
        
        # Ensure minimum size
        if width < min_size or height < min_size:
            logger.warning(f"Image too small: {pil_image.size}, resizing to minimum")
            if width < height:
                new_width = min_size
                new_height = int(height * (min_size / width))
            else:
                new_height = min_size
                new_width = int(width * (min_size / height))
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Ensure maximum size
        if max(pil_image.size) > max_size:
            ratio = max_size / max(pil_image.size)
            new_size = (int(pil_image.size[0] * ratio), int(pil_image.size[1] * ratio))
            pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Ensure dimensions are even numbers (some models prefer this)
        width, height = pil_image.size
        if width % 2 != 0:
            width -= 1
        if height % 2 != 0:
            height -= 1
        
        if (width, height) != pil_image.size:
            pil_image = pil_image.resize((width, height), Image.Resampling.LANCZOS)
        
        logger.info(f"LLaVA MLX preprocessing: {original_size} → {pil_image.size}")
        
        return pil_image
        
    except Exception as e:
        logger.error(f"LLaVA MLX preprocessing failed: {e}")
        # Return a safe fallback image
        fallback_image = Image.new('RGB', (224, 224), color='white')
        return fallback_image

def preprocess_for_model(
    image: Union[np.ndarray, Image.Image, bytes],
    model_type: str,
    config: Optional[Dict[str, Any]] = None,
    return_format: str = 'auto'
) -> Union[np.ndarray, Image.Image, bytes]:
    """
    Preprocess an image according to specific model requirements.
    
    Args:
        image: Input image in various formats
        model_type: Type of model ('phi3_vision', 'moondream2', 'llava_mlx', 'smolvlm', 'yolo8', etc.)
        config: Optional configuration parameters
        return_format: Output format ('pil', 'cv2', 'bytes', or 'auto')
        
    Returns:
        Preprocessed image in the format required by the model
    """
    if config is None:
        config = {}
    
    # Model-specific preprocessing
    model_type = model_type.lower()
    
    if 'llava_mlx' in model_type:
        # Special preprocessing for LLaVA MLX
        result = preprocess_for_llava_mlx(
            image,
            max_size=config.get('max_size', 1024),
            min_size=config.get('min_size', 224),
            quality=config.get('quality', 95)
        )
        output_format = 'pil' if return_format == 'auto' else return_format
        
    elif 'moondream2' in model_type:
        # Moondream2 preprocessing
        target_size = config.get('size', (384, 384))
        if isinstance(target_size, list) and len(target_size) >= 2:
            target_size = (target_size[0], target_size[1])
        elif isinstance(target_size, int):
            target_size = (target_size, target_size)
        
        result = preprocess_for_moondream2(
            image,
            target_size=target_size,
            quality=config.get('jpeg_quality', config.get('quality', 85))
        )
        output_format = 'pil' if return_format == 'auto' else return_format
        
    elif 'phi3' in model_type:
        # Phi-3 Vision preprocessing
        target_size = config.get('size', (384, 384))
        if isinstance(target_size, list) and len(target_size) >= 2:
            target_size = (target_size[0], target_size[1])
        elif isinstance(target_size, int):
            target_size = (target_size, target_size)
        
        result = preprocess_for_phi3_vision(
            image,
            target_size=target_size,
            quality=config.get('quality', 95)
        )
        output_format = 'pil' if return_format == 'auto' else return_format
        
    elif 'smolvlm' in model_type:
        # SmolVLM preprocessing with advanced features
        target_size = config.get('size', (1024, 1024))
        if isinstance(target_size, list) and len(target_size) >= 2:
            target_size = (target_size[0], target_size[1])
        elif isinstance(target_size, int):
            target_size = (target_size, target_size)
        
        result = preprocess_for_smolvlm(
            image,
            target_size=target_size,
            quality=config.get('jpeg_quality', config.get('quality', 95)),
            enable_advanced_processing=config.get('advanced_color', {}).get('enabled', True)
        )
        output_format = 'pil' if return_format == 'auto' else return_format
        
    elif 'yolo' in model_type:
        # YOLO8 typically uses OpenCV format (BGR)
        result = convert_to_cv2_image(image)
        output_format = 'cv2' if return_format == 'auto' else return_format
        
    elif 'qwen2_vl' in model_type:
        # Qwen2-VL preprocessing (similar to generic VLM)
        result = convert_to_pil_image(image)
        output_format = 'pil' if return_format == 'auto' else return_format
        
    else:
        # Generic case: return PIL image
        result = convert_to_pil_image(image)
        output_format = 'pil' if return_format == 'auto' else return_format
    
    # Ensure output is in the requested format
    if output_format == 'pil' and not isinstance(result, Image.Image):
        result = convert_to_pil_image(result)
    elif output_format == 'cv2' and not isinstance(result, np.ndarray):
        result = convert_to_cv2_image(result)
    elif output_format == 'bytes' and not isinstance(result, bytes):
        buf = io.BytesIO()
        if isinstance(result, Image.Image):
            result.save(buf, format='JPEG', quality=95)
        else:
            pil_img = convert_to_pil_image(result)
            pil_img.save(buf, format='JPEG', quality=95)
        result = buf.getvalue()
    
    return result

def resize_image(
    image: Union[np.ndarray, Image.Image, bytes],
    target_size: Union[Tuple[int, int], int],
    keep_aspect_ratio: bool = True,
    padding_value: Union[int, Tuple[int, int, int]] = 0,
    return_format: str = 'pil'
) -> Union[np.ndarray, Image.Image]:
    """
    Resize an image to a target size, with optional aspect ratio preservation.
    
    Args:
        image: Input image in various formats
        target_size: Target size as (width, height) or single integer for square
        keep_aspect_ratio: Whether to preserve aspect ratio
        padding_value: Value to use for padding (if aspect ratio preserved)
        return_format: Output format, 'pil' or 'cv2'
        
    Returns:
        Resized image in specified format
    """
    # Convert to appropriate format based on return type
    if return_format.lower() == 'pil':
        img = convert_to_pil_image(image)
    else:  # cv2/numpy format
        img = convert_to_cv2_image(image)
    
    # Handle single integer for square target
    if isinstance(target_size, int):
        target_size = (target_size, target_size)
    
    # Get current dimensions
    if isinstance(img, Image.Image):
        width, height = img.size
    else:  # numpy array
        height, width = img.shape[:2]
    
    if keep_aspect_ratio:
        # Calculate target dimensions preserving aspect ratio
        scale = min(target_size[0] / width, target_size[1] / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Resize the image
        if isinstance(img, Image.Image):
            resized = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Create a new image with padding
            result = Image.new(img.mode, target_size, padding_value)
            # Paste the resized image in the center
            paste_x = (target_size[0] - new_width) // 2
            paste_y = (target_size[1] - new_height) // 2
            result.paste(resized, (paste_x, paste_y))
            
            return result
        else:  # numpy array
            resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
            
            # Create a new image with padding
            if len(img.shape) == 3:
                result = np.full((target_size[1], target_size[0], img.shape[2]), padding_value, dtype=img.dtype)
            else:
                result = np.full((target_size[1], target_size[0]), padding_value, dtype=img.dtype)
            
            # Paste the resized image in the center
            paste_x = (target_size[0] - new_width) // 2
            paste_y = (target_size[1] - new_height) // 2
            result[paste_y:paste_y+new_height, paste_x:paste_x+new_width] = resized
            
            return result
    else:
        # Simple resize without preserving aspect ratio
        if isinstance(img, Image.Image):
            return img.resize(target_size, Image.LANCZOS)
        else:  # numpy array
            return cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)

def preprocess_for_moondream2(
    image: Union[np.ndarray, Image.Image, bytes],
    target_size: Tuple[int, int] = (384, 384),
    quality: int = 85
) -> Image.Image:
    """
    Special preprocessing for Moondream2 model
    
    Args:
        image: Input image
        target_size: Target size for the image
        quality: JPEG quality for saving
        
    Returns:
        Preprocessed PIL image optimized for Moondream2
    """
    try:
        # Convert to PIL image
        pil_image = convert_to_pil_image(image)
        
        # Ensure RGB format
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Smart crop and resize
        pil_image = smart_crop_and_resize(
            pil_image,
            target_size=target_size,
            preserve_aspect_ratio=True
        )
        
        logger.info(f"Moondream2 preprocessing: → {pil_image.size}")
        return pil_image
        
    except Exception as e:
        logger.error(f"Moondream2 preprocessing failed: {e}")
        # Return a safe fallback image
        fallback_image = Image.new('RGB', target_size, color='white')
        return fallback_image

def preprocess_for_phi3_vision(
    image: Union[np.ndarray, Image.Image, bytes],
    target_size: Tuple[int, int] = (384, 384),
    quality: int = 95
) -> Image.Image:
    """
    Special preprocessing for Phi-3 Vision model
    
    Args:
        image: Input image
        target_size: Target size for the image
        quality: JPEG quality for saving
        
    Returns:
        Preprocessed PIL image optimized for Phi-3 Vision
    """
    try:
        # Convert to PIL image
        pil_image = convert_to_pil_image(image)
        
        # Ensure RGB format
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Smart crop and resize with aspect ratio preservation
        pil_image = smart_crop_and_resize(
            pil_image,
            target_size=target_size,
            preserve_aspect_ratio=True
        )
        
        logger.info(f"Phi-3 Vision preprocessing: → {pil_image.size}")
        return pil_image
        
    except Exception as e:
        logger.error(f"Phi-3 Vision preprocessing failed: {e}")
        # Return a safe fallback image
        fallback_image = Image.new('RGB', target_size, color='white')
        return fallback_image

def preprocess_for_smolvlm(
    image: Union[np.ndarray, Image.Image, bytes],
    target_size: Tuple[int, int] = (1024, 1024),
    quality: int = 95,
    enable_advanced_processing: bool = True
) -> Image.Image:
    """
    Special preprocessing for SmolVLM model with advanced enhancements
    
    Args:
        image: Input image
        target_size: Target size for the image
        quality: JPEG quality for saving
        enable_advanced_processing: Enable advanced color and HDR processing
        
    Returns:
        Preprocessed PIL image optimized for SmolVLM
    """
    try:
        # Convert to PIL image
        pil_image = convert_to_pil_image(image)
        
        # Ensure RGB format
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        if enable_advanced_processing:
            # Apply advanced color enhancement for SmolVLM
            pil_image = enhance_color_balance(
                pil_image,
                method='lab',
                config={'color_factor': 1.2}
            )
        
        # Smart crop and resize
        pil_image = smart_crop_and_resize(
            pil_image,
            target_size=target_size,
            preserve_aspect_ratio=True
        )
        
        logger.info(f"SmolVLM preprocessing: → {pil_image.size}")
        return pil_image
        
    except Exception as e:
        logger.error(f"SmolVLM preprocessing failed: {e}")
        # Return a safe fallback image
        fallback_image = Image.new('RGB', target_size, color='white')
        return fallback_image
