"""
Alfred's Eyes - Computer Vision and Visual Recognition
Can see BATDAN, remember faces, analyze scenes
Knows who is important and filters out TV/strangers

Author: Daniel J Rita (BATDAN)
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import time
from datetime import datetime
from PIL import Image
import io
import base64

# Graceful degradation for optional vision dependencies
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except ImportError:
    DEEPFACE_AVAILABLE = False


class AlfredEyes:
    """
    Alfred's vision system - sees and remembers important people

    Features:
    - Face detection and recognition
    - Distinguishes BATDAN from others
    - Filters out TV/screens
    - Scene analysis with AI vision
    - Visual memory integration with AlfredBrain
    - Remembers people: BATDAN, family, friends
    """

    def __init__(self, brain=None, camera_index: int = 0):
        """
        Initialize Alfred's eyes

        Args:
            brain: AlfredBrain instance for visual memory
            camera_index: Camera device index (0 = default webcam)
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.camera_index = camera_index
        self.camera = None
        self.active = False

        # Face recognition data
        self.known_faces = {}  # name -> face encoding
        self.face_memory_path = None

        # Vision settings
        self.confidence_threshold = 0.6  # For face recognition
        self.min_face_size = (50, 50)  # Minimum face size to detect

        # Performance settings
        self.frame_skip = 2  # Process every Nth frame
        self.frame_counter = 0

        # Check capabilities
        self._check_capabilities()

        # Initialize camera
        self._initialize_camera()

        # Load known faces
        self._load_known_faces()

    def _check_capabilities(self):
        """Check what vision capabilities are available"""
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.warning("⚠️ face_recognition not available. Install with: pip install face-recognition")

        if not DEEPFACE_AVAILABLE:
            self.logger.warning("⚠️ DeepFace not available. Install with: pip install deepface")

        try:
            import cv2
            self.logger.info("✅ OpenCV available for computer vision")
        except ImportError:
            self.logger.error("❌ OpenCV not available. Install with: pip install opencv-python")

    def _initialize_camera(self):
        """Initialize the webcam"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)

            if not self.camera.isOpened():
                self.logger.error("❌ Failed to open camera")
                self.camera = None
                return

            # Set camera properties for better quality
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            self.logger.info(f"✅ Alfred's eyes initialized (camera {self.camera_index})")
            self.active = True

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize camera: {e}")
            self.camera = None

    def _load_known_faces(self):
        """Load known faces from storage"""
        if not FACE_RECOGNITION_AVAILABLE:
            return

        try:
            # Set face memory path
            if self.brain:
                from core.path_manager import PathManager
                face_dir = Path(PathManager.DATA_DIR) / "faces"
                face_dir.mkdir(exist_ok=True)
                self.face_memory_path = face_dir
            else:
                self.face_memory_path = Path("alfred_data/faces")
                self.face_memory_path.mkdir(parents=True, exist_ok=True)

            # Load BATDAN's face if it exists
            batdan_face_path = self.face_memory_path / "batdan.npy"
            if batdan_face_path.exists():
                batdan_encoding = np.load(batdan_face_path)
                self.known_faces['BATDAN'] = batdan_encoding
                self.logger.info("✅ BATDAN's face loaded from memory")

            # Load other known faces
            for face_file in self.face_memory_path.glob("*.npy"):
                if face_file.stem == 'batdan':
                    continue  # Already loaded

                name = face_file.stem.upper()
                encoding = np.load(face_file)
                self.known_faces[name] = encoding
                self.logger.info(f"✅ {name}'s face loaded from memory")

            if self.known_faces:
                self.logger.info(f"📸 Alfred recognizes {len(self.known_faces)} people")
            else:
                self.logger.info("👤 No known faces yet. Use /remember <name> to teach Alfred who you are")

        except Exception as e:
            self.logger.error(f"❌ Failed to load known faces: {e}")

    def capture_frame(self) -> Optional[np.ndarray]:
        """
        Capture a single frame from the camera

        Returns:
            Frame as numpy array (BGR format) or None
        """
        if not self.camera or not self.active:
            return None

        try:
            ret, frame = self.camera.read()
            if ret:
                return frame
            else:
                self.logger.error("❌ Failed to capture frame")
                return None

        except Exception as e:
            self.logger.error(f"❌ Frame capture error: {e}")
            return None

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[str, Tuple[int, int, int, int], float]]:
        """
        Detect and recognize faces in a frame

        Args:
            frame: Image frame (BGR format)

        Returns:
            List of (name, (top, right, bottom, left), confidence)
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return []

        try:
            # Convert BGR to RGB (face_recognition uses RGB)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect face locations
            face_locations = face_recognition.face_locations(rgb_frame, model='hog')

            if not face_locations:
                return []

            # Get face encodings
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            results = []

            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Check against known faces
                if self.known_faces:
                    # Calculate distances to all known faces
                    face_distances = face_recognition.face_distance(
                        list(self.known_faces.values()),
                        face_encoding
                    )

                    # Find best match
                    best_match_idx = np.argmin(face_distances)
                    best_distance = face_distances[best_match_idx]

                    # Convert distance to confidence (0-1)
                    confidence = 1.0 - best_distance

                    if confidence >= self.confidence_threshold:
                        name = list(self.known_faces.keys())[best_match_idx]
                    else:
                        name = "Unknown"
                        confidence = 0.0
                else:
                    name = "Unknown"
                    confidence = 0.0

                results.append((name, face_location, confidence))

            return results

        except Exception as e:
            self.logger.error(f"❌ Face detection error: {e}")
            return []

    def learn_face(self, name: str, frame: Optional[np.ndarray] = None) -> bool:
        """
        Learn a new face (teach Alfred who someone is)

        Args:
            name: Person's name (e.g., "BATDAN")
            frame: Optional frame. If None, captures from camera

        Returns:
            True if face learned successfully
        """
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.error("❌ Face recognition not available")
            return False

        try:
            # Capture frame if not provided
            if frame is None:
                frame = self.capture_frame()
                if frame is None:
                    self.logger.error("❌ Failed to capture frame")
                    return False

            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect faces
            face_locations = face_recognition.face_locations(rgb_frame)

            if not face_locations:
                self.logger.error("❌ No face detected in frame")
                return False

            if len(face_locations) > 1:
                self.logger.warning("⚠️ Multiple faces detected. Using the largest face.")
                # Find largest face (closest to camera)
                face_sizes = [(r - l) * (b - t) for t, r, b, l in face_locations]
                largest_idx = np.argmax(face_sizes)
                face_locations = [face_locations[largest_idx]]

            # Get face encoding
            face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]

            # Store in memory
            name_key = name.upper()
            self.known_faces[name_key] = face_encoding

            # Save to disk
            if self.face_memory_path:
                face_file = self.face_memory_path / f"{name.lower()}.npy"
                np.save(face_file, face_encoding)
                self.logger.info(f"💾 {name}'s face saved to {face_file}")

            # Store in AlfredBrain
            if self.brain:
                self.brain.store_knowledge(
                    category='people',
                    key=name_key,
                    value=f'Face learned on {datetime.now().isoformat()}',
                    importance=10,  # Max importance for people
                    confidence=1.0
                )

            self.logger.info(f"✅ Alfred now recognizes {name}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to learn face: {e}")
            return False

    def who_do_i_see(self) -> Dict[str, any]:
        """
        Analyze current view and identify people

        Returns:
            Dict with people seen and confidence levels
        """
        frame = self.capture_frame()
        if frame is None:
            return {'people': [], 'batdan_present': False}

        faces = self.detect_faces(frame)

        people_seen = []
        batdan_present = False

        for name, location, confidence in faces:
            people_seen.append({
                'name': name,
                'confidence': round(confidence, 3),
                'location': location
            })

            if name == 'BATDAN':
                batdan_present = True

        result = {
            'people': people_seen,
            'batdan_present': batdan_present,
            'total_faces': len(faces),
            'timestamp': datetime.now().isoformat()
        }

        # Store in brain if BATDAN is present
        if batdan_present and self.brain:
            self.brain.store_knowledge(
                category='presence',
                key='batdan_last_seen',
                value=datetime.now().isoformat(),
                importance=8
            )

        return result

    def is_batdan_present(self) -> bool:
        """
        Quick check: Is BATDAN in view?

        Returns:
            True if BATDAN's face is detected
        """
        result = self.who_do_i_see()
        return result['batdan_present']

    def analyze_scene_with_ai(self, prompt: str = "Describe what you see") -> Optional[str]:
        """
        Use AI vision to analyze the current scene
        Requires GPT-4 Vision, Claude Vision, or local vision model

        Args:
            prompt: Question/instruction for AI vision

        Returns:
            AI's description of the scene
        """
        # This would integrate with multimodel AI for vision
        # Placeholder for now - will integrate with GPT-4 Vision or Claude Vision
        frame = self.capture_frame()
        if frame is None:
            return None

        self.logger.info("🤖 AI vision analysis not yet implemented")
        self.logger.info("Will integrate with GPT-4 Vision or Claude 3 Vision")
        return "AI vision analysis coming soon"

    def watch_for_batdan(self, callback, check_interval: float = 2.0):
        """
        Continuously watch for BATDAN and call callback when seen

        Args:
            callback: Function to call when BATDAN is detected
            check_interval: Seconds between checks
        """
        self.logger.info("👁️ Watching for BATDAN...")

        try:
            while self.active:
                if self.is_batdan_present():
                    callback()

                time.sleep(check_interval)

        except KeyboardInterrupt:
            self.logger.info("🛑 Stopped watching")

    def get_frame_with_annotations(self) -> Optional[np.ndarray]:
        """
        Get current frame with face detection boxes drawn

        Returns:
            Annotated frame or None
        """
        frame = self.capture_frame()
        if frame is None:
            return None

        faces = self.detect_faces(frame)

        for name, (top, right, bottom, left), confidence in faces:
            # Draw box around face
            color = (0, 255, 0) if name == 'BATDAN' else (255, 0, 0)  # Green for BATDAN, blue for others
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Draw label
            label = f"{name} ({confidence:.2f})"
            cv2.putText(frame, label, (left, top - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame

    def show_view(self, window_name: str = "Alfred's View"):
        """
        Show what Alfred sees (with face detection)
        Press 'q' to quit, 'r' to remember face as BATDAN
        """
        if not self.camera:
            self.logger.error("❌ Camera not available")
            return

        self.logger.info(f"👁️ Showing Alfred's view (press 'q' to quit, 'r' to remember face)")

        try:
            while True:
                frame = self.get_frame_with_annotations()

                if frame is None:
                    break

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):
                    break
                elif key == ord('r'):
                    # Remember current face as BATDAN
                    if self.learn_face('BATDAN', frame):
                        self.logger.info("✅ Face learned as BATDAN")
                    else:
                        self.logger.error("❌ Failed to learn face")

        finally:
            cv2.destroyAllWindows()

    def close(self):
        """Close camera and cleanup"""
        if self.camera:
            self.camera.release()
            self.active = False
            self.logger.info("👁️ Alfred's eyes closed")

    def get_status(self) -> dict:
        """Get vision system status"""
        return {
            'active': self.active,
            'camera_available': self.camera is not None,
            'face_recognition': FACE_RECOGNITION_AVAILABLE,
            'deepface': DEEPFACE_AVAILABLE,
            'known_faces': list(self.known_faces.keys()),
            'batdan_known': 'BATDAN' in self.known_faces
        }

    def __del__(self):
        """Cleanup on deletion"""
        self.close()


# Convenience function
def create_alfred_eyes(brain=None, camera_index: int = 0) -> AlfredEyes:
    """Create Alfred's vision system"""
    return AlfredEyes(brain=brain, camera_index=camera_index)
