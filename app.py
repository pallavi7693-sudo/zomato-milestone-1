import os
import sys
import time
import sqlite3
import streamlit as st

# Ensure src directory is in path
sys.path.append(os.path.abspath("src"))
from recommendation_engine import RecommendationEngine
from filter_engine import get_candidates
from config import DB_PATH

# 1. Page Configuration
st.set_page_config(
    page_title="Zomato AI Recommendation System",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Premium Zomato-Themed CSS Styles
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Title and Branding */
    .brand-title {
        color: #CB202D;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 2px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .brand-subtitle {
        color: #888;
        font-size: 16px;
        margin-bottom: 25px;
    }
    
    /* Primary buttons */
    .stButton > button {
        background-color: #CB202D !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-size: 16px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 4px 6px rgba(203, 32, 45, 0.2) !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        background-color: #E23744 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 12px rgba(203, 32, 45, 0.35) !important;
    }
    
    /* Recommendation Card Styling */
    .recommendation-card {
        background-color: #1a1a1a;
        border: 1px solid #2d2d2d;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    .recommendation-card:hover {
        transform: translateY(-2px);
        border-color: #CB202D;
        box-shadow: 0 6px 16px rgba(203, 32, 45, 0.15);
    }
    .card-header {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        gap: 15px;
        margin-bottom: 8px;
        flex-wrap: wrap;
    }
    .restaurant-name {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        text-decoration: none;
    }
    .match-badge {
        background-color: #CB202D;
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    .card-meta {
        display: flex;
        gap: 18px;
        color: #999;
        font-size: 14px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }
    .meta-item {
        display: flex;
        align-items: center;
        gap: 5px;
    }
    .card-tags {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 15px;
    }
    .tag {
        background-color: #2b2b2b;
        color: #d1d1d1;
        padding: 3px 9px;
        border-radius: 5px;
        font-size: 12px;
        font-weight: 500;
    }
    .reason-box {
        border-left: 3px solid #CB202D;
        padding-left: 15px;
        color: #e0e0e0;
        font-style: italic;
        font-size: 15px;
        line-height: 1.5;
        background-color: #222;
        padding-top: 10px;
        padding-bottom: 10px;
        border-radius: 0 8px 8px 0;
    }
    
    /* Alert details */
    .metric-footer {
        font-size: 12px;
        color: #666;
        text-align: right;
        margin-top: 25px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Dynamic Database Helper
def get_unique_locations():
    """Queries unique locations from the database dynamically."""
    if not os.path.exists(DB_PATH):
        return ["Jayanagar", "Banashankari", "Basavanagudi", "JP Nagar", "Koramangala", "Indiranagar"]
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT location FROM restaurants ORDER BY location")
        locs = [row[0] for row in cursor.fetchall() if row[0]]
        conn.close()
        return locs
    except Exception:
        return ["Jayanagar", "Banashankari", "Basavanagudi", "JP Nagar", "Koramangala", "Indiranagar"]

# Load unique locations
db_locations = get_unique_locations()

# Initialize Recommendation Engine
@st.cache_resource
def get_engine():
    return RecommendationEngine()

engine = get_engine()

# 4. App Heading Banner
st.markdown("<div class='brand-title'>🍔 Zomato AI Recommendation System</div>", unsafe_allow_html=True)
st.markdown("<div class='brand-subtitle'>Combining hard-constraint pre-filtering with Large Language Model reasoning for perfect dining discovery.</div>", unsafe_allow_html=True)

# 5. Sidebar Navigation / Manual Filters Setup
st.sidebar.markdown("### 🔍 Filter Settings")

selected_location = st.sidebar.selectbox("Location", db_locations, index=db_locations.index("Jayanagar") if "Jayanagar" in db_locations else 0)

cuisines_list = ["Italian", "Chinese", "Biryani", "North Indian", "South Indian", "Fast Food", "Continental", "Desserts", "Bakery", "Beverages", "Street Food", "Cafe", "Burger", "Pizza", "Mughlai"]
selected_cuisines = st.sidebar.multiselect("Cuisines Preference", cuisines_list)

min_rating = st.sidebar.slider("Minimum Rating", 1.0, 5.0, 4.0, step=0.1)

max_budget = st.sidebar.slider("Maximum Cost for Two (Rs.)", 100, 3000, 1500, step=100)
min_budget = st.sidebar.slider("Minimum Cost for Two (Rs.)", 0, 1500, 0, step=100)

st.sidebar.markdown("### ⚙️ Optional Rules")
book_table = st.sidebar.checkbox("Requires Table Booking", value=False)
online_order = st.sidebar.checkbox("Requires Online Delivery", value=False)

restaurant_type_options = ["Casual Dining", "Fine Dining", "Cafe", "Pub", "Bar", "Lounge", "Microbrewery", "Quick Bites", "Dessert Parlor"]
selected_rest_types = st.sidebar.multiselect("Dining Style Types", restaurant_type_options)

max_candidates_limit = st.sidebar.slider("Max Candidates Limit", 5, 50, 5)

# 6. Main Container (Conversational Assistant vs. Manual Filters tabs)
tab_ai, tab_manual = st.tabs(["💬 AI Assistant (Conversational)", "🎛️ Interactive Filters Search"])

# RENDER RECOMMENDATION CARD helper
def render_recommendation_card(rec, p2_details=None):
    # Parse tag values if candidate details are passed
    tags_html = ""
    meta_html = ""
    
    if p2_details:
        cuisines = p2_details.get("cuisines", "").replace("|", ", ")
        rest_type = p2_details.get("restaurant_type", "")
        cost = p2_details.get("cost", 0)
        votes = p2_details.get("votes", 0)
        rating = p2_details.get("rating", 0.0)
        booking = p2_details.get("book_table")
        delivery = p2_details.get("online_order")
        
        # Tags formatting
        if cuisines:
            for c in cuisines.split(", ")[:3]:
                tags_html += f"<span class='tag'>🍲 {c}</span>"
        if rest_type:
            for t in rest_type.split(", ")[:2]:
                tags_html += f"<span class='tag'>🏢 {t}</span>"
                
        # Meta formatting
        meta_html = f"""
        <div class='card-meta'>
            <div class='meta-item'>⭐ <b>{rating}</b> ({votes:,} reviews)</div>
            <div class='meta-item'>💰 <b>Rs. {cost}</b> for two</div>
            <div class='meta-item'>{'📅 Booking Available' if booking else '❌ No Booking'}</div>
            <div class='meta-item'>{'🛵 Delivery Available' if delivery else '❌ No Delivery'}</div>
        </div>
        """
        
    card_html = f"""
    <div class='recommendation-card'>
        <div class='card-header'>
            <div class='restaurant-name'>{rec['restaurant_name']}</div>
            <div class='match-badge'>{rec['match_score']}% Match</div>
        </div>
        {meta_html}
        <div class='card-tags'>
            {tags_html}
        </div>
        <div class='reason-box'>
            "{rec['reason']}"
        </div>
    </div>
    """
    st.html(card_html)

# TAB 1: Conversational AI Assistant
with tab_ai:
    st.markdown("##### Describe your dining cravings in plain English:")
    sample_queries = [
        "I want a highly rated Italian restaurant in Jayanagar under Rs.1500 with table booking.",
        "Show me cozy cafes in Jayanagar serving Italian under Rs.1000.",
        "I need a romantic microbrewery or lounge in Jayanagar with rating >= 4.0."
    ]
    
    user_query = st.text_area(
        label="Conversational Prompt Input",
        value=sample_queries[0],
        placeholder="Type here...",
        label_visibility="collapsed"
    )
    
    st.markdown("Suggestions:")
    cols = st.columns(len(sample_queries))
    for idx, sq in enumerate(sample_queries):
        if cols[idx].button(f"Prompt {idx+1}", help=sq):
            user_query = sq
            st.rerun()

    if st.button("🚀 Find Recommendations", key="btn_ai"):
        with st.spinner("Analyzing intent and querying database..."):
            try:
                res = engine.recommend(user_query, limit=max_candidates_limit)
                
                # Fetch metadata
                meta = res["metadata"]
                parsed_filters = meta.get("parsed_filters", {})
                
                # Display parsed intent
                st.markdown("#### 🎯 Extracted Intent Search Filters:")
                st.json(parsed_intent := {k: v for k, v in parsed_filters.items() if v is not None and v != []})
                
                # Display relaxation if occurred
                if meta.get("relaxation_applied"):
                    orig_c = meta.get("original_constraints", {})
                    final_c = meta.get("final_constraints", {})
                    st.warning(
                        f"⚠️ **Constraint Relaxation Applied!** Too few candidates were found matching your criteria. "
                        f"Rating boundary was relaxed from `{orig_c.get('min_rating')}` to `{final_c.get('min_rating')}`. "
                        f"Max budget expanded from `{orig_c.get('max_budget')}` to `{final_c.get('max_budget')}`."
                    )
                    
                # Check for heuristic fallback
                if meta.get("fallback_applied"):
                    st.info("ℹ️ **Local Heuristic Scoring Active:** Showing template-ranked recommendations due to Groq API connection limits.")
                else:
                    st.success("✨ **Live Groq AI Reasoning Active:** Ranked recommendations dynamically generated by Groq LLM.")
                    
                # Display recommendations
                st.markdown("#### 🏆 Top Recommended Restaurants:")
                recs = res["recommendations"]
                
                if not recs:
                    st.error("No restaurants found matching your criteria, even after relaxation.")
                else:
                    # Reranked Summary
                    st.info(res["recommendation_summary"])
                    
                    # Connect to DB to pull full candidate details to render badges
                    conn = sqlite3.connect(DB_PATH)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    for r in recs:
                        # Fetch full row details
                        cursor.execute("SELECT * FROM restaurants WHERE name = ? COLLATE NOCASE", (r["restaurant_name"],))
                        row = cursor.fetchone()
                        p2_dict = dict(row) if row else None
                        render_recommendation_card(r, p2_dict)
                        
                    conn.close()
                    
                # Timing Metrics
                t = meta.get("timings", {})
                st.markdown(
                    f"<div class='metric-footer'>Intent: {t.get('intent_parsing_ms', 0):.1f}ms | "
                    f"DB Filter: {t.get('db_query_ms', 0):.1f}ms | "
                    f"LLM Ranking: {t.get('llm_ranking_ms', 0):.1f}ms | "
                    f"Total: {t.get('total_ms', 0) / 1000.0:.2f}s</div>",
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"Failed to fetch recommendations: {str(e)}")

# TAB 2: Interactive Sidebar Filters Search
with tab_manual:
    st.markdown("##### Search using the custom filters configured in the sidebar panel on the left.")
    
    if st.button("🔍 Search with Sidebar Filters", key="btn_manual"):
        with st.spinner("Filtering database and ranking candidates..."):
            start_time = time.perf_counter()
            
            # 1. Fetch from Filter Engine
            t0_db = time.perf_counter()
            candidates_data = get_candidates(
                location=selected_location,
                cuisines=selected_cuisines,
                min_rating=min_rating,
                min_budget=min_budget,
                max_budget=max_budget,
                online_order=online_order if online_order else None,
                book_table=book_table if book_table else None,
                restaurant_type=selected_rest_types,
                max_candidates=50
            )
            t1_db = time.perf_counter()
            db_ms = (t1_db - t0_db) * 1000.0
            
            candidates = candidates_data["results"]
            relaxation_applied = candidates_data.get("relaxation_applied", False)
            
            # 2. Rank candidates (LLM or Heuristics)
            t0_rank = time.perf_counter()
            filters = {
                "location": selected_location,
                "cuisines": selected_cuisines,
                "min_rating": min_rating,
                "min_budget": min_budget,
                "max_budget": max_budget,
                "online_order": online_order if online_order else None,
                "book_table": book_table if book_table else None,
                "restaurant_type": selected_rest_types
            }
            
            fallback_applied = False
            if engine.client and len(candidates) > 0:
                try:
                    ranked_result = engine._rank_with_llm(filters, candidates[:20], "llama-3.3-70b-versatile", max_candidates_limit)
                except Exception:
                    ranked_result = engine._rank_with_heuristics(filters, candidates, max_candidates_limit)
                    fallback_applied = True
            else:
                ranked_result = engine._rank_with_heuristics(filters, candidates, max_candidates_limit)
                fallback_applied = True
                
            t1_rank = time.perf_counter()
            rank_ms = (t1_rank - t0_rank) * 1000.0
            
            total_ms = (time.perf_counter() - start_time) * 1000.0
            
            # Displays
            if relaxation_applied:
                orig_c = candidates_data.get("original_constraints", {})
                final_c = candidates_data.get("final_constraints", {})
                st.warning(
                    f"⚠️ **Constraint Relaxation Applied!** Too few candidates met the strict criteria. "
                    f"Rating relaxed from `{orig_c.get('min_rating')}` to `{final_c.get('min_rating')}`. "
                    f"Max budget expanded from `{orig_c.get('max_budget')}` to `{final_c.get('max_budget')}`."
                )
                
            if fallback_applied:
                st.info("ℹ️ **Local Heuristic Scoring Active:** Showing template-ranked recommendations due to Groq API limits.")
            else:
                st.success("✨ **Live Groq AI Reasoning Active:** Ranked recommendations dynamically generated by Groq LLM.")
                
            st.markdown("#### 🏆 Top Recommended Restaurants:")
            recs = ranked_result.get("recommendations", [])
            
            if not recs:
                st.error("No restaurants found matching your criteria, even after relaxation.")
            else:
                st.info(ranked_result.get("recommendation_summary", ""))
                
                # Fetch full row details
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                for r in recs:
                    cursor.execute("SELECT * FROM restaurants WHERE name = ? COLLATE NOCASE", (r["restaurant_name"],))
                    row = cursor.fetchone()
                    p2_dict = dict(row) if row else None
                    render_recommendation_card(r, p2_dict)
                    
                conn.close()
                
            st.markdown(
                f"<div class='metric-footer'>DB Filter: {db_ms:.1f}ms | "
                f"LLM Ranking: {rank_ms:.1f}ms | "
                f"Total: {total_ms / 1000.0:.2f}s</div>",
                unsafe_allow_html=True
            )
