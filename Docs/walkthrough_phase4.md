# Walkthrough: Phase 4 (Streamlit Frontend UI)

Phase 4 implementation for the Zomato-inspired Restaurant Discovery & Recommendation System is complete. We designed, coded, and validated a premium Zomato-themed Streamlit dashboard.

---

## 1. File Map of Changes
* [app.py](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/app.py) [MODIFY]:
  - Replaced the placeholder code with the fully functional interactive Streamlit application.
  - Implemented custom CSS styles injecting the premium *Outfit* font from Google Fonts and a crimson red (`#CB202D`) card styling system.
  - Integrated the sidebar filters mapping directly to database fields.
  - Built a tabbed navigation system supporting natural language query input and interactive form-based searches.

---

## 2. Branding & Custom UI Aesthetics
We bypassed generic browser designs by injecting customized CSS blocks (`unsafe_allow_html=True`):
* **Typography:** Imported Google Font *Outfit* as the global font.
* **Palette:** Built around Zomato's crimson red brand color (`#CB202D`).
* **Visual Presentation:** Styled recommended restaurants inside custom HTML blocks showing:
  - Header: Restaurant name side-by-side with the AI Match Score percentage badge.
  - Meta: Review count, average rating, average cost, table booking, and delivery availability.
  - Tags: Badge tags showing cuisines and styles (e.g. Cafe, Microbrewery).
  - Justification: Border-highlighted italicized box detailing the LLM's reasoning.

---

## 3. Layout and Features

### sidebar Filter Options
Allows users to manually set parameters that map to the underlying candidate database engine:
- Location selection dropdown (populated dynamically from the database).
- Cuisine multiselect options.
- Maximum and Minimum Cost-for-Two sliders.
- Minimum Rating slider.
- Table booking and delivery requirement switches.
- Restaurant type/style multiselect list.

### Tabbed Interface
1. **💬 AI Assistant (Conversational):** Contains a large text field where users enter natural language prompts (e.g. *"Cozy cafe under 1000 in Jayanagar"*). Clicking **Find Recommendations** triggers the Groq parser, displays the extracted JSON intent tags, performs candidate filtering, and ranks recommendations.
2. **🎛️ Interactive Filters Search:** Allows traditional manual search using the sidebar configuration values, which are passed directly into candidate generation and ranked.

### Constraint Relaxation Banners
If search constraints yield fewer than 10 matches, the interface displays a warning banner explaining exactly what parameter values were relaxed:
- Original rating vs. final relaxed rating.
- Original budget limit vs. final relaxed budget.

---

## 4. Verification and Execution
To run the Streamlit app locally:
```bash
streamlit run app.py
```

### Fallback / Resilience Validation
* **When Groq API key is present:** Recommendations show a success banner `Live Groq AI Reasoning Active`.
* **When Groq API key is missing/unreachable:** Recommendations run immediately using local heuristics (weighted scoring formula + templated explanations), displaying an info banner `Local Heuristic Scoring Active`. The system remains fully functional and robust.

### timing Footers
Displays request timings at the bottom of the search results (e.g. `DB Filter: 1.88ms | LLM Ranking: 918.0ms | Total: 1.65s`).
