# ============================================================
#  parser.py (CLEAN + FINAL)
# ============================================================

import os
import json
import fitz
import docx
import pandas as pd

# ============================================================
# ✅ RESUME PARSING
# ============================================================

def parse_pdf(file_path: str) -> str:
    text = ""
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"  [PDF error] {file_path}: {e}")
    return text.strip()


def parse_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"  [DOCX error] {file_path}: {e}")
    return text.strip()


def parse_doc(file_path: str) -> str:
    try:
        return parse_docx(file_path)
    except:
        try:
            with open(file_path, "rb") as f:
                raw = f.read()
            text = raw.decode("latin-1", errors="ignore")
            lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 10]
            return "\n".join(lines)
        except Exception as e:
            print(f"  [DOC error] {file_path}: {e}")
            return ""


def parse_resume(file_path: str) -> dict:
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = parse_pdf(file_path)
    elif ext == ".docx":
        text = parse_docx(file_path)
    elif ext == ".doc":
        text = parse_doc(file_path)
    else:
        return None

    if not text:
        return None

    return {
        "name": os.path.basename(file_path),
        "file_path": file_path,
        "text": text
    }


def parse_all_resumes(folder: str) -> list:
    results = []
    files = os.listdir(folder)

    print(f"Parsing {len(files)} resume files...")

    for fname in files:
        path = os.path.join(folder, fname)
        parsed = parse_resume(path)
        if parsed:
            results.append(parsed)

    print(f"  Successfully parsed {len(results)} resumes.")
    return results


# ============================================================
# ✅ JOB REQUIREMENT (JR) PARSING
# ============================================================

def extract_job_title(text):
    lines = text.split("\n")
    for line in lines[:10]:
        line = line.strip()
        if 5 < len(line) < 100:
            return line
    return "Unknown"


# ✅ CSV
def parse_csv(file_path):
    results = []
    df = pd.read_csv(file_path)

    for i, row in df.iterrows():
        text = " ".join(str(x) for x in row.values if pd.notnull(x))

        results.append({
            "job_id": f"{os.path.basename(file_path)}_{i}",
            "job_title": extract_job_title(text),
            "jr_text": text
        })

    return results


# ✅ JSON
def parse_json(file_path):
    results = []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = [data]

    for i, item in enumerate(data):
        text = " ".join(str(v) for v in item.values() if v)

        results.append({
            "job_id": f"{os.path.basename(file_path)}_{i}",
            "job_title": extract_job_title(text),
            "jr_text": text
        })

    return results


# ✅ TXT
def parse_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    return {
        "job_id": os.path.basename(file_path),
        "job_title": extract_job_title(text),
        "jr_text": text
    }


# ✅ MAIN JR PARSER
def parse_jr(file_path: str):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".json":
        return parse_json(file_path)

    elif ext == ".csv":
        return parse_csv(file_path)

    elif ext == ".txt":
        jr = parse_txt(file_path)
        return [jr] if jr else []

    else:
        print(f"  [Skip JR] Unsupported format: {file_path}")
        return []


# ✅ PARSE ALL JRs
def parse_all_jrs(folder: str) -> list:
    results = []
    files = os.listdir(folder)

    print(f"Parsing {len(files)} JR files...")

    for fname in files:
        path = os.path.join(folder, fname)

        parsed_list = parse_jr(path)

        for item in parsed_list:
            if item and item.get("jr_text"):
                results.append(item)

    print(f"  Successfully parsed {len(results)} JRs.")
    return results