# Image Generation Services

This directory contains services for generating images using various AI providers.

## Configuration

Configure the image generation services using environment variables:

```
# Choose which image provider to use (stability_ai, aws_nova, or mock)
# This is the default provider when none is specified in the API call
IMAGE_PROVIDER=stability_ai

# Set to "True" to use mock images instead of calling APIs (useful for development)
# When set to "True", this overrides any provider specified in the API call
USE_FAKE_DATA=False

# API Keys for different providers
STABILITY_API_KEY=your_stability_ai_key
AWS_NOVA_API_KEY=your_aws_nova_key
```

## Available Providers

### Stability AI

Uses Stability AI's API to generate images. Configure with:
- `IMAGE_PROVIDER=stability_ai`
- `STABILITY_API_KEY=your_api_key`

Supports multiple models:
- ultra
- core
- sd3.5-large
- sd3.5-large-turbo
- sd3.5-medium

### AWS Nova (Placeholder)

This is a placeholder for AWS Bedrock Nova integration, which will be implemented in the future.

### Mock Provider

Returns placeholder images for testing. Enabled when:
- `USE_FAKE_DATA=True` (this takes precedence over all other settings) or
- No API key is available for the selected provider

## Usage

```python
from app.services.image_gen_service import ImageGenService, ImageProvider

# Initialize the service
image_service = ImageGenService()

# Generate an image with default parameters (provider from environment)
image_base64 = await image_service.generate_image(prompt="A cat wearing a space suit")

# Generate an image with an explicitly specified provider
# Note: If USE_FAKE_DATA=True, it will use the mock provider regardless of this setting
image_base64 = await image_service.generate_image(
    prompt="A dog on the moon",
    negative_prompt="blurry, low quality", 
    seed=202,
    output_format="jpeg",
    provider=ImageProvider.STABILITY_AI,  # Explicitly select Stability AI
    model="sd3.5-large"
)

# Use structured prompt generation for PC cases
from app.schemas import PCCaseAttributes

attributes = PCCaseAttributes(
    shape=["tower", "minimalist"],
    style=["futuristic"],
    material=["brushed aluminum", "tempered glass"],
    lighting=["RGB", "ambient"]
)

structured_prompt = await image_service.create_structured_prompt(attributes)
image_base64 = await image_service.generate_image(
    prompt="PC case", 
    structured_prompt=structured_prompt,
    provider=ImageProvider.MOCK  # Force using mock provider (unless USE_FAKE_DATA=True)
)
``` 