import os
import shutil
from core.config import ROOT_FOLDER
from engine.naming_engine import generate_cluster_name


def create_semantic_folders(cluster_assignments):
    """
    Organize files into semantically named folders.
    """

    print("📂 Organizing semantic folders...")

    for cluster_id, files in cluster_assignments.items():

        folder_name = generate_cluster_name(cluster_id)
        cluster_path = os.path.join(ROOT_FOLDER, folder_name)

        os.makedirs(cluster_path, exist_ok=True)

        for file_path in files:
            try:
                filename = os.path.basename(file_path)
                new_path = os.path.join(cluster_path, filename)

                if os.path.abspath(file_path) != os.path.abspath(new_path):
                    shutil.move(file_path, new_path)

            except Exception as e:
                print("Move error:", e)

    print("✅ Semantic folders updated")
