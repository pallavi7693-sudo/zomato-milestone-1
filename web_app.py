"""
GastroAI Web Application
Flask server serving the premium frontend and REST API endpoints.
Reuses existing src/ modules for filter_engine, recommendation_engine, etc.
"""
import os
import sys
import time
import sqlite3
import json
import math
import logging

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Ensure src directory is in path
sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(__file__)), "src"))
from recommendation_engine import RecommendationEngine
from filter_engine import get_candidates
from config import DB_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gastroai_web")

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (allow all origins for now, we can restrict this later to the vercel domain)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize recommendation engine (singleton)
engine = RecommendationEngine()


# ─── Helper Functions ───────────────────────────────────────────────────────────

def get_unique_locations():
    """Queries unique locations from the database dynamically."""
    if not os.path.exists(DB_PATH):
        return ["Jayanagar", "Banashankari", "Basavanagudi", "JP Nagar",
                "Koramangala", "Indiranagar"]
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT location FROM restaurants ORDER BY location")
        locs = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return locs
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        return ["Jayanagar", "Banashankari", "Basavanagudi", "JP Nagar",
                "Koramangala", "Indiranagar"]


def get_unique_cuisines():
    """Queries unique cuisines from the database, splitting pipe-separated values."""
    if not os.path.exists(DB_PATH):
        return ["Italian", "Chinese", "Biryani", "North Indian", "South Indian",
                "Fast Food", "Continental", "Desserts", "Bakery", "Beverages",
                "Street Food", "Cafe", "Burger", "Pizza", "Mughlai"]
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT cuisines FROM restaurants WHERE cuisines IS NOT NULL")
        all_cuisines = set()
        for row in cursor.fetchall():
            if row[0]:
                # Split pipe-separated or comma-separated cuisines
                for c in row[0].replace("|", ",").split(","):
                    cleaned = c.strip()
                    if cleaned:
                        all_cuisines.add(cleaned)
        conn.close()
        return sorted(list(all_cuisines))
    except Exception as e:
        logger.error(f"Error fetching cuisines: {e}")
        return ["Italian", "Chinese", "Biryani", "North Indian", "South Indian",
                "Fast Food", "Continental"]


def get_restaurant_types():
    """Queries unique restaurant types from the database."""
    if not os.path.exists(DB_PATH):
        return ["Casual Dining", "Fine Dining", "Cafe", "Pub", "Bar",
                "Lounge", "Quick Bites"]
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT restaurant_type FROM restaurants WHERE restaurant_type IS NOT NULL")
        all_types = set()
        for row in cursor.fetchall():
            if row[0]:
                for t in row[0].replace("|", ",").split(","):
                    cleaned = t.strip()
                    if cleaned:
                        all_types.add(cleaned)
        conn.close()
        return sorted(list(all_types))
    except Exception as e:
        logger.error(f"Error fetching restaurant types: {e}")
        return ["Casual Dining", "Fine Dining", "Cafe", "Pub", "Bar",
                "Lounge", "Quick Bites"]


def build_card_details(recs):
    """Enriches recommendation results with full DB row details for card rendering."""
    if not recs or not os.path.exists(DB_PATH):
        return recs

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for r in recs:
            name = r.get("restaurant_name", "")
            cursor.execute(
                "SELECT * FROM restaurants WHERE name = ? COLLATE NOCASE",
                (name,)
            )
            row = cursor.fetchone()
            if row:
                row_dict = dict(row)
                r["cuisines"] = row_dict.get("cuisines", "").replace("|", ", ")
                r["cost"] = row_dict.get("cost", 0)
                r["rating"] = row_dict.get("rating", 0.0)
                r["votes"] = row_dict.get("votes", 0)
                r["location"] = row_dict.get("location", "")
                r["restaurant_type"] = row_dict.get("restaurant_type", "")
                r["online_order"] = bool(row_dict.get("online_order", 0))
                r["book_table"] = bool(row_dict.get("book_table", 0))

        conn.close()
    except Exception as e:
        logger.error(f"Error enriching card details: {e}")

    return recs


# ─── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the main frontend page."""
    return render_template("index.html")


@app.route("/api/locations", methods=["GET"])
def api_locations():
    """Return unique locations from the database."""
    locations = get_unique_locations()
    return jsonify({"locations": locations})


@app.route("/api/cuisines", methods=["GET"])
def api_cuisines():
    """Return unique cuisines from the database."""
    cuisines = get_unique_cuisines()
    return jsonify({"cuisines": cuisines})


@app.route("/api/restaurant-types", methods=["GET"])
def api_restaurant_types():
    """Return unique restaurant types from the database."""
    types = get_restaurant_types()
    return jsonify({"types": types})


@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """AI Assistant mode — takes free text query, returns ranked recommendations."""
    data = request.get_json()
    query = data.get("query", "")
    limit = data.get("limit", 5)

    if not query.strip():
        return jsonify({"error": "Query text is required."}), 400

    try:
        start = time.perf_counter()
        res = engine.recommend(query, limit=limit)
        total_ms = (time.perf_counter() - start) * 1000.0

        recs = res.get("recommendations", [])
        recs = build_card_details(recs)

        meta = res.get("metadata", {})
        parsed_filters = meta.get("parsed_filters", {})

        return jsonify({
            "recommendations": recs,
            "summary": res.get("recommendation_summary", ""),
            "parsed_filters": {k: v for k, v in parsed_filters.items()
                               if v is not None and v != []},
            "relaxation_applied": meta.get("relaxation_applied", False),
            "original_constraints": meta.get("original_constraints"),
            "final_constraints": meta.get("final_constraints"),
            "fallback_applied": meta.get("fallback_applied", False),
            "timings": meta.get("timings", {}),
            "total_ms": round(total_ms, 2),
            "candidate_count": meta.get("candidate_count", 0)
        })
    except Exception as e:
        logger.error(f"Recommendation error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/filter", methods=["POST"])
def api_filter():
    """Filter Search mode — takes structured filter JSON, returns ranked results."""
    data = request.get_json()

    location = data.get("location", "Jayanagar")
    cuisines = data.get("cuisines", [])
    min_rating = float(data.get("min_rating", 0.0))
    max_budget = data.get("max_budget")
    min_budget = data.get("min_budget")
    online_order = data.get("online_order")
    book_table = data.get("book_table")
    restaurant_type = data.get("restaurant_type", [])
    limit = int(data.get("limit", 5))
    sort_by = data.get("sort_by", "match_score")
    num_people = int(data.get("num_people", 2))

    if max_budget is not None:
        max_budget = float(max_budget)
    if min_budget is not None:
        min_budget = float(min_budget)

    # Scale budget for DB query: DB stores cost-for-two, so if user specifies
    # a total budget for N people, convert to per-two-people equivalent.
    db_max_budget = max_budget
    db_min_budget = min_budget
    if num_people and num_people > 0 and num_people != 2:
        if db_max_budget is not None:
            db_max_budget = db_max_budget * 2.0 / num_people
        if db_min_budget is not None:
            db_min_budget = db_min_budget * 2.0 / num_people

    try:
        start = time.perf_counter()

        # 1. Filter Engine
        t0_db = time.perf_counter()
        candidates_data = get_candidates(
            location=location,
            cuisines=cuisines,
            min_rating=min_rating,
            min_budget=db_min_budget,
            max_budget=db_max_budget,
            online_order=online_order if online_order else None,
            book_table=book_table if book_table else None,
            restaurant_type=restaurant_type,
            max_candidates=50
        )
        db_ms = (time.perf_counter() - t0_db) * 1000.0

        candidates = candidates_data.get("results", [])
        relaxation_applied = candidates_data.get("relaxation_applied", False)
        location_relaxed = candidates_data.get("location_relaxed", False)
        searched_locations = candidates_data.get("searched_locations", [location])

        # 2. Rank candidates (Deterministic for Filter Search)
        t0_rank = time.perf_counter()
        filters = {
            "location": location,
            "cuisines": cuisines,
            "min_rating": min_rating,
            "min_budget": min_budget,
            "max_budget": max_budget,
            "online_order": online_order if online_order else None,
            "book_table": book_table if book_table else None,
            "restaurant_type": restaurant_type,
            "num_people": num_people
        }

        fallback_applied = False
        # Filter search should be deterministic, so we skip the LLM ranking
        # and strictly rank candidates by our match formula.
        ranked_result = engine._rank_with_heuristics(
            filters, candidates, limit
        )

        rank_ms = (time.perf_counter() - t0_rank) * 1000.0
        total_ms = (time.perf_counter() - start) * 1000.0

        recs = ranked_result.get("recommendations", [])
        recs = build_card_details(recs)

        return jsonify({
            "recommendations": recs,
            "summary": ranked_result.get("recommendation_summary", ""),
            "relaxation_applied": relaxation_applied,
            "location_relaxed": location_relaxed,
            "searched_locations": searched_locations,
            "original_constraints": candidates_data.get("original_constraints"),
            "final_constraints": candidates_data.get("final_constraints"),
            "fallback_applied": fallback_applied,
            "candidate_count": len(candidates),
            "num_people": num_people,
            "timings": {
                "db_query_ms": round(db_ms, 2),
                "llm_ranking_ms": round(rank_ms, 2),
                "total_ms": round(total_ms, 2)
            }
        })
    except Exception as e:
        logger.error(f"Filter error: {e}")
        return jsonify({"error": str(e)}), 500


# ─── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Starting GastroAI Web Application...")
    logger.info(f"Database path: {DB_PATH}")
    app.run(debug=True, host="0.0.0.0", port=5000)
