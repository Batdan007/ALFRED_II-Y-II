"""
CAMDAN Engineering System Client for Alfred

This module provides integration with CAMDAN (Comprehensive AI Management
for Design, Architecture & Engineering) - an AI-powered engineering and
building management system.

Author: Daniel J Rita (BATDAN)
License: Proprietary - Part of ALFRED-UBX
"""

import logging
import aiohttp
import asyncio
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
from enum import Enum


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Prevents cascading failures when CAMDAN is unavailable
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_duration: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.timeout_duration = timeout_duration
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func):
        """Decorator to wrap functions with circuit breaker"""
        async def wrapper(*args, **kwargs):
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                else:
                    raise Exception("Circuit breaker is OPEN - CAMDAN unavailable")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds >= self.timeout_duration

    def _on_success(self):
        """Reset on successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Increment failure count and open circuit if threshold reached"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


class CAMDANClient:
    """
    Production-ready client for CAMDAN engineering management system

    Features:
    - AI engineering knowledge base (NIST, EBSCO, building codes)
    - Cost estimation and budget management
    - Building code compliance checking
    - Building plan analysis with computer vision
    - Component maintenance predictions
    - Retry logic with exponential backoff
    - Connection pooling for performance
    - Circuit breaker for failure protection
    - Brain integration for caching
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        timeout: int = 30,
        max_retries: int = 3,
        brain=None
    ):
        """
        Initialize CAMDAN client with production features

        Args:
            base_url: CAMDAN API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
            brain: AlfredBrain instance for caching (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.base_url = base_url.rstrip('/')
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.brain = brain
        self.available = False

        # Connection pooling - reuse session across requests
        self._session = None
        self._session_lock = asyncio.Lock()

        # Circuit breaker to prevent cascading failures
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout_duration=60,
            expected_exception=aiohttp.ClientError
        )

        # Cache for building codes (reduces API calls)
        self._code_cache = {}
        self._cache_ttl = timedelta(hours=24)

        self.logger.info(f"CAMDAN client initialized (production mode): {self.base_url}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create persistent session for connection pooling

        Returns:
            Shared aiohttp ClientSession
        """
        async with self._session_lock:
            if self._session is None or self._session.closed:
                connector = aiohttp.TCPConnector(
                    limit=10,  # Max connections
                    limit_per_host=5,
                    ttl_dns_cache=300
                )
                self._session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=self.timeout
                )
        return self._session

    async def close(self):
        """Close persistent session (call on shutdown)"""
        if self._session and not self._session.closed:
            await self._session.close()
            self.logger.info("CAMDAN session closed")

    async def _retry_request(self, func, *args, **kwargs):
        """
        Retry logic with exponential backoff

        Args:
            func: Async function to retry
            *args, **kwargs: Arguments for function

        Returns:
            Function result

        Raises:
            Last exception if all retries fail
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    self.logger.debug(
                        f"Request attempt {attempt + 1}/{self.max_retries} failed, "
                        f"retrying in {wait_time}s: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.debug(f"Request failed after {self.max_retries} attempts: {e}")

        raise last_exception

    def _get_cached_code(self, location: str, building_type: str) -> Optional[Dict]:
        """
        Get cached building code if available and fresh

        Args:
            location: Location key
            building_type: Building type key

        Returns:
            Cached data if available and fresh, None otherwise
        """
        cache_key = f"{location}_{building_type}"
        if cache_key in self._code_cache:
            cached_data, cached_time = self._code_cache[cache_key]
            if datetime.now() - cached_time < self._cache_ttl:
                self.logger.debug(f"Cache HIT for building codes: {cache_key}")
                return cached_data

        self.logger.debug(f"Cache MISS for building codes: {cache_key}")
        return None

    def _cache_building_code(self, location: str, building_type: str, data: Dict):
        """
        Cache building code data

        Args:
            location: Location key
            building_type: Building type key
            data: Data to cache
        """
        cache_key = f"{location}_{building_type}"
        self._code_cache[cache_key] = (data, datetime.now())
        self.logger.debug(f"Cached building codes: {cache_key}")

        # Also store in AlfredBrain if available
        if self.brain:
            try:
                self.brain.store_knowledge(
                    category="camdan_building_codes",
                    key=cache_key,
                    value=json.dumps(data),
                    importance=7,
                    confidence=0.95
                )
            except Exception as e:
                self.logger.warning(f"Failed to store codes in brain: {e}")

    async def check_health(self) -> Dict[str, Any]:
        """
        Check CAMDAN system health and availability
        Uses retry logic and updates circuit breaker state

        Returns:
            Health status dictionary with service information
        """
        async def _health_check():
            session = await self._get_session()
            async with session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.available = True
                    self.logger.info("CAMDAN system is available and healthy")
                    return data
                else:
                    self.available = False
                    self.logger.debug(f"CAMDAN health check: HTTP {resp.status}")
                    return {"status": "unhealthy", "code": resp.status}

        try:
            # Use retry logic with circuit breaker protection
            result = await self._retry_request(_health_check)
            self.circuit_breaker._on_success()  # Manual success tracking
            return result

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.available = False
            self.circuit_breaker._on_failure()  # Manual failure tracking
            self.logger.debug(f"CAMDAN health check: {e}")
            return {
                "status": "unavailable",
                "error": str(e),
                "circuit_state": self.circuit_breaker.state.value
            }

    async def query_engineering(
        self,
        query: str,
        state: Optional[str] = None,
        building_type: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query CAMDAN's AI engineering assistant
        Uses circuit breaker, retry logic, and caching

        Args:
            query: Engineering question or request
            state: US state code (e.g., "CA", "TX") for location-specific info
            building_type: Type of building (e.g., "commercial", "residential")
            project_id: Optional project identifier for context

        Returns:
            Dictionary with:
            - response: AI-generated answer
            - sources: List of reference sources
            - confidence: Confidence score (0.0-1.0)
            - building_codes: Applicable building codes
            - cost_estimate: Optional cost information
            - recommendations: List of recommendations
        """
        # Check circuit breaker state
        if self.circuit_breaker.state == CircuitState.OPEN:
            self.logger.error("Circuit breaker OPEN - CAMDAN unavailable")
            return {
                "success": False,
                "error": "CAMDAN service temporarily unavailable (circuit breaker open)",
                "circuit_state": "open"
            }

        # Check cache for building codes if applicable
        if state and building_type:
            cached_codes = self._get_cached_code(state, building_type)
            if cached_codes:
                self.logger.info("Using cached building codes")

        async def _query():
            payload = {
                "query": query,
                "state": state,
                "building_type": building_type,
                "project_id": project_id
            }

            session = await self._get_session()
            async with session.post(f"{self.base_url}/api/ai/query", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.logger.info(f"Engineering query successful: {query[:50]}...")

                    # Cache building codes if present
                    if state and building_type and "building_codes" in data:
                        self._cache_building_code(state, building_type, data["building_codes"])

                    # Store in brain if available
                    if self.brain:
                        try:
                            self.brain.store_conversation(
                                user_input=f"CAMDAN query: {query}",
                                alfred_response=data.get("response", "")[:500],
                                topics=["camdan", "engineering", building_type or "general"],
                                importance=6,
                                success=True
                            )
                        except Exception as e:
                            self.logger.warning(f"Failed to store query in brain: {e}")

                    return data
                else:
                    error_text = await resp.text()
                    self.logger.error(f"Query failed: HTTP {resp.status} - {error_text}")
                    raise aiohttp.ClientError(f"HTTP {resp.status}: {error_text}")

        try:
            # Use retry logic with exponential backoff
            result = await self._retry_request(_query)
            self.circuit_breaker._on_success()
            return result

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.circuit_breaker._on_failure()
            self.logger.error(f"Engineering query failed after retries: {e}")
            return {
                "success": False,
                "error": str(e),
                "circuit_state": self.circuit_breaker.state.value
            }

    async def estimate_cost(
        self,
        description: str,
        location: str,
        square_footage: int,
        building_type: str = "commercial",
        additional_specs: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Get AI-powered cost estimation
        Uses circuit breaker, retry logic, and brain integration

        Args:
            description: Project description
            location: Location (city, state or state code)
            square_footage: Building size in square feet
            building_type: Type of building
            additional_specs: Optional additional specifications

        Returns:
            Dictionary with:
            - total_estimate: Total estimated cost
            - breakdown: Cost breakdown by category
            - confidence: Confidence in estimate
            - assumptions: Assumptions made
            - market_factors: Local market considerations
        """
        if self.circuit_breaker.state == CircuitState.OPEN:
            return {
                "success": False,
                "error": "CAMDAN service temporarily unavailable (circuit breaker open)"
            }

        async def _estimate():
            payload = {
                "project_description": description,
                "location": location,
                "square_footage": square_footage,
                "building_type": building_type
            }
            if additional_specs:
                payload.update(additional_specs)

            session = await self._get_session()
            async with session.post(f"{self.base_url}/api/ai/estimate-cost", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self.logger.info(f"Cost estimation successful: ${data.get('total_estimate', 0):,.2f}")

                    # Store in brain if available
                    if self.brain:
                        try:
                            self.brain.store_knowledge(
                                category="camdan_cost_estimates",
                                key=f"{location}_{building_type}_{square_footage}",
                                value=json.dumps({
                                    "estimate": data.get("total_estimate"),
                                    "breakdown": data.get("breakdown"),
                                    "date": datetime.now().isoformat()
                                }),
                                importance=8,
                                confidence=data.get("confidence", 0.7)
                            )
                        except Exception as e:
                            self.logger.warning(f"Failed to store estimate in brain: {e}")

                    return data
                else:
                    error_text = await resp.text()
                    raise aiohttp.ClientError(f"HTTP {resp.status}: {error_text}")

        try:
            result = await self._retry_request(_estimate)
            self.circuit_breaker._on_success()
            return result
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.circuit_breaker._on_failure()
            self.logger.error(f"Cost estimation failed after retries: {e}")
            return {"success": False, "error": str(e)}

    async def check_compliance(
        self,
        building_specs: Dict[str, Any],
        location: str,
        project_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check building code compliance
        Uses circuit breaker, retry logic, and brain integration

        Args:
            building_specs: Building specifications dictionary
            location: Location (city, state or state code)
            project_id: Optional project identifier

        Returns:
            Dictionary with:
            - status: Compliance status (compliant/violations/unknown)
            - violations: List of code violations found
            - recommendations: Remediation recommendations
            - applicable_codes: Codes checked against
            - severity: Overall severity assessment
        """
        if self.circuit_breaker.state == CircuitState.OPEN:
            return {
                "success": False,
                "error": "CAMDAN service temporarily unavailable (circuit breaker open)"
            }

        async def _check():
            payload = {
                "project_id": project_id or "alfred_integration",
                "building_specs": building_specs,
                "location": location,
                "checked_by": "Alfred AI"
            }

            session = await self._get_session()
            async with session.post(f"{self.base_url}/api/compliance/check", json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    violations = len(data.get('violations', []))
                    self.logger.info(f"Compliance check complete: {violations} violations found")

                    # Store violations in brain if any found
                    if self.brain and violations > 0:
                        try:
                            self.brain.store_knowledge(
                                category="camdan_compliance_violations",
                                key=f"{project_id}_{location}",
                                value=json.dumps({
                                    "violations": violations,
                                    "severity": data.get("severity"),
                                    "date": datetime.now().isoformat()
                                }),
                                importance=9 if violations > 0 else 5,
                                confidence=0.9
                            )
                        except Exception as e:
                            self.logger.warning(f"Failed to store compliance in brain: {e}")

                    return data
                else:
                    error_text = await resp.text()
                    raise aiohttp.ClientError(f"HTTP {resp.status}: {error_text}")

        try:
            result = await self._retry_request(_check)
            self.circuit_breaker._on_success()
            return result
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            self.circuit_breaker._on_failure()
            self.logger.error(f"Compliance check failed after retries: {e}")
            return {"success": False, "error": str(e)}

    async def analyze_building_plan(
        self,
        file_path: str,
        building_age: int = 0,
        building_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze building plans with computer vision

        Args:
            file_path: Path to building plan image (PDF, JPG, PNG)
            building_age: Age of building in years
            building_type: Type of building

        Returns:
            Dictionary with:
            - components: List of identified components
            - lifespan_predictions: Component lifespan predictions
            - maintenance_schedule: Recommended maintenance
            - cost_estimates: Maintenance cost estimates
            - ocr_text: Extracted text from plans
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}"
                }

            building_info = {
                "age_years": building_age
            }
            if building_type:
                building_info["type"] = building_type

            data = aiohttp.FormData()
            data.add_field('file',
                          open(file_path, 'rb'),
                          filename=file_path.name,
                          content_type='application/octet-stream')
            data.add_field('building_info', json.dumps(building_info))

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=60)) as session:
                async with session.post(f"{self.base_url}/api/analyze-plan", data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        components = len(result.get('components', []))
                        self.logger.info(f"Building plan analysis complete: {components} components identified")
                        return result
                    else:
                        error_text = await resp.text()
                        self.logger.error(f"Plan analysis failed: HTTP {resp.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status}",
                            "details": error_text
                        }

        except Exception as e:
            self.logger.error(f"Building plan analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_component_predictions(self, component_id: str) -> Dict[str, Any]:
        """
        Get maintenance predictions for a specific component

        Args:
            component_id: Component identifier

        Returns:
            Dictionary with:
            - expected_lifespan: Expected lifespan in years
            - remaining_life_years: Years remaining
            - next_maintenance_date: Next maintenance due date
            - replacement_cost_estimate: Estimated replacement cost
            - criticality_level: Component criticality
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/api/components/{component_id}/predictions") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.logger.info(f"Component predictions retrieved: {component_id}")
                        return data
                    else:
                        error_text = await resp.text()
                        self.logger.error(f"Component predictions failed: HTTP {resp.status}")
                        return {
                            "success": False,
                            "error": f"HTTP {resp.status}",
                            "details": error_text
                        }

        except Exception as e:
            self.logger.error(f"Component predictions error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_system_info(self) -> Dict[str, Any]:
        """
        Get CAMDAN system information and features

        Returns:
            System information dictionary
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.base_url}/") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        return {"error": f"HTTP {resp.status}"}

        except Exception as e:
            self.logger.error(f"System info error: {e}")
            return {"error": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """
        Get client status

        Returns:
            Status dictionary
        """
        return {
            "available": self.available,
            "base_url": self.base_url,
            "timeout": self.timeout.total,
            "description": "CAMDAN Engineering Management System Integration"
        }


# Graceful import handling
CAMDAN_AVAILABLE = False
try:
    # Try to create client and check availability
    # This is synchronous check, actual health check happens async
    client = CAMDANClient()
    CAMDAN_AVAILABLE = True
    logging.getLogger(__name__).info("CAMDAN client module loaded successfully")
except Exception as e:
    logging.getLogger(__name__).warning(f"CAMDAN client initialization failed: {e}")
