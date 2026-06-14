# Knowledge Graph Builder

An AI-powered web application that extracts entities and relationships from unstructured text and generates interactive Knowledge Graphs using Google's Gemini 2.5 Flash model.

## Features
- **Entity & Relationship Extraction:** Leverages Gemini 2.5 Flash to accurately parse unstructured text.
- **Interactive Visualization:** Uses PyVis to generate dynamic, physics-based network graphs.
- **Graph Statistics:** Calculates node count, edge count, unique entity types, and graph density.
- **Export Options:** Download the visual graph as a PNG or export the relationship data as a CSV.
- **Session History:** Keeps track of your 5 most recent analyses in the sidebar.
- **Modern Dashboard:** Fully responsive, dark-themed UI with glassmorphism effects and clean tables.

## Folder Structure
```text
KnowledgeGraphBuilder/
│
├── app.py                  # Main Flask application and routing
├── gemini_extractor.py     # Gemini API integration and prompt engineering
├── graph_builder.py        # NetworkX, PyVis, Matplotlib, and Pandas logic
├── requirements.txt        # Python dependencies
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore rules
├── README.md               # Project documentation
│
├── templates/
│   └── index.html          # Main HTML dashboard
│
├── static/
│   ├── style.css           # UI Styling (Dark Theme)
│   └── script.js           # Frontend logic and API calls
│
├── graphs/                 # Auto-generated PyVis HTML graphs (created at runtime)
└── exports/                # Auto-generated PNGs and CSVs (created at runtime)