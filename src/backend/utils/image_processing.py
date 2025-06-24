"""
Image Preprocessing Utilities

This module provides a centralized set of image preprocessing functions
that can be used by different models and the backend server.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Union, Dict, Any, Tuple, Optional


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
        import logging
        logging.error(f"Error enhancing image with CLAHE: {str(e)}")
        # Return original image as PIL Image if enhancement fails
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
            if len(img.shape) == 3:  # Color image
                result = np.ones((target_size[1], target_size[0], img.shape[2]), dtype=img.dtype) * padding_value
            else:  # Grayscale
                result = np.ones((target_size[1], target_size[0]), dtype=img.dtype) * padding_value
            
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
        model_type: Type of model ('phi3', 'yolo', 'llava', 'smolvlm')
        config: Optional configuration parameters
        return_format: Output format ('pil', 'cv2', 'bytes', or 'auto')
        
    Returns:
        Preprocessed image in the format required by the model
    """
    if config is None:
        config = {}
    
    # Default preprocessing: convert to appropriate format and enhance if requested
    if config.get('enhance_image', True):
        img = enhance_image_clahe(image)
    else:
        img = convert_to_pil_image(image)
    
    # Model-specific preprocessing
    model_type = model_type.lower()
    
    if 'phi3' in model_type:
        # Phi3 typically uses PIL images directly
        result = img
        output_format = 'pil' if return_format == 'auto' else return_format
        
    elif 'yolo' in model_type:
        # YOLO8 typically uses OpenCV format (BGR)
        result = convert_to_cv2_image(img)
        output_format = 'cv2' if return_format == 'auto' else return_format
        
    elif 'llava' in model_type:
        # LLaVA via Ollama typically uses image bytes
        if return_format == 'auto' or return_format == 'bytes':
            import io
            buf = io.BytesIO()
            img.save(buf, format='JPEG')
            result = buf.getvalue()
            output_format = 'bytes'
        else:
            result = img if return_format == 'pil' else convert_to_cv2_image(img)
            output_format = return_format
            
    elif 'smolvlm' in model_type:
        # SmolVLM API typically uses base64, but we'll handle that conversion separately
        result = img
        output_format = 'pil' if return_format == 'auto' else return_format
        
    else:
        # Generic case: return PIL image
        result = img
        output_format = 'pil' if return_format == 'auto' else return_format
    
    # Ensure output is in the requested format
    if output_format == 'pil' and not isinstance(result, Image.Image):
        result = convert_to_pil_image(result)
    elif output_format == 'cv2' and not isinstance(result, np.ndarray):
        result = convert_to_cv2_image(result)
    elif output_format == 'bytes' and not isinstance(result, bytes):
        import io
        buf = io.BytesIO()
        if isinstance(result, Image.Image):
            result.save(buf, format='JPEG')
        else:  # numpy array
            pil_img = convert_to_pil_image(result)
            pil_img.save(buf, format='JPEG')
        result = buf.getvalue()
    
    return result
