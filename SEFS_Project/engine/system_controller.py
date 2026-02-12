from engine.semantic_engine import build_semantic_space, visualize_semantic_graph
from engine.clustering_engine import cluster_files
from os_sync.folder_manager import create_semantic_folders


def rebuild_semantic_system():
    """
    Master controller that keeps OS, DB, and semantic structure synchronized.
    This is the brain of SEFS.
    """

    print("\n🌌 Rebuilding semantic filesystem...")

    # 1️⃣ Build semantic similarity network
    graph = build_semantic_space(threshold=0.6)

    # 2️⃣ Compute conceptual clusters
    cluster_assignments = cluster_files(graph, distance_threshold=0.5)

    # 3️⃣ Sync OS folders with semantic clusters
    create_semantic_folders(cluster_assignments)

    # 4️⃣ Refresh interactive visualization
    visualize_semantic_graph(threshold=0.6)

    print("✅ SEFS structure synchronized\n")
