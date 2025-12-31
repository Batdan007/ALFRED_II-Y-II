"""
SwarmUI Image Generation Tool for ALFRED
Provides AI-powered image generation via SwarmUI

Author: Daniel J Rita (BATDAN)
"""

import logging
from typing import Dict, Any, Optional
from .base import Tool, ToolResult

# Graceful import for SwarmUI client
try:
    from capabilities.generation.swarmui_client import SwarmUIClient
    SWARMUI_CLIENT_AVAILABLE = True
except ImportError:
    SwarmUIClient = None
    SWARMUI_CLIENT_AVAILABLE = False


class SwarmUITool(Tool):
    """
    Generate images from text prompts using local AI via SwarmUI.

    Supports:
    - Stable Diffusion XL
    - Flux models
    - Various other image generation models
    - 100% local operation (privacy-first)
    """

    def __init__(self, brain=None):
        """
        Initialize SwarmUI tool.

        Args:
            brain: Optional AlfredBrain for storing generation history
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.client: Optional[SwarmUIClient] = None
        self.swarmui_available = False

        if SWARMUI_CLIENT_AVAILABLE:
            try:
                self.client = SwarmUIClient()
                self.swarmui_available = self.client.is_available()
                if self.swarmui_available:
                    self.logger.info("SwarmUI image generation available")
                else:
                    self.logger.info("SwarmUI client loaded but server not running")
            except Exception as e:
                self.logger.warning(f"SwarmUI client init error: {e}")
        else:
            self.logger.info("SwarmUI client not available (missing dependencies)")

    @property
    def name(self) -> str:
        return "generate_image"

    @property
    def description(self) -> str:
        return (
            "Generate an image from a text prompt using local AI (SwarmUI/Stable Diffusion). "
            "100% local and private - no data leaves your machine. "
            "Supports various styles and aspect ratios."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Detailed text description of the image to generate"
                },
                "style": {
                    "type": "string",
                    "description": "Optional style hint: realistic, artistic, anime, digital art, oil painting, watercolor, sketch, 3d render, etc.",
                    "default": ""
                },
                "aspect_ratio": {
                    "type": "string",
                    "enum": ["square", "portrait", "landscape", "wide"],
                    "description": "Image aspect ratio (square=1:1, portrait=2:3, landscape=3:2, wide=16:9)",
                    "default": "square"
                },
                "negative_prompt": {
                    "type": "string",
                    "description": "What to avoid in the image (e.g., 'blurry, low quality, distorted')",
                    "default": ""
                }
            },
            "required": ["prompt"]
        }

    def execute(
        self,
        prompt: str,
        style: str = "",
        aspect_ratio: str = "square",
        negative_prompt: str = ""
    ) -> ToolResult:
        """
        Execute image generation.

        Args:
            prompt: Text description of the image
            style: Optional style modifier
            aspect_ratio: Image aspect ratio
            negative_prompt: What to avoid

        Returns:
            ToolResult with image path or error
        """
        if not self.client:
            return ToolResult(
                success=False,
                output="",
                error="SwarmUI client not available. Install dependencies: pip install requests websocket-client"
            )

        # Check server availability (may have started since init)
        if not self.swarmui_available:
            self.swarmui_available = self.client.is_available()

        if not self.swarmui_available:
            return ToolResult(
                success=False,
                output="",
                error="SwarmUI server not running. Start it first at http://localhost:7801"
            )

        # Determine dimensions based on aspect ratio
        dimensions = {
            "square": (1024, 1024),
            "portrait": (768, 1152),
            "landscape": (1152, 768),
            "wide": (1344, 768)
        }
        width, height = dimensions.get(aspect_ratio, (1024, 1024))

        # Enhance prompt with style
        full_prompt = prompt
        if style:
            full_prompt = f"{prompt}, {style} style"

        # Add quality enhancers
        if "quality" not in full_prompt.lower():
            full_prompt += ", high quality, detailed"

        # Default negative prompt if none provided
        if not negative_prompt:
            negative_prompt = "blurry, low quality, distorted, deformed, ugly, bad anatomy"

        try:
            # Generate image
            image_path = self.client.generate_image(
                prompt=full_prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height
            )

            if image_path:
                # Get full URL
                image_url = self.client.get_image_url(image_path)

                # Store in brain if available
                if self.brain:
                    try:
                        self.brain.store_knowledge(
                            category="generated_images",
                            key=prompt[:100],
                            value={
                                "path": image_path,
                                "url": image_url,
                                "prompt": full_prompt,
                                "negative_prompt": negative_prompt,
                                "dimensions": f"{width}x{height}",
                                "style": style
                            },
                            source="swarmui",
                            importance=5
                        )
                    except Exception as e:
                        self.logger.warning(f"Could not store in brain: {e}")

                return ToolResult(
                    success=True,
                    output=f"Image generated successfully!\n\nURL: {image_url}\nPath: {image_path}\nDimensions: {width}x{height}",
                    metadata={
                        "image_path": image_path,
                        "image_url": image_url,
                        "prompt": full_prompt,
                        "dimensions": f"{width}x{height}"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error="Image generation failed. Check SwarmUI logs for details."
                )

        except Exception as e:
            self.logger.error(f"Image generation error: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"Image generation error: {str(e)}"
            )

    def list_models(self) -> ToolResult:
        """
        List available models (not exposed as AI tool, for internal use).

        Returns:
            ToolResult with model list
        """
        if not self.client or not self.swarmui_available:
            return ToolResult(
                success=False,
                output="",
                error="SwarmUI not available"
            )

        try:
            models = self.client.get_model_names()
            if models:
                return ToolResult(
                    success=True,
                    output=f"Available models:\n" + "\n".join(f"  - {m}" for m in models),
                    metadata={"models": models}
                )
            else:
                return ToolResult(
                    success=True,
                    output="No models found. Check SwarmUI model configuration.",
                    metadata={"models": []}
                )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Could not list models: {e}"
            )
