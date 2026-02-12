import uuid
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from core.db_api import get_all_embeddings, store_cluster, assign_file_to_cluster
from engine.semantic_engine import semantic_graph_to_matrix

# Threshold to assign new embeddings to existing clusters
SIMILARITY_THRESHOLD = 0.75


def assign_cluster(new_embedding):
    """
    Assigns a new file embedding to an existing cluster if similar enough,
    otherwise creates a new cluster.
    """
    existing_files = get_all_embeddings()

    if not existing_files:
        # No existing files → create first cluster
        cluster_id = str(uuid.uuid4())
        store_cluster(cluster_id, "Cluster 1")
        return cluster_id

    best_cluster = None
    best_score = 0

    for file in existing_files:
        score = np.dot(new_embedding, file["embedding"]) / (
            np.linalg.norm(new_embedding) * np.linalg.norm(file["embedding"])
        )

        if score > best_score:
            best_score = score
            best_cluster = file["file_id"]

    if best_score >= SIMILARITY_THRESHOLD:
        return best_cluster

    # Create new cluster
    cluster_id = str(uuid.uuid4())
    store_cluster(cluster_id, f"Cluster {len(existing_files)+1}")
    return cluster_id


def cluster_files(adjacency, distance_threshold=0.5):
    """
    Performs Agglomerative Clustering on the semantic graph and updates the database.

    :param adjacency: adjacency dict from build_semantic_space()
    :param distance_threshold: threshold for clustering (distance)
    :return: dict {file_id: cluster_id}
    """
    if not adjacency:
        return {}

    # Convert adjacency dict to similarity matrix
    sim_matrix, file_ids = semantic_graph_to_matrix(adjacency)

    # Agglomerative clustering expects distances
    distance_matrix = 1 - sim_matrix

    # Handle single file case
    if len(file_ids) == 1:
        cluster_uuid = str(uuid.uuid4())
        store_cluster(cluster_uuid, "Cluster 1")
        assign_file_to_cluster(file_ids[0], cluster_uuid)
        return {file_ids[0]: cluster_uuid}

    # Run clustering (new scikit-learn uses `metric` instead of `affinity`)
    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric="precomputed",  # ✅ replace deprecated affinity
        linkage="average"
    )
    clustering.fit(distance_matrix)

    # Map files to clusters and store in DB
    cluster_assignments = {}
    for file_id, label in zip(file_ids, clustering.labels_):
        cluster_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cluster-{label}"))
        cluster_name = f"Cluster {label+1}"
        store_cluster(cluster_uuid, cluster_name)
        assign_file_to_cluster(file_id, cluster_uuid)
        cluster_assignments[file_id] = cluster_uuid

    return cluster_assignments
