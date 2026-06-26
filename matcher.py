# ============================================================
#  matcher.py (FINAL VERSION WITH REAL JOB TITLES)
# ============================================================

from openai import OpenAI
from embedder import embed_text
from vector_store import search_resumes, search_jrs
from config import OPENAI_API_KEY, OPENAI_ENDPOINT, OPENAI_MODEL, TOP_K
import math

# ✅ OpenAI client
client_kwargs = {"api_key": OPENAI_API_KEY}
if OPENAI_ENDPOINT:
    client_kwargs["base_url"] = OPENAI_ENDPOINT

client = OpenAI(**client_kwargs)


# ✅ SAFE AI EXPLANATION
def explain_match(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful recruitment assistant. Be concise (2-3 sentences)."
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("  [OpenAI error]", e)
        return "Explanation not available"


# ✅ CLEAN NaN
def clean_nan(obj):
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_nan(v) for v in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return 0.0
    return obj


# ✅ EMPLOYER SEARCH
def employer_search(query: str) -> list:
    query_vec = embed_text(query)
    candidates = search_resumes(query_vec, top_k=TOP_K)

    for candidate in candidates:
        try:
            prompt = f"""The employer is looking for: {query}

Here is a candidate's resume summary:
{candidate.get('resume_text', '')[:1500]}

Explain in 2-3 sentences why this candidate is or isn't a strong match."""

            candidate["explanation"] = explain_match(prompt)

        except Exception as e:
            print("Employer AI error:", e)
            candidate["explanation"] = "Explanation not available"

    return clean_nan(candidates)


# ✅ ✅ ✅ FINAL CANDIDATE SEARCH (USES REAL JOB TITLE)
def candidate_search(query: str) -> list:
    try:
        print("Running candidate search...")

        query_vec = embed_text(query)
        jrs = search_jrs(query_vec, top_k=TOP_K)

        results = []

        for jr in jrs:
            try:
                prompt = f"""A candidate described themselves as: {query}

Here is a job requirement:
{jr.get('jr_text', '')[:1500]}

Explain in 2-3 sentences why this job is or isn't a good fit for the candidate."""

                explanation = explain_match(prompt)

            except Exception as e:
                print("AI error:", e)
                explanation = "Explanation not available"

            job_id = jr.get("job_id", "Unknown")

            # ✅ ✅ ✅ REAL TITLE (from parser)
            raw_title = jr.get("job_title") or job_id

            # ✅ clean title
            clean_title = (
                raw_title.replace("(Open)", "")
                         .replace(".json", "")
                         .replace("_", " ")
                         .strip()
            )

            results.append({
                "job_id": job_id,
                "title": clean_title,
                "score": float(jr.get("score", 0)) if jr.get("score") is not None else 0.0,
                "explanation": explanation
            })

        results = clean_nan(results)

        print("Candidate results ready ✅")
        return results

    except Exception as e:
        print("❌ Candidate search crash:", e)
        raise
