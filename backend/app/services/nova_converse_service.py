import boto3
import json
import base64
from typing import Dict, List, Any, Optional, Union, BinaryIO


class NovaConverseClient:
    """Client for interacting with Amazon Bedrock's Nova models via the Converse API."""
    
    def __init__(self, region_name: str = "us-east-1", profile_name: Optional[str] = None):
        """
        Initialize the Nova Converse client.
        
        Args:
            region_name: AWS region name where Bedrock is available
            profile_name: Optional AWS profile name for credentials
        """
        session_kwargs = {}
        if profile_name:
            session_kwargs['profile_name'] = profile_name
            
        session = boto3.Session(**session_kwargs)
        self.client = session.client("bedrock-runtime", region_name=region_name)
        
        # Available Nova model IDs
        self.PRO_MODEL_ID = "us.amazon.nova-pro-v1:0"
        self.LITE_MODEL_ID = "us.amazon.nova-lite-v1:0"
        self.MICRO_MODEL_ID = "us.amazon.nova-micro-v1:0"
    
    def simple_conversation(self, user_prompt: str, system_prompt: str = None, model_id: str = None) -> Dict:
        """
        Send a single-turn conversation to Nova.
        
        Args:
            user_prompt: Text prompt from the user
            system_prompt: Optional system prompt to guide the model's behavior
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            
        Returns:
            Dict containing the model's response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        messages = [
            {"role": "user", "content": [{"text": user_prompt}]},
        ]
        
        system = None
        if system_prompt:
            system = [{"text": system_prompt}]
            
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inf_params
        )
        
        return response
    
    def multi_turn_conversation(self, 
                               messages: List[Dict], 
                               system_prompt: str = None, 
                               model_id: str = None) -> Dict:
        """
        Send a multi-turn conversation to Nova.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            system_prompt: Optional system prompt to guide the model's behavior
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            
        Returns:
            Dict containing the model's response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        system = None
        if system_prompt:
            system = [{"text": system_prompt}]
            
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inf_params
        )
        
        return response
    
    def streaming_conversation(self, 
                              user_prompt: str, 
                              system_prompt: str = None, 
                              model_id: str = None,
                              callback=None) -> Dict:
        """
        Send a conversation to Nova with streaming response.
        
        Args:
            user_prompt: Text prompt from the user
            system_prompt: Optional system prompt to guide the model's behavior
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            callback: Optional callback function to process streaming chunks
            
        Returns:
            Complete streamed response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        messages = [
            {"role": "user", "content": [{"text": user_prompt}]},
        ]
        
        system = None
        if system_prompt:
            system = [{"text": system_prompt}]
            
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        model_response = self.client.converse_stream(
            modelId=model_id,
            messages=messages,
            system=system,
            inferenceConfig=inf_params
        )
        
        full_response = ""
        stream = model_response.get("stream")
        if stream:
            for event in stream:
                if "contentBlockDelta" in event:
                    chunk = event["contentBlockDelta"]["delta"]["text"]
                    full_response += chunk
                    if callback:
                        callback(chunk)
        
        return full_response
    
    def image_understanding(self, 
                          image_path: str, 
                          prompt: str = "Describe the following image", 
                          model_id: str = None) -> Dict:
        """
        Send an image to Nova for understanding.
        
        Args:
            image_path: Path to the image file
            prompt: Text prompt about the image
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            
        Returns:
            Dict containing the model's response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        # Determine image format from file extension
        image_format = image_path.split(".")[-1].lower()
        if image_format not in ["png", "jpeg", "jpg", "gif"]:
            raise ValueError(f"Unsupported image format: {image_format}")
        
        if image_format == "jpg":
            image_format = "jpeg"
            
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            
        messages = [
            {
                "role": "user",
                "content": [
                    {"image": {"format": image_format, "source": {"bytes": image_bytes}}},
                    {"text": prompt},
                ],
            }
        ]
        
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inf_params
        )
        
        return response
    
    def multi_image_understanding(self, 
                                image_paths: List[str], 
                                prompt: str = "Describe these images", 
                                model_id: str = None) -> Dict:
        """
        Send multiple images to Nova for understanding.
        
        Args:
            image_paths: List of paths to image files
            prompt: Text prompt about the images
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            
        Returns:
            Dict containing the model's response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        content = []
        
        for image_path in image_paths:
            # Determine image format from file extension
            image_format = image_path.split(".")[-1].lower()
            if image_format not in ["png", "jpeg", "jpg", "gif"]:
                raise ValueError(f"Unsupported image format: {image_format}")
            
            if image_format == "jpg":
                image_format = "jpeg"
                
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                
            content.append({"image": {"format": image_format, "source": {"bytes": image_bytes}}})
            
        content.append({"text": prompt})
        
        messages = [
            {
                "role": "user",
                "content": content,
            }
        ]
        
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inf_params
        )
        
        return response
    
    def video_understanding(self, 
                          video_path: str, 
                          prompt: str = "Describe the following video", 
                          model_id: str = None) -> Dict:
        """
        Send a video to Nova for understanding.
        
        Args:
            video_path: Path to the video file
            prompt: Text prompt about the video
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            
        Returns:
            Dict containing the model's response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        # Determine video format from file extension
        video_format = video_path.split(".")[-1].lower()
        if video_format not in ["mp4", "mov", "avi"]:
            raise ValueError(f"Unsupported video format: {video_format}")
            
        with open(video_path, "rb") as f:
            video_bytes = f.read()
            
        messages = [
            {
                "role": "user",
                "content": [
                    {"video": {"format": video_format, "source": {"bytes": video_bytes}}},
                    {"text": prompt},
                ],
            }
        ]
        
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inf_params
        )
        
        return response
    
    def video_understanding_s3(self,
                             s3_uri: str,
                             prompt: str = "Describe the following video",
                             model_id: str = None) -> Dict:
        """
        Send a video from S3 to Nova for understanding.
        
        Args:
            s3_uri: S3 URI to the video file (e.g., s3://bucket-name/file-path.mp4)
            prompt: Text prompt about the video
            model_id: Nova model ID to use (defaults to LITE_MODEL_ID)
            
        Returns:
            Dict containing the model's response
        """
        if model_id is None:
            model_id = self.LITE_MODEL_ID
            
        # Determine video format from file extension
        video_format = s3_uri.split(".")[-1].lower()
        if video_format not in ["mp4", "mov", "avi"]:
            raise ValueError(f"Unsupported video format: {video_format}")
            
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "video": {
                            "format": video_format,
                            "source": {
                                "s3Location": {
                                    "uri": s3_uri
                                }
                            },
                        }
                    },
                    {"text": prompt},
                ],
            }
        ]
        
        inf_params = {"maxTokens": 300, "topP": 0.1, "temperature": 0.3}
        
        response = self.client.converse(
            modelId=model_id,
            messages=messages,
            inferenceConfig=inf_params
        )
        
        return response
    
    def get_response_text(self, response: Dict) -> str:
        """
        Extract the text content from a Nova response.
        
        Args:
            response: The response dictionary from Nova
            
        Returns:
            The text content from the response
        """
        return response["output"]["message"]["content"][0]["text"]


# Example usage
if __name__ == "__main__":
    # Initialize the client
    # By default, boto3 will use credentials from ~/.aws/credentials or environment variables
    nova_client = NovaConverseClient()
    
    # Simple conversation example
    response = nova_client.simple_conversation(
        user_prompt="What are the benefits of quantum computing?",
        system_prompt="You are a helpful AI assistant specializing in quantum physics."
    )
    print("\nSimple Conversation Response:")
    print(nova_client.get_response_text(response))
    
    # Streaming example with a callback
    def print_chunk(chunk):
        print(chunk, end="")
    
    print("\nStreaming Response:")
    full_text = nova_client.streaming_conversation(
        user_prompt="Tell me a short story about a robot learning to paint.",
        system_prompt="You are a creative storyteller.",
        callback=print_chunk
    )
    
    # Note: Using image or video examples requires actual files
    # Uncomment these if you have the appropriate files
    """
    # Image understanding example
    image_response = nova_client.image_understanding(
        image_path="path/to/your/image.jpg",
        prompt="What's happening in this image?"
    )
    print("\nImage Understanding Response:")
    print(nova_client.get_response_text(image_response))
    
    # Multi-image understanding example
    multi_image_response = nova_client.multi_image_understanding(
        image_paths=["path/to/image1.jpg", "path/to/image2.png"],
        prompt="Compare these two images."
    )
    print("\nMulti-Image Understanding Response:")
    print(nova_client.get_response_text(multi_image_response))
    
    # Video understanding example
    video_response = nova_client.video_understanding(
        video_path="path/to/your/video.mp4",
        prompt="Summarize what happens in this video."
    )
    print("\nVideo Understanding Response:")
    print(nova_client.get_response_text(video_response))
    
    # S3 video understanding example
    s3_video_response = nova_client.video_understanding_s3(
        s3_uri="s3://your-bucket/path/to/video.mp4",
        prompt="What's the main event in this video?"
    )
    print("\nS3 Video Understanding Response:")
    print(nova_client.get_response_text(s3_video_response))
    """
