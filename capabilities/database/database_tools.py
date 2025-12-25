#!/usr/bin/env python3
"""
Alfred Database Tools - Professional Database Operations
Integrated from Alfred the Batcomputer

Features:
- Schema design and generation
- Migration creation (Alembic, Django, Prisma)
- Query optimization and analysis
- SQL generation from natural language
- Database performance analysis
- Schema validation and suggestions
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class DatabaseTools:
    """
    Professional database tools for schema design, migrations, and optimization
    """

    def __init__(self):
        self.supported_databases = ["postgresql", "mysql", "sqlite", "mssql", "oracle"]
        self.supported_frameworks = ["alembic", "django", "prisma", "sequelize"]

    # ============================================================================
    # SCHEMA DESIGN
    # ============================================================================

    def design_schema(self, description: str, database_type: str = "postgresql") -> Dict[str, Any]:
        """
        Design database schema from natural language description

        Args:
            description: Natural language description of requirements
            database_type: Target database type

        Returns:
            Complete schema design with tables, columns, relationships
        """
        print(f"[Schema Designer] Analyzing: {description[:100]}...")

        # Parse entities from description
        entities = self._extract_entities(description)

        # Generate schema
        schema = {
            "database_type": database_type,
            "tables": [],
            "relationships": [],
            "indexes": [],
            "created_at": datetime.now().isoformat()
        }

        for entity in entities:
            table = self._generate_table_definition(entity, database_type)
            schema["tables"].append(table)

        # Add relationships
        schema["relationships"] = self._infer_relationships(schema["tables"])

        # Add recommended indexes
        schema["indexes"] = self._recommend_indexes(schema["tables"])

        return schema

    def _extract_entities(self, description: str) -> List[str]:
        """Extract likely database entities from description"""
        # Common entity keywords
        entity_keywords = ["user", "customer", "product", "order", "payment",
                          "profile", "account", "transaction", "item", "post",
                          "comment", "review", "category", "tag"]

        entities = []
        description_lower = description.lower()

        for keyword in entity_keywords:
            if keyword in description_lower:
                entities.append(keyword.title())

        # If no entities found, extract nouns (simplified)
        if not entities:
            words = re.findall(r'\b[A-Z][a-z]+\b', description)
            entities = list(set(words))[:5]  # Limit to 5 entities

        return entities if entities else ["Entity"]

    def _generate_table_definition(self, entity_name: str, database_type: str) -> Dict:
        """Generate table definition for an entity"""
        table = {
            "name": entity_name.lower() + "s",
            "columns": [
                {
                    "name": "id",
                    "type": "SERIAL" if database_type == "postgresql" else "INTEGER",
                    "primary_key": True,
                    "auto_increment": True
                },
                {
                    "name": "created_at",
                    "type": "TIMESTAMP",
                    "default": "CURRENT_TIMESTAMP",
                    "nullable": False
                },
                {
                    "name": "updated_at",
                    "type": "TIMESTAMP",
                    "default": "CURRENT_TIMESTAMP",
                    "nullable": False
                }
            ]
        }

        # Add entity-specific columns
        if "user" in entity_name.lower():
            table["columns"].extend([
                {"name": "email", "type": "VARCHAR(255)", "unique": True, "nullable": False},
                {"name": "username", "type": "VARCHAR(100)", "unique": True, "nullable": False},
                {"name": "password_hash", "type": "VARCHAR(255)", "nullable": False},
                {"name": "is_active", "type": "BOOLEAN", "default": "TRUE"}
            ])
        elif "product" in entity_name.lower():
            table["columns"].extend([
                {"name": "name", "type": "VARCHAR(255)", "nullable": False},
                {"name": "description", "type": "TEXT"},
                {"name": "price", "type": "DECIMAL(10,2)", "nullable": False},
                {"name": "sku", "type": "VARCHAR(100)", "unique": True}
            ])
        else:
            # Generic columns
            table["columns"].extend([
                {"name": "name", "type": "VARCHAR(255)", "nullable": False},
                {"name": "description", "type": "TEXT"}
            ])

        return table

    def _infer_relationships(self, tables: List[Dict]) -> List[Dict]:
        """Infer relationships between tables"""
        relationships = []

        # Simple relationship inference
        for table in tables:
            for other_table in tables:
                if table["name"] != other_table["name"]:
                    # Check for common relationship patterns
                    if "user" in table["name"] and "post" in other_table["name"]:
                        relationships.append({
                            "from": other_table["name"],
                            "to": table["name"],
                            "type": "many_to_one",
                            "foreign_key": "user_id"
                        })

        return relationships

    def _recommend_indexes(self, tables: List[Dict]) -> List[Dict]:
        """Recommend indexes for performance"""
        indexes = []

        for table in tables:
            # Index on foreign keys
            for column in table["columns"]:
                if column["name"].endswith("_id"):
                    indexes.append({
                        "table": table["name"],
                        "columns": [column["name"]],
                        "type": "btree"
                    })

                # Index on unique columns
                if column.get("unique"):
                    indexes.append({
                        "table": table["name"],
                        "columns": [column["name"]],
                        "type": "btree",
                        "unique": True
                    })

        return indexes

    # ============================================================================
    # MIGRATION GENERATION
    # ============================================================================

    def generate_migration(self, name: str, operations: List[str],
                          framework: str = "alembic") -> str:
        """
        Generate database migration code

        Args:
            name: Migration name
            operations: List of operations to perform
            framework: Migration framework (alembic, django, prisma)

        Returns:
            Generated migration code
        """
        if framework not in self.supported_frameworks:
            return f"Error: Unsupported framework '{framework}'. Supported: {self.supported_frameworks}"

        if framework == "alembic":
            return self._generate_alembic_migration(name, operations)
        elif framework == "django":
            return self._generate_django_migration(name, operations)
        elif framework == "prisma":
            return self._generate_prisma_migration(name, operations)
        elif framework == "sequelize":
            return self._generate_sequelize_migration(name, operations)

    def _generate_alembic_migration(self, name: str, operations: List[str]) -> str:
        """Generate Alembic migration"""
        revision_id = name.lower().replace(" ", "_").replace("-", "_")

        code = f'''"""
{name}

Revision ID: {revision_id}
Revises:
Create Date: {datetime.now().isoformat()}

Generated by Alfred Ultimate Database Tools
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '{revision_id}'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade database schema"""
'''

        for operation in operations:
            code += self._parse_operation_to_alembic(operation)

        code += '''

def downgrade() -> None:
    """Downgrade database schema"""
'''

        for operation in reversed(operations):
            code += self._parse_operation_to_alembic_downgrade(operation)

        return code

    def _parse_operation_to_alembic(self, operation: str) -> str:
        """Parse natural language operation to Alembic code"""
        op_lower = operation.lower()

        if "create table" in op_lower:
            table_name = self._extract_table_name(operation)
            return f'''
    op.create_table(
        '{table_name}',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
'''

        elif "add column" in op_lower or "add field" in op_lower:
            return f'''
    # {operation}
    op.add_column('table_name', sa.Column('column_name', sa.String(), nullable=True))
'''

        elif "add index" in op_lower:
            return f'''
    # {operation}
    op.create_index(op.f('ix_table_column'), 'table_name', ['column_name'], unique=False)
'''

        else:
            return f'''
    # {operation}
    pass  # TODO: Implement
'''

    def _parse_operation_to_alembic_downgrade(self, operation: str) -> str:
        """Generate downgrade operations"""
        op_lower = operation.lower()

        if "create table" in op_lower:
            table_name = self._extract_table_name(operation)
            return f'''
    op.drop_table('{table_name}')
'''

        elif "add column" in op_lower:
            return f'''
    # Reverse: {operation}
    op.drop_column('table_name', 'column_name')
'''

        else:
            return f'''
    # Reverse: {operation}
    pass  # TODO: Implement reverse
'''

    def _generate_django_migration(self, name: str, operations: List[str]) -> str:
        """Generate Django migration"""
        return f'''from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        # Add dependencies here
    ]

    operations = [
{chr(10).join([f"        # {op}" for op in operations])}
    ]
'''

    def _generate_prisma_migration(self, name: str, operations: List[str]) -> str:
        """Generate Prisma schema changes"""
        newline = chr(10)
        ops_text = newline.join([f"// {op}" for op in operations])
        return f'''// Prisma Schema Migration: {name}
// Generated: {datetime.now().isoformat()}

{ops_text}

// Apply with: npx prisma migrate dev --name {name.replace(" ", "_")}
'''

    def _generate_sequelize_migration(self, name: str, operations: List[str]) -> str:
        """Generate Sequelize migration"""
        newline = chr(10)
        ops_text = newline.join([f"    // {op}" for op in operations])
        return f'''module.exports = {{
  up: async (queryInterface, Sequelize) => {{
    // {name}
{ops_text}
  }},

  down: async (queryInterface, Sequelize) => {{
    // Reverse migration
  }}
}};
'''

    def _extract_table_name(self, operation: str) -> str:
        """Extract table name from operation description"""
        match = re.search(r'(?:table|for)\s+([a-z_]+)', operation.lower())
        return match.group(1) if match else "table_name"

    # ============================================================================
    # SQL QUERY GENERATION
    # ============================================================================

    def generate_query(self, description: str, database: str = "postgresql") -> str:
        """
        Generate SQL query from natural language

        Args:
            description: Natural language description
            database: Target database type

        Returns:
            Generated SQL query
        """
        desc_lower = description.lower()

        # SELECT queries
        if any(word in desc_lower for word in ["get", "find", "fetch", "select", "list", "show"]):
            return self._generate_select_query(description)

        # INSERT queries
        elif any(word in desc_lower for word in ["add", "insert", "create", "new"]):
            return self._generate_insert_query(description)

        # UPDATE queries
        elif any(word in desc_lower for word in ["update", "modify", "change", "set"]):
            return self._generate_update_query(description)

        # DELETE queries
        elif any(word in desc_lower for word in ["delete", "remove", "drop"]):
            return self._generate_delete_query(description)

        # JOIN queries
        elif any(word in desc_lower for word in ["join", "combine", "merge"]):
            return self._generate_join_query(description)

        else:
            return f"-- Could not generate query for: {description}\n-- Please provide more specific instructions"

    def _generate_select_query(self, description: str) -> str:
        """Generate SELECT query"""
        # Extract table name
        table = self._extract_table_name(description) or "table_name"

        # Check for conditions
        if "where" in description.lower() or "with" in description.lower():
            return f"""-- {description}
SELECT *
FROM {table}
WHERE condition = value
ORDER BY created_at DESC
LIMIT 100;"""
        else:
            return f"""-- {description}
SELECT *
FROM {table}
ORDER BY created_at DESC
LIMIT 100;"""

    def _generate_insert_query(self, description: str) -> str:
        """Generate INSERT query"""
        table = self._extract_table_name(description) or "table_name"

        return f"""-- {description}
INSERT INTO {table} (column1, column2, column3)
VALUES (value1, value2, value3)
RETURNING id;"""

    def _generate_update_query(self, description: str) -> str:
        """Generate UPDATE query"""
        table = self._extract_table_name(description) or "table_name"

        return f"""-- {description}
UPDATE {table}
SET column1 = value1,
    column2 = value2,
    updated_at = CURRENT_TIMESTAMP
WHERE id = ?
RETURNING *;"""

    def _generate_delete_query(self, description: str) -> str:
        """Generate DELETE query"""
        table = self._extract_table_name(description) or "table_name"

        return f"""-- {description}
DELETE FROM {table}
WHERE id = ?
RETURNING *;"""

    def _generate_join_query(self, description: str) -> str:
        """Generate JOIN query"""
        return f"""-- {description}
SELECT t1.*, t2.*
FROM table1 t1
INNER JOIN table2 t2 ON t1.id = t2.table1_id
WHERE t1.condition = value
ORDER BY t1.created_at DESC
LIMIT 100;"""

    # ============================================================================
    # QUERY OPTIMIZATION
    # ============================================================================

    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze SQL query for performance issues

        Args:
            query: SQL query to analyze

        Returns:
            Analysis with recommendations
        """
        issues = []
        recommendations = []

        query_upper = query.upper()

        # Check for SELECT *
        if "SELECT *" in query_upper:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Using SELECT * instead of specific columns",
                "impact": "Fetches unnecessary data, wastes bandwidth and memory"
            })
            recommendations.append("Specify only the columns you need: SELECT id, name, email")

        # Check for missing LIMIT
        if "SELECT" in query_upper and "LIMIT" not in query_upper:
            issues.append({
                "severity": "HIGH",
                "issue": "No LIMIT clause on SELECT query",
                "impact": "Could return millions of rows, causing performance issues"
            })
            recommendations.append("Add LIMIT clause to prevent fetching too many rows")

        # Check for OR in WHERE clause (can prevent index usage)
        if "WHERE" in query_upper and " OR " in query_upper:
            issues.append({
                "severity": "MEDIUM",
                "issue": "Using OR in WHERE clause",
                "impact": "May prevent efficient index usage"
            })
            recommendations.append("Consider using UNION or IN clause instead")

        # Check for LIKE with leading wildcard
        if re.search(r"LIKE\s+['\"]%", query, re.IGNORECASE):
            issues.append({
                "severity": "HIGH",
                "issue": "LIKE pattern starts with wildcard (%)",
                "impact": "Cannot use indexes, will perform full table scan"
            })
            recommendations.append("Avoid leading wildcards in LIKE patterns, or use full-text search")

        # Check for missing WHERE clause on UPDATE/DELETE
        if ("UPDATE" in query_upper or "DELETE" in query_upper) and "WHERE" not in query_upper:
            issues.append({
                "severity": "CRITICAL",
                "issue": "UPDATE/DELETE without WHERE clause",
                "impact": "Will modify/delete ALL rows in the table!"
            })
            recommendations.append("ALWAYS include WHERE clause in UPDATE/DELETE queries")

        return {
            "query": query,
            "issues": issues,
            "recommendations": recommendations,
            "severity_summary": {
                "CRITICAL": len([i for i in issues if i["severity"] == "CRITICAL"]),
                "HIGH": len([i for i in issues if i["severity"] == "HIGH"]),
                "MEDIUM": len([i for i in issues if i["severity"] == "MEDIUM"]),
                "LOW": len([i for i in issues if i["severity"] == "LOW"])
            }
        }

    def optimize_query(self, query: str) -> str:
        """
        Suggest optimized version of query

        Args:
            query: SQL query to optimize

        Returns:
            Optimized query with comments explaining changes
        """
        optimized = query
        changes = []

        # Replace SELECT * with specific columns (commented suggestion)
        if "SELECT *" in query.upper():
            optimized = re.sub(r'SELECT\s+\*', 'SELECT id, /* add other columns */', optimized, flags=re.IGNORECASE)
            changes.append("Replaced SELECT * with specific columns")

        # Add LIMIT if missing
        if "SELECT" in query.upper() and "LIMIT" not in query.upper():
            optimized += "\nLIMIT 100  -- Added for safety"
            changes.append("Added LIMIT clause")

        if changes:
            return f"""-- OPTIMIZED QUERY
-- Changes made: {', '.join(changes)}

{optimized}"""
        else:
            return f"""-- Query is already optimized

{query}"""


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """CLI for database tools"""
    import sys

    print("="*80)
    print("ALFRED DATABASE TOOLS")
    print("="*80)
    print()

    db = DatabaseTools()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "schema":
            description = " ".join(sys.argv[2:])
            print(f"Designing schema for: {description}")
            schema = db.design_schema(description)
            print(json.dumps(schema, indent=2))

        elif command == "migration":
            name = sys.argv[2]
            operations = sys.argv[3:]
            print(f"Generating migration: {name}")
            code = db.generate_migration(name, operations)
            print(code)

        elif command == "query":
            description = " ".join(sys.argv[2:])
            print(f"Generating query for: {description}")
            query = db.generate_query(description)
            print(query)

        elif command == "analyze":
            query = " ".join(sys.argv[2:])
            analysis = db.analyze_query(query)
            print(json.dumps(analysis, indent=2))

    else:
        print("Available commands:")
        print("  schema <description>        - Design database schema")
        print("  migration <name> <ops...>   - Generate migration")
        print("  query <description>         - Generate SQL query")
        print("  analyze <query>             - Analyze query performance")
        print()
        print("Examples:")
        print("  python database_tools.py schema 'e-commerce with users and products'")
        print("  python database_tools.py migration 'add_email_to_users' 'add column email to users table'")
        print("  python database_tools.py query 'find all active users'")
        print("  python database_tools.py analyze 'SELECT * FROM users'")


if __name__ == "__main__":
    main()
