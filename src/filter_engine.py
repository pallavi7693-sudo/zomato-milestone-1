import sqlite3
import math
import logging
import os
import sys
from typing import List, Dict, Any, Union

# Ensure config parameters can be imported
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from config import DB_PATH, RELAXATION_TARGET_COUNT, RATING_RELAX_STEP, BUDGET_RELAX_PERCENT

logger = logging.getLogger("filter_engine")

# ─── Bangalore Locality Proximity Map ────────────────────────────────────────
# Maps each location to a list of nearby locations (ordered by proximity).
# When a location yields too few results, the engine will try these neighbors.
NEARBY_LOCATIONS = {
    "Indiranagar":           ["Domlur", "CV Raman Nagar", "Ulsoor", "Old Airport Road", "Jeevan Bhima Nagar", "Koramangala", "MG Road"],
    "Koramangala":           ["Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 7th Block", "Koramangala 8th Block", "Ejipura", "Indiranagar", "BTM", "HSR"],
    "Koramangala 1st Block": ["Koramangala", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 7th Block", "Koramangala 8th Block"],
    "Koramangala 2nd Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 7th Block", "Koramangala 8th Block"],
    "Koramangala 3rd Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 7th Block", "Koramangala 8th Block"],
    "Koramangala 4th Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 7th Block", "Koramangala 8th Block"],
    "Koramangala 5th Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 6th Block", "Koramangala 7th Block", "Koramangala 8th Block"],
    "Koramangala 6th Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 7th Block", "Koramangala 8th Block"],
    "Koramangala 7th Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 8th Block"],
    "Koramangala 8th Block": ["Koramangala", "Koramangala 1st Block", "Koramangala 2nd Block", "Koramangala 3rd Block", "Koramangala 4th Block", "Koramangala 5th Block", "Koramangala 6th Block", "Koramangala 7th Block"],
    "Jayanagar":             ["JP Nagar", "Basavanagudi", "Banashankari", "BTM", "Kumaraswamy Layout", "Wilson Garden"],
    "JP Nagar":              ["Jayanagar", "Banashankari", "BTM", "Kumaraswamy Layout", "Kanakapura Road", "Basavanagudi"],
    "Banashankari":          ["Jayanagar", "JP Nagar", "Basavanagudi", "Kumaraswamy Layout", "Kanakapura Road", "Rajarajeshwari Nagar"],
    "Basavanagudi":          ["Jayanagar", "Banashankari", "Shanti Nagar", "Wilson Garden", "City Market"],
    "BTM":                   ["Koramangala", "HSR", "JP Nagar", "Jayanagar", "Bommanahalli", "Ejipura"],
    "HSR":                   ["BTM", "Koramangala", "Bellandur", "Bommanahalli", "Sarjapur Road", "Ejipura"],
    "Whitefield":            ["ITPL Main Road, Whitefield", "Varthur Main Road, Whitefield", "Brookefield", "Marathahalli", "KR Puram", "Old Madras Road"],
    "ITPL Main Road, Whitefield": ["Whitefield", "Varthur Main Road, Whitefield", "Brookefield", "Marathahalli"],
    "Varthur Main Road, Whitefield": ["Whitefield", "ITPL Main Road, Whitefield", "Brookefield", "Sarjapur Road"],
    "Marathahalli":          ["Whitefield", "Bellandur", "Old Airport Road", "Brookefield", "Domlur", "Indiranagar"],
    "Bellandur":             ["HSR", "Marathahalli", "Sarjapur Road", "Koramangala", "Whitefield"],
    "Electronic City":       ["Bommanahalli", "Hosur Road", "Bannerghatta Road", "JP Nagar"],
    "Malleshwaram":          ["Rajajinagar", "Sadashiv Nagar", "Seshadripuram", "Yeshwantpur", "Basaveshwara Nagar", "Sankey Road"],
    "Rajajinagar":           ["Malleshwaram", "Basaveshwara Nagar", "Magadi Road", "Yeshwantpur", "Vijay Nagar"],
    "MG Road":               ["Brigade Road", "Church Street", "St. Marks Road", "Lavelle Road", "Residency Road", "Richmond Road", "Shivajinagar", "Commercial Street", "Infantry Road"],
    "Brigade Road":          ["MG Road", "Church Street", "St. Marks Road", "Lavelle Road", "Residency Road", "Richmond Road", "Commercial Street"],
    "Church Street":         ["MG Road", "Brigade Road", "St. Marks Road", "Lavelle Road", "Shivajinagar"],
    "Lavelle Road":          ["MG Road", "Brigade Road", "St. Marks Road", "Residency Road", "Richmond Road", "Vasanth Nagar"],
    "Residency Road":        ["MG Road", "Brigade Road", "Lavelle Road", "Richmond Road", "Shanti Nagar"],
    "Richmond Road":         ["MG Road", "Brigade Road", "Lavelle Road", "Residency Road", "Langford Town", "Shanti Nagar"],
    "St. Marks Road":        ["MG Road", "Brigade Road", "Church Street", "Lavelle Road"],
    "Commercial Street":     ["MG Road", "Brigade Road", "Shivajinagar", "Frazer Town", "Infantry Road"],
    "Frazer Town":           ["Commercial Street", "Shivajinagar", "Kammanahalli", "Kalyan Nagar", "Ulsoor"],
    "Kalyan Nagar":          ["Kammanahalli", "Banaswadi", "HBR Layout", "Hennur", "RT Nagar"],
    "Kammanahalli":          ["Kalyan Nagar", "Banaswadi", "Frazer Town", "HBR Layout", "Kaggadasapura"],
    "Hebbal":                ["Sahakara Nagar", "Yelahanka", "RT Nagar", "Nagawara", "Sanjay Nagar"],
    "Bannerghatta Road":     ["JP Nagar", "Jayanagar", "Bommanahalli", "Arekere", "Electronic City"],
    "Sarjapur Road":         ["Bellandur", "HSR", "Marathahalli", "Whitefield", "Koramangala"],
    "Old Airport Road":      ["Indiranagar", "Domlur", "Marathahalli", "CV Raman Nagar"],
    "Domlur":                ["Indiranagar", "Old Airport Road", "Koramangala", "Ejipura"],
    "Ejipura":               ["Koramangala", "BTM", "Domlur", "Indiranagar"],
    "Bommanahalli":          ["BTM", "HSR", "Electronic City", "Bannerghatta Road"],
    "Shivajinagar":          ["MG Road", "Commercial Street", "Frazer Town", "Ulsoor", "Infantry Road"],
    "Ulsoor":                ["MG Road", "Indiranagar", "Shivajinagar", "Frazer Town"],
    "Yeshwantpur":           ["Malleshwaram", "Rajajinagar", "Peenya", "New BEL Road"],
    "Peenya":                ["Yeshwantpur", "Rajajinagar", "Jalahalli", "Nagarbhavi"],
    "Brookefield":           ["Whitefield", "ITPL Main Road, Whitefield", "Marathahalli", "Old Madras Road"],
    "Hennur":                ["Kalyan Nagar", "Banaswadi", "HBR Layout", "Nagawara", "Hebbal"],
    "Banaswadi":             ["Kalyan Nagar", "Kammanahalli", "Hennur", "HBR Layout", "Rammurthy Nagar"],
    "HBR Layout":            ["Kalyan Nagar", "Kammanahalli", "Banaswadi", "Hennur"],
    "RT Nagar":              ["Hebbal", "Kalyan Nagar", "Sanjay Nagar", "Sadashiv Nagar"],
    "New BEL Road":          ["Malleshwaram", "Sadashiv Nagar", "Yeshwantpur", "Sankey Road"],
    "Sankey Road":           ["Malleshwaram", "Sadashiv Nagar", "Race Course Road", "New BEL Road"],
    "Race Course Road":      ["Sankey Road", "Sadashiv Nagar", "Vasanth Nagar", "Cunningham Road"],
    "Cunningham Road":       ["Vasanth Nagar", "Race Course Road", "Infantry Road", "Shivajinagar"],
    "Infantry Road":         ["MG Road", "Commercial Street", "Cunningham Road", "Shivajinagar"],
    "Kanakapura Road":       ["JP Nagar", "Banashankari", "Kumaraswamy Layout", "Uttarahalli"],
    "Wilson Garden":         ["Basavanagudi", "Jayanagar", "Shanti Nagar", "Langford Town"],
    "Shanti Nagar":          ["Residency Road", "Richmond Road", "Wilson Garden", "Basavanagudi"],
    "Langford Town":         ["Richmond Road", "Wilson Garden", "Shanti Nagar"],
    "Hosur Road":            ["Electronic City", "Bommanahalli", "Koramangala"],
    "Thippasandra":          ["Indiranagar", "CV Raman Nagar", "Jeevan Bhima Nagar", "Old Airport Road"],
    "Jeevan Bhima Nagar":    ["Indiranagar", "Thippasandra", "Old Airport Road", "CV Raman Nagar"],
    "CV Raman Nagar":        ["Indiranagar", "Old Airport Road", "Thippasandra", "Jeevan Bhima Nagar"],
    "Yelahanka":             ["Hebbal", "Sahakara Nagar", "North Bangalore"],
    "Sahakara Nagar":        ["Hebbal", "Yelahanka", "RT Nagar"],
    "Sadashiv Nagar":        ["Malleshwaram", "Sankey Road", "Race Course Road", "RT Nagar"],
    "Vasanth Nagar":         ["Lavelle Road", "Cunningham Road", "Race Course Road", "MG Road"],
    "Seshadripuram":         ["Malleshwaram", "Rajajinagar", "Majestic"],
    "Majestic":              ["City Market", "Seshadripuram", "Rajajinagar", "Central Bangalore"],
    "City Market":           ["Majestic", "Basavanagudi", "Shivajinagar", "Central Bangalore"],
    "Nagarbhavi":            ["Rajajinagar", "Peenya", "West Bangalore", "Kengeri"],
    "Kengeri":               ["Nagarbhavi", "Rajarajeshwari Nagar", "West Bangalore"],
    "Rajarajeshwari Nagar":  ["Banashankari", "Kengeri", "Nagarbhavi"],
    "Kumaraswamy Layout":    ["JP Nagar", "Banashankari", "Kanakapura Road"],
    "Uttarahalli":           ["Kanakapura Road", "Banashankari", "JP Nagar"],
    "Vijay Nagar":           ["Rajajinagar", "Basaveshwara Nagar", "Nagarbhavi"],
    "Basaveshwara Nagar":    ["Rajajinagar", "Vijay Nagar", "Malleshwaram"],
    "Rammurthy Nagar":       ["Banaswadi", "KR Puram", "Old Madras Road"],
    "KR Puram":              ["Whitefield", "Old Madras Road", "Rammurthy Nagar"],
    "Old Madras Road":       ["KR Puram", "Whitefield", "Brookefield", "Rammurthy Nagar"],
    "Kaggadasapura":         ["Kammanahalli", "CV Raman Nagar", "Old Airport Road"],
    "Nagawara":              ["Hebbal", "Hennur", "Kalyan Nagar"],
    "Jalahalli":             ["Peenya", "Yeshwantpur"],
    "Sanjay Nagar":          ["RT Nagar", "Hebbal", "Sadashiv Nagar"],
    "Magadi Road":           ["Rajajinagar", "Majestic", "West Bangalore"],
    "Mysore Road":           ["Kengeri", "Rajarajeshwari Nagar", "West Bangalore"],
    # Broad area aliases
    "Central Bangalore":     ["MG Road", "Brigade Road", "Church Street", "Commercial Street", "Majestic", "City Market", "Shivajinagar"],
    "North Bangalore":       ["Hebbal", "Yelahanka", "Sahakara Nagar", "RT Nagar"],
    "South Bangalore":       ["JP Nagar", "Jayanagar", "Banashankari", "Bannerghatta Road", "Kumaraswamy Layout"],
    "East Bangalore":        ["Whitefield", "Marathahalli", "KR Puram", "Old Madras Road"],
    "West Bangalore":        ["Rajajinagar", "Nagarbhavi", "Kengeri", "Rajarajeshwari Nagar"],
}

def calculate_popularity_score(rating: float, votes: int) -> float:
    """
    Calculates a popularity score based on a weighted formula:
    Score = (Rating * 0.6) + (log1p(Votes) * 0.4)
    """
    safe_rating = float(rating) if rating is not None else 0.0
    safe_votes = int(votes) if votes is not None else 0
    # Use natural log (log1p) to scale votes gracefully
    return (safe_rating * 0.6) + (math.log1p(safe_votes) * 0.4)

def execute_filter_query(
    conn: sqlite3.Connection,
    locations: Union[str, List[str]],
    cuisines_list: List[str],
    min_rating: float,
    max_budget: Union[int, float, None],
    online_order: Union[bool, None],
    book_table: Union[bool, None],
    min_budget: Union[int, float, None] = None,
    restaurant_type_list: List[str] = None
) -> List[Dict[str, Any]]:
    """Runs a query on SQLite DB with specific filter constraints.
    Accepts a single location string or a list of locations."""
    cursor = conn.cursor()
    
    # Normalize locations to a list
    if isinstance(locations, str):
        loc_list = [locations.strip()]
    else:
        loc_list = [l.strip() for l in locations if l and l.strip()]
    
    if len(loc_list) == 1:
        query = """
            SELECT id, name, location, cuisines, rating, cost, votes, online_order, book_table, restaurant_type
            FROM restaurants
            WHERE location = ?
        """
        params = [loc_list[0]]
    else:
        placeholders = ",".join(["?"] * len(loc_list))
        query = f"""
            SELECT id, name, location, cuisines, rating, cost, votes, online_order, book_table, restaurant_type
            FROM restaurants
            WHERE location IN ({placeholders})
        """
        params = list(loc_list)
    
    # 1. Rating filter
    query += " AND rating >= ?"
    params.append(min_rating)
    
    # 2. Budget filters
    if min_budget is not None:
        query += " AND cost >= ?"
        params.append(min_budget)
    if max_budget is not None:
        query += " AND cost <= ?"
        params.append(max_budget)
        
    # 3. Online Order filter
    if online_order is not None:
        query += " AND online_order = ?"
        params.append(1 if online_order else 0)
        
    # 4. Table Booking filter
    if book_table is not None:
        query += " AND book_table = ?"
        params.append(1 if book_table else 0)
        
    # 5. Cuisines filter (match any requested cuisine)
    if cuisines_list:
        cuisine_conditions = []
        for cuisine in cuisines_list:
            cuisine_conditions.append("cuisines LIKE ?")
            params.append(f"%{cuisine}%")
        query += " AND (" + " OR ".join(cuisine_conditions) + ")"
        
    # 6. Restaurant Type filter (match any requested type)
    if restaurant_type_list:
        type_conditions = []
        for r_type in restaurant_type_list:
            type_conditions.append("restaurant_type LIKE ?")
            params.append(f"%{r_type}%")
        query += " AND (" + " OR ".join(type_conditions) + ")"
        
    cursor.execute(query, params)
    
    # Map rows to list of dictionaries
    col_names = [col[0] for col in cursor.description]
    results = []
    for row in cursor.fetchall():
        row_dict = dict(zip(col_names, row))
        # Convert sqlite integer 1/0 back to python boolean
        row_dict["online_order"] = bool(row_dict["online_order"])
        row_dict["book_table"] = bool(row_dict["book_table"])
        results.append(row_dict)
        
    return results

def get_candidates(
    location: str,
    cuisines: Union[str, List[str], None] = None,
    min_rating: float = 0.0,
    max_budget: Union[int, float, None] = None,
    online_order: Union[bool, None] = None,
    book_table: Union[bool, None] = None,
    max_relaxation_steps: int = 10,
    max_candidates: int = 50,
    min_budget: Union[int, float, None] = None,
    restaurant_type: Union[str, List[str], None] = None
) -> Dict[str, Any]:
    """
    Filters restaurants from database based on user constraints.
    Constraint relaxation is applied in two phases:
      Phase 1: Relax rating and budget while keeping the original location.
      Phase 2 (Location Relaxation): If still not enough results, expand
               search to nearby locations using the NEARBY_LOCATIONS map.
    """
    import time
    start_time = time.perf_counter()
    
    logger.info(
        "Candidate generation started: location=%s, cuisines=%s, min_rating=%.1f, budget_range=[%s, %s], max_candidates=%d, rest_type=%s",
        location, cuisines, min_rating, min_budget, max_budget, max_candidates, restaurant_type
    )
    
    # Standardize cuisines into a list of lowercase strings
    cuisines_list = []
    if cuisines:
        if isinstance(cuisines, str):
            cuisines_list = [c.strip().lower() for c in cuisines.replace("|", ",").split(",") if c.strip()]
        elif isinstance(cuisines, list):
            cuisines_list = [str(c).strip().lower() for c in cuisines if str(c).strip()]
            
    # Standardize restaurant types into a list of lowercase strings
    restaurant_type_list = []
    if restaurant_type:
        if isinstance(restaurant_type, str):
            restaurant_type_list = [t.strip().lower() for t in restaurant_type.replace("|", ",").split(",") if t.strip()]
        elif isinstance(restaurant_type, list):
            restaurant_type_list = [str(t).strip().lower() for t in restaurant_type if str(t).strip()]
            
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file not found at: {DB_PATH}. Run ingestion pipeline first.")
        
    conn = sqlite3.connect(str(DB_PATH))
    try:
        current_rating = float(min_rating)
        current_budget_max = float(max_budget) if max_budget is not None else None
        current_budget_min = float(min_budget) if min_budget is not None else None
        
        step = 0
        candidates = []
        initial_count = None
        location_relaxed = False
        searched_locations = [location]  # Track all locations searched
        
        # ── Phase 1: Rating & Budget Relaxation (original location only) ──
        while step <= max_relaxation_steps:
            candidates = execute_filter_query(
                conn, location, cuisines_list, current_rating, current_budget_max, online_order, book_table, current_budget_min, restaurant_type_list
            )
            count = len(candidates)
            
            if initial_count is None:
                initial_count = count
                logger.info("Initial candidate count before relaxation: %d", initial_count)
            
            logger.info(
                "Step %d: Found %d candidates (rating >= %.1f, budget range [%s, %s])",
                step, count, current_rating, current_budget_min, current_budget_max
            )
            
            # Check if target candidates are met or rating cannot be relaxed further
            if count >= RELAXATION_TARGET_COUNT or current_rating <= 1.0:
                break
                
            # Perform relaxation step
            step += 1
            old_rating = current_rating
            old_budget_min = current_budget_min
            old_budget_max = current_budget_max
            
            current_rating = max(1.0, current_rating - RATING_RELAX_STEP)
            if current_budget_max is not None:
                current_budget_max = current_budget_max * (1.0 + BUDGET_RELAX_PERCENT)
            if current_budget_min is not None:
                current_budget_min = max(0.0, current_budget_min * (1.0 - BUDGET_RELAX_PERCENT))
                
            logger.info(
                "Relaxation triggered (count %d < %d). New values: rating %.1f -> %.1f, budget [%s, %s] -> [%s, %s]",
                count, RELAXATION_TARGET_COUNT, old_rating, current_rating, old_budget_min, old_budget_max, current_budget_min, current_budget_max
            )
        
        # ── Phase 2: Location Relaxation (nearby locations) ──
        # If we still don't have enough results, expand to nearby areas
        if len(candidates) < RELAXATION_TARGET_COUNT:
            nearby = NEARBY_LOCATIONS.get(location, [])
            if nearby:
                logger.info(
                    "Location relaxation triggered: %d candidates < %d target. Expanding to %d nearby locations: %s",
                    len(candidates), RELAXATION_TARGET_COUNT, len(nearby), nearby
                )
                # Collect IDs already found to avoid duplicates
                existing_ids = {c["id"] for c in candidates}
                
                # Query nearby locations with the (already relaxed) rating/budget constraints
                nearby_candidates = execute_filter_query(
                    conn, nearby, cuisines_list, current_rating, current_budget_max,
                    online_order, book_table, current_budget_min, restaurant_type_list
                )
                
                # Merge results (deduplicated)
                for nc in nearby_candidates:
                    if nc["id"] not in existing_ids:
                        candidates.append(nc)
                        existing_ids.add(nc["id"])
                
                searched_locations.extend(nearby)
                location_relaxed = True
                
                logger.info(
                    "After location relaxation: %d total candidates (added from %s)",
                    len(candidates), nearby
                )
        
        logger.info("Final candidate count after all relaxation: %d", len(candidates))
        
        # Calculate popularity score for each candidate
        for item in candidates:
            item["popularity_score"] = calculate_popularity_score(item["rating"], item["votes"])
            
        # Sort candidates by: rating desc, votes desc, popularity_score desc
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (x["rating"], x["votes"], x["popularity_score"]),
            reverse=True
        )
        
        # Enforce max_candidates=50 safeguard
        safeguard_max_candidates = min(50, max_candidates)
        top_candidates = sorted_candidates[:safeguard_max_candidates]
        
        # Determine if relaxation was applied (rating decreased or budget range expanded)
        relaxation_applied = (
            (current_rating < float(min_rating)) or
            (current_budget_max is not None and max_budget is not None and current_budget_max > float(max_budget)) or
            (current_budget_min is not None and min_budget is not None and current_budget_min < float(min_budget))
        )
        
        end_time = time.perf_counter()
        query_execution_ms = (end_time - start_time) * 1000.0
        
        logger.info(
            "Candidate generation completed in %.2f ms. Returning %d (out of %d) candidates. Relaxation applied: %s, Location relaxed: %s",
            query_execution_ms, len(top_candidates), len(sorted_candidates), relaxation_applied, location_relaxed
        )
        
        return {
            "results": top_candidates,
            "relaxation_applied": relaxation_applied,
            "location_relaxed": location_relaxed,
            "searched_locations": searched_locations,
            "relaxation_steps_applied": step,
            "original_rating": float(min_rating),
            "final_rating": round(current_rating, 2),
            "original_budget": float(max_budget) if max_budget is not None else None,
            "final_budget": round(current_budget_max, 2) if current_budget_max is not None else None,
            "original_constraints": {
                "location": location,
                "cuisines": cuisines,
                "min_rating": float(min_rating),
                "min_budget": float(min_budget) if min_budget is not None else None,
                "max_budget": float(max_budget) if max_budget is not None else None,
                "online_order": online_order,
                "book_table": book_table,
                "restaurant_type": restaurant_type
            },
            "final_constraints": {
                "location": searched_locations if location_relaxed else location,
                "cuisines": cuisines,
                "min_rating": round(current_rating, 2),
                "min_budget": round(current_budget_min, 2) if current_budget_min is not None else None,
                "max_budget": round(current_budget_max, 2) if current_budget_max is not None else None,
                "online_order": online_order,
                "book_table": book_table,
                "restaurant_type": restaurant_type
            },
            "query_execution_ms": round(query_execution_ms, 2)
        }
        
    finally:
        conn.close()
