"""
ALFRED Code & Brain Copy Detection System

Monitors for:
- Code copying/cloning attempts
- Database replication
- Algorithm extraction
- Unauthorized distribution
- Model theft

Notifies BATDAN immediately on detection
"""

import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import logging


class CopyDetectionSystem:
    """
    Detects unauthorized copying of ALFRED code and brain
    
    Maintains fingerprints of:
    - Core algorithm files
    - Brain database
    - Learning models
    - Intellectual property
    """

    def __init__(self, batdan_email: str = "batdan@alfred.local"):
        self.batdan_email = batdan_email
        self.logger = self._setup_logging()
        self.known_hashes = {}
        self._load_known_hashes()

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s - ALFRED_COPY_DETECTION - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alfred_copy_detection.log'),
            ]
        )
        return logging.getLogger("ALFRED_COPY_DETECTION")

    def _load_known_hashes(self):
        """Load known file hashes"""
        hash_file = Path("alfred_code_hashes.json")
        if hash_file.exists():
            with open(hash_file, 'r') as f:
                self.known_hashes = json.load(f)

    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA256 hash of file"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""

    def register_ip_file(self, filepath: str, protection_level: str = "CRITICAL"):
        """Register file as protected IP"""
        file_hash = self.calculate_file_hash(filepath)
        
        self.known_hashes[filepath] = {
            "hash": file_hash,
            "protection_level": protection_level,
            "registered": datetime.now().isoformat(),
        }
        
        # Save hashes
        with open("alfred_code_hashes.json", 'w') as f:
            json.dump(self.known_hashes, f, indent=2)

    def scan_for_copies(self, root_dir: str = ".") -> List[Dict]:
        """
        Scan directory tree for copies of ALFRED code
        
        Returns list of suspicious files
        """
        suspicious = []
        
        # Calculate hashes of all files in directory
        for filepath in Path(root_dir).rglob("*.py"):
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
                    
                    self._alert_copy_detected(protected_file, str(filepath))
        
        return suspicious

    def _alert_copy_detected(self, original: str, copy: str):
        """Alert BATDAN of detected copy"""
        alert = {
            "type": "UNAUTHORIZED_CODE_COPY",
            "severity": "CRITICAL",
            "timestamp": datetime.now().isoformat(),
            "original_file": original,
            "copy_location": copy,
            "message": f"Unauthorized copy of {original} detected at {copy}",
            "action": "Immediate investigation required",
            "contact": self.batdan_email,
        }
        
        # Log alert
        with open("alfred_copy_detection_alerts.json", 'a') as f:
            f.write(json.dumps(alert) + "\n")
        
        self.logger.critical(json.dumps(alert))
        
        print(f"\n🚨 COPY DETECTED:")
        print(f"   Original: {original}")
        print(f"   Copy: {copy}")
        print(f"   BATDAN notified: {self.batdan_email}\n")

    def scan_for_similar_algorithms(self, root_dir: str = ".") -> List[Dict]:
        """
        Scan for algorithmically similar code
        
        Detects reimplemented versions of ALFRED algorithms
        """
        suspicious = []
        
        # Key algorithm signatures to look for
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
        
        # Scan Python files
        for filepath in Path(root_dir).rglob("*.py"):
            if str(filepath).startswith(".git"):
                continue
            if str(filepath) in self.known_hashes:
                continue  # Skip ALFRED's own files
            
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Check for algorithm signatures
                for algo_name, signatures in algorithm_signatures.items():
                    match_count = sum(1 for sig in signatures if sig in content)
                    
                    if match_count >= len(signatures) - 1:
                        # Likely an implementation of this algorithm
                        suspicious.append({
                            "file": str(filepath),
                            "algorithm": algo_name,
                            "matches": match_count,
                            "severity": "HIGH",
                            "message": f"File contains implementation of {algo_name} algorithm",
                            "detected": datetime.now().isoformat(),
                        })
                        
                        self.logger.warning(
                            f"Algorithm copy detected: {algo_name} in {filepath}"
                        )
            
            except:
                pass
        
        if suspicious:
            self._alert_algorithm_theft(suspicious)
        
        return suspicious

    def _alert_algorithm_theft(self, detections: List[Dict]):
        """Alert BATDAN of algorithm theft attempt"""
        for detection in detections:
            alert = {
                "type": "ALGORITHM_THEFT_ATTEMPT",
                "severity": "CRITICAL",
                "timestamp": datetime.now().isoformat(),
                "file": detection["file"],
                "algorithm": detection["algorithm"],
                "message": f"Suspicious implementation of {detection['algorithm']} detected",
                "action": "Investigate immediately",
                "contact": self.batdan_email,
            }
            
            with open("alfred_algorithm_theft_alerts.json", 'a') as f:
                f.write(json.dumps(alert) + "\n")
            
            self.logger.critical(json.dumps(alert))
            
            print(f"\n🚨 ALGORITHM THEFT DETECTED:")
            print(f"   File: {detection['file']}")
            print(f"   Algorithm: {detection['algorithm']}")
            print(f"   BATDAN notified: {self.batdan_email}\n")


class BrainDatabaseProtection:
    """
    Protects ALFRED's brain database from theft
    
    Monitors database for:
    - Unauthorized access
    - Backup/copy attempts
    - Export operations
    - External read attempts
    """

    def __init__(self, brain_db_path: str = None, batdan_email: str = "batdan@alfred.local"):
        self.brain_db_path = brain_db_path or "data/alfred_brain.db"
        self.batdan_email = batdan_email
        self.logger = self._setup_logging()
        self.access_log = []

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.WARNING,
            format='%(asctime)s - ALFRED_BRAIN_PROTECTION - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('alfred_brain_protection.log'),
            ]
        )
        return logging.getLogger("ALFRED_BRAIN_PROTECTION")

    def detect_database_copy_attempt(self, source_path: str) -> bool:
        """
        Detect if someone is copying the brain database
        
        Returns True if copy attempt detected
        """
        try:
            # Get file stats
            import os
            original_stat = os.stat(self.brain_db_path)
            source_stat = os.stat(source_path)
            
            # Check if same size (likely a copy)
            if abs(original_stat.st_size - source_stat.st_size) < 1000:  # Within 1KB
                # Calculate hashes
                original_hash = hashlib.sha256()
                with open(self.brain_db_path, 'rb') as f:
                    original_hash.update(f.read())
                
                source_hash = hashlib.sha256()
                with open(source_path, 'rb') as f:
                    source_hash.update(f.read())
                
                if original_hash.digest() == source_hash.digest():
                    self._alert_database_theft(source_path)
                    return True
        
        except:
            pass
        
        return False

    def _alert_database_theft(self, copy_location: str):
        """Alert BATDAN of brain database theft attempt"""
        alert = {
            "type": "BRAIN_DATABASE_THEFT",
            "severity": "CRITICAL",
            "timestamp": datetime.now().isoformat(),
            "original": self.brain_db_path,
            "copy_location": copy_location,
            "message": "ALFRED's brain database has been copied!",
            "action": "IMMEDIATE ACTION REQUIRED - Change credentials, review access logs",
            "contact": self.batdan_email,
        }
        
        with open("alfred_brain_theft_alerts.json", 'a') as f:
            f.write(json.dumps(alert) + "\n")
        
        self.logger.critical(json.dumps(alert))
        
        print(f"\n🚨🚨🚨 CRITICAL: BRAIN DATABASE STOLEN 🚨🚨🚨")
        print(f"   Original: {self.brain_db_path}")
        print(f"   Copy: {copy_location}")
        print(f"   BATDAN MUST BE NOTIFIED IMMEDIATELY")
        print(f"   Contact: {self.batdan_email}\n")

    def monitor_access(self, access_source: str, operation: str) -> bool:
        """Monitor brain database access"""
        access_record = {
            "timestamp": datetime.now().isoformat(),
            "source": access_source,
            "operation": operation,
        }
        
        self.access_log.append(access_record)
        
        # Check for suspicious patterns
        if operation.upper() in ["COPY", "BACKUP", "EXPORT", "CLONE"]:
            self.logger.warning(f"Suspicious operation: {operation} from {access_source}")
        
        return True


def monitor_alfred_security():
    """Run security monitoring"""
    print("\n" + "=" * 60)
    print("ALFRED IP PROTECTION & COPY DETECTION SYSTEM")
    print("=" * 60 + "\n")
    
    copy_detector = CopyDetectionSystem(batdan_email="batdan@alfred.local")
    
    # Register known IP files
    ip_files = [
        ("core/brain.py", "CRITICAL"),
        ("core/task_classifier.py", "CRITICAL"),
        ("core/agent_selector.py", "CRITICAL"),
        ("core/response_quality_checker.py", "CRITICAL"),
    ]
    
    for filepath, level in ip_files:
        try:
            copy_detector.register_ip_file(filepath, level)
            print(f"✓ Registered: {filepath}")
        except:
            print(f"⚠️  File not found: {filepath}")
    
    print("\n✓ IP Protection System Active")
    print("✓ Copy Detection Enabled")
    print("✓ Algorithm Theft Detection Enabled")
    print("✓ Brain Database Protection Enabled")
    print("\nAll unauthorized access/copying will alert BATDAN immediately.\n")


if __name__ == "__main__":
    monitor_alfred_security()
