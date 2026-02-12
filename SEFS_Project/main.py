# main.py
import time

from core.database import initialize_database
from engine.event_engine import start_event_engine, bootstrap_existing_files
from core.db_api import debug_show_files
from engine.semantic_engine import (
    build_semantic_space,
    print_semantic_graph,
    visualize_semantic_graph
)
from engine.visualization_engine import visualize_semantic_space

from engine.clustering_engine import cluster_files
from os_sync.folder_manager import create_semantic_folders
from engine.search_engine import print_search_results   # ✅ NEW


def main():
    print("🌌 Initializing SEFS...")
    initialize_database()

    # Scan existing files before live monitoring
    print("📂 Bootstrapping existing files in root folder...")
    bootstrap_existing_files()

    print("🟢 Starting OS live monitoring...")
    start_event_engine()

    print("🔍 Current database state:")
    debug_show_files()

    print("🧠 Computing semantic space...")
    graph = build_semantic_space(threshold=0.6)

    print("Semantic graph adjacency list:")
    print_semantic_graph(threshold=0.6)

    print("📎 Clustering files based on semantic similarity...")
    cluster_assignments = cluster_files(graph, distance_threshold=0.5)
    print("🌐 Launching semantic galaxy...")
    visualize_semantic_space()

    print("🗂 Organizing OS folders into semantic clusters...")
    create_semantic_folders(cluster_assignments)
    print("✅ Files reorganized into semantic folders!")

    print("🌐 Launching interactive semantic map...")
    visualize_semantic_graph(threshold=0.6)

    print("🟢 SEFS is running. Monitoring folder for live changes...")

    # -------- INTERACTIVE SEARCH LOOP --------
    try:
        while True:
            query = input("\nAsk SEFS (or type exit): ")
            if query.lower() == "exit":
                print("🛑 Shutting down SEFS...")
                break

            print_search_results(query, top_k=5)

    except KeyboardInterrupt:
        print("\n🛑 Shutting down SEFS...")


if __name__ == "__main__":
    main()
