"""
ALFRED SYSTEMS Platform Server
Main entry point combining all platform features

Run: python -m platform.server
Or: uvicorn platform.server:app --reload --port 8000

Author: Daniel J Rita (BATDAN)
"""

import logging
import os
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .billing import router as billing_router
from .maiai import router as maiai_router

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="ALFRED SYSTEMS",
    description="""
## Personal AI Agent Platform

Create and customize your own AI assistants with MaiAI technology.

### Features
- **MaiAI Birth**: Create personalized AI agents with unique personalities
- **Persistent Memory**: Your agents learn and remember
- **Multi-Model AI**: Powered by local and cloud AI
- **Privacy First**: Your data stays yours

### Patent-Pending Technology
- ALFRED Brain Memory System (USPTO 63/915,217)
- AI Agent Birth System (USPTO 63/952,796)

**Created by Daniel J Rita (BATDAN) | CAMDAN Enterprises LLC**
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(billing_router, prefix="/api")
app.include_router(maiai_router, prefix="/api")

# Static files
STATIC_DIR = Path(__file__).parent / "static"
WEB_DIR = Path(__file__).parent.parent / "web" / "static"

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
elif WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


# ============================================================================
# Landing Page & Web Routes
# ============================================================================

LANDING_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALFRED SYSTEMS - Personal AI Agents</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg: #0a0a0f;
            --bg-card: #12121a;
            --accent: #e94560;
            --accent-glow: rgba(233, 69, 96, 0.3);
            --text: #fff;
            --text-dim: #888;
            --gradient: linear-gradient(135deg, #e94560 0%, #ff6b6b 50%, #ffa07a 100%);
        }

        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Header */
        header {
            padding: 20px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }

        nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 24px;
            font-weight: 700;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-links {
            display: flex;
            gap: 30px;
            align-items: center;
        }

        .nav-links a {
            color: var(--text-dim);
            text-decoration: none;
            transition: color 0.3s;
        }

        .nav-links a:hover { color: var(--text); }

        .btn {
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.3s;
            cursor: pointer;
            border: none;
            font-size: 14px;
        }

        .btn-primary {
            background: var(--gradient);
            color: white;
        }

        .btn-primary:hover {
            box-shadow: 0 10px 40px var(--accent-glow);
            transform: translateY(-2px);
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--accent);
            color: var(--accent);
        }

        /* Hero */
        .hero {
            padding: 100px 0;
            text-align: center;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(233, 69, 96, 0.1);
            border: 1px solid var(--accent);
            color: var(--accent);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            margin-bottom: 30px;
        }

        h1 {
            font-size: 56px;
            font-weight: 700;
            margin-bottom: 20px;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .hero p {
            font-size: 20px;
            color: var(--text-dim);
            max-width: 600px;
            margin: 0 auto 40px;
        }

        .hero-buttons {
            display: flex;
            gap: 20px;
            justify-content: center;
        }

        /* Features */
        .features {
            padding: 80px 0;
        }

        .features h2 {
            text-align: center;
            font-size: 36px;
            margin-bottom: 60px;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
        }

        .feature-card {
            background: var(--bg-card);
            border-radius: 16px;
            padding: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s;
        }

        .feature-card:hover {
            border-color: var(--accent);
            transform: translateY(-5px);
        }

        .feature-icon {
            font-size: 40px;
            margin-bottom: 20px;
        }

        .feature-card h3 {
            font-size: 20px;
            margin-bottom: 10px;
        }

        .feature-card p {
            color: var(--text-dim);
        }

        /* Pricing */
        .pricing {
            padding: 80px 0;
            background: var(--bg-card);
        }

        .pricing h2 {
            text-align: center;
            font-size: 36px;
            margin-bottom: 60px;
        }

        .pricing-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 30px;
            max-width: 900px;
            margin: 0 auto;
        }

        .price-card {
            background: var(--bg);
            border-radius: 16px;
            padding: 40px 30px;
            border: 1px solid rgba(255,255,255,0.1);
            text-align: center;
        }

        .price-card.featured {
            border-color: var(--accent);
            transform: scale(1.05);
        }

        .price-card h3 {
            font-size: 24px;
            margin-bottom: 10px;
        }

        .price {
            font-size: 48px;
            font-weight: 700;
            margin: 20px 0;
        }

        .price span {
            font-size: 16px;
            color: var(--text-dim);
        }

        .price-features {
            list-style: none;
            margin: 30px 0;
            text-align: left;
        }

        .price-features li {
            padding: 10px 0;
            color: var(--text-dim);
        }

        .price-features li::before {
            content: "✓";
            color: var(--accent);
            margin-right: 10px;
        }

        /* Beta Signup */
        .beta-signup {
            padding: 100px 0;
            text-align: center;
        }

        .beta-signup h2 {
            font-size: 36px;
            margin-bottom: 20px;
        }

        .beta-signup p {
            color: var(--text-dim);
            max-width: 500px;
            margin: 0 auto 40px;
        }

        .signup-form {
            max-width: 500px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
        }

        .signup-form input {
            flex: 1;
            padding: 15px 20px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: var(--bg-card);
            color: var(--text);
            font-size: 16px;
        }

        .signup-form input:focus {
            outline: none;
            border-color: var(--accent);
        }

        .signup-form button {
            padding: 15px 30px;
        }

        .signup-message {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            display: none;
        }

        .signup-message.success {
            background: rgba(74, 222, 128, 0.1);
            color: #4ade80;
            display: block;
        }

        .signup-message.error {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            display: block;
        }

        /* Footer */
        footer {
            padding: 40px 0;
            border-top: 1px solid rgba(255,255,255,0.1);
            text-align: center;
            color: var(--text-dim);
        }

        footer a {
            color: var(--accent);
            text-decoration: none;
        }

        /* Mobile */
        @media (max-width: 768px) {
            h1 { font-size: 36px; }
            .nav-links { display: none; }
            .hero-buttons { flex-direction: column; }
            .signup-form { flex-direction: column; }
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <nav>
                <div class="logo">ALFRED SYSTEMS</div>
                <div class="nav-links">
                    <a href="#features">Features</a>
                    <a href="#pricing">Pricing</a>
                    <a href="/api/docs">API Docs</a>
                    <a href="#beta" class="btn btn-primary">Join Beta</a>
                </div>
            </nav>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <span class="hero-badge">Patent-Pending AI Technology</span>
                <h1>Birth Your Own AI</h1>
                <p>Create personalized AI agents that learn, remember, and evolve. MaiAI technology gives you complete control over your digital companion.</p>
                <div class="hero-buttons">
                    <a href="#beta" class="btn btn-primary">Join the Beta</a>
                    <a href="/api/docs" class="btn btn-secondary">View API</a>
                </div>
            </div>
        </section>

        <section class="features" id="features">
            <div class="container">
                <h2>What Makes MaiAI Different</h2>
                <div class="feature-grid">
                    <div class="feature-card">
                        <div class="feature-icon">🧬</div>
                        <h3>Personality DNA</h3>
                        <p>Each agent has unique traits, voice, and behavior. Create a butler, coder, coach, or design your own.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🧠</div>
                        <h3>Persistent Memory</h3>
                        <p>Your agent remembers everything. Conversations, preferences, patterns - all stored securely.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Privacy First</h3>
                        <p>Local AI by default. Your data stays on your terms. Cloud features require explicit consent.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔗</div>
                        <h3>NEXUS Protocol</h3>
                        <p>Coming soon: Agent-to-agent communication. Let your AIs collaborate and share knowledge.</p>
                    </div>
                </div>
            </div>
        </section>

        <section class="pricing" id="pricing">
            <div class="container">
                <h2>Simple Pricing</h2>
                <div class="pricing-grid">
                    <div class="price-card">
                        <h3>Free</h3>
                        <div class="price">$0<span>/month</span></div>
                        <ul class="price-features">
                            <li>1 MaiAI Agent</li>
                            <li>100 messages/day</li>
                            <li>5 personality presets</li>
                            <li>Community support</li>
                        </ul>
                        <a href="#beta" class="btn btn-secondary">Get Started</a>
                    </div>
                    <div class="price-card featured">
                        <h3>Pro</h3>
                        <div class="price">$9.99<span>/month</span></div>
                        <ul class="price-features">
                            <li>5 MaiAI Agents</li>
                            <li>1,000 messages/day</li>
                            <li>Custom personalities</li>
                            <li>Voice customization</li>
                            <li>Priority support</li>
                        </ul>
                        <a href="#beta" class="btn btn-primary">Join Beta</a>
                    </div>
                    <div class="price-card">
                        <h3>Enterprise</h3>
                        <div class="price">$49.99<span>/month</span></div>
                        <ul class="price-features">
                            <li>Unlimited Agents</li>
                            <li>Unlimited messages</li>
                            <li>API access</li>
                            <li>Custom integrations</li>
                            <li>Dedicated support</li>
                        </ul>
                        <a href="mailto:danieljrita@hotmail.com" class="btn btn-secondary">Contact Us</a>
                    </div>
                </div>
            </div>
        </section>

        <section class="beta-signup" id="beta">
            <div class="container">
                <h2>Join the Beta</h2>
                <p>Be among the first to birth your own AI. Limited spots available.</p>
                <form class="signup-form" id="betaForm">
                    <input type="email" placeholder="Enter your email" required id="betaEmail">
                    <button type="submit" class="btn btn-primary">Sign Up</button>
                </form>
                <div class="signup-message" id="signupMessage"></div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>Patent-Pending Technology by <a href="mailto:danieljrita@hotmail.com">Daniel J Rita (BATDAN)</a></p>
            <p>CAMDAN Enterprises LLC &copy; 2025-2026</p>
        </div>
    </footer>

    <script>
        document.getElementById('betaForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = document.getElementById('betaEmail').value;
            const msg = document.getElementById('signupMessage');

            try {
                const response = await fetch('/api/auth/beta-signup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });

                const data = await response.json();

                msg.textContent = data.message || 'Thanks for signing up!';
                msg.className = 'signup-message success';
                document.getElementById('betaEmail').value = '';

            } catch (error) {
                msg.textContent = 'Something went wrong. Please try again.';
                msg.className = 'signup-message error';
            }
        });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    """Serve landing page"""
    return HTMLResponse(content=LANDING_PAGE)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "ALFRED SYSTEMS Platform",
        "version": "1.0.0",
        "description": "Personal AI Agent Platform with MaiAI technology",
        "endpoints": {
            "auth": "/api/auth/*",
            "billing": "/api/billing/*",
            "maiai": "/api/maiai/*"
        },
        "docs": "/api/docs",
        "patent_numbers": ["63/915,217", "63/952,796"]
    }


# ============================================================================
# Run Server
# ============================================================================

def main():
    """Run the platform server"""
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info("=" * 60)
    logger.info("ALFRED SYSTEMS Platform Server")
    logger.info("=" * 60)
    logger.info(f"Server: http://{host}:{port}")
    logger.info(f"API Docs: http://{host}:{port}/api/docs")
    logger.info(f"Landing: http://{host}:{port}/")
    logger.info("=" * 60)

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
