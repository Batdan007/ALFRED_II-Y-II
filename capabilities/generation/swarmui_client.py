"""
SwarmUI API Client for ALFRED
Provides local AI image generation via SwarmUI server.

SwarmUI is a modular web UI for AI image generation supporting:
- Stable Diffusion XL, Flux, and other models
- ComfyUI backend integration
- 100% local operation (privacy-first)

Author: Daniel J Rita (BATDAN)
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any, Callable
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from websocket import create_connection
    HAS_WEBSOCKET = True
except ImportError:
    HAS_WEBSOCKET = False


class SwarmUIClient:
    """
    Client for SwarmUI image generation API.

    Provides synchronous HTTP and optional WebSocket-based
    image generation with progress callbacks.
    """

    def __init__(self, base_url: str = None):
        """
        Initialize SwarmUI client.

        Args:
            base_url: SwarmUI server URL (default: http://localhost:7801)
        """
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url or os.getenv("SWARMUI_URL", "http://localhost:7801")
        self.api_url = f"{self.base_url}/API"
        self.session_id: Optional[str] = None
        self.headers = {"Content-Type": "application/json"}

        # Default generation settings
        self.default_model = os.getenv(
            "SWARMUI_DEFAULT_MODEL",
            "OfficialStableDiffusion/sd_xl_base_1.0"
        )
        self.default_steps = int(os.getenv("SWARMUI_DEFAULT_STEPS", "20"))
        self.default_cfg_scale = float(os.getenv("SWARMUI_DEFAULT_CFG", "7.5"))

    def _ensure_session(self) -> bool:
        """
        Ensure we have a valid session.

        Returns:
            True if session is valid, False otherwise
        """
        if self.session_id:
            return True
        return self._get_new_session()

    def _get_new_session(self) -> bool:
        """
        Get a new session from SwarmUI.

        Returns:
            True if session acquired, False otherwise
        """
        if not HAS_REQUESTS:
            self.logger.error("requests library not installed")
            return False

        try:
            response = requests.post(
                f"{self.api_url}/GetNewSession",
                json={},
                headers=self.headers,
                timeout=10
            )
            data = response.json()
            self.session_id = data.get("session_id")

            if self.session_id:
                self.logger.info(f"SwarmUI session acquired: {self.session_id[:16]}...")
                return True
            return False

        except requests.exceptions.ConnectionError:
            self.logger.warning("SwarmUI server not reachable")
            return False
        except Exception as e:
            self.logger.error(f"Session error: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if SwarmUI server is available.

        Returns:
            True if server is running and accessible
        """
        if not HAS_REQUESTS:
            return False

        try:
            response = requests.post(
                f"{self.api_url}/GetNewSession",
                json={},
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get SwarmUI server status.

        Returns:
            Status dictionary with queue info, backend status, etc.
        """
        if not self._ensure_session():
            return {"available": False, "error": "Could not establish session"}

        try:
            response = requests.post(
                f"{self.api_url}/GetCurrentStatus",
                json={"session_id": self.session_id},
                headers=self.headers,
                timeout=10
            )
            data = response.json()
            data["available"] = True
            return data
        except Exception as e:
            return {"available": False, "error": str(e)}

    def generate_image(
        self,
        prompt: str,
        model: str = None,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = None,
        cfg_scale: float = None,
        seed: int = -1,
        save: bool = True
    ) -> Optional[str]:
        """
        Generate an image synchronously (HTTP method).

        Args:
            prompt: Text description of the image to generate
            model: Model to use (default: sd_xl_base_1.0)
            negative_prompt: What to avoid in the image
            width: Image width in pixels
            height: Image height in pixels
            steps: Number of inference steps
            cfg_scale: Classifier-free guidance scale
            seed: Random seed (-1 for random)
            save: Whether to save to SwarmUI history

        Returns:
            Image path on success (relative to SwarmUI), None on failure
        """
        if not HAS_REQUESTS:
            self.logger.error("requests library not installed")
            return None

        if not self._ensure_session():
            self.logger.error("Could not establish SwarmUI session")
            return None

        # Use defaults if not specified
        model = model or self.default_model
        steps = steps or self.default_steps
        cfg_scale = cfg_scale or self.default_cfg_scale

        try:
            self.logger.info(f"Generating image: '{prompt[:50]}...'")

            response = requests.post(
                f"{self.api_url}/GenerateText2Image",
                json={
                    "session_id": self.session_id,
                    "images": 1,
                    "prompt": prompt,
                    "negativeprompt": negative_prompt,
                    "model": model,
                    "width": width,
                    "height": height,
                    "cfgscale": cfg_scale,
                    "steps": steps,
                    "seed": seed,
                    "donotsave": not save
                },
                headers=self.headers,
                timeout=300  # 5 min timeout for generation
            )

            data = response.json()

            # Handle session expiry
            if data.get("error_id") == "invalid_session_id":
                self.logger.info("Session expired, refreshing...")
                self.session_id = None
                if self._get_new_session():
                    return self.generate_image(
                        prompt, model, negative_prompt,
                        width, height, steps, cfg_scale, seed, save
                    )
                return None

            # Handle other errors
            if data.get("error"):
                self.logger.error(f"Generation error: {data['error']}")
                return None

            # Return image path
            if "images" in data and data["images"]:
                image_path = data["images"][0]
                self.logger.info(f"Image generated: {image_path}")
                return image_path

            return None

        except requests.exceptions.Timeout:
            self.logger.error("Generation timed out (5 min limit)")
            return None
        except Exception as e:
            self.logger.error(f"SwarmUI generation error: {e}")
            return None

    def generate_image_with_progress(
        self,
        prompt: str,
        on_progress: Callable[[float, Optional[str]], None] = None,
        model: str = None,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        steps: int = None,
        cfg_scale: float = None,
        seed: int = -1
    ) -> Optional[str]:
        """
        Generate an image with real-time progress updates (WebSocket method).

        Args:
            prompt: Text description of the image
            on_progress: Callback(percent, preview_base64) for progress updates
            model: Model to use
            negative_prompt: What to avoid
            width: Image width
            height: Image height
            steps: Inference steps
            cfg_scale: Guidance scale
            seed: Random seed

        Returns:
            Image path on success, None on failure
        """
        if not HAS_WEBSOCKET:
            self.logger.warning("WebSocket not available, falling back to HTTP")
            return self.generate_image(
                prompt, model, negative_prompt,
                width, height, steps, cfg_scale, seed
            )

        if not self._ensure_session():
            return None

        model = model or self.default_model
        steps = steps or self.default_steps
        cfg_scale = cfg_scale or self.default_cfg_scale

        try:
            ws_url = self.api_url.replace("http", "ws") + "/GenerateText2ImageWS"
            ws = create_connection(ws_url, timeout=300)

            # Send generation request
            request = {
                "session_id": self.session_id,
                "images": 1,
                "prompt": prompt,
                "negativeprompt": negative_prompt,
                "model": model,
                "width": width,
                "height": height,
                "cfgscale": cfg_scale,
                "steps": steps,
                "seed": seed
            }
            ws.send(json.dumps(request))

            image_path = None

            while True:
                try:
                    msg = ws.recv()
                    data = json.loads(msg)

                    # Progress update
                    if "gen_progress" in data and on_progress:
                        progress = data["gen_progress"]
                        percent = progress.get("overall_percent", 0)
                        preview = progress.get("preview")
                        on_progress(percent, preview)

                    # Image complete
                    if "image" in data:
                        image_data = data["image"]
                        image_path = image_data.get("image")
                        self.logger.info(f"Image generated: {image_path}")

                    # Check for close signal
                    if data.get("socket_intention") == "close":
                        break

                except Exception as e:
                    self.logger.error(f"WebSocket error: {e}")
                    break

            ws.close()
            return image_path

        except Exception as e:
            self.logger.error(f"WebSocket generation error: {e}")
            return None

    def list_models(self, model_type: str = "Stable-Diffusion") -> List[Dict[str, Any]]:
        """
        List available models.

        Args:
            model_type: Model type to list (Stable-Diffusion, LoRA, VAE, etc.)

        Returns:
            List of model info dictionaries
        """
        if not self._ensure_session():
            return []

        try:
            response = requests.post(
                f"{self.api_url}/ListModels",
                json={
                    "session_id": self.session_id,
                    "path": "",
                    "depth": 2,
                    "subtype": model_type,
                    "sortBy": "Name",
                    "allowRemote": False,
                    "dataImages": False
                },
                headers=self.headers,
                timeout=30
            )
            data = response.json()
            return data.get("files", [])
        except Exception as e:
            self.logger.error(f"List models error: {e}")
            return []

    def get_model_names(self, model_type: str = "Stable-Diffusion") -> List[str]:
        """
        Get just the model names (simplified list).

        Args:
            model_type: Model type to list

        Returns:
            List of model name strings
        """
        models = self.list_models(model_type)
        return [m.get("name", "") for m in models if m.get("name")]

    def download_image(self, image_path: str) -> Optional[bytes]:
        """
        Download a generated image.

        Args:
            image_path: Relative path from SwarmUI (from generate_image)

        Returns:
            Image bytes on success, None on failure
        """
        if not HAS_REQUESTS:
            return None

        try:
            url = f"{self.base_url}/{image_path}"
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return response.content
            return None
        except Exception as e:
            self.logger.error(f"Download error: {e}")
            return None

    def get_image_url(self, image_path: str) -> str:
        """
        Get full URL for an image.

        Args:
            image_path: Relative path from generate_image

        Returns:
            Full URL to the image
        """
        return f"{self.base_url}/{image_path}"

    def interrupt_generation(self) -> bool:
        """
        Interrupt any running generations.

        Returns:
            True if successful
        """
        if not self._ensure_session():
            return False

        try:
            response = requests.post(
                f"{self.api_url}/InterruptAll",
                json={
                    "session_id": self.session_id,
                    "other_sessions": False
                },
                headers=self.headers,
                timeout=10
            )
            return response.json().get("success", False)
        except Exception:
            return False
