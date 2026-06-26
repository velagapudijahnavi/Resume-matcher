# ============================================================
#  azure_loader.py
#  Downloads resumes and JRs from TWO Azure Blob containers:
#    - resumes-source → resumes
#    - workday-raw    → JRs
# ============================================================

import os
from azure.storage.blob import BlobServiceClient
from config import (
    AZURE_CONNECTION_STRING,
    RESUME_CONTAINER,
    JR_CONTAINER,
    RESUME_LOCAL_DIR,
    JR_LOCAL_DIR
)

RESUME_EXTENSIONS = (".pdf", ".docx", ".doc")

def download_and_sort_all():
    """
    Downloads resumes and JRs from separate containers.
    Saves resumes → data/resumes
    Saves JRs → data/jrs
    """

    os.makedirs(RESUME_LOCAL_DIR, exist_ok=True)
    os.makedirs(JR_LOCAL_DIR, exist_ok=True)

    client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)

    resume_container = client.get_container_client(RESUME_CONTAINER)
    jr_container = client.get_container_client(JR_CONTAINER)

    counts = {"resumes": 0, "jrs": 0, "skipped": 0, "ignored": 0}

    # ================= RESUMES =================
    print("Downloading resumes from Azure...")

    for blob in resume_container.list_blobs():
        name_lower = blob.name.lower()
        flat_name = blob.name.replace("/", "_")

        if not name_lower.endswith(RESUME_EXTENSIONS):
            continue

        local_path = os.path.join(RESUME_LOCAL_DIR, flat_name)

        if os.path.exists(local_path):
            counts["skipped"] += 1
            continue

        blob_client = resume_container.get_blob_client(blob.name)

        with open(local_path, "wb") as f:
            f.write(blob_client.download_blob().readall())

        counts["resumes"] += 1
        print(f"  Downloaded resume: {blob.name}")

    # ================= JRS =================
    print("Downloading JRs from Azure...")

    for blob in jr_container.list_blobs():
        name_lower = blob.name.lower()
        flat_name = blob.name.replace("/", "_")

        # ✅ Allow JSON + CSVs
        if not name_lower.endswith(".json"):
            continue

        local_path = os.path.join(JR_LOCAL_DIR, flat_name)

        if os.path.exists(local_path):
            counts["skipped"] += 1
            continue

        blob_client = jr_container.get_blob_client(blob.name)

        with open(local_path, "wb") as f:
            f.write(blob_client.download_blob().readall())

        counts["jrs"] += 1
        print(f"  Downloaded JR: {blob.name}")

    print(
        f"Done. {counts['resumes']} resumes, {counts['jrs']} JRs downloaded, "
        f"{counts['skipped']} already existed, {counts['ignored']} ignored."
    )

    return counts


# For compatibility with main.py
def download_resumes():
    return download_and_sort_all()


def download_jrs():
    return None
