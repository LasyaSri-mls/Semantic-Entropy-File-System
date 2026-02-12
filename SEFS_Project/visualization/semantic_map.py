import sys
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from core.db_api import get_all_embeddings, get_file_path_by_id
from engine.semantic_engine import build_semantic_space

class SemanticMapWindow(QMainWindow):
    def __init__(self, threshold=0.6):
        super().__init__()
        self.setWindowTitle("SEFS Semantic Map")
        self.resize(900, 700)
        self.threshold = threshold

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Info label
        self.info_label = QLabel("Hover on a node to see file path")
        self.layout.addWidget(self.info_label)

        # Matplotlib figure
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.build_graph()

    def build_graph(self):
        self.ax.clear()

        # Build semantic graph
        adjacency = build_semantic_space(threshold=self.threshold)
        G = nx.Graph()

        # Add nodes and edges
        for file_id, neighbors in adjacency.items():
            file_path = get_file_path_by_id(file_id)
            G.add_node(file_id, label=file_path)
            for neighbor_id, sim in neighbors:
                G.add_edge(file_id, neighbor_id, weight=sim)

        # Layout
        pos = nx.spring_layout(G, seed=42)  # force-directed layout

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color="skyblue", node_size=500)
        nx.draw_networkx_edges(G, pos, ax=self.ax, alpha=0.5)
        nx.draw_networkx_labels(G, pos, {n: n[:6] for n in G.nodes()}, font_size=8)

        # Refresh canvas
        self.canvas.draw()

# ---------------- MAIN ----------------
def run_semantic_map(threshold=0.6):
    app = QApplication(sys.argv)
    window = SemanticMapWindow(threshold=threshold)
    window.show()
    sys.exit(app.exec_())

# For testing
if __name__ == "__main__":
    run_semantic_map()
