
import numpy as np
from engine.semantic_engine import generate_embedding, cosine_similarity
from core.db_api import get_all_embeddings


# ---------------- SEMANTIC SEARCH ----------------

def semantic_search(query, top_k=5):
    """
    Find files most semantically similar to the query.
    Returns ranked list of (file_path, similarity).
    """

    print("🔎 Understanding query...")
    query_embedding = generate_embedding(query)

    if query_embedding is None:
        print("⚠ Could not understand query")
        return []

    all_files = get_all_embeddings()

    if not all_files:
        print("⚠ No indexed files found")
        return []

    results = []

    for file in all_files:
        score = cosine_similarity(query_embedding, file["embedding"])
        results.append((file["path"], float(score)))

    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)

    return results[:top_k]


# ---------------- PRINT RESULTS ----------------

def print_search_results(query, top_k=5):
    results = semantic_search(query, top_k)

    if not results:
        print("No relevant files found.")
        return

    print("\n📄 Most relevant files:\n")

    for i, (path, score) in enumerate(results, start=1):
        print(f"{i}. {path}")
        print(f"   similarity: {score:.3f}")
