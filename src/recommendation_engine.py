import os
import time
import json
import logging
import math
from typing import Dict, Any, List, Optional, Union
from groq import Groq
from dotenv import load_dotenv

from intent_parser import IntentParser, clean_json_response
from filter_engine import get_candidates

# Load environment variables
load_dotenv()

logger = logging.getLogger("recommendation_engine")

class RecommendationEngine:
    def __init__(self, api_key: Optional[str] = None):
        """Initializes the recommendation engine with an intent parser and Groq client."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.intent_parser = IntentParser(api_key=self.api_key)
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully in RecommendationEngine.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client in RecommendationEngine: {e}")
        else:
            logger.warning("GROQ_API_KEY is not set. RecommendationEngine will use heuristic fallback.")

    def recommend(
        self, 
        query_text: str, 
        model_name: str = "llama-3.3-70b-versatile", 
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Runs the end-to-end recommendation workflow:
        1. Extract filters from query_text.
        2. Query database for candidates (with relaxation).
        3. Rank candidates and generate explanations using Groq LLM (or heuristic fallback).
        """
        start_time = time.perf_counter()
        logger.info(f"Recommendation request received: '{query_text}'")

        # 1. Intent Extraction
        intent_start = time.perf_counter()
        filters = self.intent_parser.parse_intent(query_text)
        intent_time_ms = (time.perf_counter() - intent_start) * 1000.0
        logger.info(f"Parsed filters: {filters} in {intent_time_ms:.2f} ms")

        location = filters.get("location")
        if not location:
            # Safe default fallback for location if not present
            logger.warning("No location extracted from query. Defaulting to 'Jayanagar'.")
            location = "Jayanagar"
            filters["location"] = location

        # 2. Database Retrieval
        db_start = time.perf_counter()
        candidates_data = get_candidates(
            location=location,
            cuisines=filters.get("cuisines"),
            min_rating=filters.get("min_rating") or 0.0,
            min_budget=filters.get("min_budget"),
            max_budget=filters.get("max_budget"),
            online_order=filters.get("online_order"),
            book_table=filters.get("book_table"),
            restaurant_type=filters.get("restaurant_type"),
            max_candidates=50 # Safeguard candidate limit
        )
        db_time_ms = (time.perf_counter() - db_start) * 1000.0
        
        candidates = candidates_data.get("results", [])
        relaxation_applied = candidates_data.get("relaxation_applied", False)
        
        logger.info(f"Found {len(candidates)} database candidates in {db_time_ms:.2f} ms. Relaxation applied: {relaxation_applied}")

        if not candidates:
            # Return graceful no-results schema
            total_time_ms = (time.perf_counter() - start_time) * 1000.0
            return {
                "recommendations": [],
                "recommendation_summary": "We couldn't find any restaurants matching your search criteria. Please try broadening your preferences.",
                "metadata": {
                    "parsed_filters": filters,
                    "relaxation_applied": relaxation_applied,
                    "candidate_count": 0,
                    "fallback_applied": False,
                    "timings": {
                        "intent_parsing_ms": round(intent_time_ms, 2),
                        "db_query_ms": round(db_time_ms, 2),
                        "llm_ranking_ms": 0.0,
                        "total_ms": round(total_time_ms, 2)
                    }
                }
            }

        # 3. LLM Ranking & Explanation (or fallback)
        llm_start = time.perf_counter()
        fallback_applied = False
        
        if self.client and len(candidates) > 0:
            try:
                ranked_result = self._rank_with_llm(filters, candidates[:20], model_name, limit) # Pass top 20 candidates to avoid token bloat
            except Exception as e:
                logger.error(f"LLM ranking failed: {e}. Falling back to heuristic scoring.")
                ranked_result = self._rank_with_heuristics(filters, candidates, limit)
                fallback_applied = True
        else:
            ranked_result = self._rank_with_heuristics(filters, candidates, limit)
            fallback_applied = True

        llm_time_ms = (time.perf_counter() - llm_start) * 1000.0
        total_time_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "recommendations": ranked_result["recommendations"],
            "recommendation_summary": ranked_result["recommendation_summary"],
            "metadata": {
                "parsed_filters": filters,
                "relaxation_applied": relaxation_applied,
                "original_constraints": candidates_data.get("original_constraints"),
                "final_constraints": candidates_data.get("final_constraints"),
                "candidate_count": len(candidates),
                "fallback_applied": fallback_applied,
                "timings": {
                    "intent_parsing_ms": round(intent_time_ms, 2),
                    "db_query_ms": round(db_time_ms, 2),
                    "llm_ranking_ms": round(llm_time_ms, 2),
                    "total_ms": round(total_time_ms, 2)
                }
            }
        }

    def _rank_with_llm(self, filters: Dict[str, Any], candidates: List[Dict[str, Any]], model_name: str, limit: int) -> Dict[str, Any]:
        """Calls Groq to rank candidates and generate natural explanations."""
        # Standardize inputs to reduce token consumption
        compact_candidates = []
        for c in candidates:
            compact_candidates.append({
                "id": c["id"],
                "name": c["name"],
                "location": c["location"],
                "cuisines": c["cuisines"],
                "rating": c["rating"],
                "cost": c["cost"],
                "votes": c["votes"],
                "restaurant_type": c["restaurant_type"],
                "online_order": "Yes" if c["online_order"] else "No",
                "book_table": "Yes" if c["book_table"] else "No"
            })

        system_prompt = (
            "You are an expert culinary advisor and restaurant recommendation coordinator. "
            "Your task is to rank the candidate restaurants and write clear explanations for why they fit the user's criteria. "
            "Return a list of recommendations containing at most the requested limit.\n\n"
            "Ranking Criteria:\n"
            "1. IMPORTANT: If 'ambience' keywords (like romantic, cozy, rooftop) are provided in the user profile, you MUST strongly prioritize candidates that fit this vibe and explicitly explain why they fit the vibe in the 'reason'.\n"
            "2. Prioritize candidates that match optional requirements (e.g. online order, table booking, restaurant type).\n"
            "3. Rank highly rated and highly popular (based on number of votes) restaurants higher.\n"
            "4. Assess cost suitability based on budget bounds.\n\n"
            "Output Format:\n"
            "Provide your output strictly as a JSON object matching the following structure:\n"
            "{\n"
            "  \"recommendations\": [\n"
            "    {\n"
            "      \"rank\": 1,\n"
            "      \"restaurant_name\": \"Restaurant Name\",\n"
            "      \"match_score\": 95,\n"
            "      \"reason\": \"Detailed explanation of why it fits the user profile, mentioning specific attributes.\"\n"
            "    }\n"
            "  ],\n"
            "  \"recommendation_summary\": \"A short, helpful overall summary of the recommended choices.\"\n"
            "}\n"
            "Rules:\n"
            "- Output ONLY raw valid JSON.\n"
            "- Do not wrap the JSON in markdown code blocks. Do not add intro/outro text.\n"
            "- Make reasons personalized, professional, and convincing."
        )

        user_prompt = {
            "user_profile": {
                "location": filters["location"],
                "cuisines": filters["cuisines"],
                "min_rating": filters["min_rating"],
                "min_budget": filters["min_budget"],
                "max_budget": filters["max_budget"],
                "online_order": "Yes" if filters["online_order"] else None,
                "book_table": "Yes" if filters["book_table"] else None,
                "restaurant_type": filters["restaurant_type"],
                "ambience": filters.get("ambience", [])
            },
            "candidate_limit": limit,
            "candidates": compact_candidates
        }

        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt)}
            ],
            model=model_name,
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        content = chat_completion.choices[0].message.content
        cleaned = clean_json_response(content)
        parsed = json.loads(cleaned)
        
        # Schema validation checks
        if "recommendations" not in parsed or not isinstance(parsed["recommendations"], list):
            raise ValueError("LLM response missing 'recommendations' array.")
            
        return parsed

    def _rank_with_heuristics(self, filters: Dict[str, Any], candidates: List[Dict[str, Any]], limit: int) -> Dict[str, Any]:
        """Resilient rule-based scoring and template ranking engine fallback."""
        logger.info("Executing heuristic recommendation fallback.")
        scored_candidates = []

        for item in candidates:
            # Base score = rating * 0.6 + log1p(votes) * 0.4
            rating = item.get("rating") or 0.0
            votes = item.get("votes") or 0
            base_score = (rating * 0.6) + (math.log1p(votes) * 0.4)
            
            # Convert to a 100-point scale: rating 5.0 and votes ~1000 gives approx score of 6.0
            # Normalize so that top scores are around 90-100
            match_score = min(100, int((base_score / 6.0) * 100))

            # Optional filter alignment boosts (add 5 points for matching optional inputs)
            boost = 0
            if filters.get("online_order") is not None and item.get("online_order") == filters["online_order"]:
                boost += 5
            if filters.get("book_table") is not None and item.get("book_table") == filters["book_table"]:
                boost += 5
            if filters.get("restaurant_type"):
                matched_types = [t for t in filters["restaurant_type"] if t.lower() in (item.get("restaurant_type") or "").lower()]
                if matched_types:
                    boost += 5 * len(matched_types)
                    
            final_score = min(100, match_score + boost)
            
            # Generate structured reasoning template
            cuisine_list = item.get("cuisines", "").replace("|", ", ")
            votes_text = f"{votes} customer reviews" if votes > 0 else "newly registered"
            
            reason = (
                f"{item['name']} in {item['location']} matches your criteria well. "
                f"It holds an excellent rating of {rating}/5 based on {votes_text}, and falls within your budget at "
                f"Rs. {item['cost']} for two people. It features {item['restaurant_type'] or 'standard dining'} and serves "
                f"cuisines including {cuisine_list}."
            )
            if item.get("book_table"):
                reason += " Convenient table booking is available."
            if item.get("online_order"):
                reason += " It also offers online delivery."

            scored_candidates.append({
                "restaurant_name": item["name"],
                "match_score": final_score,
                "reason": reason,
                "cost": item["cost"],
                "rating": item["rating"],
                "votes": item["votes"]
            })

        # Sort by match score desc, then rating desc, then votes desc
        scored_candidates.sort(key=lambda x: (x["match_score"], x["rating"], x["votes"]), reverse=True)
        top_recs = scored_candidates[:limit]
        
        # Re-assign ranks
        for idx, rec in enumerate(top_recs, 1):
            rec["rank"] = idx
            # Clean temporary sorting fields
            del rec["cost"]
            del rec["rating"]
            del rec["votes"]

        if top_recs:
            summary = f"Based on our matching heuristics, we recommend {top_recs[0]['restaurant_name']} as your top option due to its strong rating and review profile, followed by {len(top_recs)-1} other highly relevant candidates in {filters.get('location')}."
        else:
            summary = f"No restaurants matched your criteria in {filters.get('location')}. Try broadening your filters or selecting a different location."

        return {
            "recommendations": top_recs,
            "recommendation_summary": summary
        }
