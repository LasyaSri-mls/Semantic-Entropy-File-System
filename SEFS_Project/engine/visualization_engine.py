import os
import numpy as np
import networkx as nx
from pyvis.network import Network
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px

from core.db_api import get_all_embeddings


def generate_semantic_galaxy(output_path="visualization/semantic_galaxy.html"):
    """
    Create a 2D semantic space visualization of all files.
    Uses PCA to position files based on embedding similarity.
    """

    print("🌌 Building semantic galaxy...")

    files = get_all_embeddings()

    if not files:
        print("⚠ No embeddings found")
        return

    file_ids = []
    file_names = []
    embeddings = []

    for f in files:
        if f["embedding"] is None:
            continue
        file_ids.append(f["file_id"])
        file_names.append(os.path.basename(f["path"]))
        embeddings.append(np.array(f["embedding"]))

    if len(embeddings) < 2:
        print("⚠ Not enough files to visualize")
        return

    embeddings = np.array(embeddings)

    # ---------- DIMENSION REDUCTION ----------
    pca = PCA(n_components=2)
    coords = pca.fit_transform(embeddings)

    # ---------- BUILD GRAPH ----------
    G = nx.Graph()

    for i, fid in enumerate(file_ids):
        x, y = coords[i]
        G.add_node(
            fid,
            label=file_names[i],
            title=file_names[i],
            x=float(x) * 500,
            y=float(y) * 500,
            physics=False
        )

    # ---------- VISUALIZE ----------
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    net = Network(
        height="800px",
        width="100%",
        bgcolor="#111111",
        font_color="white"
    )

    net.from_nx(G)
    net.show(output_path)

    print(f"✅ Semantic galaxy saved → {output_path}")



def visualize_semantic_space():
    """
    Reduce high-dimensional embeddings to 2D and plot them.
    """

    print("🌐 Building semantic galaxy...")

    data = get_all_embeddings()

    if not data:
        print("⚠ No embeddings found")
        return

    paths = [d["path"] for d in data]
    embeddings = np.array([d["embedding"] for d in data])

    # Reduce dimensions to 2D for visualization
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(5, len(embeddings)-1))
    reduced = tsne.fit_transform(embeddings)

    x = reduced[:, 0]
    y = reduced[:, 1]

    fig = px.scatter(
        x=x,
        y=y,
        text=paths,
        title="SEFS Semantic Galaxy"
    )

    fig.update_traces(textposition="top center")
    fig.write_html("semantic_galaxy.html")

    print("✨ Galaxy generated: semantic_galaxy.html")
    print("Opening in browser...")

    import webbrowser
    webbrowser.open("semantic_galaxy.html")