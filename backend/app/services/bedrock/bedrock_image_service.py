from typing import Dict, Any, Optional, List, Literal
import json
import logging
import base64
from pathlib import Path
import boto3
import os
from dotenv import load_dotenv
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from boto3.session import Session
from app.services.bedrock.file_utils import save_base64_image, save_base64_images
from datetime import datetime

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
# Increasing timeout for image generation
config = Config(read_timeout=300)


class BedrockImageGenerator:
    """A class to handle image generation using AWS Bedrock service.

    This class provides functionality to generate images using AWS Bedrock's image generation
    models. It handles the AWS client initialization, API calls, and response processing.

    Attributes:
        DEFAULT_MODEL_ID (str): The default AWS Bedrock model ID for image generation.
        DEFAULT_REGION (str): The default AWS region for the Bedrock service.
        region_name (str): The AWS region being used.
        save_output (bool): Whether to save request/response files locally.
        output_directory (Path): Directory path where generated files will be saved.
        bedrock_client (boto3.client): The initialized AWS Bedrock client.
    """

    DEFAULT_MODEL_ID: str = "amazon.nova-canvas-v1:0"
    DEFAULT_REGION: str = os.environ.get("AWS_REGION", "us-east-1")
    # AWS credentials from environment variables
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

    def __init__(
        self,
        region_name: str = None,
        save_output: bool = False,
        output_directory: str = None,
        profile_name: Optional[str] = None,
    ) -> None:
        """Initialize the BedrockImageGenerator.

        Args:
            region_name (str): AWS region name. Defaults to value from env or DEFAULT_REGION.
            save_output (bool): Whether to save request/response files locally.
            output_directory (str): Directory for saving output files if save_output is True.
            profile_name (str, optional): AWS profile name to use for credentials.

        Raises:
            Exception: If the Bedrock client initialization fails.
        """
        # Use provided region or fall back to env variable or default
        self.region_name = region_name or self.DEFAULT_REGION
        self.save_output = save_output
        
        # Set up output directory with timestamp if save_output is True
        if save_output:
            if output_directory is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_directory = f"./output/bedrock_images_{timestamp}"
            
            self.output_directory = Path(output_directory)
            # Create the directory if it doesn't exist
            self.output_directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Image output will be saved to: {self.output_directory}")
        else:
            self.output_directory = None
            
        self.bedrock_client = self._initialize_bedrock_client(profile_name)

    def _initialize_bedrock_client(self, profile_name: Optional[str] = None) -> boto3.client:
        """Initialize and return the AWS Bedrock client.

        Args:
            profile_name (str, optional): AWS profile name to use for credentials.

        Returns:
            boto3.client: Initialized Bedrock client.

        Raises:
            Exception: If client initialization fails due to AWS service errors.
        """
        try:
            session_kwargs = {}
            
            # Add AWS credentials if available in environment
            if self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY:
                session_kwargs['aws_access_key_id'] = self.AWS_ACCESS_KEY_ID
                session_kwargs['aws_secret_access_key'] = self.AWS_SECRET_ACCESS_KEY
            
            # Use named profile if provided
            if profile_name:
                session_kwargs['profile_name'] = profile_name
                
            session = boto3.Session(**session_kwargs)
            return session.client(
                service_name="bedrock-runtime",
                region_name=self.region_name,
                config=config
            )
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to initialize Bedrock client: {str(e)}")
            raise Exception(f"Failed to initialize AWS Bedrock client: {str(e)}")

    @staticmethod
    def check_aws_credentials() -> bool:
        """Check if AWS credentials are properly configured."""
        return (
            bool(os.environ.get("AWS_ACCESS_KEY_ID")) and
            bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
        )

    def _save_json_to_file(self, data: Dict[str, Any], filename: str) -> None:
        """Save JSON data to a file in the output directory if save_output is True."""
        if not self.save_output:
            return
            
        try:
            self.output_directory.mkdir(parents=True, exist_ok=True)
            filepath = self.output_directory / filename
            with filepath.open("w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save {filename}: {str(e)}")

    def _get_inference_params_for_model(
        self,
        model_id: str,
        prompt: str,
        negative_prompt: Optional[str] = "",
        width: int = 1024,
        height: int = 1024,
        number_of_images: int = 1,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get appropriate inference parameters based on model ID.
        
        Args:
            model_id: The model ID to use
            prompt: Text prompt for image generation
            negative_prompt: Things to avoid in the image
            width: Image width
            height: Image height
            number_of_images: Number of images to generate
            seed: Seed for reproducibility
            
        Returns:
            Dict with inference parameters specific to the model
        """
        # Default parameters that work for most models
        default_params = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt,
            },
            "imageGenerationConfig": {
                "numberOfImages": min(number_of_images, 5),  # Max 5 images
                "quality": "standard",
                "width": width,
                "height": height,
                "cfgScale": 7.0,
            }
        }
        
        # Add negative prompt if provided
        if negative_prompt:
            default_params["textToImageParams"]["negativeText"] = negative_prompt
            
        # Add seed if provided
        if seed is not None:
            default_params["imageGenerationConfig"]["seed"] = seed
        
        # Model-specific parameter adjustments
        if "amazon.titan-image" in model_id:
            # Titan models use different parameter structure
            titan_params = {
                "taskType": "TEXT_TO_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    "negativeText": negative_prompt if negative_prompt else "",
                },
                "imageGenerationConfig": {
                    "numberOfImages": min(number_of_images, 5),
                    "height": height,
                    "width": width,
                    "cfgScale": 8.0
                }
            }
            
            if seed is not None:
                titan_params["imageGenerationConfig"]["seed"] = seed
                
            return titan_params
            
        elif "stability.stable-image-ultra-v1:1" in model_id:
            # Stability AI models use slightly different parameters
            stability_params = {
                "prompt": prompt,
                "seed": seed if seed is not None else 0,
                #"steps": 30,
                #"width": width,
                #"height": height
                "aspect_ratio": "1:1",
                "mode": "text-to-image",
                "output_format": "jpeg"
            }
            
            if negative_prompt:
                stability_params["negative_prompt"] = negative_prompt
                
            return stability_params
            
        elif "anthropic.claude-3" in model_id:
            # Claude 3 Vision may have different parameters
            claude_params = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Generate an image based on this description: {prompt}"
                            }
                        ]
                    }
                ]
            }
            return claude_params
            
        # For Nova-canvas models (default model)
        elif "amazon.nova-canvas" in model_id:
            # Default parameters already fit Nova Canvas
            return default_params
            
        # For any other model, return default params
        return default_params

    def generate_image(
        self,
        prompt: str,
        negative_prompt: Optional[str] = "",
        seed: Optional[int] = 222,
        output_format: Optional[Literal["webp", "jpeg", "png"]] = "jpeg",
        model_id: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        number_of_images: int = 1
    ) -> Dict[str, Any]:
        """Generate images using AWS Bedrock's image generation models.

        Args:
            prompt (str): The text prompt for image generation
            negative_prompt (str, optional): Things to avoid in the image
            seed (int, optional): Seed for reproducibility
            output_format (str, optional): Image format
            model_id (str, optional): Override the model ID
            width (int, optional): Image width
            height (int, optional): Image height
            number_of_images (int, optional): Number of images to generate (1-5)

        Returns:
            Dict[str, Any]: Dictionary with base64 image and metadata
        """
        try:
            # Use provided model or default
            if model_id is None:
                model_id = self.DEFAULT_MODEL_ID
                
            # Get appropriate inference parameters for the model
            inference_params = self._get_inference_params_for_model(
                model_id=model_id,
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                number_of_images=number_of_images,
                seed=seed
            )
            
            # Log generation details
            logger.info(f"Generating {number_of_images} image(s) with model {model_id}")
            if seed is not None:
                logger.info(f"Using seed: {seed}")

            # Make the API call
            body_json = json.dumps(inference_params)
            
            logger.info(f"Using model: {model_id}")
            logger.info(f"Request parameters: {json.dumps(inference_params, indent=2)}")
            
            response = self.bedrock_client.invoke_model(
                body=body_json,
                modelId=model_id,
                accept="application/json",
                contentType="application/json",
            )

            # Process response
            response_body = json.loads(response.get("body").read())
            
            # Logger response headers and metadata for debugging
            logger.debug(f"Response metadata: {response.get('ResponseMetadata', {})}")

            # Check for errors
            if "error" in response_body and response_body["error"]:
                logger.error(f"Error in response: {response_body['error']}")
                return {"error": response_body["error"]}

            # Extract images based on model type
            images = []
            
            # Handle different model response formats
            if "stability.stable-diffusion" in model_id:
                # Stability AI format
                if "artifacts" in response_body:
                    images = [artifact.get("base64") for artifact in response_body.get("artifacts", [])]
            elif "amazon.titan-image" in model_id:
                # Titan Image format
                if "images" in response_body:
                    images = response_body["images"]
            elif "anthropic.claude" in model_id:
                # Claude format - we would need to extract image from text response
                # This is a placeholder since Claude doesn't directly generate images
                logger.warning("Claude models don't directly generate images")
                return {"error": "Claude models don't directly generate images"}
            else:
                # Nova Canvas and default format
                if "images" in response_body:
                    images = response_body["images"]
            
            # Check if we extracted any images
            if not images:
                logger.error(f"No images found in response for model {model_id}")
                logger.error(f"Response keys: {list(response_body.keys())}")
                return {"error": f"No images found in response for model {model_id}"}
                
            # Return the result
            if images:
                # Save the images if save_output is enabled
                if self.save_output and self.output_directory:
                    try:
                        # Create a safe filename by removing special characters
                        safe_model_id = model_id.replace(':', '_').replace('.', '_')
                        self.save_images(
                            images,
                            custom_output_dir=None,  # Use the instance's output directory
                            base_name=f"bedrock_image_{safe_model_id}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to save images: {str(e)}")
                
                # For compatibility with image_gen_service, return the first image 
                # in the format expected by that service
                return {
                    "image": images[0],
                    "all_images": images,
                    "model_id": model_id,
                    "prompt": prompt
                }

        except (BotoCoreError, ClientError) as e:
            logger.error(f"AWS service error: {str(e)}")
            return {"error": f"AWS service error: {str(e)}"}

        except Exception as e:
            logger.error(f"Unexpected error during image generation: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def save_images(self, images: List[str], custom_output_dir: Optional[str] = None, base_name: str = "bedrock_image") -> str:
        """Save a list of base64 encoded images to disk.
        
        Args:
            images (List[str]): List of base64 encoded image strings
            custom_output_dir (str, optional): Custom output directory. Uses the instance's output_directory if None.
            base_name (str): Base name for the saved image files
            
        Returns:
            str: Path to the directory where images were saved
        """
        # Determine output directory
        output_dir = Path(custom_output_dir) if custom_output_dir else self.output_directory
        
        # If no output directory is set, create one with timestamp
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"./output/bedrock_images_{timestamp}")
        
        # Ensure directory exists
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            if len(images) > 1:
                save_base64_images(
                    images,
                    str(output_dir),
                    base_name=base_name
                )
            else:
                save_base64_image(
                    images[0],
                    str(output_dir),
                    base_name=base_name,
                    suffix=""
                )
            logger.info(f"Saved {len(images)} image(s) to {output_dir}")
            return str(output_dir)
        except Exception as e:
            logger.error(f"Failed to save images: {str(e)}")
            return ""

    def list_available_models(self) -> List[Dict[str, str]]:
        """
        List all available AWS Bedrock models for image generation.
        
        Returns:
            List of dictionaries with model information
        """
        try:
            # Create a bedrock client (not runtime) to list models
            bedrock_client = boto3.client('bedrock', region_name=self.region_name)
            
            # Get all foundation models
            response = bedrock_client.list_foundation_models()
            
            # Filter for image generation models
            image_models = []
            
            for model in response.get('modelSummaries', []):
                model_id = model.get('modelId', '')
                
                # Check if it's an image generation model based on model ID or capabilities
                is_image_model = False
                
                # Check model ID for known image generation models
                if any(name in model_id.lower() for name in ['image', 'stable-diffusion', 'nova-canvas', 'titan-image']):
                    is_image_model = True
                
                # Check model capabilities if available
                if 'modelCapabilities' in model:
                    capabilities = model.get('modelCapabilities', [])
                    if 'IMAGE_GENERATION' in capabilities or 'TEXT_IMAGE_GENERATION' in capabilities:
                        is_image_model = True
                
                if is_image_model:
                    image_models.append({
                        'model_id': model_id,
                        'model_name': model.get('modelName', ''),
                        'provider': model.get('providerName', ''),
                        'input_modalities': model.get('inputModalities', []),
                        'output_modalities': model.get('outputModalities', [])
                    })
            
            # If no image models found, return some well-known ones
            if not image_models:
                return [
                    {
                        'model_id': 'amazon.nova-canvas-v1:0',
                        'model_name': 'Amazon Nova Canvas',
                        'provider': 'Amazon',
                        'input_modalities': ['TEXT'],
                        'output_modalities': ['IMAGE']
                    },
                    {
                        'model_id': 'amazon.titan-image-generator-v1:0',
                        'model_name': 'Titan Image Generator',
                        'provider': 'Amazon',
                        'input_modalities': ['TEXT'],
                        'output_modalities': ['IMAGE']
                    },
                    {
                        'model_id': 'stability.stable-diffusion-xl-v1:0',
                        'model_name': 'Stable Diffusion XL',
                        'provider': 'Stability AI',
                        'input_modalities': ['TEXT'],
                        'output_modalities': ['IMAGE']
                    }
                ]
                
            return image_models
            
        except Exception as e:
            logger.error(f"Error listing Bedrock models: {str(e)}")
            # Return some well-known models as fallback
            return [
                {
                    'model_id': 'amazon.nova-canvas-v1:0',
                    'model_name': 'Amazon Nova Canvas',
                    'provider': 'Amazon',
                    'input_modalities': ['TEXT'],
                    'output_modalities': ['IMAGE']
                },
                {
                    'model_id': 'amazon.titan-image-generator-v1:0',
                    'model_name': 'Titan Image Generator',
                    'provider': 'Amazon',
                    'input_modalities': ['TEXT'],
                    'output_modalities': ['IMAGE']
                },
                {
                    'model_id': 'stability.stable-diffusion-xl-v1:0',
                    'model_name': 'Stable Diffusion XL',
                    'provider': 'Stability AI',
                    'input_modalities': ['TEXT'],
                    'output_modalities': ['IMAGE']
                }
            ]

    async def generate_with_multiple_models(
        self, 
        prompt: str,
        negative_prompt: Optional[str] = "",
        model_ids: Optional[List[str]] = None,
        save_images: bool = True,
        seed: Optional[int] = None,
        width: int = 1024,
        height: int = 1024
    ) -> Dict[str, Any]:
        """
        Generate images using multiple models in parallel for comparison.
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Things to avoid in the image
            model_ids: List of model IDs to use (if None, uses default models)
            save_images: Whether to save the generated images
            seed: Seed for reproducibility
            width: Image width
            height: Image height
            
        Returns:
            Dictionary with results from each model
        """
        import asyncio
        import concurrent.futures
        
        # Use default models if none provided
        if not model_ids:
            model_ids = [
                'amazon.nova-canvas-v1:0',
                'amazon.titan-image-generator-v1:0',
                'stability.stable-diffusion-xl-v1:0'
            ]
        
        # Create a timestamp-based output directory
        if save_images:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = Path(f"./output/bedrock_comparison_{timestamp}")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save prompt to a text file
            prompt_file = output_dir / "prompt.txt"
            with open(prompt_file, "w") as f:
                f.write(f"Prompt: {prompt}\n")
                if negative_prompt:
                    f.write(f"Negative prompt: {negative_prompt}\n")
                if seed is not None:
                    f.write(f"Seed: {seed}\n")
        else:
            output_dir = None
        
        # Create a function to generate with one model
        def generate_with_model(model_id):
            try:
                old_save_output = self.save_output
                old_output_dir = self.output_directory
                
                # Temporarily disable saving since we'll handle it here
                self.save_output = False
                
                result = self.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    seed=seed,
                    model_id=model_id,
                    width=width,
                    height=height,
                    number_of_images=1
                )
                
                # Restore original settings
                self.save_output = old_save_output
                self.output_directory = old_output_dir
                
                # Add model ID to result
                if "error" not in result:
                    result["model_id"] = model_id
                
                # Save the image if requested
                if save_images and output_dir and "image" in result:
                    try:
                        from app.services.bedrock.file_utils import save_base64_image
                        # Create a safe filename
                        safe_model_id = model_id.replace(':', '_').replace('.', '_')
                        save_base64_image(
                            result["image"],
                            str(output_dir),
                            base_name=safe_model_id,
                            suffix=""
                        )
                    except Exception as e:
                        logger.error(f"Failed to save comparison image for {model_id}: {str(e)}")
                
                return result
            except Exception as e:
                logger.error(f"Error generating with model {model_id}: {str(e)}")
                return {"error": str(e), "model_id": model_id}
        
        # Use ThreadPoolExecutor to run generation in parallel
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit tasks and gather results
            tasks = [
                loop.run_in_executor(executor, generate_with_model, model_id)
                for model_id in model_ids
            ]
            results = await asyncio.gather(*tasks)
        
        # Organize results by model ID
        results_by_model = {result.get("model_id"): result for result in results}
        
        # Return a comprehensive result
        return {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "seed": seed,
            "models": model_ids,
            "results": results_by_model,
            "output_directory": str(output_dir) if output_dir else None
        }
