"""
CAMDAN Engineering Tool
AI-powered engineering and building management for Alfred Tool Mode
"""

import logging
import asyncio
from typing import Dict, Any
from tools.base import Tool, ToolResult


class CAMDANTool(Tool):
    """
    CAMDAN Engineering Management Integration Tool

    Provides access to:
    - AI engineering knowledge base (NIST, EBSCO, building codes)
    - Cost estimation and budget management
    - Building code compliance checking (all 50 US states)
    - Building plan analysis with computer vision
    - Component maintenance predictions

    Allows Alfred to answer engineering questions like:
    - "What building codes apply to a 5-story office in California?"
    - "Estimate the cost to build a 50,000 sq ft warehouse"
    - "Check if my design meets fire safety codes"
    - "Analyze this building plan for maintenance needs"
    """

    def __init__(self, brain=None):
        """
        Initialize CAMDAN tool

        Args:
            brain: AlfredBrain for storing engineering interactions
        """
        self.logger = logging.getLogger(__name__)
        self.brain = brain
        self.camdan_available = False
        self.client = None

        self._check_availability()

    def _check_availability(self):
        """Check if CAMDAN service is available"""
        try:
            from capabilities.engineering.camdan_client import CAMDANClient

            self.client = CAMDANClient()

            # Try async health check
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            health = loop.run_until_complete(self.client.check_health())

            if health.get("status") == "healthy":
                self.camdan_available = True
                self.logger.info("CAMDAN engineering service is available")
            else:
                self.logger.warning(f"CAMDAN service unhealthy: {health.get('status')}")

        except ImportError as e:
            # CAMDAN dependencies not installed (aiohttp, etc.) - optional integration
            self.logger.debug(f"CAMDAN dependencies not installed: {e}")
            self.camdan_available = False
        except Exception as e:
            self.logger.debug(f"CAMDAN service not available: {e}")
            self.camdan_available = False

    @property
    def name(self) -> str:
        return "camdan_engineering"

    @property
    def description(self) -> str:
        return (
            "Access CAMDAN (Comprehensive AI Management for Design, Architecture & Engineering) capabilities. "
            "Query engineering knowledge base trained on NIST data, EBSCO research, and all 50 US state building codes. "
            "Get AI-powered cost estimates, check building code compliance, analyze building plans with computer vision, "
            "and predict component maintenance needs. Use for construction, engineering, and building management queries."
        )

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["query", "estimate_cost", "check_compliance", "analyze_plan", "predict_maintenance"],
                    "description": (
                        "Action to perform:\n"
                        "- query: Ask engineering questions (building codes, standards, specifications)\n"
                        "- estimate_cost: Get AI cost estimation for construction projects\n"
                        "- check_compliance: Check building code compliance (all 50 US states)\n"
                        "- analyze_plan: Analyze building plans with computer vision\n"
                        "- predict_maintenance: Get component maintenance predictions"
                    )
                },
                "query": {
                    "type": "string",
                    "description": "Engineering question or description (for query and estimate_cost actions)"
                },
                "location": {
                    "type": "string",
                    "description": "Location (state code or city, state) for building codes and cost estimation"
                },
                "building_type": {
                    "type": "string",
                    "description": "Type of building (e.g., 'commercial', 'residential', 'industrial', 'municipal')"
                },
                "square_footage": {
                    "type": "integer",
                    "description": "Building size in square feet (for cost estimation)"
                },
                "building_specs": {
                    "type": "object",
                    "description": "Building specifications (for compliance checking)"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to building plan image file (for analyze_plan action)"
                },
                "building_age": {
                    "type": "integer",
                    "description": "Age of building in years (for plan analysis and maintenance prediction)"
                },
                "component_id": {
                    "type": "string",
                    "description": "Component identifier (for predict_maintenance action)"
                }
            },
            "required": ["action"]
        }

    def execute(
        self,
        action: str,
        query: str = None,
        location: str = None,
        building_type: str = None,
        square_footage: int = None,
        building_specs: Dict = None,
        file_path: str = None,
        building_age: int = None,
        component_id: str = None
    ) -> ToolResult:
        """
        Execute CAMDAN engineering action

        Args:
            action: Action to perform
            query: Engineering question or description
            location: Location (state code or city, state)
            building_type: Type of building
            square_footage: Building size in square feet
            building_specs: Building specifications
            file_path: Path to building plan image
            building_age: Age of building in years
            component_id: Component identifier

        Returns:
            ToolResult with engineering data or error
        """
        # Check availability
        if not self.camdan_available:
            return ToolResult(
                success=False,
                output="",
                error=(
                    "CAMDAN engineering service is not available. "
                    "Ensure CAMDAN is running at http://localhost:8001"
                )
            )

        try:
            # Get event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Execute action
            if action == "query":
                result = loop.run_until_complete(self._execute_query(query, location, building_type))
            elif action == "estimate_cost":
                result = loop.run_until_complete(self._execute_cost_estimate(query, location, square_footage, building_type))
            elif action == "check_compliance":
                result = loop.run_until_complete(self._execute_compliance_check(building_specs, location))
            elif action == "analyze_plan":
                result = loop.run_until_complete(self._execute_plan_analysis(file_path, building_age, building_type))
            elif action == "predict_maintenance":
                result = loop.run_until_complete(self._execute_maintenance_prediction(component_id))
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown action: {action}"
                )

            return result

        except Exception as e:
            self.logger.error(f"Error executing CAMDAN action: {e}")
            return ToolResult(
                success=False,
                output="",
                error=f"CAMDAN execution error: {str(e)}"
            )

    async def _execute_query(self, query: str, location: str = None, building_type: str = None) -> ToolResult:
        """Execute engineering query"""
        if not query:
            return ToolResult(success=False, output="", error="Query is required")

        response = await self.client.query_engineering(
            query=query,
            state=location,
            building_type=building_type
        )

        if not response.get("success", True):
            return ToolResult(success=False, output="", error=response.get("error", "Query failed"))

        # Format output
        output = self._format_query_output(response)

        # Store in brain
        if self.brain:
            self.brain.store_conversation(
                user_input=query,
                alfred_response=response.get("response", ""),
                context={"camdan_engineering": True, "location": location, "building_type": building_type},
                models_used=["camdan-ai"],
                importance=7,
                success=True
            )
            # Store applicable codes as knowledge
            if response.get("building_codes"):
                for code in response.get("building_codes", []):
                    self.brain.store_knowledge(
                        category="building_codes",
                        key=f"{location}_{code.get('code', 'unknown')}",
                        value=code.get("title", ""),
                        importance=6
                    )

        return ToolResult(
            success=True,
            output=output,
            metadata={
                "confidence": response.get("confidence"),
                "sources": response.get("sources", []),
                "building_codes": response.get("building_codes", [])
            }
        )

    async def _execute_cost_estimate(self, description: str, location: str, square_footage: int, building_type: str) -> ToolResult:
        """Execute cost estimation"""
        if not description or not location or not square_footage:
            return ToolResult(success=False, output="", error="Description, location, and square_footage are required")

        response = await self.client.estimate_cost(
            description=description,
            location=location,
            square_footage=square_footage,
            building_type=building_type or "commercial"
        )

        if not response.get("success", True):
            return ToolResult(success=False, output="", error=response.get("error", "Estimation failed"))

        # Format output
        output = self._format_cost_output(response)

        # Store in brain
        if self.brain:
            self.brain.store_knowledge(
                category="engineering_costs",
                key=f"{location}_{building_type}_{square_footage}sqft",
                value=f"${response.get('total_estimate', 0):,.2f}",
                importance=7
            )

        return ToolResult(
            success=True,
            output=output,
            metadata={
                "total_estimate": response.get("total_estimate"),
                "breakdown": response.get("breakdown", {}),
                "confidence": response.get("confidence")
            }
        )

    async def _execute_compliance_check(self, building_specs: Dict, location: str) -> ToolResult:
        """Execute compliance check"""
        if not building_specs or not location:
            return ToolResult(success=False, output="", error="Building specs and location are required")

        response = await self.client.check_compliance(
            building_specs=building_specs,
            location=location
        )

        if not response.get("success", True):
            return ToolResult(success=False, output="", error=response.get("error", "Compliance check failed"))

        # Format output
        output = self._format_compliance_output(response)

        # Store in brain as security scan
        if self.brain:
            violations = response.get("violations", [])
            severity = "critical" if len(violations) > 5 else "high" if len(violations) > 2 else "medium" if violations else "low"

            self.brain.store_security_scan(
                target=f"{location}_building",
                scan_type="building_code_compliance",
                findings={"violations": violations, "applicable_codes": response.get("applicable_codes", [])},
                severity_summary=f"{len(violations)} code violations found",
                recommendations=response.get("recommendations", []),
                authorized=True,
                notes=f"Compliance check for {location}"
            )

        return ToolResult(
            success=True,
            output=output,
            metadata={
                "status": response.get("status"),
                "violations": response.get("violations", []),
                "severity": severity
            }
        )

    async def _execute_plan_analysis(self, file_path: str, building_age: int, building_type: str) -> ToolResult:
        """Execute building plan analysis"""
        if not file_path:
            return ToolResult(success=False, output="", error="File path is required")

        response = await self.client.analyze_building_plan(
            file_path=file_path,
            building_age=building_age or 0,
            building_type=building_type
        )

        if not response.get("success", True):
            return ToolResult(success=False, output="", error=response.get("error", "Plan analysis failed"))

        # Format output
        output = self._format_plan_analysis_output(response)

        # Store components as patterns in brain
        if self.brain:
            for component in response.get("components", []):
                self.brain.record_pattern(
                    pattern_type="building_component",
                    pattern_data={
                        "component": component.get("name"),
                        "lifespan": component.get("expected_lifespan"),
                        "maintenance_cost": component.get("maintenance_cost")
                    },
                    success=True
                )

        return ToolResult(
            success=True,
            output=output,
            metadata={
                "components_found": len(response.get("components", [])),
                "components": response.get("components", [])
            }
        )

    async def _execute_maintenance_prediction(self, component_id: str) -> ToolResult:
        """Execute maintenance prediction"""
        if not component_id:
            return ToolResult(success=False, output="", error="Component ID is required")

        response = await self.client.get_component_predictions(component_id)

        if not response.get("success", True):
            return ToolResult(success=False, output="", error=response.get("error", "Prediction failed"))

        # Format output
        output = self._format_maintenance_output(response)

        return ToolResult(
            success=True,
            output=output,
            metadata=response
        )

    def _format_query_output(self, response: Dict) -> str:
        """Format engineering query output"""
        lines = []
        lines.append("=== CAMDAN Engineering Query Response ===\n")
        lines.append(response.get("response", "No response available"))

        if response.get("building_codes"):
            lines.append("\n\nApplicable Building Codes:")
            for code in response.get("building_codes", []):
                lines.append(f"  - {code.get('code', 'N/A')}: {code.get('title', 'N/A')}")

        if response.get("sources"):
            lines.append("\n\nSources:")
            for source in response.get("sources", [])[:5]:
                lines.append(f"  - {source}")

        if response.get("confidence"):
            lines.append(f"\n\nConfidence: {response.get('confidence', 0):.0%}")

        return "\n".join(lines)

    def _format_cost_output(self, response: Dict) -> str:
        """Format cost estimation output"""
        lines = []
        lines.append("=== CAMDAN Cost Estimation ===\n")
        lines.append(f"Total Estimated Cost: ${response.get('total_estimate', 0):,.2f}")

        if response.get("breakdown"):
            lines.append("\nCost Breakdown:")
            for category, cost in response.get("breakdown", {}).items():
                lines.append(f"  - {category}: ${cost:,.2f}")

        if response.get("assumptions"):
            lines.append("\nAssumptions:")
            for assumption in response.get("assumptions", []):
                lines.append(f"  - {assumption}")

        if response.get("confidence"):
            lines.append(f"\nConfidence: {response.get('confidence', 0):.0%}")

        return "\n".join(lines)

    def _format_compliance_output(self, response: Dict) -> str:
        """Format compliance check output"""
        lines = []
        lines.append("=== CAMDAN Building Code Compliance Check ===\n")
        lines.append(f"Status: {response.get('status', 'unknown').upper()}")

        violations = response.get("violations", [])
        if violations:
            lines.append(f"\n{len(violations)} Code Violation(s) Found:")
            for i, violation in enumerate(violations[:10], 1):
                lines.append(f"\n{i}. {violation.get('code', 'N/A')}")
                lines.append(f"   Description: {violation.get('description', 'N/A')}")
                lines.append(f"   Severity: {violation.get('severity', 'N/A')}")
        else:
            lines.append("\nNo violations found - Building appears compliant")

        if response.get("recommendations"):
            lines.append("\nRecommendations:")
            for rec in response.get("recommendations", [])[:5]:
                lines.append(f"  - {rec}")

        return "\n".join(lines)

    def _format_plan_analysis_output(self, response: Dict) -> str:
        """Format building plan analysis output"""
        lines = []
        lines.append("=== CAMDAN Building Plan Analysis ===\n")

        components = response.get("components", [])
        lines.append(f"Components Identified: {len(components)}")

        if components:
            lines.append("\nComponent Details:")
            for i, comp in enumerate(components[:10], 1):
                lines.append(f"\n{i}. {comp.get('name', 'Unknown')}")
                lines.append(f"   Category: {comp.get('category', 'N/A')}")
                lines.append(f"   Expected Lifespan: {comp.get('expected_lifespan', 'N/A')} years")
                if comp.get("remaining_life"):
                    lines.append(f"   Remaining Life: {comp.get('remaining_life', 'N/A')} years")

            if len(components) > 10:
                lines.append(f"\n... and {len(components) - 10} more components")

        return "\n".join(lines)

    def _format_maintenance_output(self, response: Dict) -> str:
        """Format maintenance prediction output"""
        lines = []
        lines.append("=== CAMDAN Maintenance Prediction ===\n")
        lines.append(f"Expected Lifespan: {response.get('expected_lifespan', 'N/A')} years")
        lines.append(f"Remaining Life: {response.get('remaining_life_years', 'N/A')} years")
        lines.append(f"Next Maintenance: {response.get('next_maintenance_date', 'N/A')}")
        lines.append(f"Estimated Replacement Cost: ${response.get('replacement_cost_estimate', 0):,.2f}")
        lines.append(f"Criticality Level: {response.get('criticality_level', 'N/A')}")

        return "\n".join(lines)


# Graceful import check
def create_camdan_tool(brain=None) -> CAMDANTool:
    """
    Factory function to create CAMDAN tool with graceful degradation

    Args:
        brain: AlfredBrain instance

    Returns:
        CAMDANTool instance (may be unavailable if CAMDAN not running)
    """
    return CAMDANTool(brain)
