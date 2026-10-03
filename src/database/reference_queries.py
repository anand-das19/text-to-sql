"""Verified reference queries and benchmark sample questions.

Provides curated questions across Sales, Customers, Budgets, and Regions
with validated SQLite queries, expected behaviors, and fallback results.
"""
from typing import List, Dict, Any, Optional

REFERENCE_QUERIES: List[Dict[str, Any]] = [
    {
        "category": "Sales Performance",
        "question": "What are the top 5 best-selling products by total revenue?",
        "sql": """SELECT 
    p."Product Name", 
    ROUND(SUM(s."Line Total"), 2) AS total_revenue,
    SUM(s."Order Quantity") AS total_units_sold
FROM sales_order s
JOIN products p ON s."Product Description Index" = p."Index"
GROUP BY p."Product Name"
ORDER BY total_revenue DESC
LIMIT 5;""",
        "explanation": "Joins `sales_order` with `products`, aggregates the sum of `Line Total` and units sold, and orders by revenue descending."
    },
    {
        "category": "Customer Analytics",
        "question": "Which customers generated the highest sales order value?",
        "sql": """SELECT 
    c."Customer Names", 
    ROUND(SUM(s."Line Total"), 2) AS total_spent,
    COUNT(s."OrderNumber") AS total_orders
FROM sales_order s
JOIN customers c ON s."Customer Name Index" = c."Customer Index"
GROUP BY c."Customer Names"
ORDER BY total_spent DESC
LIMIT 5;""",
        "explanation": "Aggregates revenue and order counts per customer by joining `sales_order` with `customers`."
    },
    {
        "category": "Budgets & Targets",
        "question": "What was the budget of Product 12?",
        "sql": """SELECT 
    "Product Name", 
    "2017 Budgets" AS budget
FROM budgets_2017
WHERE "Product Name" = 'Product 12';""",
        "explanation": "Queries the `budgets_2017` table for 'Product 12'."
    },
    {
        "category": "Regional Analysis",
        "question": "What is the total sales breakdown by US geographic region?",
        "sql": """SELECT 
    sr."Region", 
    ROUND(SUM(s."Line Total"), 2) AS total_sales,
    COUNT(DISTINCT s."OrderNumber") AS total_orders
FROM sales_order s
JOIN regions r ON s."Delivery Region Index" = r."id"
JOIN state_regions sr ON r."state_code" = sr."State Code"
GROUP BY sr."Region"
ORDER BY total_sales DESC;""",
        "explanation": "Executes a three-way join between `sales_order`, `regions`, and `state_regions` to aggregate sales by macro region."
    },
    {
        "category": "Customer Lookup",
        "question": "What is the total 'Line Total' for Geiss Company?",
        "sql": """SELECT 
    c."Customer Names", 
    ROUND(SUM(s."Line Total"), 2) AS total_sales
FROM sales_order s
JOIN customers c ON s."Customer Name Index" = c."Customer Index"
WHERE c."Customer Names" = 'Geiss Company'
GROUP BY c."Customer Names";""",
        "explanation": "Filters for 'Geiss Company' and sums `Line Total`."
    },
    {
        "category": "Time & Channels",
        "question": "What is the sales breakdown by sales channel?",
        "sql": """SELECT 
    s."Channel", 
    ROUND(SUM(s."Line Total"), 2) AS total_sales,
    COUNT(s."OrderNumber") AS order_count
FROM sales_order s
GROUP BY s."Channel"
ORDER BY total_sales DESC;""",
        "explanation": "Groups `sales_order` by `Channel` to assess distribution channels."
    },
    {
        "category": "Demographics",
        "question": "Find the top 5 cities by population in the regions table.",
        "sql": """SELECT 
    name AS city, 
    state, 
    population, 
    median_income
FROM regions
ORDER BY population DESC
LIMIT 5;""",
        "explanation": "Queries the `regions` table sorted by population descending."
    }
]


def get_reference_by_question(question: str) -> Optional[Dict[str, Any]]:
    """Look up a reference query by flexible question matching."""
    def clean(s: str) -> str:
        return s.strip().lower().rstrip("?.! ")

    target = clean(question)
    for ref in REFERENCE_QUERIES:
        if clean(ref["question"]) == target:
            return ref
    return None


def get_sample_questions() -> List[str]:
    """Get list of sample questions for suggestions."""
    return [q["question"] for q in REFERENCE_QUERIES]
