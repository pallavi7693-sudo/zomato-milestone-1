import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger("intent_parser")

# Default list of common localities in Zomato Bangalore dataset
COMMON_LOCATIONS = [
    "Banashankari", "Basavanagudi", "Jayanagar", "JP Nagar", "Koramangala",
    "Indiranagar", "BTM", "HSR", "Whitefield", "Marathahalli", "Bellandur",
    "Malleshwaram", "Rajajinagar", "MG Road", "Brigade Road", "Lavelle Road",
    "Residency Road", "Richmond Road", "Bannerghatta Road", "Electronic City",
    "Sarjapur Road", "Kalyan Nagar", "Kammanahalli", "Frazer Town"
]

# Common cuisines in the dataset
COMMON_CUISINES = [
    "Italian", "Chinese", "Biryani", "North Indian", "South Indian", "Mughlai",
    "Fast Food", "Continental", "Desserts", "Bakery", "Beverages", "Street Food",
    "Cafe", "Burger", "Pizza", "Seafood", "Asian", "Thai", "American"
]

# Common restaurant type / experience keywords mapped to their standard DB representations
COMMON_EXPERIENCES = {
    "casual dining": "Casual Dining",
    "fine dining": "Fine Dining",
    "cafe": "Cafe",
    "bakery": "Bakery",
    "pub": "Pub",
    "bar": "Bar",
    "lounge": "Lounge",
    "microbrewery": "Microbrewery",
    "sweet shop": "Sweet Shop",
    "quick bites": "Quick Bites"
}

def clean_json_response(text: str) -> str:
    """Strips markdown code blocks and whitespace from LLM response to get raw JSON."""
    text = text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        # Match ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    return text

class IntentParser:
    def __init__(self, api_key: Optional[str] = None):
        """Initializes the Groq client. Uses environment variables if api_key not provided."""
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq client initialized successfully in IntentParser.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
        else:
            logger.warning("GROQ_API_KEY is not set. IntentParser will use heuristic fallback.")

    def parse_intent(self, query_text: str, model_name: str = "llama-3.1-8b-instant") -> Dict[str, Any]:
        """
        Parses the user's natural language query to extract structured filters.
        Attempts to use Groq LLM first. Falls back to rule-based heuristics on error or if key is missing.
        """
        if not query_text or not query_text.strip():
            return self._get_empty_intent()

        if self.client:
            try:
                return self._parse_with_groq(query_text, model_name)
            except Exception as e:
                logger.error(f"Groq intent parsing failed: {e}. Falling back to heuristics.")
                return self._parse_with_heuristics(query_text)
        else:
            return self._parse_with_heuristics(query_text)

    def _parse_with_groq(self, query_text: str, model_name: str) -> Dict[str, Any]:
        """Uses Groq LLM to parse intent."""
        system_prompt = (
            "You are a helpful Zomato search intent extraction assistant. "
            "Your task is to parse a user query and output a structured JSON object containing the search filters. "
            "Extract these fields strictly: \n"
            "- 'location': string (or null if not found). ALWAYS correct common spelling mistakes in Bangalore location names (e.g., 'Kormanagala' -> 'Koramangala', 'Indra Nagar' -> 'Indiranagar').\n"
            "- 'cuisines': array of strings (or null/empty array if not found)\n"
            "- 'min_rating': float (or null if not found)\n"
            "- 'min_budget': float/int (or null if not found)\n"
            "- 'max_budget': float/int (or null if not found)\n"
            "- 'online_order': boolean (or null if not found)\n"
            "- 'book_table': boolean (or null if not found)\n"
            "- 'restaurant_type': array of strings (representing restaurant/dining experience types. You MUST ONLY extract from this list: ['Casual Dining', 'Fine Dining', 'Cafe', 'Pub', 'Bar', 'Lounge', 'Microbrewery', 'Sweet Shop', 'Quick Bites', 'Bakery', 'Dessert Parlor']. Do not extract descriptive keywords like 'rooftop', 'romantic', or 'cozy' into this list. Set to null/empty array if not found)\n"
            "- 'ambience': array of strings (representing descriptive vibe/ambience keywords like 'romantic', 'rooftop', 'cozy', 'live music', 'quiet', 'pet friendly'. Set to null/empty array if not found)\n\n"
            "Rules:\n"
            "1. Output ONLY the JSON object. Do NOT include any conversation, conversational wrapping, or introductory text.\n"
            "2. Ensure budget values are numeric (clean any currency symbols like Rs or ₹).\n"
            "3. For budget boundaries: if query says 'under X' or 'below X' or 'max X', set max_budget=X and min_budget=null. If 'above X' or 'min X' or 'more than X', set min_budget=X and max_budget=null. If 'between X and Y', set min_budget=X and max_budget=Y.\n"
            "4. If budget tiers are mentioned like 'expensive', 'premium', 'high-end', set min_budget to 1500 and max_budget to 2500. If 'cheap' or 'budget' is mentioned, set max_budget to 800."
        )

        user_prompt = f"User Query: \"{query_text}\""

        # Call Groq API
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=model_name,
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        response_text = chat_completion.choices[0].message.content
        cleaned_text = clean_json_response(response_text)
        
        parsed = json.loads(cleaned_text)
        
        # Standardize empty lists/nulls to match expected schema
        standardized = self._get_empty_intent()
        for key in standardized.keys():
            if key in parsed:
                # Type sanitization
                if key in ["cuisines", "restaurant_type", "ambience"] and parsed[key] is not None:
                    if isinstance(parsed[key], str):
                        standardized[key] = [parsed[key]]
                    elif isinstance(parsed[key], list):
                        standardized[key] = [str(item) for item in parsed[key]]
                elif key in ["online_order", "book_table"] and parsed[key] is not None:
                    standardized[key] = bool(parsed[key])
                elif key == "min_rating" and parsed[key] is not None:
                    try:
                        standardized[key] = float(parsed[key])
                    except (ValueError, TypeError):
                        standardized[key] = None
                elif key in ["min_budget", "max_budget"] and parsed[key] is not None:
                    try:
                        standardized[key] = float(parsed[key])
                    except (ValueError, TypeError):
                        standardized[key] = None
                else:
                    standardized[key] = parsed[key]
                    
        return standardized

    def _parse_with_heuristics(self, query_text: str) -> Dict[str, Any]:
        """A robust fallback intent parser using regular expressions and keyword matching."""
        logger.info("Parsing intent with heuristic fallback.")
        result = self._get_empty_intent()
        query_lower = query_text.lower()

        # 1. Location Matching
        for loc in COMMON_LOCATIONS:
            if re.search(r'\b' + re.escape(loc.lower()) + r'\b', query_lower):
                result["location"] = loc
                break

        # 2. Cuisine Matching
        cuisines_found = []
        for cuisine in COMMON_CUISINES:
            if re.search(r'\b' + re.escape(cuisine.lower()) + r'\b', query_lower):
                cuisines_found.append(cuisine)
        if cuisines_found:
            result["cuisines"] = cuisines_found

        # 3. Rating Matching
        # Patterns like: "above 4.2", "rating >= 4.0", "rating of 4.5", "4.0 rating", "4.2 rating"
        rating_match = re.search(r'(?:rating|rating of|above|>=)\s*([0-5](?:\.\d+)?)', query_lower)
        if rating_match:
            try:
                result["min_rating"] = float(rating_match.group(1))
            except ValueError:
                pass
        else:
            # Fallback to look for any float like 4.2 or 4.5 in context of rating
            rating_match_lone = re.search(r'\b([3-4]\.[0-9]|5\.0)\b', query_lower)
            if rating_match_lone:
                result["min_rating"] = float(rating_match_lone.group(1))

        # 4. Budget Tiers & Cost Matching
        # Budget keywords
        is_expensive = any(word in query_lower for word in ["expensive", "premium", "luxury", "high-end", "fine dining"])
        is_cheap = any(word in query_lower for word in ["cheap", "budget", "low-cost", "pocket-friendly", "affordable"])

        # Numbers extraction for budgets (e.g. "under 1500", "budget 800", "500 to 1200")
        numbers = re.findall(r'\b(?:rs\.?|rs|inr|₹)?\s*(\d{3,5})\b', query_lower)
        if len(numbers) >= 2:
            # If two numbers, treat lower as min and higher as max
            nums = sorted([int(n) for n in numbers])
            result["min_budget"] = float(nums[0])
            result["max_budget"] = float(nums[1])
        elif len(numbers) == 1:
            val = float(numbers[0])
            if "under" in query_lower or "below" in query_lower or "max" in query_lower or "within" in query_lower or "<=" in query_lower or "budget" in query_lower:
                result["max_budget"] = val
            elif "above" in query_lower or "over" in query_lower or "min" in query_lower or ">=" in query_lower:
                result["min_budget"] = val
            else:
                # Default to max budget if only one number mentioned
                result["max_budget"] = val
        else:
            # Apply default tiers if no numbers found
            if is_expensive:
                result["min_budget"] = 1500.0
                result["max_budget"] = 2500.0
            elif is_cheap:
                result["max_budget"] = 800.0

        # 5. Online Order Availability
        if any(word in query_lower for word in ["delivery", "online", "order"]):
            result["online_order"] = True

        # 6. Table Booking Availability
        if any(word in query_lower for word in ["book", "booking", "reservation", "reserve", "table"]):
            result["book_table"] = True

        # 7. Experience / Restaurant Type
        exp_found = []
        for kw, db_val in COMMON_EXPERIENCES.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', query_lower):
                exp_found.append(db_val)
        if exp_found:
            result["restaurant_type"] = exp_found

        return result

    def _get_empty_intent(self) -> Dict[str, Any]:
        """Returns default search intent filters dictionary structure."""
        return {
            "location": None,
            "cuisines": [],
            "min_rating": None,
            "min_budget": None,
            "max_budget": None,
            "online_order": None,
            "book_table": None,
            "restaurant_type": [],
            "ambience": []
        }
