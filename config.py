import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration for AI Mock Interviewer."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-ai-mock-interviewer-secret-key-2026")
    
    # Storage paths
    SCORECARD_FOLDER = os.environ.get("SCORECARD_FOLDER", str(BASE_DIR / "generated_scorecards"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(BASE_DIR / "interviews.db"))
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Server Port (default 5001 so it can run alongside Resume Enhancer on 5000)
    PORT = int(os.environ.get("PORT", 5001))
    
    APP_NAME = "AI Mock Technical Interviewer & Code Evaluator"
    VERSION = "1.0.0"


os.makedirs(Config.SCORECARD_FOLDER, exist_ok=True)
