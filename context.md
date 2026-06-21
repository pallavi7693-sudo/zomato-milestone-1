# Context: AI-Powered Restaurant Recommendation System (Zomato-Inspired)

This document provides a comprehensive overview of the context, objectives, requirements, architecture, and success criteria for the AI-Powered Restaurant Recommendation System, as defined in [Problem statement.txt](file:///c:/Users/palla/OneDrive/Desktop/Zomato%20milestone1/Docs/Problem%20statement.txt).

---

## 1. Project Background & Motivation

Standard restaurant discovery platforms (like Zomato) feature thousands of dining options. However, traditional search and filter interfaces (by location, cuisine, rating, cost) often return a long, unranked, and unexplainable list of results. 

By integrating **Large Language Models (LLMs)** with structured restaurant data, this project aims to create an intelligent, conversational, and context-aware discovery tool. The system will combine:
- **Traditional data filtering** (for speed, cost-effectiveness, and correctness).
- **LLM-based reasoning and natural language generation** (for personalized ranking, comparative analysis, and clear explanations).

---

## 2. Core Problem & Objectives

### Problem Definition
Design and build an application that ingests a real-world restaurant dataset, collects structured and natural language user preferences, filters down candidates, and uses an LLM to rank and explain recommendations.

### Objectives
1. **Personalized Recommendations:** Tailor dining choices to precise user constraints.
2. **Explainable AI Suggestions:** Generate natural language justifications explaining *why* each restaurant matches the user's specific context.
3. **Intelligent Ranking:** Rank options based on reasoning (balancing ratings, budget, popularity, and extra constraints) rather than simple sort keys.
4. **Premium UX:** Present recommendations in an elegant, interactive interface.
5. **Real-World Data:** Use the Hugging Face Zomato Restaurant Recommendation Dataset.

---

## 3. Dataset Specifications

- **Source Dataset:** [ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation)
- **Key Attributes to Ingest & Clean:**
  - `Restaurant Name`: Name of the dining establishment.
  - `Location`: City or locality.
  - `Cuisine`: Types of cuisines offered (often comma-separated lists).
  - `Rating`: Numerical customer rating.
  - `Cost`: Average cost for two people.
  - `Votes`: Total number of reviews/votes.
  - `Restaurant Type`: E.g., Casual Dining, Cafe, Fine Dining, Pub, etc.
  - `Online Order Availability`: Yes/No flag.
  - `Table Booking Availability`: Yes/No flag.

---

## 4. Functional Architecture & Modules

The system is structured into five core functional modules:

### Module 1: Data Ingestion and Preprocessing
- Load dataset from Hugging Face repository.
- Clean missing or noisy values.
- Standardize location formats and normalize rating/cost fields.
- Store cleaned data in a fast, queryable format (e.g., pandas DataFrame, SQLite, or a vector/document store).

### Module 2: User Preference Collection
Collects user queries through a structured form or natural language input containing:
- **Mandatory Fields:** Location, Budget Range, Cuisine, and Minimum Rating.
- **Optional Fields:** Family-friendly, Quick service, Fine dining, Outdoor seating, Delivery availability, Table booking availability, and Veg/Vegan options.

*Example User Query:*
> "I am looking for an Italian restaurant in Bangalore with a budget of ₹1500 for two people and a rating above 4.2. It should be family-friendly and have table booking available."

### Module 3: Recommendation Candidate Generation
- Run fast query-based filtering on the database to reduce the search space.
- Apply hard constraints (e.g., matching location, budget constraints, rating thresholds, cuisine).
- Shrink the search space from thousands of entries down to a concise candidate list (typically 20–50 candidate restaurants).

### Module 4: LLM-Based Recommendation Engine (Powered by Groq)
- Inject the candidate list and the user profile JSON into a carefully engineered prompt.
- Integrate with the Groq API (using models such as Llama-3-70b-8192 or Llama-3-8b-8192) for high-performance, low-latency recommendations.
- **Tasks performed by the LLM:**
  - **Ranking:** Sort candidates intelligently based on match scores.
  - **Explanations:** Generate customized, natural language reasons (e.g., *"This restaurant is selected because it matches your target budget, offers table booking, and is highly reviewed for its family-friendly dining environment"*).
  - **Comparisons:** Provide trade-offs between the top options.
  - **Summary:** Offer a helpful concluding summary.

### Module 5: Recommendation Presentation Layer
- Present results in an attractive, readable grid/table layout containing:
  - Rank and Restaurant Details (Cuisine, Rating, Cost for Two).
  - Custom LLM-generated matching score or explanation.

---

## 5. Non-Functional Requirements

- **Performance:** Deliver recommendation results (filtering + LLM invocation) in **under 5 seconds**.
- **Scalability:** Scale to support thousands of database entries and multiple concurrent users.
- **Explainability:** Ensure every recommended choice includes a human-readable justification.
- **Reliability:** Gracefully handle incomplete input queries, empty filters (back-off strategies), or missing data values without throwing exceptions.
- **Usability:** Provide a responsive and clean layout compatible with both mobile devices and desktops.

---

## 6. System Design Flow Chart

```text
                  +-------------------------------+
                  |        User Interface         |
                  |  (Collects query/preferences) |
                  +---------------+---------------+
                                  |
                                  v
                  +-------------------------------+
                  |        Input Processor        |
                  | (Parses parameters/JSON profile) |
                  +---------------+---------------+
                                  |
                                  v
                  +-------------------------------+
                  |       Restaurant Filter       |
                  | (Applies location, budget, rating) |
                  +---------------+---------------+
                                  |
                                  v
                  +-------------------------------+
                  |       Candidate Results       |
                  |      (Shortlist of 20-50)     |
                  +---------------+---------------+
                                  |
                                  v
                  +-------------------------------+
                  |           LLM Layer           |
                  |  (Prompts LLM for ranking,    |
                  |   explaining, and comparing)  |
                  +---------------+---------------+
                                  |
                                  v
                  +-------------------------------+
                  |       Recommendation UI       |
                  |  (Displays ranked list + text)|
                  +-------------------------------+
```

---

## 7. Deliverables & Evaluation

### Expected Deliverables
1. **Pipeline:** Data Ingestion & preprocessing scripts.
2. **Filtering Engine:** Database querying & preprocessing code.
3. **Prompt Strategy:** Prompt templates and LLM orchestration layer.
4. **Integration Component:** API wrapper to call the LLM.
5. **Interactive UI:** Streamlit, Flask, React, or standard web application.
6. **Documentation:** System architecture, evaluation, and prompt design reports.

### Success Metrics
- **Relevance:** Recommendations closely align with user intent.
- **Personalization:** Adaptable recommendations for varying profiles.
- **Explainability:** High quality, conversational explanations.
- **Accuracy:** Correct constraints application.
- **Response Time:** Under 5 seconds.
- **User Satisfaction:** Utility of the recommended lists.
