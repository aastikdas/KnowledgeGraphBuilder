import os
import uuid
import networkx as nx
from pyvis.network import Network
import pandas as pd
import matplotlib
# Use Agg backend for matplotlib to prevent GUI thread issues in Flask
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def process_graph_data(kg_data):
    """
    Takes the parsed JSON knowledge graph, builds a NetworkX graph, calculates stats,
    generates a PyVis HTML interactive graph, a Matplotlib PNG, and a Pandas CSV.
    """
    graph_id = str(uuid.uuid4())[:8]
    
    entities = kg_data.get("entities", [])
    relationships = kg_data.get("relationships", [])

    # 1. Build NetworkX Graph
    G = nx.DiGraph()
    
    # Track unique entity types for stats
    entity_types = set()
    
    # Add Nodes
    for ent in entities:
        name = ent.get("name")
        ent_type = ent.get("type", "Unknown")
        entity_types.add(ent_type)
        if name:
            # Assign colors based on common types just to make it pretty
            color = "#4CAF50" # Default green
            if ent_type.lower() in ["person", "individual"]: color = "#2196F3"
            elif ent_type.lower() in ["organization", "company"]: color = "#FF9800"
            elif ent_type.lower() in ["location", "place"]: color = "#F44336"
            
            G.add_node(name, title=ent_type, color=color, label=name)

    # Add Edges
    for rel in relationships:
        source = rel.get("source")
        target = rel.get("target")
        relation = rel.get("relation")
        if source and target and relation:
            # Ensure nodes exist even if missed in entity extraction
            if not G.has_node(source): G.add_node(source, title="Unknown", color="#9E9E9E")
            if not G.has_node(target): G.add_node(target, title="Unknown", color="#9E9E9E")
            G.add_edge(source, target, label=relation)

    # 2. Calculate Statistics (Bonus D)
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    
    # Directed graph density formula: E / (V * (V - 1))
    density = nx.density(G) if num_nodes > 1 else 0

    stats = {
        "total_entities": num_nodes,
        "total_relationships": num_edges,
        "unique_types": len(entity_types),
        "density": round(density, 3)
    }

    # 3. Generate PyVis Interactive Graph
    net = Network(height="400px", width="100%", bgcolor="#1e1e2e", font_color="white", directed=True)
    net.from_nx(G)
    
    # Add physics options for smooth interaction
    net.set_options("""
    var options = {
      "physics": {
        "forceAtlas2Based": {
          "gravitationalConstant": -50,
          "centralGravity": 0.01,
          "springLength": 100,
          "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
      }
    }
    """)
    html_filename = f"graph_{graph_id}.html"
    html_path = os.path.join("graphs", html_filename)
    net.save_graph(html_path)

    # 4. Export as PNG using Matplotlib (Bonus A)
    png_filename = f"export_{graph_id}.png"
    png_path = os.path.join("exports", png_filename)
    
    plt.figure(figsize=(10, 8), facecolor='#1e1e2e')
    ax = plt.gca()
    ax.set_facecolor('#1e1e2e')
    
    pos = nx.spring_layout(G, k=1.5, seed=42)
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=2000, ax=ax)
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=10, font_color='black', font_weight='bold', ax=ax)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='white', ax=ax)
    
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='#1e1e2e')
    plt.close()

    # 5. Export Relationships as CSV using Pandas (Bonus B)
    csv_filename = f"relationships_{graph_id}.csv"
    csv_path = os.path.join("exports", csv_filename)
    if relationships:
        df = pd.DataFrame(relationships)
        # Ensure column order
        df = df[['source', 'relation', 'target']]
        df.to_csv(csv_path, index=False)
    else:
        # Create empty CSV with headers if no relationships
        pd.DataFrame(columns=['source', 'relation', 'target']).to_csv(csv_path, index=False)

    return {
        "graph_id": graph_id,
        "html_filename": html_filename,
        "png_filename": png_filename,
        "csv_filename": csv_filename,
        "stats": stats
    }