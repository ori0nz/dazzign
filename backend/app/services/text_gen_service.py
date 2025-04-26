from typing import Dict, Any, Optional, List
import json
import logging
import os
import httpx
import boto3
import base64
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from app.schemas.text_gen.domain import PCCaseAttributes, ToSpec

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class NovaConverseClient:
    """Client for interacting with Amazon Bedrock's Nova models via the Converse API."""
    
    # AWS credentials from environment variables
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    
    def __init__(self, region_name: str = None, profile_name: Optional[str] = None):
        """Initialize the Nova Converse client."""
        session_kwargs = {}
        
        # Use provided region or fall back to env variable or default
        if region_name is None:
            region_name = self.AWS_REGION
            
        # Add AWS credentials if available in environment
        if self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY:
            session_kwargs['aws_access_key_id'] = self.AWS_ACCESS_KEY_ID
            session_kwargs['aws_secret_access_key'] = self.AWS_SECRET_ACCESS_KEY
        
        # Use named profile if provided
        if profile_name:
            session_kwargs['profile_name'] = profile_name
            
        session = boto3.Session(**session_kwargs)
        self.client = session.client("bedrock-runtime", region_name=region_name)
        
        # Available Nova model IDs
        self.PRO_MODEL_ID = "us.amazon.nova-pro-v1:0"
        self.LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"
        self.MICRO_MODEL_ID = "us.amazon.nova-micro-v1:0"
    
    def simple_conversation(self, user_prompt: str, system_prompt: str = None, model_id: str = None) -> Dict:
        """Send a single-turn conversation to Nova."""
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        messages = [
            {"role": "user", "content": [{"text": user_prompt}]},
        ]
        
        system = None
        if system_prompt:
            system = [{"text": system_prompt}]
            
        inf_params = {"maxTokens": 1000, "topP": 0.9, "temperature": 0.9}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inf_params
        )
        
        return response
        
    def get_response_text(self, response: Dict) -> str:
        """Extract the text content from a Nova response."""
        return response["output"]["message"]["content"][0]["text"]
        
    @staticmethod
    def check_aws_credentials() -> bool:
        """Check if AWS credentials are properly configured."""
        return (
            bool(os.environ.get("AWS_ACCESS_KEY_ID")) and
            bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
        )

class BedrockClaudeService:
    """Client for interacting with Amazon Bedrock's Claude multimodal models."""
    
    # AWS credentials from environment variables
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_REGION = os.environ.get("AWS_REGION", "us-west-2")
    
    # Claude model IDs
    CLAUDE_3_SONNET = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    
    def __init__(self, region_name: str = None, profile_name: Optional[str] = None):
        """Initialize the Bedrock Claude client."""
        session_kwargs = {}
        
        # Use provided region or fall back to env variable or default
        if region_name is None:
            region_name = self.AWS_REGION
            
        # Add AWS credentials if available in environment
        if self.AWS_ACCESS_KEY_ID and self.AWS_SECRET_ACCESS_KEY:
            session_kwargs['aws_access_key_id'] = self.AWS_ACCESS_KEY_ID
            session_kwargs['aws_secret_access_key'] = self.AWS_SECRET_ACCESS_KEY
        
        # Use named profile if provided
        if profile_name:
            session_kwargs['profile_name'] = profile_name
            
        session = boto3.Session(**session_kwargs)
        self.client = session.client("bedrock-runtime", region_name=region_name)
    
    def run_multi_modal_prompt(self, model_id: str, 
                               messages: List[Dict], 
                               max_tokens: int = 2000,
                               temperature: float = 0.7,
                               top_p: float = 0.9,
                               top_k: int = 100) -> Dict:
        """
        Invokes a model with a multimodal prompt.
        
        Args:
            model_id (str): The model ID to use.
            messages (List[Dict]): The messages to send to the model.
            max_tokens (int): The maximum number of tokens to generate.
            
        Returns:
            Dict: The model's response.
        """
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
            }
        )

        try:
            response = self.client.invoke_model(
                body=body, modelId=model_id)
            response_body = json.loads(response.get('body').read())
            return response_body
        except ClientError as err:
            message = err.response["Error"]["Message"]
            logger.error("A client error occurred: %s", message)
            raise
    
    def process_image_with_text(self, prompt: str, image_base64: str = None, model_id: str = None, max_tokens: int = 1000) -> str:
        """
        Process an image with a text prompt using Claude multimodal capabilities.
        
        Args:
            image_path (str): Path to the image file.
            prompt (str): Text prompt to send with the image.
            model_id (str, optional): Model ID to use. Defaults to Claude 3 Sonnet.
            max_tokens (int, optional): Maximum tokens to generate. Defaults to 1000.
            
        Returns:
            str: The generated response text.
        """
        if model_id is None:
            model_id = self.CLAUDE_3_SONNET
            
        # Read and encode image
        # image_ext = image_path.split(".")[-1]
        # with open(image_path, "rb") as image_file:
        #     content_image = base64.b64encode(image_file.read()).decode('utf8')

        # Create message payload
        message = {
            "role": "user",
            "content": [
                {
                    "type": "image", 
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg", 
                        "data": image_base64
                    }
                },
                {
                    "type": "text", 
                    "text": prompt
                }
            ]
        }
        
        messages = [message]
        
        # Call the model
        response = self.run_multi_modal_prompt(model_id, messages, max_tokens)
        
        # Extract the response text
        if "content" in response and len(response["content"]) > 0:
            for item in response["content"]:
                if item.get("type") == "text":
                    return item.get("text", "")
        
        return ""
    
    @staticmethod
    def check_aws_credentials() -> bool:
        """Check if AWS credentials are properly configured."""
        return (
            bool(os.environ.get("AWS_ACCESS_KEY_ID")) and
            bool(os.environ.get("AWS_SECRET_ACCESS_KEY"))
        )

class TextGenService:
    """Service for handling text-to-image conversions using LLM"""
    
    # OpenAI API credentials
    USE_FAKE_DATA = os.environ.get("USE_FAKE_DATA", "True").lower() == "true"
    API_KEY = os.environ.get("OPENAI_API_KEY")
    API_URL = "https://api.openai.com/v1/responses"
    MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-nano")
    
    # Provider constants
    PROVIDER_OPENAI = "openai"
    PROVIDER_NOVA = "nova"
    PROVIDER_CLAUDE = "claude"
    
    @staticmethod
    async def text_to_image_attributes(prompt: str, provider: str = None, model_id: str = None, image_base64: str = None) -> ToSpec:
        """
        Convert free-form text to structured PC case design attributes using LLM
        
        Args:
            prompt: The user's text prompt
            provider: The LLM provider to use (openai, nova, or claude)
            model_id: The specific model ID to use
        """
        # Set default provider if not specified
        if not provider:
            provider = TextGenService.PROVIDER_OPENAI if not TextGenService.USE_FAKE_DATA else "mock"
            
        # Check if AWS credentials are available for Nova or Claude
        if provider in [TextGenService.PROVIDER_NOVA, TextGenService.PROVIDER_CLAUDE] and not NovaConverseClient.check_aws_credentials():
            logger.warning(f"AWS credentials not found for {provider} provider, falling back to mock")
            provider = "mock"
        
        # LLM system prompt for attribute extraction
        start_prompt = "You are an AI assistant whose job is to extract structured PC case design attributes from any free-form user prompt."
        image_start_prompt = """You are an AI assistant whose job is to extract design attributes from user image.
                                You MUST follow these rules:***Do NOT add any explanations or extra text-output ONLY the JSON object***
                             """
        # LLM system prompt for attribute extraction
        system_prompt = """
                        Your task is to always output a JSON object containing the following attributes as arrays of English strings, even if the user prompt is vague or lacks detail.
                        If the information is not explicit, you should make reasonable assumptions based on the context or general conventions.
                        color: Main and accent colors (e.g., "Black", "Red", "Navy Blue", "Gold").
                        style: Design style or theme (e.g., "Minimalist", "Futuristic", "Steampunk", "Cthulhu-Ghibli").
                        shape: Form factor or silhouette (e.g., "Mid-Tower", "Cube", "Spherical", "Open-Frame").
                        material: Construction materials (e.g., "Aluminum", "Tempered Glass", "Wood", "Acrylic").
                        ventilation: Vent and airflow features (e.g., "Mesh Front", "Side Vents", "Open-Air Design").
                        lighting: Lighting setup (e.g., "ARGB Fans", "LED Strips", "Ambient Glow", "No Lighting").
                        features: Functional features (e.g., "Water Cooling", "Vertical GPU Mount", "Cable Management", "LCD Display").
                        environment: Visual setting or background (e.g., "Dark Room", "On a Gaming Desk", "Futuristic Lab").
                        You MUST follow these rules:
                        Always return a single JSON object containing ALL of the above keys.
                        Each attribute must be represented as an array of strings, even if only one value is extracted or assumed.
                        If the user prompt does not specify an attribute, make a reasonable guess or use a common default (e.g., "Black" for color, "Minimalist" for style, "Mid-Tower" for shape, etc.).
                        All extracted or assumed values must be in English, even if the user input is in another language.
                        Do NOT add any explanations or extra text-output ONLY the JSON object.
                        Below are a few examples:
                        """
        
        few_shot_examples = """
                        User Prompt: "我想要一個木頭風格的中塔機殼，有RGB燈條和側邊透氣孔，內建水冷，整體走日系極簡風，擺在書桌上很好看，風扇要兩個"
                        Output:
                        {
                        "color": ["Wood Brown"],
                        "style": ["Minimalist", "Japanese"],
                        "shape": ["Mid-Tower"],
                        "material": ["Wood"],
                        "ventilation": ["Side Vents"],
                        "lighting": ["RGB Lighting"],
                        "features": ["Water Cooling"],
                        "environment": ["On a Desk"],
                        "modifiers": ["2 Fans"]
                        }
                        User Prompt: "A cyberpunk cube case with open sides, neon ARGB glow, and vertical GPU mount. It should be small and look good in a dark gaming room. I want three USB ports and a removable side panel."
                        Output:
                        {
                        "color": ["Neon Colors", "Black"],
                        "style": ["Cyberpunk"],
                        "shape": ["Cube", "Compact"],
                        "material": ["Aluminum", "Acrylic"],
                        "ventilation": ["Open-Air Design"],
                        "lighting": ["ARGB Lighting", "Neon"],
                        "features": ["Vertical GPU Mount"],
                        "environment": ["Dark Room", "Gaming Setup"],
                        }
                        User Prompt: "我要一個很普通的機殼"
                        Output:
                        {
                        "color": ["Black"],
                        "style": ["Minimalist"],
                        "shape": ["Mid-Tower"],
                        "material": ["Steel"],
                        "ventilation": ["Mesh Front"],
                        "lighting": ["No Lighting"],
                        "features": ["Cable Management"],
                        "environment": ["On a Desk"],
                        }
                        """

        image_few_shot_examples = """
                        User Prompt: ""
                        Output:
                        {
                        "color": ["Wood Brown"],
                        "style": ["Minimalist", "Japanese"],
                        "shape": ["Mid-Tower"],
                        "material": ["Wood"],
                        "ventilation": ["Side Vents"],
                        "lighting": ["RGB Lighting"],
                        "features": ["Water Cooling"],
                        "environment": ["On a Desk"],
                        }
                        User Prompt: ""
                        Output:
                        {
                        "color": ["Black"],
                        "style": ["Minimalist"],
                        "shape": ["Mid-Tower"],
                        "material": ["Steel"],
                        "ventilation": ["Mesh Front"],
                        "lighting": ["No Lighting"],
                        "features": ["Cable Management"],
                        "environment": ["On a Desk"],
                        }
                        """

        final_prompt = f"{start_prompt}\n\n{system_prompt}\n\n{few_shot_examples}"
        image_final_prompt = f"{image_start_prompt}\n\n{system_prompt}\n\n{image_few_shot_examples}"

        try:
            # Process based on provider
            if provider == TextGenService.PROVIDER_OPENAI:
                # Make API call to OpenAI
                attributes_dict = await TextGenService._call_openai_api(final_prompt, prompt, model_id)
            elif provider == TextGenService.PROVIDER_NOVA:
                # Make API call to Amazon Bedrock Nova
                attributes_dict = await TextGenService._call_nova_api(final_prompt, prompt, model_id)
            elif provider == TextGenService.PROVIDER_CLAUDE:
                # Make API call to Amazon Bedrock Claude
                attributes_dict = await TextGenService._call_claude_api(system_prompt=image_final_prompt, 
                                                                        model_id=model_id, 
                                                                        image_base64=image_base64)
            else:
                # Fallback to mock extraction
                logger.warning(f"Using mock extraction (provider: {provider})")
                attributes_dict = TextGenService._mock_extract_attributes(prompt)
            
            # Convert the dictionary to our Pydantic model
            attributes = PCCaseAttributes(**attributes_dict)
            logger.info(f"Attributes: {attributes}")
            
            # Generate a structured prompt
            structured_prompt = ""
            
            return ToSpec(
                prompt=prompt,
                attributes=attributes,
                structured_prompt=structured_prompt
            )
            
        except Exception as e:
            logger.error(f"Error in text_to_image conversion: {e}")
            # Return empty attributes in case of failure
            attributes = PCCaseAttributes()
            return ToSpec(
                prompt=prompt,
                attributes=attributes,
                structured_prompt=prompt
            )
    
    @staticmethod
    async def _call_openai_api(system_prompt: str, user_prompt: str = None, model_id: str = None) -> Dict[str, Any]:
        """Call OpenAI API to extract attributes from text"""
        try:
            if not model_id:
                model_id = TextGenService.MODEL
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    TextGenService.API_URL,
                    json={
                        "model": model_id,
                        "input": f"{system_prompt}\n\nUser: {user_prompt}" if user_prompt else system_prompt,
                        "temperature": 0.1,
                    },
                    headers={"Authorization": f"Bearer {TextGenService.API_KEY}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Extract text from the Response API format
                    text = result["output"][0]["content"][0]["text"]
                    # Parse the JSON response from the LLM
                    return json.loads(text)
                else:
                    logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                    # Return empty dict on error
                    return {}
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return {}
    
    @staticmethod
    async def _call_nova_api(system_prompt: str, user_prompt: str, model_id: str = None) -> Dict[str, Any]:
        """Call Amazon Bedrock Nova API to extract attributes from text"""
        try:
            # Initialize the Nova client
            nova_client = NovaConverseClient()
            
            # Use default model if not specified
            if not model_id:
                model_id = nova_client.LITE_MODEL_ID
                
            # Call the Nova API
            response = nova_client.simple_conversation(
                user_prompt=user_prompt,
                system_prompt=system_prompt,
                model_id=model_id
            )
            
            # Extract text from response
            text = nova_client.get_response_text(response)
            
            # Parse the JSON response from the LLM
            return json.loads(text)
        except Exception as e:
            logger.error(f"Error calling Nova API: {e}")
            return {}
    
    @staticmethod
    async def _call_claude_api(system_prompt: str, model_id: str = None, image_base64: str = None) -> Dict[str, Any]:
        """Call Amazon Bedrock Claude API to extract attributes from text"""
        try:
            # Initialize the Claude client
            claude_client = BedrockClaudeService()
            
            # Use default model if not specified
            if not model_id:
                model_id = claude_client.CLAUDE_3_SONNET
                
            # Format the messages for Claude
            # messages = [
            #     {
            #         "role": "system",
            #         "content": [
            #             {
            #                 "type": "text",
            #                 "text": system_prompt
            #             }
            #         ]
            #     },
            #     {
            #         "role": "user",
            #         "content": [
            #             {
            #                 "type": "text",
            #                 "text": user_prompt
            #             }
            #         ]
            #     }
            # ]
            
            # Call the Claude API
            response = claude_client.process_image_with_text(
                prompt=system_prompt,
                image_base64=image_base64,
                model_id=model_id
            )
            
            # Parse the JSON response from the LLM
            logger.info(f"Claude API response: {response}")
            return json.loads(response)
        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {}
    
    @staticmethod
    def _mock_extract_attributes(prompt: str) -> Dict[str, Any]:
        """Mock: Extract design attributes from prompt using keyword scanning."""
        attributes = {}
        prompt_lower = prompt.lower()

        # Keyword dictionaries
        shape_keywords = ["mid-tower", "cube", "spherical", "slim", "open-frame", "compact", "ultra-tower"]
        style_keywords = ["futuristic", "steampunk", "minimalist", "modern", "sleek", "industrial", "cthulhu", "ghibli"]
        color_keywords = ["black", "white", "red", "blue", "green", "silver", "gray", "gold", "brown", "navy"]
        material_keywords = ["aluminum", "tempered glass", "wood", "acrylic", "steel", "carbon fiber", "glass"]
        ventilation_keywords = ["mesh", "side vents", "open-air", "airflow", "intake", "cooling"]
        lighting_keywords = ["argb", "rgb", "led", "ambient glow", "neon", "illuminated", "no lighting"]
        feature_keywords = ["lcd", "handle", "psu shroud", "decorative", "water cooling", "cable management", "vertical gpu"]
        environment_keywords = [
            "dark room", "spotlight", "studio", "on a desk", "with peripherals", "in a showcase", "in a gaming setup",
            "cyberpunk city", "nature background", "futuristic lab"
        ]

        def match_and_append(attr, keywords, format_fn=lambda x: x.title()):
            for keyword in keywords:
                if keyword in prompt_lower:
                    attributes.setdefault(attr, []).append(format_fn(keyword))

        match_and_append("shape", shape_keywords)
        match_and_append("style", style_keywords)
        match_and_append("color", color_keywords)
        match_and_append("material", material_keywords)
        match_and_append("ventilation", ventilation_keywords)
        match_and_append("lighting", lighting_keywords, lambda x: x.upper() + " lighting" if x in ["rgb", "argb", "led"] else x.title())
        match_and_append("features", feature_keywords)
        match_and_append("environment", environment_keywords)

        return attributes


    @staticmethod
    def _create_structured_prompt(original_prompt: str, attributes: PCCaseAttributes) -> str:
        """Create a natural-language prompt based on attribute template mapping."""

        parts = ["A high-resolution render of"]

        # Shape and Style
        if attributes.shape:
            shape_desc = f"a {' and '.join(attributes.shape)} PC case"
        else:
            shape_desc = "a PC case"

        if attributes.style:
            style_desc = f"with a {' and '.join(attributes.style)} aesthetic"
            parts.append(f"{shape_desc} {style_desc}")
        else:
            parts.append(shape_desc)

        # Materials
        if attributes.material:
            parts.append(f"made of {' and '.join(attributes.material)}")

        # Ventilation
        if attributes.ventilation:
            parts.append(f"featuring {' and '.join(attributes.ventilation)}")

        # Lighting
        if attributes.lighting:
            parts.append(f"illuminated by {' and '.join(attributes.lighting)}")

        # Features
        if attributes.features:
            parts.append(f"including {' and '.join(attributes.features)}")

        # Environment
        if attributes.environment:
            parts.append(f"set in {' and '.join(attributes.environment)}")

        # Final composition
        prompt = "; ".join(parts) + "."
        return prompt
    
    @staticmethod
    async def merge_attributes(text_attributes: PCCaseAttributes, image_attributes: PCCaseAttributes) -> PCCaseAttributes:
        """Merge text and image attributes into a single PCCaseAttributes object"""
        merged_attributes = PCCaseAttributes()
        merged_attributes.shape = text_attributes.shape + image_attributes.shape
        merged_attributes.style = text_attributes.style + image_attributes.style
        merged_attributes.material = text_attributes.material + image_attributes.material
        merged_attributes.ventilation = text_attributes.ventilation + image_attributes.ventilation
        merged_attributes.lighting = text_attributes.lighting + image_attributes.lighting
        merged_attributes.features = text_attributes.features + image_attributes.features
        merged_attributes.environment = text_attributes.environment + image_attributes.environment
        return merged_attributes
