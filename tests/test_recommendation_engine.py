import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure src directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from recommendation_engine import RecommendationEngine
from config import DB_PATH

def test_heuristic_recommendation_flow():
    """Verify that when no API key is provided, the engine runs heuristic recommendations."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist. Run ingestion first.")
        
    engine = RecommendationEngine(api_key=None)
    engine.client = None
    engine.intent_parser.client = None
    
    # Query for Italian food in Banashankari under 1500
    res = engine.recommend("Italian food in Banashankari under 1500")
    
    assert "recommendations" in res
    assert "recommendation_summary" in res
    assert "metadata" in res
    
    recs = res["recommendations"]
    assert len(recs) > 0
    # Check that recommendations are ordered by rank
    for idx, rec in enumerate(recs, 1):
        assert rec["rank"] == idx
        assert "restaurant_name" in rec
        assert "match_score" in rec
        assert "reason" in rec
        assert isinstance(rec["match_score"], int)
        
    metadata = res["metadata"]
    assert metadata["fallback_applied"] is True
    assert "timings" in metadata
    timings = metadata["timings"]
    assert "intent_parsing_ms" in timings
    assert "db_query_ms" in timings
    assert "llm_ranking_ms" in timings
    assert "total_ms" in timings

def test_zero_candidates_handling():
    """Verify engine handles queries that yield no database records gracefully."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    engine = RecommendationEngine(api_key=None)
    engine.client = None
    engine.intent_parser.client = None
    
    # Query for a location that doesn't exist
    res = engine.recommend("Italian in Atlantis under 100")
    
    assert res["recommendations"] == []
    assert "couldn't find" in res["recommendation_summary"]
    assert res["metadata"]["candidate_count"] == 0

@patch("recommendation_engine.Groq")
def test_groq_recommendation_success(mock_groq_class):
    """Verify recommendation pipeline works when Groq client returns a successful response."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    # Mock setup
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    mock_completion = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    
    mock_message = MagicMock()
    mock_completion.choices = [MagicMock(message=mock_message)]
    
    # Mock returned JSON recommendations from Groq
    mock_message.content = """
    {
      "recommendations": [
        {
          "rank": 1,
          "restaurant_name": "Sreenidhi Gold",
          "match_score": 95,
          "reason": "Top rated South Indian breakfast spot with high popularity."
        },
        {
          "rank": 2,
          "restaurant_name": "Taaza Thindi",
          "match_score": 92,
          "reason": "Highly rated budget cafe offering authentic quick bites."
        }
      ],
      "recommendation_summary": "Taaza Thindi and Sreenidhi Gold are excellent options."
    }
    """
    
    engine = RecommendationEngine(api_key="mock_key")
    res = engine.recommend("South Indian in Banashankari under 800", model_name="llama-3.3-70b-versatile", limit=2)
    
    assert len(res["recommendations"]) == 2
    assert res["recommendations"][0]["restaurant_name"] == "Sreenidhi Gold"
    assert res["recommendations"][1]["restaurant_name"] == "Taaza Thindi"
    assert "excellent options" in res["recommendation_summary"]
    assert res["metadata"]["fallback_applied"] is False

@patch("recommendation_engine.Groq")
def test_groq_recommendation_fallback_on_api_error(mock_groq_class):
    """Verify that if Groq API throws an error, the engine falls back to heuristic ranking."""
    if not os.path.exists(DB_PATH):
        pytest.skip("Database does not exist.")
        
    mock_client = MagicMock()
    mock_groq_class.return_value = mock_client
    
    # Throw an exception during chat completion
    mock_client.chat.completions.create.side_effect = Exception("API Key Expired")
    
    engine = RecommendationEngine(api_key="mock_key")
    res = engine.recommend("Italian food in Banashankari under 1500", model_name="llama-3.3-70b-versatile")
    
    assert len(res["recommendations"]) > 0
    assert res["metadata"]["fallback_applied"] is True
    assert "heuristic" in res["recommendations"][0]["reason"].lower() or "matches your criteria" in res["recommendations"][0]["reason"].lower()
