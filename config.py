import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# Load environment variables
load_dotenv(BASE_DIR / ".env")

# Detect serverless environment (e.g. Vercel)
IS_SERVERLESS = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
DEFAULT_STORAGE = Path("/tmp") if IS_SERVERLESS else BASE_DIR

# If running on serverless, copy pre-bundled db to /tmp for write access
if IS_SERVERLESS:
    bundled_db = BASE_DIR / "interviews.db"
    tmp_db = DEFAULT_STORAGE / "interviews.db"
    if bundled_db.exists() and not tmp_db.exists():
        try:
            shutil.copyfile(str(bundled_db), str(tmp_db))
        except Exception:
            pass


class Config:
    """Application configuration for AI Mock Interviewer."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-ai-mock-interviewer-secret-key-2026")
    
    # Storage paths (serverless safe)
    SCORECARD_FOLDER = os.environ.get("SCORECARD_FOLDER", str(DEFAULT_STORAGE / "generated_scorecards"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", str(DEFAULT_STORAGE / "interviews.db"))
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
    
    # Server Port
    PORT = int(os.environ.get("PORT", 5001))
    
    APP_NAME = "AI Mock Technical Interviewer & Code Evaluator"
    VERSION = "1.0.0"


# Ensure runtime directory exists
try:
    os.makedirs(Config.SCORECARD_FOLDER, exist_ok=True)
except Exception:
    pass
