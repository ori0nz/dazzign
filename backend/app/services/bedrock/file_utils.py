import base64
import io
import os
from pathlib import Path
from typing import List

from PIL import Image


def base64_to_image(base64_image: str) -> Image.Image:
    """
    Converts a base64 encoded image string to a PIL Image object.
    
    Args:
        base64_image (str): The base64 encoded image string.
        
    Returns:
        PIL.Image.Image: The Pillow Image object.
    """
    image_bytes = base64.b64decode(base64_image)
    return Image.open(io.BytesIO(image_bytes))


def image_to_base64(image: Image.Image, format: str = "JPEG") -> str:
    """
    Converts a PIL Image object to a base64 encoded string.
    
    Args:
        image (PIL.Image.Image): The Pillow Image object.
        format (str): The image format (JPEG, PNG, etc.).
        
    Returns:
        str: Base64 encoded image string.
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def save_base64_image(base64_image: str, output_directory: str, base_name: str = "image", suffix: str = "_1") -> Image.Image:
    """
    Saves a base64 encoded image to a specified output directory.
    
    Args:
        base64_image (str): The base64 encoded image string.
        output_directory (str): The directory where the image will be saved.
        base_name (str): Base name for the image file.
        suffix (str): A suffix to add to the filename.
        
    Returns:
        PIL.Image.Image: The Pillow Image object.
    """
    image = base64_to_image(base64_image)
    
    # Create directory if it doesn't exist
    output_path = Path(output_directory)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save the image
    file_name = f"{base_name}{suffix}.png"
    file_path = output_path / file_name
    image.save(file_path)
    
    return image


def save_base64_images(base64_images: List[str], output_directory: str, base_name: str = "image") -> List[Image.Image]:
    """
    Saves a list of base64 encoded images to a specified output directory.
    
    Args:
        base64_images (List[str]): A list of base64 encoded image strings.
        output_directory (str): The directory where the images will be saved.
        base_name (str): Base name for the image files.
        
    Returns:
        List[PIL.Image.Image]: List of Pillow Image objects.
    """
    images = []
    for i, base64_image in enumerate(base64_images):
        image = save_base64_image(
            base64_image, 
            output_directory, 
            base_name=base_name, 
            suffix=f"_{i+1}"
        )
        images.append(image)
    
    return images
