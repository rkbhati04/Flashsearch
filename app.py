"""
Flask Web API for FlashSearch
"""
from flask import Flask, request, jsonify
from indexer import build_index
from search_engine import SearchEngine

# Initialize Flask app
app = Flask(__name__)

# Build index on startup
inverted_index, documents = build_index()
engine = SearchEngine(inverted_index, documents)

# Get statistics
stats = engine.get_stats()


@app.route('/', methods=['GET'])
def home():
    """Home endpoint - API information"""
    return jsonify({
        "name": "FlashSearch API",
        "version": "1.0.0",
        "description": "Full-text search engine for Wikipedia documents",
        "endpoints": {
            "GET /": "This help message",
            "GET /stats": "Index statistics",
            "POST /search": "Search documents (AND query)",
            "POST /search/or": "Search documents (OR query)"
        }
    })


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get index statistics"""
    return jsonify({
        "total_tokens": stats['total_tokens'],
        "total_documents": stats['total_documents']
    })


@app.route('/search', methods=['POST'])
def search():
    """
    Search endpoint - AND search (all terms must match)
    
    Expected JSON:
    {
        "query": "search terms"
    }
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' field"}), 400
    
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    
    results = engine.search(query)
    
    return jsonify({
        "query": query,
        "search_type": "AND",
        "results_count": len(results),
        "results": results
    })


@app.route('/search/or', methods=['POST'])
def search_or():
    """
    OR Search endpoint - any term can match
    
    Expected JSON:
    {
        "query": "search terms"
    }
    """
    data = request.get_json()
    
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' field"}), 400
    
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    
    results = engine.search_or(query)
    
    return jsonify({
        "query": query,
        "search_type": "OR",
        "results_count": len(results),
        "results": results
    })


@app.route('/document/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    """Get full document by ID"""
    if doc_id < 1 or doc_id > len(documents):
        return jsonify({"error": "Document not found"}), 404
    
    doc = documents[doc_id - 1]  # doc_id is 1-indexed
    return jsonify(doc)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print(f"FlashSearch API Server")
    print(f"Loaded {stats['total_documents']} documents with {stats['total_tokens']} unique tokens")
    print(f"Starting server on http://127.0.0.1:5000")
    print(f"Use POST /search or POST /search/or to search\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)

