# ============================================================
#  config.py
#  Loads all settings from the .env file.
#  You should NOT need to edit this file directly —
#  edit the .env file instead, this file just reads it.
# ============================================================

from dotenv import load_dotenv
import os

# Load the .env file sitting next to this file
load_dotenv()

def get_env(key: str, default: str = None) -> str:
    """Small helper that reads an environment variable and warns if missing."""
    value = os.getenv(key, default)
    if value is None or value.startswith("PASTE_YOUR"):
        print(f"  [WARNING] {key} is not set properly in your .env file!")
    return value


# ---------------------------------------------------------------
# 1) AZURE BLOB STORAGE
# ---------------------------------------------------------------
AZURE_CONNECTION_STRING = get_env("AZURE_STORAGE_CONNECTION_STRING")
RESUME_CONTAINER        = get_env("RESUME_CONTAINER", "resumes")
JR_CONTAINER            = get_env("JR_CONTAINER", "job-requirements")

RESUME_LOCAL_DIR = "data/resumes"
JR_LOCAL_DIR     = "data/jrs"
FAISS_INDEX_PATH = "data/faiss_index"


# ---------------------------------------------------------------
# 2) AZURE OPENAI — used only for EMBEDDINGS
# ---------------------------------------------------------------
AZURE_OPENAI_ENDPOINT    = get_env("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY     = get_env("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = get_env("AZURE_OPENAI_API_VERSION")
AZURE_EMBED_DEPLOYMENT   = get_env("AZURE_EMBED_DEPLOYMENT")


# ---------------------------------------------------------------
# 3) REGULAR OPENAI — used only for AI REASONING / explanations
# ---------------------------------------------------------------
OPENAI_API_KEY     = get_env("OPENAI_API_KEY")
OPENAI_ENDPOINT     = get_env("OPENAI_ENDPOINT")          # base_url for the OpenAI client
OPENAI_API_VERSION  = get_env("OPENAI_API_VERSION")       # only used if your endpoint needs it
OPENAI_MODEL        = get_env("OPENAI_MODEL", "gpt-4o-mini")


# ---------------------------------------------------------------
# General settings
# ---------------------------------------------------------------
TOP_K = 5   # how many results to return per search
