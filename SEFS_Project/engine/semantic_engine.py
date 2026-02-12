# engine/semantic_engine.py

import os
import numpy as np
import networkx as nx
from pyvis.network import Network
from sentence_transformers import SentenceTransformer
from core.db_api import get_all_embeddings


# ------------------- LOAD MODEL -------------------
model = SentenceTransformer("all-MiniLM-L6-v2")


# ------------------- EMBEDDING FUNCTIONS -------------------
def generate_embedding(text):
    """
    Convert text into semantic vector.
    """
    if not text or len(text.strip()) == 0:
        return None
    return model.encode(text)


def cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    """
    if vec1 is None or vec2 is None:
        return 0.0

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    denom = np.linalg.norm(vec1) * np.linalg.norm(vec2)
    if denom == 0:
        return 0.0

    return float(np.dot(vec1, vec2) / denom)


# ------------------- SEMANTIC SPACE -------------------
def build_semantic_space(threshold=0.6):
    """
    Build adjacency dictionary of semantic similarity.
    Returns:
        {file_id: [(neighbor_id, similarity), ...]}
    """
    all_files = get_all_embeddings()

    # Remove files without embeddings
    all_files = [f for f in all_files if f["embedding"] is not None]

    adjacency = {}
    n = len(all_files)

    for i in range(n):
        file_i = all_files[i]
        adjacency[file_i["file_id"]] = []

        for j in range(i + 1, n):  # avoid duplicate comparisons
            file_j = all_files[j]

            sim = cosine_similarity(
                file_i["embedding"],
                file_j["embedding"]
            )

            if sim >= threshold:
                adjacency[file_i["file_id"]].append((file_j["file_id"], sim))
                adjacency.setdefault(file_j["file_id"], []).append((file_i["file_id"], sim))

    return adjacency


# ------------------- INTERACTIVE GRAPH -------------------
def visualize_semantic_graph(threshold=0.6, output_path="visualization/semantic_graph.html"):
    """
    Create interactive browser graph of semantic relationships.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    adjacency = build_semantic_space(threshold)
    all_files = get_all_embeddings()
    file_info = {f["file_id"]: f["path"] for f in all_files}

    G = nx.Graph()

    # Add nodes
    for fid, path in file_info.items():
        label = os.path.basename(path)
        G.add_node(fid, title=path, label=label)

    # Add edges
    for fid, neighbors in adjacency.items():
        for neighbor_id, sim in neighbors:
            if not G.has_edge(fid, neighbor_id):
                G.add_edge(fid, neighbor_id, value=sim, title=f"Similarity: {sim:.2f}")

    net = Network(
        height="750px",
        width="100%",
        bgcolor="#111111",
        font_color="white",
        notebook=False
    )

    net.from_nx(G)
    net.show_buttons(filter_=["physics"])
    net.write_html(output_path, open_browser=True)

    print(f"Interactive semantic graph opened → {output_path}")


# ------------------- DEBUG PRINT -------------------
def print_semantic_graph(threshold=0.6):
    adjacency = build_semantic_space(threshold)
    for file_id, neighbors in adjacency.items():
        neighbor_str = [(n, round(s, 2)) for n, s in neighbors]
        print(f"{file_id} -> {neighbor_str}")


# ------------------- MATRIX FOR CLUSTERING -------------------
def semantic_graph_to_matrix(adjacency):
    file_ids = list(adjacency.keys())
    n = len(file_ids)
    sim_matrix = np.zeros((n, n))

    id_to_index = {fid: i for i, fid in enumerate(file_ids)}

    for fid, neighbors in adjacency.items():
        i = id_to_index[fid]
        for neighbor_id, sim in neighbors:
            j = id_to_index[neighbor_id]
            sim_matrix[i, j] = sim

    return sim_matrix, file_ids
