"""
GOVs-AI — FastAPI Application Entry Point
AI-Powered Government Scheme Eligibility Platform

Startup flow:
1. Initialize database (create tables)
2. Load FAISS vector index
3. Seed scheme data if DB is empty
4. Register all API routes
5. Start Uvicorn server
"""

import json
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database.connection import init_db, SessionLocal
from database.models import GovernmentScheme, User, Profile, ConversationMemory
from api.auth import hash_password

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(name)s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("govsai")


def seed_schemes(db):
    """Seed government schemes from JSON if database is empty."""
    count = db.query(GovernmentScheme).count()
    if count > 0:
        logger.info(f"  📋 {count} schemes already in database, skipping seed.")
        return

    data_path = os.path.join(os.path.dirname(__file__), "data", "schemes.json")
    if not os.path.exists(data_path):
        logger.warning(f"  ⚠️  Schemes data file not found: {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        schemes = json.load(f)

    for s in schemes:
        scheme = GovernmentScheme(
            name=s["name"],
            short_name=s.get("short_name"),
            category=s["category"],
            description=s["description"],
            eligibility=s["eligibility"],
            benefits=s["benefits"],
            benefits_amount=s.get("benefits_amount"),
            documents_required=s["documents_required"],
            application_process=s.get("application_process"),
            website_url=s.get("website_url"),
            ministry=s.get("ministry"),
            state=s.get("state", "Central"),
        )
        db.add(scheme)

    db.commit()
    logger.info(f"  ✅ Seeded {len(schemes)} government schemes.")


def seed_demo_users(db):
    """Create demo user accounts for hackathon demonstration."""
    demo_path = os.path.join(os.path.dirname(__file__), "data", "demo_users.json")
    if not os.path.exists(demo_path):
        return

    existing = db.query(User).filter(User.email.like("%@demo.govsai.in")).count()
    if existing > 0:
        logger.info(f"  👤 {existing} demo users already exist, skipping.")
        return

    with open(demo_path, "r", encoding="utf-8") as f:
        demo_users = json.load(f)

    for du in demo_users:
        user = User(
            email=du["email"],
            password_hash=hash_password(du["password"]),
            role=du.get("role", "citizen"),
        )
        db.add(user)
        db.flush()

        profile = Profile(
            user_id=user.id,
            name=du["profile"]["name"],
            age=du["profile"].get("age"),
            gender=du["profile"].get("gender"),
            state=du["profile"].get("state"),
            district=du["profile"].get("district"),
            occupation=du["profile"].get("occupation"),
            annual_income=du["profile"].get("annual_income"),
            category=du["profile"].get("category"),
            education=du["profile"].get("education"),
            land_area_acres=du["profile"].get("land_area_acres"),
            has_disability=du["profile"].get("has_disability", False),
            family_size=du["profile"].get("family_size"),
            marital_status=du["profile"].get("marital_status"),
            has_bank_account=du["profile"].get("has_bank_account", True),
            has_aadhaar=du["profile"].get("has_aadhaar", True),
            bpl_card=du["profile"].get("bpl_card", False),
        )
        db.add(profile)

        memory = ConversationMemory(user_id=user.id, memory_data={})
        db.add(memory)

    db.commit()
    logger.info(f"  ✅ Seeded {len(demo_users)} demo users.")

    # Also create admin user
    admin_exists = db.query(User).filter(User.email == "admin@govsai.in").first()
    if not admin_exists:
        admin = User(email="admin@govsai.in", password_hash=hash_password("admin123"), role="admin")
        db.add(admin)
        db.flush()
        db.add(Profile(user_id=admin.id, name="Admin"))
        db.add(ConversationMemory(user_id=admin.id, memory_data={}))
        db.commit()
        logger.info("  ✅ Admin user created (admin@govsai.in / admin123)")


def ingest_scheme_data_to_vector_store(db):
    """Load scheme data into FAISS for RAG retrieval."""
    try:
        from rag.retriever import init_index, get_index_stats
        from rag.ingestion import ingest_scheme_data

        init_index()
        stats = get_index_stats()

        if stats.get("total_vectors", 0) > 0:
            logger.info(f"  🔍 FAISS index already has {stats['total_vectors']} vectors.")
            return

        schemes = db.query(GovernmentScheme).all()
        scheme_dicts = [
            {
                "id": s.id,
                "name": s.name,
                "short_name": s.short_name,
                "category": s.category,
                "description": s.description,
                "eligibility": s.eligibility,
                "benefits": s.benefits,
                "documents_required": s.documents_required,
            }
            for s in schemes
        ]

        if scheme_dicts:
            count = ingest_scheme_data(scheme_dicts)
            logger.info(f"  ✅ Ingested {count} chunks into FAISS vector store.")
    except Exception as e:
        logger.warning(f"  ⚠️  FAISS initialization skipped: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    logger.info("=" * 60)
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("=" * 60)

    # Step 1: Initialize database
    logger.info("📦 Initializing database...")
    init_db()
    logger.info("  ✅ Database tables created.")

    # Step 2: Seed data
    db = SessionLocal()
    try:
        logger.info("🌱 Seeding data...")
        seed_schemes(db)
        seed_demo_users(db)

        # Step 3: Initialize FAISS
        logger.info("🔍 Initializing FAISS vector store...")
        ingest_scheme_data_to_vector_store(db)
    finally:
        db.close()

    logger.info("=" * 60)
    logger.info(f"✅ {settings.APP_NAME} is ready!")
    logger.info(f"   API: http://localhost:{settings.PORT}/docs")
    if settings.should_use_mock:
        logger.info("   ⚠️  Running in MOCK LLM mode (no Gemini API key)")
    logger.info("=" * 60)

    yield

    # Shutdown
    logger.info("👋 Shutting down GOVs-AI...")


# ── FastAPI Application ──────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Government Scheme Eligibility Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routes ─────────────────────────────────────────────
from api.routes.auth_routes import router as auth_router
from api.routes.chat_routes import router as chat_router
from api.routes.profile_routes import router as profile_router
from api.routes.scheme_routes import router as scheme_router
from api.routes.document_routes import router as document_router
from api.routes.notification_routes import router as notification_router
from api.routes.admin_routes import router as admin_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(scheme_router)
app.include_router(document_router)
app.include_router(notification_router)
app.include_router(admin_router)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mock_mode": settings.should_use_mock,
    }


@app.get("/api/health", tags=["Health"])
def api_health():
    """API health check with component status."""
    from rag.retriever import get_index_stats
    return {
        "status": "healthy",
        "components": {
            "database": "connected",
            "vector_store": get_index_stats(),
            "llm": "mock" if settings.should_use_mock else "gemini",
        },
    }


# ── Run with Uvicorn ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
