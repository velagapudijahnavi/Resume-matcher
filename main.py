# ============================================================
#  main.py  — FastAPI application
#  Run with:  uvicorn main:app --reload --port 8000
#
#  Endpoints:
#    POST /setup        → Download from Azure, parse, embed, index
#    POST /employer     → Employer query → matching candidates
#    POST /candidate    → Candidate query → matching JRs
#    GET  /status       → Check if indexes are ready
# ============================================================

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

from azure_loader import download_resumes
from parser import parse_all_resumes, parse_all_jrs
from vector_store import build_resume_index, build_jr_index, load_indexes
from matcher import employer_search, candidate_search
from config import RESUME_LOCAL_DIR, JR_LOCAL_DIR, FAISS_INDEX_PATH

app = FastAPI(title="Resume Matcher API")

# Allow the HTML frontend to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend HTML file at /ui
app.mount("/ui", StaticFiles(directory="../frontend", html=True), name="frontend")


# ── On startup, load indexes if they already exist ──────────

@app.on_event("startup")
def startup_event():
    print("App starting up...")
    idx_exists = os.path.exists(os.path.join(FAISS_INDEX_PATH, "resumes.index"))
    if idx_exists:
        print("Found existing indexes. Loading...")
        load_indexes()
    else:
        print("No indexes found. Call POST /setup to build them.")


# ── Request models ───────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str


# ── Routes ───────────────────────────────────────────────────

@app.get("/status")
def status():
    """Check if indexes are built and ready."""
    resume_ready = os.path.exists(os.path.join(FAISS_INDEX_PATH, "resumes.index"))
    jr_ready = os.path.exists(os.path.join(FAISS_INDEX_PATH, "jrs.index"))
    return {
        "resume_index_ready": resume_ready,
        "jr_index_ready": jr_ready,
        "ready": resume_ready and jr_ready
    }


@app.post("/setup")
def setup():
    """
    Full pipeline setup:
    1. Download files from Azure Blob Storage
    2. Parse all resumes and JRs
    3. Build FAISS indexes

    Call this ONCE when you first deploy, or whenever you add new data.
    This will take several minutes for 100s of files.
    """
    try:
        # Step 1: Download from Azure (single container, auto-sorted by file type)
        download_resumes()

        # Step 2: Parse
        resumes = parse_all_resumes(RESUME_LOCAL_DIR)
        jrs = parse_all_jrs(JR_LOCAL_DIR)

        # ✅ Remove invalid JRs (IMPORTANT FIX)
        clean_jrs = []
        for jr in jrs:
            if (
                jr
                and jr.get("jr_text")
                and isinstance(jr["jr_text"], str)
                and jr["jr_text"].strip() != ""
            ):
                clean_jrs.append(jr)

        jrs = clean_jrs[:100]

        print(f"✅ Clean JRs after filtering: {len(jrs)}")



        if not resumes:
            raise HTTPException(status_code=400, detail="No resumes found or parsed.")
        if not jrs:
            raise HTTPException(status_code=400, detail="No JRs found or parsed.")

        # Step 3: Build FAISS indexes
        build_resume_index(resumes)
        build_jr_index(jrs)

        return {
            "status": "success",
            "resumes_indexed": len(resumes),
            "jrs_indexed": len(jrs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/employer")
def employer_query(req: QueryRequest):
    """
    Employer asks a question → returns matching candidates with AI explanations.
    Example: {"query": "Give me a candidate with 5+ years in finance and Python skills"}
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        results = employer_search(req.query)
        return {"query": req.query, "results": results}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e) + " — Run POST /setup first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/candidate")
def candidate_query(req: QueryRequest):
    """
    Candidate describes themselves → returns matching JRs with AI explanations.
    Example: {"query": "I have 3 years in data science with Python and SQL skills"}
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        results = candidate_search(req.query)
        return {"query": req.query, "results": results}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e) + " — Run POST /setup first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
