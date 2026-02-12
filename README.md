# 🌌 SEFS — Semantic File System
---
## 🧠 Description

SEFS (Semantic File System) automatically organizes files based on their **meaning**, not just filenames or folders.

The system watches a root directory, extracts content from files, generates semantic embeddings using AI, clusters similar files together, and organizes them into semantic folders. It also creates an interactive visualization showing relationships between files.

This creates a **self-organizing intelligent filesystem**.

---

## 🧰 Tech Stack

- Python 3.12  
- TensorFlow / Transformers  
- scikit-learn  
- SQLite  
- Watchdog (file monitoring)  
- Network visualization (HTML graph)  
- NumPy / SciPy  

---

## 📁 Project Structure

```
SEFS_Project/
│
├── core/
│   ├── config.py
│   ├── database.py
│   └── db_api.py
│
├── engine/
│   ├── content_engine.py
│   ├── semantic_engine.py
│   ├── clustering_engine.py
│   ├── event_engine.py
│   ├── naming_engine.py
│   └── system_controller.py
│
├── os_sync/
│   └── folder_manager.py
│
├── main.py
└── README.md
```

---

## ⚙️ How to Run the Project

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/sefs-project.git
cd sefs-project
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure root folder

Edit:

```
core/config.py
```

Set:
```python
ROOT_FOLDER = r"C:\SEFS_Root"
DATABASE_PATH = "sefs.db"
```

Create the root folder manually.

---

### 4️⃣ Run SEFS
```bash
python main.py
```

SEFS will:

- initialize database  
- scan existing files  
- generate embeddings  
- cluster files  
- create semantic folders  
- generate visualization  
- start live monitoring  

---

## 📦 Dependencies

Create `requirements.txt` with:

```
tensorflow
numpy
scikit-learn
watchdog
networkx
matplotlib
transformers
```

Install with:
```bash
pip install -r requirements.txt
```

---

## ❗ Important Instructions

- Only supported file types are processed  
- Files must contain readable text  
- Visualization is generated as an HTML file  
- Do not manually edit semantic folders created by SEFS  
- Database file `sefs.db` is auto-generated  

If database errors occur:
```bash
delete sefs.db and rerun
```


## 💡 Future Improvements

- Natural language search  
- Web dashboard  
- Better clustering tuning  
- Multi-modal file support  
- Cloud storage support  
- Real-time graph UI  

