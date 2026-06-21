# Data Dictionary - Zomato Restaurants Dataset

This data dictionary outlines the schema and definitions for the cleaned `restaurants` database table.

| Column Name | Data Type | Description | Example Value |
| :--- | :--- | :--- | :--- |
| id | INTEGER | Primary key, auto-incremented identifier for each restaurant record. | 1 |
| name | TEXT | The name of the restaurant. | "Jalsa" |
| location | TEXT | The locality, neighborhood, or area in which the restaurant is situated. | "Banashankari" |
| cuisines | TEXT | Pipe-separated (|) list of normalized, lowercase cuisines offered by the restaurant. | "north indian|mughlai|chinese" |
| rating | REAL | Aggregated user rating score, ranging between 1.0 and 5.0. | 4.1 |
| cost | INTEGER | Estimated cost of dining for two people. | 800 |
| votes | INTEGER | Total number of votes or reviews received by the restaurant. | 775 |
| online_order | BOOLEAN | Indicates whether the restaurant accepts online orders (True/False). | True |
| book_table | BOOLEAN | Indicates whether the restaurant allows online table bookings (True/False). | True |
| restaurant_type | TEXT | Categorical type representing the restaurant style (e.g., Casual Dining, Cafe, Pub). | "Casual Dining" |
