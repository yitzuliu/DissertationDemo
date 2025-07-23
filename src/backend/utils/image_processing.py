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
from skimage import color

logger = logging.getLogger(__name__)

def convert_to_pil_image(image: Union[np.ndarray, Image.Image, bytes]) -> Image.Image:
    """
    Convert various image formats to PIL Image for consistent handling.
    
    Args:
        image: Input image in various formats (numpy array, PIL Image, bytes)
        
    Returns:
        PIL Image object
    """
    if isinstance(image, Image.Image):
        return image
    
    if isinstance(image, bytes):
        # Convert bytes to numpy array
        try:
            nparr = np.frombuffer(image, np.uint8)
            # Decode image
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
            return Image.fromarray(cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB))
        except Exception as e:
            # If decoding fails, try direct PIL open
            import io
            return Image.open(io.BytesIO(image))
    
    if isinstance(image, np.ndarray):
        # Check if the array is in BGR format (common for OpenCV)
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Convert BGR to RGB
            return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        else:
            # Grayscale or already RGB
            return Image.fromarray(image)
    
    raise TypeError(f"Unsupported image type: {type(image)}")


def convert_to_cv2_image(image: Union[np.ndarray, Image.Image, bytes]) -> np.ndarray:
    """
    Convert various image formats to OpenCV (numpy array) format for consistent handling.
    
    Args:
        image: Input image in various formats (numpy array, PIL Image, bytes)
        
    Returns:
        numpy array in BGR format for OpenCV
    """
    if isinstance(image, np.ndarray):
        # If already numpy array, ensure it's in BGR format for OpenCV if 3 channels
        if len(image.shape) == 3 and image.shape[2] == 3:
            # Assume it might be in RGB format
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
    """
    Enhance image using CLAHE (Contrast Limited Adaptive Histogram Equalization).
    
    Args:
        image: Input image in various formats
        
    Returns:
        Enhanced image as PIL Image
    """
    # Convert to OpenCV format
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
        # Return original image as PIL Image if enhancement fails
        return convert_to_pil_image(image)


def enhance_color_balance(
    image: Union[np.ndarray, Image.Image, bytes],
    method: str = 'lab',
    config: Optional[Dict] = None
) -> Image.Image:
    """
    Enhance image color balance.
    
    Args:
        image: Input image
        method: Color processing method ('lab', 'rgb', 'auto_wb')
        config: Color enhancement parameters
        
    Returns:
        Processed image
    """
    if config is None:
        config = {}
        
    try:
        pil_image = convert_to_pil_image(image)
        
        if method == 'lab':
            # LAB color space processing
            img_array = np.array(pil_image)
            lab_image = color.rgb2lab(img_array)
            
            # Enhance L channel (lightness)
            l_boost = float(config.get("l_channel_boost", 1.2))
            l_channel = lab_image[:,:,0]
            l_channel = np.clip(l_channel * l_boost, 0, 100)
            lab_image[:,:,0] = l_channel
            
            # Enhance a,b channels (color)
            ab_boost = float(config.get("ab_channel_boost", 1.2))
            lab_image[:,:,1:] *= ab_boost
            
            # Convert back to RGB
            enhanced_array = color.lab2rgb(lab_image)
            return Image.fromarray((enhanced_array * 255).astype(np.uint8))
            
        elif method == 'rgb':
            # RGB channel independent enhancement
            r_factor = float(config.get("r_factor", 1.0))
            g_factor = float(config.get("g_factor", 1.0))
            b_factor = float(config.get("b_factor", 1.0))
            
            r, g, b = pil_image.split()
            r = ImageEnhance.Brightness(r).enhance(r_factor)
            g = ImageEnhance.Brightness(g).enhance(g_factor)
            b = ImageEnhance.Brightness(b).enhance(b_factor)
            
            return Image.merge('RGB', (r, g, b))
            
        elif method == 'auto_wb':
            # Automatic white balance
            img_array = np.array(pil_image)
            result = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
            # Calculate average values with correct data type
            avg_a = float(np.mean(result[:, :, 1].astype(np.float64)))
            avg_b = float(np.mean(result[:, :, 2].astype(np.float64)))
            result[:, :, 1] = result[:, :, 1] - ((avg_a - 128) * (result[:, :, 0] / 255.0) * 1.1)
            result[:, :, 2] = result[:, :, 2] - ((avg_b - 128) * (result[:, :, 0] / 255.0) * 1.1)
            result = cv2.cvtColor(result, cv2.COLOR_LAB2RGB)
            return Image.fromarray(result)
            
        else:
            logger.warning(f"Unknown color balance method: {method}")
            return pil_image
            
    except Exception as e:
        logger.error(f"Color balance enhancement failed: {e}")
        return convert_to_pil_image(image)


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


def smart_crop_and_resize(
    image: Union[np.ndarray, Image.Image, bytes],
    target_size: Tuple[int, int],
    min_size: int = 512,
    preserve_aspect_ratio: bool = True
) -> Image.Image:
    """
    Smart crop and resize image while maintaining important content.
    
    Args:
        image: Input image
        target_size: Target dimensions (width, height)
        min_size: Minimum size limit
        preserve_aspect_ratio: Whether to maintain aspect ratio
        
    Returns:
        Processed image
    """
    try:
        pil_image = convert_to_pil_image(image)
        
        if preserve_aspect_ratio:
            # Calculate target dimensions
            width, height = pil_image.size
            scale = min(target_size[0]/width, target_size[1]/height)
            
            # Ensure not smaller than minimum size
            new_width = max(int(width * scale), min_size)
            new_height = max(int(height * scale), min_size)
            
            # Use LANCZOS resampling method
            return pil_image.resize((new_width, new_height), resample=3)  # 3 = LANCZOS
        else:
            return pil_image.resize(target_size, resample=3)  # 3 = LANCZOS
            
    except Exception as e:
        logger.error(f"Smart crop and resize failed: {e}")
        return pil_image


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
        model_type: Type of model ('phi3', 'yolo', 'llava', 'llava_mlx', 'smolvlm')
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
        
    elif 'llava' in model_type:
        # Standard LLaVA preprocessing
        if config.get('enhance_image', True):
            img = enhance_image_clahe(image)
        else:
            img = convert_to_pil_image(image)
        
        # LLaVA via Ollama typically uses image bytes
        if return_format == 'auto' or return_format == 'bytes':
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=95)
            result = buf.getvalue()
            output_format = 'bytes'
        else:
            result = img
            output_format = return_format
            
    elif 'phi3' in model_type:
        # Phi3 typically uses PIL images directly
        result = convert_to_pil_image(image)
        output_format = 'pil' if return_format == 'auto' else return_format
        
    elif 'yolo' in model_type:
        # YOLO8 typically uses OpenCV format (BGR)
        result = convert_to_cv2_image(image)
        output_format = 'cv2' if return_format == 'auto' else return_format
        
    elif 'smolvlm' in model_type:
        # SmolVLM API typically uses PIL images
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
            Image.fromarray(result).save(buf, format='JPEG', quality=95)
        result = buf.getvalue()
    
    return result
