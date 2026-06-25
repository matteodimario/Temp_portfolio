from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import torch

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Load model
model = SentenceTransformer("./fine_tuned_model", device="cpu")
website_embeddings = torch.load("./website_embeddings.pt", map_location=torch.device("cpu"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route("/api/retrieve", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query", "")
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        query_embedding = model.encode(query, convert_to_tensor=True)
        similarities = {
            url: util.pytorch_cos_sim(query_embedding, emb).item()
            for url, emb in website_embeddings.items()
        }
        top_websites = sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:5]
        return jsonify({"websites": [url for url, _ in top_websites]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)