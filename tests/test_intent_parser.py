import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure src directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from intent_parser import IntentParser

def test_heuristic_parser_location():
    """Verify that heuristic fallback correctly identifies locations in the query."""
    parser = IntentParser(api_key=None)
    parser.client = None  # Force heuristic path bypasses Groq API key in env
    
    # Test typical Jayanagar query
    res = parser.parse_intent("I want to find a restaurant in Jayanagar")
    assert res["location"] == "Jayanagar"
    
    # Test case-insensitivity
    res_lower = parser.parse_intent("some cafe in banashankari")
    assert res_lower["location"] == "Banashankari"
    
    # Test no location
    res_none = parser.parse_intent("just show me some pizzas")
    assert res_none["location"] is None

def test_heuristic_parser_cuisines():
    """Verify that cuisines are correctly parsed from the query."""
    parser = IntentParser(api_key=None)
    parser.client = None
    
    # Single cuisine
    res1 = parser.parse_intent("looking for Italian food")
    assert "Italian" in res1["cuisines"]
    
    # Multiple cuisines
    res2 = parser.parse_intent("Chinese and Biryani in Basavanagudi")
    assert "Chinese" in res2["cuisines"]
    assert "Biryani" in res2["cuisines"]
    assert res2["location"] == "Basavanagudi"

def test_heuristic_parser_ratings():
    """Verify that ratings are correctly extracted."""
    parser = IntentParser(api_key=None)
    parser.client = None
    
    res1 = parser.parse_intent("restaurants with rating above 4.2 in Jayanagar")
    assert res1["min_rating"] == 4.2
    
    res2 = parser.parse_intent("4.5 stars dining in Indiranagar")
    assert res2["min_rating"] == 4.5
    
    res3 = parser.parse_intent("quick bites rating >= 3.8")
    assert res3["min_rating"] == 3.8

def test_heuristic_parser_budgets():
    """Verify budget extraction rules and default tiers."""
    parser = IntentParser(api_key=None)
    parser.client = None
    
    # Max budget only
    res1 = parser.parse_intent("Italian under 1500")
    assert res1["max_budget"] == 1500.0
    assert res1["min_budget"] is None
    
    # Budget range
    res2 = parser.parse_intent("biryani from 500 to 1200 rs")
    assert res2["min_budget"] == 500.0
    assert res2["max_budget"] == 1200.0
    
    # Default tiers
    res_expensive = parser.parse_intent("expensive high-end dining in JP Nagar")
    assert res_expensive["min_budget"] == 1500.0
    assert res_expensive["max_budget"] == 2500.0
    
    res_cheap = parser.parse_intent("cheap street food")
    assert res_cheap["max_budget"] == 800.0

def test_heuristic_parser_booleans():
    """Verify table booking and online order flags."""
    parser = IntentParser(api_key=None)
    parser.client = None
    
    # Test "reserve table"
    res_booking = parser.parse_intent("reserve table in Banashankari")
    assert res_booking["book_table"] is True
    
    res_delivery = parser.parse_intent("online delivery in Koramangala")
    assert res_delivery["online_order"] is True

def test_heuristic_parser_experiences():
    """Verify restaurant experience/style types extraction."""
    parser = IntentParser(api_key=None)
    parser.client = None
    
    res = parser.parse_intent("best pub or microbrewery in Indiranagar")
    assert "Pub" in res["restaurant_type"]
    assert "Microbrewery" in res["restaurant_type"]

def test_empty_query_resilience():
    """Verify parser behaves safely with empty or whitespace queries."""
    parser = IntentParser(api_key=None)
    parser.client = None
    res = parser.parse_intent("")
    assert res["location"] is None
    assert res["cuisines"] == []
    
    res_space = parser.parse_intent("   ")
    assert res_space["location"] is None

@patch("intent_parser.Groq")
def test_groq_parser_success(mock_groq_class):
    """Verify intent extraction with a mocked Groq API success response."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    
    mock_message = MagicMock()
    mock_completion.choices = [MagicMock(message=mock_message)]
    
    # Simulated JSON output from Groq
    mock_message.content = """
    ```json
    {
      "location": "Jayanagar",
      "cuisines": ["Italian", "Pizza"],
      "min_rating": 4.1,
      "min_budget": null,
      "max_budget": 1200,
      "online_order": true,
      "book_table": false,
      "restaurant_type": ["Cafe"]
    }
    ```
    """
    
    parser = IntentParser(api_key="mock_key")
    # Verify it uses the mocked client
    res = parser.parse_intent("Italian cafe in Jayanagar under 1200 with delivery", model_name="llama-3.1-8b-instant")
    
    assert res["location"] == "Jayanagar"
    assert "Italian" in res["cuisines"]
    assert "Pizza" in res["cuisines"]
    assert res["min_rating"] == 4.1
    assert res["max_budget"] == 1200.0
    assert res["online_order"] is True
    assert res["book_table"] is False
    assert "Cafe" in res["restaurant_type"]

@patch("intent_parser.Groq")
def test_groq_parser_fallback_on_error(mock_groq_class):
    """Verify that if the Groq client throws an error, the parser falls back to heuristics."""
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Force API call to raise an exception
    mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")
    
    parser = IntentParser(api_key="mock_key")
    # This query should fall back to rule-based heuristics
    res = parser.parse_intent("expensive dining in Banashankari with rating of 4.5", model_name="llama-3.1-8b-instant")
    
    assert res["location"] == "Banashankari"
    assert res["min_rating"] == 4.5
    assert res["min_budget"] == 1500.0
    assert res["max_budget"] == 2500.0
