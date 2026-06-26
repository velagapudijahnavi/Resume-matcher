# ============================================================
#  vector_store.py
#  Builds and searches FAISS indexes for resumes and JRs.
#  FAISS is a free, fast library by Meta for vector search.
#  Think of it as a "search engine for embeddings".
# ============================================================

import os
import json
import faiss
import numpy as np
from embedder import embed_texts
from config import FAISS_INDEX_PATH


# We maintain two separate indexes: one for resumes, one for JRs.
# We also store the metadata (name, text, etc.) in parallel lists.

_resume_index    = None
_resume_metadata = []   # list of dicts: [{name, text, file_path}, ...]

_jr_index    = None
_jr_metadata = []       # list of dicts: [{job_id, title, text, raw}, ...]


def build_resume_index(resumes: list):
    """
    Takes a list of parsed resume dicts and builds a FAISS index.
    Saves both the index and metadata to disk.
    """
    global _resume_index, _resume_metadata

    print(f"Building resume index for {len(resumes)} resumes...")
    texts = [r["text"] for r in resumes]
    vectors = embed_texts(texts)

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)          # Inner product = cosine similarity (after normalizing)
    faiss.normalize_L2(vectors)             # Normalize so inner product == cosine similarity
    index.add(vectors)

    _resume_index    = index
    _resume_metadata = resumes

    # Save to disk
    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)
    faiss.write_index(index, os.path.join(FAISS_INDEX_PATH, "resumes.index"))
    with open(os.path.join(FAISS_INDEX_PATH, "resumes_meta.json"), "w") as f:
        # Save only the fields we need (not the full text, to keep it light)
        meta = [{"name": r["name"], "file_path": r["file_path"], "text": r["text"]} for r in resumes]
        json.dump(meta, f)

    print(f"  Resume index built and saved. {index.ntotal} vectors stored.")

def build_jr_index(jrs: list):
    """
    Takes a list of parsed JR dicts and builds a FAISS index.
    """
    global _jr_index, _jr_metadata

    print(f"Building JR index for {len(jrs)} job requirements...")

    # ✅ only keep JRs that actually have text
    filtered_jrs = [j for j in jrs if j.get("jr_text")]

    texts = [j["jr_text"] for j in filtered_jrs]

    try:
        vectors = embed_texts(texts)
    except Exception as e:
        print("❌ JR embedding error:", e)
        return

    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)

    faiss.normalize_L2(vectors)
    index.add(vectors)

    # ✅ IMPORTANT: metadata should match filtered list
    _jr_index = index
    _jr_metadata = filtered_jrs

    os.makedirs(FAISS_INDEX_PATH, exist_ok=True)

    faiss.write_index(index, os.path.join(FAISS_INDEX_PATH, "jrs.index"))

    # ✅ ✅ ✅ FINAL TITLE FIX (NO job_id fallback)
    with open(os.path.join(FAISS_INDEX_PATH, "jrs_meta.json"), "w") as f:
        meta = []

        for j in filtered_jrs:
            raw = j.get("raw", {})

            # ✅ only real titles (no job_id)
            title = (
                j.get("job_title")
                or raw.get("Designation")
                or raw.get("Job_Requisition")
                or "No Title"
            )

            meta.append({
                "job_id": j.get("job_id", ""),
                "title": title,
                "text": j.get("jr_text", ""),
                "raw": raw
            })

        json.dump(meta, f)

    print(f"✅ JR index built and saved. {index.ntotal} vectors stored.")

def load_indexes():
    """Load saved indexes from disk (called on app startup)."""
    global _resume_index, _resume_metadata, _jr_index, _jr_metadata

    resume_idx_path = os.path.join(FAISS_INDEX_PATH, "resumes.index")
    resume_meta_path = os.path.join(FAISS_INDEX_PATH, "resumes_meta.json")
    jr_idx_path = os.path.join(FAISS_INDEX_PATH, "jrs.index")
    jr_meta_path = os.path.join(FAISS_INDEX_PATH, "jrs_meta.json")

    if os.path.exists(resume_idx_path):
        _resume_index = faiss.read_index(resume_idx_path)
        with open(resume_meta_path) as f:
            _resume_metadata = json.load(f)
        print(f"  Loaded resume index: {_resume_index.ntotal} vectors")

    if os.path.exists(jr_idx_path):
        _jr_index = faiss.read_index(jr_idx_path)
        with open(jr_meta_path) as f:
            _jr_metadata = json.load(f)
        print(f"  Loaded JR index: {_jr_index.ntotal} vectors")


def search_resumes(query_vector: np.ndarray, top_k: int = 5) -> list:
    """
    Given a query vector, find the top_k most similar resumes.
    Returns a list of dicts with candidate info + similarity score.
    """
    if _resume_index is None:
        raise RuntimeError("Resume index not loaded. Run build_resume_index first.")

    q = query_vector.reshape(1, -1).astype("float32")
    faiss.normalize_L2(q)
    scores, indices = _resume_index.search(q, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        meta = _resume_metadata[idx]
        results.append({
            "candidate_name": meta["name"],
            "file_path": meta["file_path"],
            "resume_text": meta["text"],
            "score": float(round(score, 4))
        })
    return results


def search_jrs(query_vector: np.ndarray, top_k: int = 5) -> list:
    """
    Given a query vector (from a candidate's resume or question),
    find the top_k most similar job requirements.
    """
    if _jr_index is None:
        raise RuntimeError("JR index not loaded. Run build_jr_index first.")

    q = query_vector.reshape(1, -1).astype("float32")
    faiss.normalize_L2(q)
    scores, indices = _jr_index.search(q, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        meta = _jr_metadata[idx]
        results.append({
            "job_id": meta["job_id"],
            "job_title": meta.get("title", "Unknown"),
            "jr_text": meta.get("text", ""),
            "raw": meta.get("raw", {}),
            "score": float(round(score, 4))
        })
    return results
