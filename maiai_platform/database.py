"""
Platform Database Models
SQLite database for users, subscriptions, and AI agents

Author: Daniel J Rita (BATDAN)
"""

import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "platform.db"


def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables"""
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            email_verified BOOLEAN DEFAULT FALSE,
            verification_token TEXT,
            reset_token TEXT,
            reset_expires TIMESTAMP,
            stripe_customer_id TEXT,
            subscription_tier TEXT DEFAULT 'free',
            subscription_status TEXT DEFAULT 'active',
            subscription_expires TIMESTAMP,
            beta_access BOOLEAN DEFAULT FALSE,
            last_login TIMESTAMP
        )
    """)

    # Sessions table (for JWT-like tokens)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # MaiAI Agents table (birthed AI agents)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS maiai_agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            agent_name TEXT NOT NULL,
            agent_type TEXT DEFAULT 'assistant',
            personality TEXT,
            voice_preset TEXT DEFAULT 'neutral',
            birth_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP,
            memory_db_path TEXT,
            status TEXT DEFAULT 'active',
            total_conversations INTEGER DEFAULT 0,
            config_json TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Subscriptions/Payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stripe_payment_id TEXT,
            amount_cents INTEGER NOT NULL,
            currency TEXT DEFAULT 'usd',
            status TEXT DEFAULT 'pending',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Beta signups (for waitlist)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS beta_signups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            interest TEXT,
            signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invited BOOLEAN DEFAULT FALSE,
            invited_date TIMESTAMP,
            source TEXT DEFAULT 'website'
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """Hash password with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, hash_hex = stored_hash.split(':')
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hashed.hex() == hash_hex
    except Exception:
        return False


def generate_token() -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(32)


class UserDB:
    """User database operations"""

    @staticmethod
    def create_user(email: str, password: str, name: Optional[str] = None,
                    beta_access: bool = False) -> Optional[int]:
        """Create new user, return user ID"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            password_hash = hash_password(password)
            verification_token = generate_token()
            cursor.execute("""
                INSERT INTO users (email, password_hash, name, verification_token, beta_access)
                VALUES (?, ?, ?, ?, ?)
            """, (email.lower(), password_hash, name, verification_token, beta_access))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # Email already exists
        finally:
            conn.close()

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def verify_email(token: str) -> bool:
        """Verify email with token"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET email_verified = TRUE, verification_token = NULL
            WHERE verification_token = ?
        """, (token,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict]:
        """Authenticate user, return user dict if valid"""
        user = UserDB.get_user_by_email(email)
        if user and verify_password(password, user['password_hash']):
            # Update last login
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET last_login = ? WHERE id = ?",
                          (datetime.now(), user['id']))
            conn.commit()
            conn.close()
            return user
        return None

    @staticmethod
    def create_session(user_id: int, ip: str = None, user_agent: str = None) -> str:
        """Create login session, return token"""
        conn = get_db()
        cursor = conn.cursor()
        token = generate_token()
        expires = datetime.now() + timedelta(days=30)
        cursor.execute("""
            INSERT INTO sessions (user_id, token, expires_at, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, token, expires, ip, user_agent))
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def get_user_by_session(token: str) -> Optional[Dict]:
        """Get user from session token"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.* FROM users u
            JOIN sessions s ON u.id = s.user_id
            WHERE s.token = ? AND s.expires_at > ?
        """, (token, datetime.now()))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def delete_session(token: str):
        """Delete session (logout)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
        conn.close()

    @staticmethod
    def update_subscription(user_id: int, tier: str, status: str,
                           stripe_customer_id: str = None, expires: datetime = None):
        """Update user subscription"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users SET
                subscription_tier = ?,
                subscription_status = ?,
                stripe_customer_id = COALESCE(?, stripe_customer_id),
                subscription_expires = ?
            WHERE id = ?
        """, (tier, status, stripe_customer_id, expires, user_id))
        conn.commit()
        conn.close()


class AgentDB:
    """MaiAI Agent database operations"""

    @staticmethod
    def birth_agent(user_id: int, name: str, personality: str = None,
                   voice_preset: str = "neutral", agent_type: str = "assistant",
                   config: dict = None) -> Optional[int]:
        """Create (birth) a new AI agent for user"""
        conn = get_db()
        cursor = conn.cursor()
        import json

        # Create unique memory database path for this agent
        memory_db_path = f"data/agents/{user_id}_{secrets.token_hex(8)}.db"

        cursor.execute("""
            INSERT INTO maiai_agents
            (user_id, agent_name, agent_type, personality, voice_preset, memory_db_path, config_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name, agent_type, personality, voice_preset,
              memory_db_path, json.dumps(config) if config else None))
        conn.commit()
        agent_id = cursor.lastrowid
        conn.close()
        return agent_id

    @staticmethod
    def get_user_agents(user_id: int) -> List[Dict]:
        """Get all agents for a user"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM maiai_agents
            WHERE user_id = ? AND status = 'active'
            ORDER BY birth_date DESC
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def get_agent(agent_id: int, user_id: int) -> Optional[Dict]:
        """Get specific agent (must belong to user)"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM maiai_agents
            WHERE id = ? AND user_id = ?
        """, (agent_id, user_id))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_agent_activity(agent_id: int):
        """Update agent's last active time and conversation count"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE maiai_agents SET
                last_active = ?,
                total_conversations = total_conversations + 1
            WHERE id = ?
        """, (datetime.now(), agent_id))
        conn.commit()
        conn.close()


class BetaDB:
    """Beta signup database operations"""

    @staticmethod
    def add_signup(email: str, name: str = None, interest: str = None,
                  source: str = "website") -> bool:
        """Add email to beta waitlist"""
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO beta_signups (email, name, interest, source)
                VALUES (?, ?, ?, ?)
            """, (email.lower(), name, interest, source))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already signed up
        finally:
            conn.close()

    @staticmethod
    def get_all_signups() -> List[Dict]:
        """Get all beta signups"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM beta_signups ORDER BY signup_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    @staticmethod
    def mark_invited(email: str):
        """Mark signup as invited"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE beta_signups SET invited = TRUE, invited_date = ?
            WHERE email = ?
        """, (datetime.now(), email.lower()))
        conn.commit()
        conn.close()

    @staticmethod
    def is_beta_user(email: str) -> bool:
        """Check if email is on beta list"""
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM beta_signups WHERE email = ?", (email.lower(),))
        result = cursor.fetchone() is not None
        conn.close()
        return result


# Initialize database on import
init_db()
