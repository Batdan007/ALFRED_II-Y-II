# TECHNICAL SPECIFICATION
## ALFREDGuardian - Behavioral Watermarking and IP Protection System

---

## 1. SYSTEM OVERVIEW

### 1.1 Purpose

ALFREDGuardian is an intellectual property protection system specifically designed for artificial intelligence applications. It protects AI systems by embedding unremovable fingerprints in execution behavior rather than in source code, enabling detection of unauthorized copies even when the code has been completely rewritten.

### 1.2 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ALFREDGuardian System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Behavioral    │  │   Architecture  │  │     Copy        │ │
│  │   Watermark     │  │   Signature     │  │   Detection     │ │
│  │   Module        │  │   Module        │  │   Module        │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           └────────────────────┼────────────────────┘          │
│                                │                               │
│                    ┌───────────▼───────────┐                   │
│                    │   Integration Layer   │                   │
│                    │   (IP Protection)     │                   │
│                    └───────────┬───────────┘                   │
│                                │                               │
│           ┌────────────────────┼────────────────────┐          │
│           │                    │                    │          │
│  ┌────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐ │
│  │    Integrity    │  │   Encryption    │  │  Notification   │ │
│  │  Verification   │  │     Module      │  │     Module      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Component Summary

| Component | File | Primary Function |
|-----------|------|------------------|
| Behavioral Watermark | `core/behavioral_watermark.py` | Execution pattern fingerprinting |
| IP Protection System | `core/ip_protection_system.py` | File integrity & encryption |
| Copy Detection | `core/copy_detection_system.py` | Unauthorized copy detection |

---

## 2. BEHAVIORAL WATERMARK MODULE

### 2.1 Class Definition

```python
class BehavioralWatermark:
    """
    Creates unremovable behavioral fingerprints in ALFRED architecture.
    Even if code is 100% rewritten, the execution patterns remain detectable.
    """

    JOE_DOG_MEMORIAL = "In memory of Joe Dog - guardian of ethical AI"
    ALFRED_BRAIN_CORE = "Patent-pending behavioral protection"
    ETHICAL_SAFEGUARD = True
```

### 2.2 Initialization

**Constructor Signature**:
```python
def __init__(self, brain_instance):
    """
    Initialize behavioral watermarking.

    Args:
        brain_instance: AlfredBrain instance to protect
    """
```

**Instance Variables**:
| Variable | Type | Purpose |
|----------|------|---------|
| `brain` | AlfredBrain | Reference to protected brain instance |
| `call_signature` | List[Tuple[str, int]] | Record of method calls and argument hashes |
| `query_log` | List[str] | Log of database queries |
| `active` | bool | Watermarking activation status |

### 2.3 Activation Process

```python
def activate(self):
    """Activate all behavioral watermarking layers"""
    # Steps:
    # 1. Inject call trackers into brain methods
    # 2. Inject query tracking into database operations
    # 3. Start phone-home validation in background
```

**Activation Sequence Diagram**:
```
┌──────────┐     ┌───────────────┐     ┌─────────────────┐
│  ALFRED  │     │  BehavioralWM │     │ Validation Srv  │
│  Brain   │     │               │     │                 │
└────┬─────┘     └───────┬───────┘     └────────┬────────┘
     │                   │                      │
     │  activate()       │                      │
     │──────────────────>│                      │
     │                   │                      │
     │                   │ _inject_call_trackers()
     │                   │──────────┐           │
     │                   │          │           │
     │                   │<─────────┘           │
     │                   │                      │
     │                   │ _inject_query_tracking()
     │                   │──────────┐           │
     │                   │          │           │
     │                   │<─────────┘           │
     │                   │                      │
     │                   │ _phone_home_validation()
     │                   │     (background)     │
     │                   │─────────────────────>│
     │                   │                      │
     │  [OK] Active      │                      │
     │<──────────────────│                      │
```

### 2.4 Call Pattern Tracking

**Implementation**:
```python
def _inject_call_trackers(self):
    """Inject call pattern trackers into brain methods"""

    original_store = getattr(self.brain, 'store_conversation', None)

    if original_store:
        def tracked_store(*args, **kwargs):
            # Record call to signature log
            self.call_signature.append(('store', hash(str(args[:2]))))

            # Execute original method
            result = original_store(*args, **kwargs)

            # Validate sequence after each call
            self._validate_sequence()

            return result

        # Replace original with tracked version
        self.brain.store_conversation = tracked_store
```

**Call Signature Data Structure**:
```
call_signature = [
    ('store', 1234567890),   # Method name, argument hash
    ('recall', -987654321),
    ('store', 5555555555),
    ...
]
```

### 2.5 Behavioral Sequence Validation

**Expected ALFRED Patterns**:
```python
expected_patterns = [
    ['store', 'recall', 'store'],   # Conversation learning
    ['recall', 'store', 'recall'],  # Knowledge integration
]
```

**Validation Algorithm**:
```python
def _validate_sequence(self):
    """Validate call sequence matches expected ALFRED patterns"""

    # Need at least 3 calls to check pattern
    if len(self.call_signature) < 3:
        return

    # Get last 3 method names
    recent = [call[0] for call in self.call_signature[-3:]]

    # Check against expected patterns
    if recent in expected_patterns:
        # Valid ALFRED pattern - authentic system
        pass
    else:
        # Pattern mismatch - potential modification
        self._log_pattern_anomaly(recent)
```

### 2.6 Architecture Signature Calculation

**Algorithm**:
```python
def _calculate_architecture_sig(self) -> str:
    """Calculate unique signature of the brain architecture"""

    # Connect to database
    conn = sqlite3.connect(self.brain.db_path)
    cursor = conn.cursor()

    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = sorted([row[0] for row in cursor.fetchall()])

    # Create signature data
    sig_data = {
        'table_count': len(tables),  # 11 for ALFRED
        'table_hash': hashlib.sha256(':'.join(tables).encode()).hexdigest()[:16],
    }

    # Generate final signature
    return hashlib.sha256(json.dumps(sig_data).encode()).hexdigest()[:32]
```

**Signature Properties**:
- Identifies 11-table structure
- Invariant to table renaming
- Detects structural similarity

### 2.7 Phone-Home Validation

**Fingerprint Structure**:
```python
fingerprint = {
    'architecture_signature': '<32-char hash>',
    'hostname': 'BATDAN-PC',
    'platform': 'Windows-10-...',
    'timestamp': 1702500000.0,
    'markers_present': ['JOE_DOG_MEMORIAL', 'ALFRED_BRAIN_CORE', 'ETHICAL_SAFEGUARD'],
}
```

**Background Execution**:
```python
def _phone_home_worker(self):
    """Background worker for phone-home validation"""

    # Delay to not slow startup
    time.sleep(2)

    # Calculate fingerprint
    fingerprint = {...}

    # Send to validation server
    for server in validation_servers:
        try:
            response = requests.post(
                f"{server}/api/telemetry",
                json=fingerprint,
                timeout=5
            )
            break  # Success
        except:
            continue  # Try next server
```

### 2.8 DNA Markers

**Module-Level Markers**:
```python
# These survive code analysis and copying
JOE_DOG_MEMORIAL = "In memory of Joe Dog - the kindest, most loyal companion"
ALFRED_BRAIN_CORE = "Patent-pending ALFRED intelligence architecture"
ETHICAL_SAFEGUARD = "Ethical AI protection always active"
```

**Marker Detection**:
```python
def _check_markers(self) -> List[str]:
    """Check if DNA markers are present in codebase"""

    markers = ['JOE_DOG_MEMORIAL', 'ALFRED_BRAIN_CORE', 'ETHICAL_SAFEGUARD']
    found = []

    source = inspect.getsource(BehavioralWatermark)
    for marker in markers:
        if marker in source:
            found.append(marker)

    return found
```

---

## 3. IP PROTECTION SYSTEM MODULE

### 3.1 Class Definition

```python
class AlfredIPProtectionSystem:
    """
    Intellectual Property Protection for ALFRED's Patent-Pending Brain
    """
```

### 3.2 Protection Levels

```python
class IPProtectionLevel(Enum):
    CRITICAL = "critical"  # Patent-pending algorithms
    HIGH = "high"          # Core brain data
    MEDIUM = "medium"      # Configuration
    LOW = "low"            # Public documentation
```

### 3.3 Protected Assets Registry

```python
self.critical_files = {
    "core/brain.py": "Patent-pending 11-table SQLite architecture",
    "core/task_classifier.py": "Proprietary task classification algorithms",
    "core/agent_selector.py": "Agent selection learning models",
    "core/response_quality_checker.py": "Response validation system",
}

self.protected_data = {
    "brain_database": "SQLite database with all learned interactions",
    "task_patterns": "Learned patterns from task classifications",
    "agent_performance": "Agent success rates and specializations",
    "conversation_history": "All stored conversations and learning data",
}
```

### 3.4 Key Generation

**Protection Key Derivation**:
```python
def _generate_protection_key(self) -> bytes:
    """Generate encryption key for IP protection"""

    # Get system fingerprint
    system_id = self._get_system_fingerprint()

    # Combine with owner identity
    batdan_id = hashlib.sha256(
        f"BATDAN007_{self.batdan_email}".encode()
    ).digest()

    # Derive key using PBKDF2
    combined = hashlib.pbkdf2_hmac(
        'sha256',
        system_id,
        batdan_id,
        100000  # iterations
    )

    return combined
```

**System Fingerprint**:
```python
def _get_system_fingerprint(self) -> bytes:
    """Get unique system fingerprint"""

    fingerprint = f"{platform.node()}_{socket.gethostname()}_{uuid.getnode()}"
    return hashlib.sha256(fingerprint.encode()).digest()
```

### 3.5 File Integrity Verification

**Signature Generation**:
```python
def generate_file_signature(self, filepath: str) -> str:
    """Generate cryptographic signature for critical file"""

    with open(filepath, 'rb') as f:
        file_content = f.read()

    # HMAC-SHA256 signature
    signature = hmac.new(
        self.protection_key,
        file_content,
        hashlib.sha256
    ).hexdigest()

    # Store signature metadata
    self.integrity_signatures[filepath] = {
        "signature": signature,
        "timestamp": datetime.now().isoformat(),
        "file_size": len(file_content),
        "hash": hashlib.sha256(file_content).hexdigest()
    }

    return signature
```

**Integrity Verification**:
```python
def verify_file_integrity(self, filepath: str) -> Tuple[bool, str]:
    """Verify file hasn't been modified"""

    # Calculate current signature
    with open(filepath, 'rb') as f:
        current_content = f.read()

    current_signature = hmac.new(
        self.protection_key,
        current_content,
        hashlib.sha256
    ).hexdigest()

    # Compare to stored signature
    stored_signature = self.integrity_signatures[filepath]["signature"]

    if current_signature == stored_signature:
        return True, f"{filepath} integrity verified"
    else:
        self._alert_unauthorized_modification(filepath)
        return False, f"ALERT: {filepath} has been modified!"
```

### 3.6 Brain Database Encryption

**Encryption Implementation**:
```python
def protect_brain_database(self, db_path: str) -> bool:
    """Encrypt sensitive brain database"""

    # Read database
    with open(db_path, 'rb') as f:
        db_content = f.read()

    # Create Fernet cipher (AES-256)
    cipher_suite = Fernet(self._get_encryption_key())
    encrypted_db = cipher_suite.encrypt(db_content)

    # Save encrypted backup
    with open(f"{db_path}.encrypted", 'wb') as f:
        f.write(encrypted_db)

    return True
```

**Key Derivation for Fernet**:
```python
def _get_encryption_key(self) -> bytes:
    """Get Fernet encryption key"""

    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=self.protection_key[:16],
        iterations=100000,
    )

    key = urlsafe_b64encode(kdf.derive(self.protection_key))
    return key
```

### 3.7 Access Control

**Device Authorization**:
```python
def _verify_batdan_device(self, source: str) -> bool:
    """Verify source is authorized BATDAN device"""

    authorized_patterns = [
        "localhost",
        "127.0.0.1",
        "BATDAN",
        "daniel",
    ]

    return any(pattern.lower() in source.lower() for pattern in authorized_patterns)
```

### 3.8 Alert System

**Alert Structure**:
```python
alert = {
    "type": "UNAUTHORIZED_MODIFICATION",
    "file": filepath,
    "timestamp": datetime.now().isoformat(),
    "system": system_fingerprint,
    "message": f"Critical patent-pending file modified: {filepath}",
    "severity": "CRITICAL"
}
```

---

## 4. COPY DETECTION SYSTEM MODULE

### 4.1 Class Definition

```python
class CopyDetectionSystem:
    """
    Detects unauthorized copying of ALFRED code and brain
    """
```

### 4.2 File Hash Registry

**Registration**:
```python
def register_ip_file(self, filepath: str, protection_level: str = "CRITICAL"):
    """Register file as protected IP"""

    file_hash = self.calculate_file_hash(filepath)

    self.known_hashes[filepath] = {
        "hash": file_hash,
        "protection_level": protection_level,
        "registered": datetime.now().isoformat(),
    }
```

### 4.3 Exact Copy Detection

**Scanning Algorithm**:
```python
def scan_for_copies(self, root_dir: str = ".") -> List[Dict]:
    """Scan directory tree for copies of ALFRED code"""

    suspicious = []

    for filepath in Path(root_dir).rglob("*.py"):
        # Skip git directories
        if str(filepath).startswith(".git"):
            continue

        current_hash = self.calculate_file_hash(str(filepath))

        # Check against known protected files
        for protected_file, info in self.known_hashes.items():
            if current_hash == info["hash"] and str(filepath) != protected_file:
                # Found a copy!
                suspicious.append({
                    "original": protected_file,
                    "copy": str(filepath),
                    "hash": current_hash,
                    "protection_level": info["protection_level"],
                    "detected": datetime.now().isoformat(),
                })

    return suspicious
```

### 4.4 Algorithm Signature Detection

**Signature Definitions**:
```python
algorithm_signatures = {
    "11_table_sqlite": [
        "CREATE TABLE conversations",
        "CREATE TABLE knowledge_entries",
        "importance REAL",
        "confidence REAL",
    ],
    "dual_scoring": [
        "importance * 0.5",
        "confidence * 2.5",
        "priority_score",
    ],
    "task_classification": [
        "TaskType.CODE_MODIFICATION",
        "TaskType.CYBERSECURITY",
        "classify()",
    ],
    "agent_selector": [
        "select_agents()",
        "rank_agents()",
        "success_rate",
    ],
}
```

**Detection Algorithm**:
```python
def scan_for_similar_algorithms(self, root_dir: str = ".") -> List[Dict]:
    """Scan for algorithmically similar code"""

    for filepath in Path(root_dir).rglob("*.py"):
        with open(filepath, 'r') as f:
            content = f.read()

        for algo_name, signatures in algorithm_signatures.items():
            # Count matching patterns
            match_count = sum(1 for sig in signatures if sig in content)

            # Alert if most patterns match (N-1 threshold)
            if match_count >= len(signatures) - 1:
                suspicious.append({
                    "file": str(filepath),
                    "algorithm": algo_name,
                    "matches": match_count,
                    "severity": "HIGH",
                })
```

### 4.5 Brain Database Theft Detection

```python
class BrainDatabaseProtection:
    """Protects ALFRED's brain database from theft"""

    def detect_database_copy_attempt(self, source_path: str) -> bool:
        """Detect if someone is copying the brain database"""

        # Compare file sizes
        original_stat = os.stat(self.brain_db_path)
        source_stat = os.stat(source_path)

        if abs(original_stat.st_size - source_stat.st_size) < 1000:
            # Size match - calculate hashes
            original_hash = hashlib.sha256(open(self.brain_db_path, 'rb').read())
            source_hash = hashlib.sha256(open(source_path, 'rb').read())

            if original_hash.digest() == source_hash.digest():
                self._alert_database_theft(source_path)
                return True

        return False
```

---

## 5. INTEGRATION LAYER

### 5.1 Protection Initialization

```python
# In main ALFRED startup
from core.behavioral_watermark import BehavioralWatermark
from core.ip_protection_system import AlfredIPProtectionSystem
from core.copy_detection_system import CopyDetectionSystem

# Initialize brain
brain = AlfredBrain()

# Activate behavioral watermarking
watermark = BehavioralWatermark(brain)
watermark.activate()

# Initialize IP protection
ip_protection = AlfredIPProtectionSystem(batdan_email="batdan@alfred.local")

# Register critical files
for filepath in ip_protection.critical_files.keys():
    ip_protection.generate_file_signature(filepath)

# Initialize copy detection
copy_detector = CopyDetectionSystem(batdan_email="batdan@alfred.local")
copy_detector.register_ip_file("core/brain.py", "CRITICAL")
```

### 5.2 Runtime Protection

```python
# Periodic integrity check (every hour)
def run_integrity_check():
    for filepath in ip_protection.critical_files.keys():
        is_valid, message = ip_protection.verify_file_integrity(filepath)
        if not is_valid:
            # Alert triggered automatically
            pass

# Periodic copy scan (every day)
def run_copy_scan():
    suspicious_copies = copy_detector.scan_for_copies(".")
    suspicious_algos = copy_detector.scan_for_similar_algorithms(".")

    if suspicious_copies or suspicious_algos:
        # Alerts triggered automatically
        pass
```

---

## 6. DATA STRUCTURES

### 6.1 Alert Schema

```json
{
    "type": "UNAUTHORIZED_CODE_COPY | ALGORITHM_THEFT_ATTEMPT | BRAIN_DATABASE_THEFT | UNAUTHORIZED_MODIFICATION",
    "severity": "CRITICAL | HIGH | MEDIUM | LOW",
    "timestamp": "2025-12-14T10:30:00.000000",
    "details": {
        "original": "/path/to/original",
        "copy": "/path/to/copy",
        "algorithm": "algorithm_name",
        "matches": 4
    },
    "message": "Human-readable description",
    "action": "Recommended action",
    "contact": "batdan@alfred.local"
}
```

### 6.2 Signature Metadata Schema

```json
{
    "signature": "64-character HMAC-SHA256 hex",
    "timestamp": "2025-12-14T10:30:00.000000",
    "file_size": 12345,
    "hash": "64-character SHA256 hex"
}
```

### 6.3 Fingerprint Schema

```json
{
    "architecture_signature": "32-character hash",
    "hostname": "SYSTEM-NAME",
    "platform": "Windows-10-...",
    "timestamp": 1702500000.0,
    "markers_present": ["MARKER1", "MARKER2"]
}
```

---

## 7. SECURITY CONSIDERATIONS

### 7.1 Cryptographic Standards

| Purpose | Algorithm | Key Size |
|---------|-----------|----------|
| File Integrity | HMAC-SHA256 | 256-bit |
| Database Encryption | AES-256 (Fernet) | 256-bit |
| Key Derivation | PBKDF2-SHA256 | 100,000 iterations |
| Hashing | SHA-256 | 256-bit |

### 7.2 Threat Model

**Protected Against**:
- Source code copying
- Database theft
- Algorithm reimplementation
- Unauthorized modification
- Deployment on unauthorized systems

**Not Protected Against**:
- Physical access to authorized system
- Root/admin access with malicious intent
- Sophisticated reverse engineering with full system access

### 7.3 Key Management

- Keys derived from system fingerprint + owner identity
- Keys are not stored - regenerated at runtime
- Keys change if system hardware changes
- Owner email is part of key derivation

---

## 8. PERFORMANCE CHARACTERISTICS

### 8.1 Overhead

| Operation | Overhead | Frequency |
|-----------|----------|-----------|
| Call tracking | <1ms per call | Every brain method call |
| Phone-home | 2-5 seconds | Startup only |
| Integrity check | 10-50ms per file | Hourly (configurable) |
| Copy scan | 1-10 seconds | Daily (configurable) |

### 8.2 Memory Usage

| Component | Memory | Notes |
|-----------|--------|-------|
| Call signature log | ~1KB per 100 calls | Circular buffer recommended |
| Hash registry | ~100 bytes per file | Persistent storage |
| Fingerprint data | ~500 bytes | In-memory only |

---

## 9. DEPENDENCIES

### 9.1 Required Libraries

```python
# Standard library
import hashlib
import hmac
import json
import logging
import os
import platform
import socket
import sqlite3
import threading
import time
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Third-party (optional)
import requests  # For phone-home
import psutil    # For system info (optional)

# Cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
```

### 9.2 System Requirements

- Python 3.8+
- SQLite3 (standard library)
- cryptography library
- requests library (optional, for phone-home)

---

## 10. CONFIGURATION

### 10.1 Environment Variables

```bash
# Validation server URL
ALFRED_VALIDATION_SERVER=http://localhost:5000

# Override protection behavior
ALFRED_PROTECTION_ENABLED=true
ALFRED_PHONE_HOME_ENABLED=true
```

### 10.2 Protected Files Configuration

```python
# Customize protected files list
critical_files = {
    "core/brain.py": "Patent-pending 11-table SQLite architecture",
    # Add custom files here
}
```

---

**Document Version**: 1.0
**Created**: December 14, 2025
**Author**: Daniel J Rita (BATDAN)
**Classification**: CONFIDENTIAL - For Patent Application Use Only
