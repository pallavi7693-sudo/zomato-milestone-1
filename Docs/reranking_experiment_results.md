# Semantic Reranking Experiment Report

This report documents the results of the semantic re-ranking experiment comparing the baseline database filtering/sorting rules (Phase 2) against the Large Language Model re-ranking coordinator (Phase 3).

## Match Score Evaluation Dimensions
The LLM evaluated each candidate on a scale of 0-100 based on five core dimensions:
1. **Cuisine Relevance:** Direct and semantic cuisine matching (e.g. momos under Chinese).
2. **Budget Fit:** Proximity to maximum and minimum target budget bounds.
3. **Rating Quality:** Customer feedback weight.
4. **Restaurant Type Match:** Alignment with dining styles (e.g. Quick Bites vs Fine Dining).
5. **User Intent Alignment:** Semantic suitability relative to unstructured tags (e.g. 'cozy', 'romantic', 'rooftop').

---

## Query 1: "I want a cozy cafe in Jayanagar serving Italian under Rs.1000."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["Italian"], "min_rating": null, "min_budget": 0.0, "max_budget": 1000.0, "online_order": null, "book_table": null, "restaurant_type": ["Cafe"]}
**Candidates Found:** 5

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Tea Villa Cafe | 4.3 | Rs. 800 | 633 | Cafe, Casual Dining | 95 | Unchanged: High rating, high votes, and matches all criteria including location, cuisine, budget, and type. |
| 2 | 2 | The Airos | 4.1 | Rs. 650 | 130 | Cafe | 90 | Unchanged: Good rating, matches location, cuisine, budget, and type, but lower votes compared to Tea Villa Cafe. |
| 3 | 3 | Grazers | 3.9 | Rs. 650 | 291 | Cafe | 85 | Unchanged: Matches location, cuisine, budget, and type, but slightly lower rating and fewer votes than top two. |
| 4 | 4 | Mug N Bean | 3.9 | Rs. 400 | 247 | Cafe | 80 | Unchanged: Lower cost, matches location, cuisine, and type, but lower rating and fewer votes. |
| 5 | 5 | Brew Bakes | 3.4 | Rs. 550 | 13 | Cafe | 70 | Unchanged: Matches location, cuisine, and type, but significantly lower rating and very few votes. |

---

## Query 2: "I want a rooftop pizza place in Jayanagar."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["Pizza"], "min_rating": null, "min_budget": null, "max_budget": null, "online_order": null, "book_table": null, "restaurant_type": null}
**Candidates Found:** 13

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Once Upon a Rooftop | 4.3 | Rs. 1000 | 1278 | Casual Dining, Bar | 95 | Unchanged: Highly relevant rooftop pizza place in Jayanagar with a good rating and variety of cuisines. |
| 2 | 2 | Enerjuvate Studio & Cafe | 4.2 | Rs. 800 | 731 | Cafe | 80 | Unchanged: Cafe with pizza option in Jayanagar, but not specifically a rooftop, hence a lower score. |
| 3 | 3 | Salut | 4.1 | Rs. 1200 | 442 | Pub, Casual Dining | 75 | Unchanged: Has pizza, but not primarily a pizza place and lacks rooftop feature, hence a lower score. |
| 4 | 4 | The Airos | 4.1 | Rs. 650 | 130 | Cafe | 70 | Unchanged: Cafe with pizza, but not a rooftop and lower votes compared to top options. |
| 5 | 5 | Ragoo's | 3.9 | Rs. 800 | 233 | Casual Dining | 65 | Unchanged: Casual dining with pizza, but lacks rooftop and has lower rating and votes. |

---

## Query 3: "I want a quick bites Chinese joint in Jayanagar under Rs.600."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["Chinese"], "min_rating": null, "min_budget": 0.0, "max_budget": 600.0, "online_order": null, "book_table": null, "restaurant_type": ["Quick Bites"]}
**Candidates Found:** 20

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Mystique Palate | 4.1 | Rs. 300 | 337 | Quick Bites | 92 | Unchanged: High rating, perfect cuisine match, and suitable budget. |
| 2 | 2 | Kabab Magic | 4.0 | Rs. 400 | 952 | Quick Bites | 90 | Unchanged: High votes, good rating, and matches the quick bites criteria. |
| 3 | 3 | Food Springs | 4.0 | Rs. 400 | 232 | Quick Bites | 88 | Unchanged: Good rating, suitable cost, and aligns with the user's location preference. |
| 4 | 4 | Kalpavriksha Upahara | 3.9 | Rs. 400 | 126 | Quick Bites | 85 | Unchanged: Matches the quick bites and Chinese cuisine criteria, but has a slightly lower rating. |
| 5 | 5 | Upahara Darshini | 3.8 | Rs. 400 | 339 | Quick Bites | 83 | Unchanged: Good votes, suitable cost, and aligns with the user's location and cuisine preferences. |

---

## Query 4: "I want a highly rated romantic lounge or microbrewery in Jayanagar."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": null, "min_rating": 4.0, "min_budget": null, "max_budget": null, "online_order": null, "book_table": null, "restaurant_type": ["Lounge", "Microbrewery"]}
**Candidates Found:** 2

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Brew Meister | 4.1 | Rs. 1500 | 970 | Microbrewery, Casual Dining | 95 | Unchanged: Highly rated microbrewery in Jayanagar with a high rating of 4.1, matching the user's semantic context of a 'romantic lounge or microbrewery'. |
| 2 | 2 | The Lounge - Eden Park Restaurants | 3.7 | Rs. 1350 | 151 | Lounge | 70 | Unchanged: Lounge in Jayanagar but with a lower rating of 3.7, not meeting the user's minimum rating requirement of 4.0, thus scoring lower. |

---

## Query 5: "Pocket friendly South Indian breakfast under Rs.300 in Jayanagar."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["South Indian"], "min_rating": null, "min_budget": 300.0, "max_budget": null, "online_order": null, "book_table": null, "restaurant_type": null}
**Candidates Found:** 20

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 5 | 1 | Ranganna Military Hotel | 4.2 | Rs. 350 | 725 | Quick Bites | 95 | **+4 Up** (Semantic Boost): High score due to perfect match of South Indian cuisine, budget-friendly cost of Rs. 350, and alignment with 'Pocket friendly' semantic context. |
| 12 | 2 | The Krishna Grand Xpress | 4.0 | Rs. 350 | 136 | Quick Bites | 92 | **+10 Up** (Semantic Boost): High score due to match of South Indian cuisine, budget-friendly cost of Rs. 350, and alignment with 'Pocket friendly' semantic context. |
| 15 | 3 | Bangalore Agarwal Bhavan | 3.9 | Rs. 400 | 134 | Quick Bites | 90 | **+12 Up** (Semantic Boost): High score due to match of South Indian cuisine, budget-friendly cost of Rs. 400, and alignment with 'Pocket friendly' semantic context. |
| 11 | 4 | Food Springs | 4.0 | Rs. 400 | 232 | Quick Bites | 88 | **+7 Up** (Semantic Boost): High score due to match of South Indian cuisine, budget-friendly cost of Rs. 400, and alignment with 'Pocket friendly' semantic context. |
| 19 | 5 | Rustic Stove | 3.8 | Rs. 900 | 577 | Casual Dining | 85 | **+14 Up** (Semantic Boost): High score due to match of South Indian cuisine, budget-friendly cost of Rs. 400, and alignment with 'Pocket friendly' semantic context. |

---

## Query 6: "Expensive premium high-end dining under Rs.2500 in Jayanagar with Italian."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["Italian"], "min_rating": null, "min_budget": 1500.0, "max_budget": 2500.0, "online_order": null, "book_table": null, "restaurant_type": null}
**Candidates Found:** 0

*No candidates found in database matching intent.*

---

## Query 7: "Family friendly restaurant in Jayanagar with North Indian and table booking."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["North Indian"], "min_rating": null, "min_budget": null, "max_budget": null, "online_order": null, "book_table": true, "restaurant_type": null}
**Candidates Found:** 20

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Sea Lions BBQ & Grills | 4.6 | Rs. 1100 | 538 | Casual Dining | 92 | Unchanged: High rating, diverse cuisines including North Indian, and table booking available. |
| 2 | 2 | Cable Car | 4.4 | Rs. 1000 | 1224 | Casual Dining | 90 | Unchanged: High rating, North Indian cuisine available, and table booking option. |
| 3 | 3 | Subz | 4.2 | Rs. 1000 | 2022 | Casual Dining | 88 | Unchanged: High votes, North Indian cuisine, and table booking facility. |
| 4 | 4 | The Royal Corner - Pai Viceroy | 4.2 | Rs. 900 | 815 | Casual Dining | 86 | Unchanged: North Indian cuisine, moderate cost, and table booking available. |
| 5 | 5 | Chutney Chang | 4.1 | Rs. 1500 | 2339 | Casual Dining | 84 | Unchanged: High votes, North Indian and other cuisines, but higher cost. |

---

## Query 8: "A quiet dessert parlour or sweet shop in Jayanagar under Rs.500."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["Dessert Parlor", "Sweet Shop"], "min_rating": null, "min_budget": 0.0, "max_budget": 500.0, "online_order": null, "book_table": null, "restaurant_type": null}
**Candidates Found:** 0

*No candidates found in database matching intent.*

---

## Query 9: "Late night fast food delivery under Rs.600 in Jayanagar."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": ["Fast Food"], "min_rating": null, "min_budget": null, "max_budget": 600.0, "online_order": true, "book_table": false, "restaurant_type": null}
**Candidates Found:** 20

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Shake It Off | 4.4 | Rs. 600 | 659 | Beverage Shop, Quick Bites | 92 | Unchanged: High rating, perfect location, and fast food cuisine match with a cost at the upper limit of the budget. |
| 2 | 2 | Tummy Fuel | 4.2 | Rs. 400 | 449 | Cafe | 90 | Unchanged: Good rating, lower cost, and fast food available, making it a strong candidate for late night delivery. |
| 3 | 3 | Rooftop Cafe | 4.1 | Rs. 400 | 796 | Cafe | 88 | Unchanged: High votes and good rating, with fast food and lower cost, but 'rooftop' does not align with 'late night delivery' context. |
| 4 | 4 | Roll Over | 4.1 | Rs. 500 | 438 | Dessert Parlor | 85 | Unchanged: Good rating, variety of cuisines including fast food, and moderate cost, but not specifically known for late night delivery. |
| 5 | 5 | Leon Grill | 4.1 | Rs. 500 | 414 | Quick Bites | 84 | Unchanged: Good rating, variety of cuisines, moderate cost, but 'grill' might not fit the 'fast food' context as closely as others. |

---

## Query 10: "Pub with great music and finger food in Jayanagar."
**Parsed Filters:** {"location": "Jayanagar", "cuisines": null, "min_rating": null, "min_budget": null, "max_budget": null, "online_order": null, "book_table": null, "restaurant_type": ["Pub"]}
**Candidates Found:** 3

| P2 Rank | P3 Rank | Restaurant Name | Rating | Cost | Votes | Type | LLM Score | Rank Shift Details |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: | :--- |
| 1 | 1 | Salut | 4.1 | Rs. 1200 | 442 | Pub, Casual Dining | 92 | Unchanged: High rating, diverse cuisines including finger food, and presence in Jayanagar with a pub type matches the user's semantic context. |
| 2 | 2 | LIT Gastro Pub | 3.8 | Rs. 1000 | 197 | Pub | 85 | Unchanged: Matches the pub type and location, but slightly lower rating and less votes compared to Salut. |
| 3 | 3 | English Channel | 3.7 | Rs. 1200 | 47 | Pub | 78 | Unchanged: Although it's a pub with finger food in Jayanagar, lower rating and fewer votes decrease its score. |

---

