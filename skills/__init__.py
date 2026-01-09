"""
ALFRED Skills System - PAI-inspired semantic routing

Skills are modular capability packages with:
- SKILL.md files defining triggers and workflows
- Semantic routing based on "USE WHEN" clauses
- 7-phase algorithm: OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN

Usage:
    from skills.router import SkillRouter, create_skill_router

    router = create_skill_router()
    result = router.route("Scan example.com for vulnerabilities")
    if result.skill:
        print(f"Matched: {result.skill.name} (confidence: {result.confidence})")

Author: Daniel J Rita (BATDAN) | GxEum Technologies / CAMDAN Enterprizes
"""

from .router import SkillRouter, Skill, RouteResult, create_skill_router

__all__ = ['SkillRouter', 'Skill', 'RouteResult', 'create_skill_router']
