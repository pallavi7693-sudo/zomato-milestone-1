# Edge Case Analysis & Corner Scenarios

This document analyzes the corner scenarios, potential failure modes, and robust handling strategies for the AI-Powered Restaurant Recommendation System, as defined in [context.md](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/context.md).

---

## 1. Data Ingestion & Preprocessing Edge Cases

| Scenario | Potential Failure / Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Missing or Malformed Ratings** | Ratings represented as `"NEW"`, `"-"`, or `"3.8/5"` can break float casting, causing ingestion script crashes. | - Clean rating string using regex: extract the float before `/`. <br> - Default `"NEW"`, `"-"`, or empty strings to `None` or `0.0`. |
| **Formatting Anomalies in Cost** | Cost for two represented as strings with commas (e.g., `"1,200"`) or null values. | - Strip out non-numeric characters (commas, currency symbols). <br> - Cast to integer. Replace null values with the median cost of the locality. |
| **Missing Cuisines** | Empty or missing cuisine values fail string-matching filters. | - Replace nulls with `"Unknown"`. <br> - Use case-insensitive substring search (e.g., `LIKE '%cuisine%'`) instead of exact matches. |
| **Varying Location/Localities** | A user inputs `"Koramangala"`, but the database records list detailed sectors (e.g., `"Koramangala 5th Block"`). | - Implement hierarchical mapping: match the parent locality if exact sector is not found. <br> - Provide standardized dropdown selectors in the UI alongside text search. |

---

## 2. User Preference & Input Edge Cases

| Scenario | Potential Failure / Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Overly Restrictive Constraints** | A user requests rating > `4.8`, budget < `₹200`, and cuisine = `Japanese`. This results in **0 database candidates**. | **Constraint Relaxation Algorithm:** <br> 1. Stepwise decrease min rating threshold (e.g., by `0.2`). <br> 2. Stepwise increase budget constraint (e.g., by `20%`). <br> 3. If still zero, search for the target cuisine in neighboring localities and alert the user: *"No exact matches found. Showing relaxed recommendations."* |
| **Natural Language Ambiguity** | Natural language queries with typos (e.g., `"Italien food"`) or abstract descriptors (e.g., `"expensive dining"`). | - Normalize query using standard fuzzy string matching. <br> - Map abstract descriptors to numeric filters (e.g., `"cheap"` $\rightarrow$ cost < median; `"expensive"` $\rightarrow$ cost > 75th percentile). |
| **Missing Mandatory Parameters** | User leaves location or budget empty. | - Validate fields in the UI before submission. <br> - Fallback to default parameters (e.g., Locality = popular hub, Budget = average city median). |

---

## 3. Candidate Generation Edge Cases

| Scenario | Potential Failure / Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Candidate Overflow (>50 entries)** | Too many restaurants match the criteria, leading to high LLM token costs and latency, or exceeding the model context window. | - Sort candidates by a hybrid score: $(\text{Rating} \times 0.7) + (\text{Votes} \times 0.3)$. <br> - Take only the **top 25-30** records to construct the prompt. |
| **Candidate Underflow (<5 entries)** | Very few results are passed to the LLM, reducing the value of LLM ranking and comparison. | - Relax optional constraints (e.g., drop "family-friendly" or "table booking" filters first) to back-fill candidates up to a minimum count of `10`. |

---

## 4. LLM & Groq API Edge Cases

| Scenario | Potential Failure / Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Groq API Rate Limits / Timeouts** | The application hangs or crashes when the Groq service returns a `429 (Rate Limit)` or `503` error. | - Implement connection timeouts (max 3 seconds) using `timeout` parameters. <br> - Integrate the **Heuristics Fallback Engine**: automatically bypass the LLM and generate a pre-formatted template-based recommendation based on rating and popularity scores. |
| **Invalid JSON Output** | The LLM returns conversational text or malformed JSON (e.g. unescaped quotes or missing keys) that breaks python's `json.loads`. | - Enforce JSON mode in the API options: `response_format={"type": "json_object"}`. <br> - Apply regex cleaners to isolate the JSON block `{...}` from any wrapping text. <br> - Run structured error correction (retry loop) or fallback to database sorting if parsing fails. |
| **Hallucinated Candidates** | The LLM "invents" a restaurant name or lists a restaurant that was not part of the input candidate array. | - Validate the LLM's output: cross-check the output restaurant IDs or names against the candidate list. <br> - Filter out any hallucinated entries before rendering on the frontend. |
| **Attribute Mismatch (Hallucinated booking status)** | LLM claims a restaurant is "family-friendly" or "offers table booking" when the candidate data shows otherwise. | - The system prompts instructions to strict compliance: *"Only state attributes directly supported by the candidate JSON."* <br> - Display database metadata directly from the source records in the UI table cards, relying on the LLM only for the "explanation string". |

---

## 5. UI & Environment Edge Cases

| Scenario | Potential Failure / Risk | Mitigation Strategy |
| :--- | :--- | :--- |
| **Missing API Key** | App starts but fails on user request because `GROQ_API_KEY` is not configured. | - During startup, check for `os.environ.get("GROQ_API_KEY")`. <br> - If missing, display a clear warning banner in Streamlit asking the developer to configure `.env` and disable LLM functionality (falling back to heuristics mode). |
| **Concurrent UI Submissions** | A user repeatedly clicks the search button while a query is loading, triggering duplicate backend requests. | - Disable the submit button in the UI using Streamlit's loading spinner state while request is active. |
