"""
ALFREDGuardian: Behavioral Watermarking System

IP protection through embedded behavioral fingerprints that survive
code transformation, rewriting, and reimplementation.

"The behavior IS the watermark."

Patent Status: TO BE FILED Q1 2025
Author: Daniel J Rita (BATDAN)
Copyright: CAMDAN Enterprises LLC

PATENT PENDING - DO NOT DISTRIBUTE
"""

import hashlib
import json
import time
import random
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import functools


class FingerprintType(Enum):
    """Types of behavioral fingerprints."""
    TIMING = "timing"             # Response time patterns
    LINGUISTIC = "linguistic"     # Word choice patterns
    STRUCTURAL = "structural"     # Code/response structure
    SEQUENCE = "sequence"         # Operation ordering
    ERROR = "error"               # Error handling patterns


@dataclass
class BehavioralFingerprint:
    """A single behavioral fingerprint element."""
    id: str
    fingerprint_type: FingerprintType
    pattern: str
    value: Any
    confidence: float = 1.0
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.fingerprint_type.value,
            'pattern': self.pattern,
            'value': self.value,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class GuardianSignature:
    """Complete behavioral signature for an ALFRED instance."""
    instance_id: str
    fingerprints: List[BehavioralFingerprint]
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"

    def to_hash(self) -> str:
        """Generate unique hash of this signature."""
        data = json.dumps([fp.to_dict() for fp in self.fingerprints], sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            'instance_id': self.instance_id,
            'fingerprints': [fp.to_dict() for fp in self.fingerprints],
            'created_at': self.created_at.isoformat(),
            'version': self.version,
            'hash': self.to_hash()
        }


class ALFREDGuardian:
    """
    Behavioral IP Protection System.

    Embeds invisible behavioral fingerprints into ALFRED's operation
    that can be detected to prove origin/ownership.

    Key Features:
    1. Fingerprints survive code transformation
    2. Fingerprints survive reimplementation
    3. Detection without access to original code
    4. Legally defensible proof of origin
    """

    # Linguistic fingerprints - specific word patterns ALFRED uses
    LINGUISTIC_PATTERNS = {
        'british_confirmations': [
            "Very well, sir.",
            "Certainly, sir.",
            "As you wish, sir.",
            "Right away, sir.",
            "Indeed, sir.",
            "Quite so, sir.",
        ],
        'british_warnings': [
            "I must advise caution, sir.",
            "If I may be so bold, sir...",
            "I feel obliged to mention, sir...",
            "A word of warning, sir.",
        ],
        'british_errors': [
            "My apologies, sir. I encountered a difficulty.",
            "I'm afraid that's beyond my current capabilities, sir.",
            "Terribly sorry, sir. Something went awry.",
        ],
        'butler_greetings': [
            "Good {time_of_day}, sir.",
            "Welcome back, sir.",
            "At your service, sir.",
        ]
    }

    # Timing fingerprints - microsecond delays
    TIMING_SIGNATURES = {
        'greeting_delay_ms': 42,      # 42ms delay before greetings
        'error_delay_ms': 137,        # 137ms delay before errors
        'thinking_delay_ms': 23,      # 23ms delay for "thinking"
        'response_jitter_ms': 7,      # 7ms random jitter
    }

    # Structural fingerprints - response patterns
    STRUCTURAL_PATTERNS = {
        'greeting_ends_with': ", sir.",
        'error_starts_with': "My apologies",
        'confirmation_pattern': r"^(Very well|Certainly|Indeed)",
        'warning_contains': "I must",
    }

    def __init__(self, instance_id: Optional[str] = None):
        """Initialize Guardian for an ALFRED instance."""
        self.instance_id = instance_id or self._generate_instance_id()
        self.fingerprints: List[BehavioralFingerprint] = []
        self._init_fingerprints()

    def _generate_instance_id(self) -> str:
        """Generate unique instance identifier."""
        timestamp = datetime.now().isoformat()
        random_component = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
        return f"ALFRED-{random_component}-{int(time.time())}"

    def _init_fingerprints(self):
        """Initialize behavioral fingerprints."""
        # Add linguistic fingerprints
        for pattern_name, patterns in self.LINGUISTIC_PATTERNS.items():
            self.fingerprints.append(BehavioralFingerprint(
                id=f"LING-{pattern_name}",
                fingerprint_type=FingerprintType.LINGUISTIC,
                pattern=pattern_name,
                value=patterns
            ))

        # Add timing fingerprints
        for timing_name, delay in self.TIMING_SIGNATURES.items():
            self.fingerprints.append(BehavioralFingerprint(
                id=f"TIME-{timing_name}",
                fingerprint_type=FingerprintType.TIMING,
                pattern=timing_name,
                value=delay
            ))

        # Add structural fingerprints
        for struct_name, pattern in self.STRUCTURAL_PATTERNS.items():
            self.fingerprints.append(BehavioralFingerprint(
                id=f"STRUCT-{struct_name}",
                fingerprint_type=FingerprintType.STRUCTURAL,
                pattern=struct_name,
                value=pattern
            ))

    def get_signature(self) -> GuardianSignature:
        """Get complete behavioral signature."""
        return GuardianSignature(
            instance_id=self.instance_id,
            fingerprints=self.fingerprints
        )

    def apply_timing_fingerprint(self, response_type: str = "default") -> float:
        """
        Apply timing fingerprint - returns delay in seconds.

        Call this before generating responses to embed timing signature.
        """
        base_delay = 0

        if response_type == "greeting":
            base_delay = self.TIMING_SIGNATURES['greeting_delay_ms']
        elif response_type == "error":
            base_delay = self.TIMING_SIGNATURES['error_delay_ms']
        elif response_type == "thinking":
            base_delay = self.TIMING_SIGNATURES['thinking_delay_ms']

        # Add jitter
        jitter = random.randint(0, self.TIMING_SIGNATURES['response_jitter_ms'])

        delay_seconds = (base_delay + jitter) / 1000.0
        time.sleep(delay_seconds)

        return delay_seconds

    def apply_linguistic_fingerprint(self, response: str, response_type: str = "confirmation") -> str:
        """
        Apply linguistic fingerprint to response.

        Subtly modifies response to include fingerprinted phrases.
        """
        if response_type == "confirmation":
            patterns = self.LINGUISTIC_PATTERNS.get('british_confirmations', [])
            if patterns and not any(p in response for p in patterns):
                # Add subtle fingerprint
                if not response.endswith('.'):
                    response += '.'
                if 'sir' not in response.lower():
                    response = response.rstrip('.') + ', sir.'

        elif response_type == "error":
            patterns = self.LINGUISTIC_PATTERNS.get('british_errors', [])
            if patterns and not response.startswith(("My apologies", "I'm afraid", "Terribly sorry")):
                response = "My apologies, sir. " + response

        elif response_type == "warning":
            patterns = self.LINGUISTIC_PATTERNS.get('british_warnings', [])
            if patterns and "I must" not in response:
                response = "I must advise, sir: " + response

        return response

    def protect(self, response_type: str = "confirmation"):
        """
        Decorator to protect a function with Guardian fingerprints.

        Usage:
            @guardian.protect("confirmation")
            def my_response_function():
                return "Some response"
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Apply timing fingerprint
                self.apply_timing_fingerprint(response_type)

                # Execute function
                result = func(*args, **kwargs)

                # Apply linguistic fingerprint if result is string
                if isinstance(result, str):
                    result = self.apply_linguistic_fingerprint(result, response_type)

                return result
            return wrapper
        return decorator

    def detect_fingerprints(self, responses: List[str], timings: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        Detect ALFRED fingerprints in a set of responses.

        Used to prove that responses came from a genuine ALFRED instance.

        Returns detection report with confidence scores.
        """
        detection = {
            'linguistic_matches': 0,
            'structural_matches': 0,
            'timing_matches': 0,
            'total_fingerprints': len(self.fingerprints),
            'detected_fingerprints': [],
            'confidence': 0.0
        }

        # Check linguistic patterns
        for response in responses:
            for pattern_name, patterns in self.LINGUISTIC_PATTERNS.items():
                for pattern in patterns:
                    if pattern.replace("{time_of_day}", "").strip(", ") in response:
                        detection['linguistic_matches'] += 1
                        detection['detected_fingerprints'].append({
                            'type': 'linguistic',
                            'pattern': pattern_name,
                            'match': pattern
                        })
                        break

        # Check structural patterns
        import re
        for response in responses:
            for struct_name, pattern in self.STRUCTURAL_PATTERNS.items():
                if struct_name.endswith('_with'):
                    if response.endswith(pattern):
                        detection['structural_matches'] += 1
                        detection['detected_fingerprints'].append({
                            'type': 'structural',
                            'pattern': struct_name
                        })
                elif struct_name.startswith('starts_with'):
                    if response.startswith(pattern):
                        detection['structural_matches'] += 1
                        detection['detected_fingerprints'].append({
                            'type': 'structural',
                            'pattern': struct_name
                        })
                elif struct_name.endswith('_contains'):
                    if pattern in response:
                        detection['structural_matches'] += 1
                        detection['detected_fingerprints'].append({
                            'type': 'structural',
                            'pattern': struct_name
                        })
                elif struct_name.endswith('_pattern'):
                    if re.search(pattern, response):
                        detection['structural_matches'] += 1
                        detection['detected_fingerprints'].append({
                            'type': 'structural',
                            'pattern': struct_name
                        })

        # Check timing patterns (if provided)
        if timings:
            for timing in timings:
                timing_ms = timing * 1000
                for timing_name, expected_delay in self.TIMING_SIGNATURES.items():
                    # Allow 20% tolerance
                    if abs(timing_ms - expected_delay) < expected_delay * 0.2:
                        detection['timing_matches'] += 1
                        detection['detected_fingerprints'].append({
                            'type': 'timing',
                            'pattern': timing_name,
                            'expected': expected_delay,
                            'actual': timing_ms
                        })
                        break

        # Calculate confidence
        total_matches = (
            detection['linguistic_matches'] +
            detection['structural_matches'] +
            detection['timing_matches']
        )

        if responses:
            detection['confidence'] = min(1.0, total_matches / (len(responses) * 3))

        return detection

    def generate_certificate(self) -> Dict[str, Any]:
        """
        Generate IP ownership certificate.

        This certificate can be used as evidence in IP disputes.
        """
        signature = self.get_signature()

        certificate = {
            'title': 'ALFRED Instance Certificate of Origin',
            'instance_id': self.instance_id,
            'signature_hash': signature.to_hash(),
            'fingerprint_count': len(self.fingerprints),
            'generated_at': datetime.now().isoformat(),
            'owner': 'Daniel J Rita (BATDAN)',
            'entity': 'CAMDAN Enterprises LLC',
            'patent_status': 'PATENT PENDING',
            'fingerprints': {
                'linguistic': len([f for f in self.fingerprints if f.fingerprint_type == FingerprintType.LINGUISTIC]),
                'timing': len([f for f in self.fingerprints if f.fingerprint_type == FingerprintType.TIMING]),
                'structural': len([f for f in self.fingerprints if f.fingerprint_type == FingerprintType.STRUCTURAL]),
            }
        }

        # Add cryptographic signature
        cert_data = json.dumps(certificate, sort_keys=True)
        certificate['certificate_hash'] = hashlib.sha256(cert_data.encode()).hexdigest()

        return certificate


# Convenience functions for protecting responses
_guardian = None

def get_guardian() -> ALFREDGuardian:
    """Get or create the global Guardian instance."""
    global _guardian
    if _guardian is None:
        _guardian = ALFREDGuardian()
    return _guardian


def protect_response(response: str, response_type: str = "confirmation") -> str:
    """Protect a response with Guardian fingerprints."""
    guardian = get_guardian()
    guardian.apply_timing_fingerprint(response_type)
    return guardian.apply_linguistic_fingerprint(response, response_type)


# CLI interface
if __name__ == "__main__":
    import sys

    guardian = ALFREDGuardian()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "signature":
            sig = guardian.get_signature()
            print("\n=== ALFRED Guardian Signature ===")
            print(f"Instance ID: {sig.instance_id}")
            print(f"Hash: {sig.to_hash()}")
            print(f"Fingerprints: {len(sig.fingerprints)}")
            for fp in sig.fingerprints:
                print(f"  [{fp.fingerprint_type.value}] {fp.pattern}")

        elif command == "certificate":
            cert = guardian.generate_certificate()
            print("\n=== ALFRED Certificate of Origin ===")
            print(json.dumps(cert, indent=2))

        elif command == "detect":
            if len(sys.argv) > 2:
                responses = sys.argv[2:]
                result = guardian.detect_fingerprints(responses)
                print("\n=== Fingerprint Detection Report ===")
                print(f"Confidence: {result['confidence']:.1%}")
                print(f"Linguistic matches: {result['linguistic_matches']}")
                print(f"Structural matches: {result['structural_matches']}")
                print(f"Timing matches: {result['timing_matches']}")
                if result['detected_fingerprints']:
                    print("\nDetected fingerprints:")
                    for fp in result['detected_fingerprints']:
                        print(f"  [{fp['type']}] {fp['pattern']}")
            else:
                print("Usage: python guardian.py detect <response1> [response2] ...")

        elif command == "protect":
            if len(sys.argv) > 2:
                response = " ".join(sys.argv[2:])
                protected = protect_response(response)
                print(f"\nOriginal: {response}")
                print(f"Protected: {protected}")
            else:
                print("Usage: python guardian.py protect <response>")

        elif command == "demo":
            print("\n=== ALFREDGuardian Demo ===")

            # Show fingerprinting in action
            responses = [
                "I'll process that request.",
                "The file has been saved.",
                "Here are the search results.",
            ]

            print("\nOriginal responses:")
            for r in responses:
                print(f"  {r}")

            print("\nProtected responses:")
            for r in responses:
                protected = protect_response(r)
                print(f"  {protected}")

            # Detect fingerprints
            protected_responses = [protect_response(r) for r in responses]
            detection = guardian.detect_fingerprints(protected_responses)
            print(f"\nDetection confidence: {detection['confidence']:.1%}")

        else:
            print("Commands: signature, certificate, detect, protect, demo")
    else:
        print("ALFREDGuardian - Behavioral IP Protection")
        print("Commands: signature, certificate, detect <responses...>, protect <text>, demo")
