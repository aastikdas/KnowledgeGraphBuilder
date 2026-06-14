import os
from flask import Flask, render_template, request, jsonify, session, send_from_directory
from dotenv import load_dotenv
from gemini_extractor import extract_knowledge_graph
from graph_builder import process_graph_data

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret_key_for_dev")

# Ensure required directories exist
os.makedirs("graphs", exist_ok=True)
os.makedirs("exports", exist_ok=True)

@app.route("/")
def index():
    # Initialize session history if it doesn't exist
    if 'history' not in session:
        session['history'] = []
    return render_template("index.html", history=session['history'])

@app.route("/api/analyze", methods=["POST"])
def analyze_text():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # 1 & 2. Extract Entities and Relationships using Gemini
        kg_json = extract_knowledge_graph(text)
        
        if "error" in kg_json:
            return jsonify({"error": kg_json["error"]}), 500

        # 3 & 4 & Bonus. Build Graph, calculate stats, and generate exports
        graph_assets = process_graph_data(kg_json)

        # 5. Update Session History (Bonus E)
        history_entry = {
            "id": graph_assets["graph_id"],
            "snippet": text[:40] + "..." if len(text) > 40 else text
        }
        
        history = session.get('history', [])
        history.insert(0, history_entry)
        session['history'] = history[:5]  # Keep only last 5
        session.modified = True

        # Combine results to return to frontend
        response_data = {
            "entities": kg_json.get("entities", []),
            "relationships": kg_json.get("relationships", []),
            "stats": graph_assets["stats"],
            "graph_html_url": f"/graphs/{graph_assets['html_filename']}",
            "png_url": f"/exports/{graph_assets['png_filename']}",
            "csv_url": f"/exports/{graph_assets['csv_filename']}"
        }

        return jsonify(response_data)

    except Exception as e:
        print(f"Server Error: {str(e)}")
        return jsonify({"error": "An internal server error occurred while processing the text."}), 500

@app.route("/graphs/<filename>")
def serve_graph(filename):
    """Serve the generated PyVis HTML files"""
    return send_from_directory("graphs", filename)

@app.route("/exports/<filename>")
def serve_export(filename):
    """Serve the generated PNG and CSV export files"""
    return send_from_directory("exports", filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )