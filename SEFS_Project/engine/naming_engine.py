import os
from core.db_api import get_files_in_cluster
from engine.content_engine import extract_text


def generate_cluster_name(cluster_id):
    """
    Generate a human-readable name for a semantic cluster.
    Strategy:
    - Collect text from files in cluster
    - Extract most common keywords
    - Use them as folder name
    """

    files = get_files_in_cluster(cluster_id)

    if not files:
        return "Empty Cluster"

    combined_text = ""

    for path in files[:5]:  # limit for performance
        if os.path.exists(path):
            text = extract_text(path)
            if text:
                combined_text += " " + text.lower()

    if not combined_text:
        return "Uncategorized"

    # Simple keyword frequency
    words = combined_text.split()
    freq = {}

    for w in words:
        if len(w) < 4:
            continue
        freq[w] = freq.get(w, 0) + 1

    if not freq:
        return "General"

    top_words = sorted(freq, key=freq.get, reverse=True)[:2]
    name = "_".join(top_words)

    return name.capitalize()
