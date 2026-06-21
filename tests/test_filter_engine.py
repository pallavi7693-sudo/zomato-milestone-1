import os
import sys
import pytest
import sqlite3

# Ensure src directory is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from filter_engine import get_candidates, calculate_popularity_score
from config import DB_PATH

def test_popularity_score_calculation():
    """Verify popularity score weighting logic."""
    # Score = (Rating * 0.6) + (log1p(Votes) * 0.4)
    # Test case 1: rating 4.0, votes 0 -> 4.0*0.6 + log1p(0)*0.4 = 2.4
    score_1 = calculate_popularity_score(4.0, 0)
    assert pytest.approx(score_1, 0.001) == 2.4
    
    # Test case 2: rating 5.0, votes 100
    score_2 = calculate_popularity_score(5.0, 100)
    assert score_2 > 4.8

def test_filter_by_location_case_insensitive():
    """Verify that location search is case-insensitive."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist. Run ingestion first.")
        
    res_lower = get_candidates(location="banashankari")
    res_proper = get_candidates(location="Banashankari")
    
    assert len(res_lower["results"]) > 0
    assert len(res_lower["results"]) == len(res_proper["results"])
    
    # Check that all elements returned are in banashankari
    for item in res_lower["results"]:
        assert item["location"].lower() == "banashankari"

def test_filter_by_cuisines():
    """Verify that cuisine filtering matches single or list queries."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Test with string
    res_str = get_candidates(location="Banashankari", cuisines="Chinese")
    for item in res_str["results"]:
        assert "chinese" in item["cuisines"].lower()
        
    # Test with list matching any of the cuisines
    res_list = get_candidates(location="Banashankari", cuisines=["Chinese", "Italian"])
    for item in res_list["results"]:
        c_lower = item["cuisines"].lower()
        assert "chinese" in c_lower or "italian" in c_lower

def test_rating_and_budget_constraints():
    """Verify rating and cost limits are applied."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Test strict constraints where results > 10 (no relaxation expected)
    res = get_candidates(location="Banashankari", min_rating=3.5, max_budget=1000)
    
    # Verify that all returned candidates satisfy the original constraint
    for item in res["results"]:
        assert item["rating"] >= 3.5
        assert item["cost"] <= 1000
    
    assert res["relaxation_applied"] is False
    assert res["original_rating"] == 3.5
    assert res["final_rating"] == 3.5
    assert res["original_budget"] == 1000.0
    assert res["final_budget"] == 1000.0

def test_boolean_filters():
    """Verify online_order and book_table filters work as expected."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Filter for table booking available
    res_booking = get_candidates(location="Banashankari", book_table=True)
    for item in res_booking["results"]:
        assert item["book_table"] is True
        
    # Filter for online ordering available
    res_online = get_candidates(location="Banashankari", online_order=True)
    for item in res_online["results"]:
        assert item["online_order"] is True

def test_constraint_relaxation():
    """Verify that constraints are relaxed if matches are less than 10."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Set extremely strict constraints that should trigger relaxation
    strict_res = get_candidates(location="Banashankari", min_rating=4.8, max_budget=200)
    
    # Since original search had < 10 results, relaxation must have occurred.
    assert len(strict_res["results"]) > 0
    assert strict_res["relaxation_applied"] is True
    assert strict_res["original_rating"] == 4.8
    assert strict_res["final_rating"] < 4.8
    assert strict_res["original_budget"] == 200.0
    assert strict_res["final_budget"] > 200.0
    
    # Check that we relaxed rating downwards and budget upwards
    violation_found = False
    for item in strict_res["results"]:
        if item["rating"] < 4.8 or item["cost"] > 200:
            violation_found = True
            break
    assert violation_found, "Relaxation should have returned candidates outside original boundaries."

def test_candidate_sorting():
    """Verify candidates are sorted by rating desc, votes desc, popularity desc."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    res = get_candidates(location="Banashankari")
    assert len(res["results"]) >= 2
    
    for i in range(len(res["results"]) - 1):
        curr = res["results"][i]
        nxt = res["results"][i+1]
        
        # Test sorting order: rating desc, then votes desc, then popularity desc
        if curr["rating"] == nxt["rating"]:
            if curr["votes"] == nxt["votes"]:
                assert curr["popularity_score"] >= nxt["popularity_score"]
            else:
                assert curr["votes"] > nxt["votes"]
        else:
            assert curr["rating"] > nxt["rating"]

def test_relaxation_metadata_format():
    """Explicitly verify that the returned dictionary matches the requested JSON metadata format."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    res = get_candidates(location="Banashankari", min_rating=4.5, max_budget=500)
    
    assert isinstance(res, dict)
    assert "results" in res
    assert "relaxation_applied" in res
    assert "original_rating" in res
    assert "final_rating" in res
    assert "original_budget" in res
    assert "final_budget" in res
    assert "query_execution_ms" in res
    
    assert isinstance(res["results"], list)
    assert isinstance(res["relaxation_applied"], bool)
    assert isinstance(res["original_rating"], float)
    assert isinstance(res["final_rating"], float)
    assert res["original_budget"] == 500.0
    assert isinstance(res["final_budget"], float)
    assert isinstance(res["query_execution_ms"], float)
    assert res["query_execution_ms"] >= 0.0

def test_max_candidates_limit():
    """Verify that specifying a custom max_candidates returns at most that number of candidates."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Query with max_candidates = 5
    res = get_candidates(location="Banashankari", max_candidates=5)
    assert len(res["results"]) == 5, f"Expected 5 candidates, but got {len(res['results'])}"

def test_returned_candidates_satisfy_active_constraints():
    """Verify that all returned candidates satisfy the relaxed active constraints (final_rating, final_budget)."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Run a query with parameters that might trigger relaxation or not
    res = get_candidates(location="Banashankari", min_rating=4.3, max_budget=600, cuisines="Pizza")
    
    final_rating = res["final_rating"]
    final_budget = res["final_budget"]
    
    assert len(res["results"]) > 0
    
    for item in res["results"]:
        # Rating constraint
        assert item["rating"] >= final_rating, f"Rating {item['rating']} is less than final rating constraint {final_rating} for {item['name']}"
        # Budget constraint
        if final_budget is not None:
            assert item["cost"] <= final_budget, f"Cost {item['cost']} exceeds final budget constraint {final_budget} for {item['name']}"
        # Location constraint
        assert item["location"].lower() == "banashankari"
        # Cuisine constraint
        assert "pizza" in item["cuisines"].lower(), f"Cuisine Pizza not found in {item['cuisines']} for {item['name']}"

def test_budget_tiers_filtering():
    """Verify that using budget tiers (both min_budget and max_budget) restricts cost to that exact range."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Query Jayanagar with Premium tier range (₹1200 - ₹1600)
    res = get_candidates(location="Jayanagar", min_budget=1200, max_budget=1600)
    
    assert len(res["results"]) > 0
    for item in res["results"]:
        assert item["cost"] >= 1200, f"Restaurant {item['name']} cost {item['cost']} is below min_budget threshold 1200"
        assert item["cost"] <= 1600, f"Restaurant {item['name']} cost {item['cost']} is above max_budget threshold 1600"

def test_dining_experience_filtering():
    """Verify that filtering by dining experience (restaurant_type) matches style tags correctly."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Query Koramangala with 'Pub' experience
    res = get_candidates(location="Jayanagar", restaurant_type="Pub")
    
    assert len(res["results"]) > 0
    for item in res["results"]:
        assert "pub" in item["restaurant_type"].lower(), f"Restaurant type {item['restaurant_type']} does not match experience filter 'Pub' for {item['name']}"

def test_symmetrical_budget_relaxation():
    """Verify that min_budget and max_budget are relaxed symmetrically (min drops, max increases) when results are < 10."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Strict range that yields few results: Jayanagar, rating >= 4.7, cost in [1400, 1600]
    res = get_candidates(location="Jayanagar", min_rating=4.7, min_budget=1400, max_budget=1600)
    
    # Assert relaxation was applied
    assert res["relaxation_applied"] is True
    assert res["final_rating"] < 4.7
    
    final_constraints = res["final_constraints"]
    # min_budget should drop below 1400
    assert final_constraints["min_budget"] < 1400
    # max_budget should increase above 1600
    assert final_constraints["max_budget"] > 1600
    
    # Confirm every returned item complies with final relaxed boundaries
    for item in res["results"]:
        assert item["rating"] >= final_constraints["min_rating"]
        assert item["cost"] >= final_constraints["min_budget"]
        assert item["cost"] <= final_constraints["max_budget"]
