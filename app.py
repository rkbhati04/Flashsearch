"""
Flask Web API & Frontend Server for FlashSearch
"""
from flask import Flask, request, jsonify, render_template
from indexer import build_index
from search_engine import SearchEngine

# ─── Initialize ─────────────────────────────────────────────
app = Flask(__name__)

print("Loading corpus and building index...")
inverted_index, documents = build_index()
engine = SearchEngine(inverted_index, documents)
stats = engine.get_stats()
print(f"Ready: {stats['total_documents']} docs, {stats['total_tokens']} tokens\n")


# ─── Frontend ────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    """Serve the search UI."""
    return render_template("index.html")


# ─── API Endpoints ───────────────────────────────────────────
@app.route("/api", methods=["GET"])
def api_info():
    """API documentation endpoint."""
    return jsonify({
        "name": "FlashSearch API",
        "version": "2.0.0",
        "description": "Full-text search engine with TF-IDF ranking",
        "endpoints": {
            "GET /": "Search UI",
            "GET /api": "This help message",
            "GET /api/stats": "Index and cache statistics",
            "POST /api/search": "Search documents (AND query)",
            "POST /api/search/or": "Search documents (OR query)",
            "GET /api/document/<id>": "Get full document by ID",
            "GET /api/health": "Health check",
        },
    })


@app.route("/api/stats", methods=["GET"])
def get_stats():
    """Get index and cache statistics."""
    return jsonify(engine.get_stats())


@app.route("/api/search", methods=["POST"])
def search():
    """
    AND search — all terms must match.

    JSON body:
        {"query": "search terms", "limit": 20, "offset": 0}
    """
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field"}), 400

    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    limit = min(int(data.get("limit", 20)), 100)
    offset = max(int(data.get("offset", 0)), 0)

    result = engine.search(query, limit=limit, offset=offset)
    return jsonify(result)


@app.route("/api/search/or", methods=["POST"])
def search_or():
    """
    OR search — any term can match.

    JSON body:
        {"query": "search terms", "limit": 20, "offset": 0}
    """
    data = request.get_json()

    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' field"}), 400

    query = data.get("query", "").strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    limit = min(int(data.get("limit", 20)), 100)
    offset = max(int(data.get("offset", 0)), 0)

    result = engine.search_or(query, limit=limit, offset=offset)
    return jsonify(result)


@app.route("/api/document/<int:doc_id>", methods=["GET"])
def get_document(doc_id):
    """Get full document by ID."""
    if doc_id < 1 or doc_id > len(documents):
        return jsonify({"error": "Document not found"}), 404

    doc = documents[doc_id - 1]
    return jsonify(doc)


@app.route("/api/health", methods=["GET"])
def health():
    """Health check for deployment monitoring."""
    return jsonify({
        "status": "healthy",
        "documents": stats["total_documents"],
        "tokens": stats["total_tokens"],
    })


# ─── Error Handlers ──────────────────────────────────────────
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ─── Run ─────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"FlashSearch API — http://127.0.0.1:5000")
    print(f"Endpoints: POST /api/search | POST /api/search/or\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
