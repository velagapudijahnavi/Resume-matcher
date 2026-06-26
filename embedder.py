# ============================================================
#  embedder.py
#  Converts text (resumes, JRs, user queries) into vectors
#  using YOUR Azure OpenAI embedding deployment.
# ============================================================

from openai import AzureOpenAI
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_API_VERSION,
    AZURE_EMBED_DEPLOYMENT,
)
import numpy as np

# Create one Azure OpenAI client to reuse for every request.
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
)


def embed_text(text: str) -> np.ndarray:
    """
    Convert a single text string into a vector (1D numpy array).
    Used for user queries at search time.
    """
    # Azure OpenAI embedding inputs have a token limit (~8000 tokens for ada-002).
    # We trim very long resumes to be safe.
    text = text[:20000]

    response = client.embeddings.create(
        model=AZURE_EMBED_DEPLOYMENT,   # this must be your DEPLOYMENT name, not the raw model name
        input=text
    )
    vector = response.data[0].embedding
    return np.array(vector, dtype="float32")


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Convert a list of texts into a 2D array of vectors.
    Used during indexing (batch processing all resumes/JRs).
    We send them in small batches to avoid hitting request size limits.
    """
    all_vectors = []
    batch_size = 16

    for i in range(0, len(texts), batch_size):
        batch = [t[:20000] for t in texts[i:i + batch_size]]
        response = client.embeddings.create(
            model=AZURE_EMBED_DEPLOYMENT,
            input=batch
        )
        for item in response.data:
            all_vectors.append(item.embedding)
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)}")

    return np.array(all_vectors, dtype="float32")
