"""Database schema definitions, documentation, and prompt formatting helpers.

Provides structured schema information and LLM-friendly schema descriptions
highlighting foreign key relationships and SQLite syntax guidelines.
"""
import sqlite3
from typing import Dict, List, Any
import pandas as pd
from src.config import DB_PATH

# Human-readable documentation of the tables and key relationships
SCHEMA_RELATIONSHIPS = """
DATABASE RELATIONSHIPS:
1. sales_order."Customer Name Index" = customers."Customer Index"
2. sales_order."Product Description Index" = products."Index"
3. sales_order."Delivery Region Index" = regions."id"
4. regions."state_code" = state_regions."State Code" (or regions."state" = state_regions."State")
5. products."Product Name" = budgets_2017."Product Name" (also aliased as "2017_budgets")

TABLE DESCRIPTIONS:
- sales_order (also aliased as sales_orders): 64,104 transactions.
  Columns:
    - OrderNumber (TEXT): Unique order identifier, e.g. 'SO - 000101'
    - OrderDate (TEXT): Date in 'YYYY-MM-DD' format, e.g. '2021-01-01'
    - Customer Name Index (INTEGER): Foreign key to customers."Customer Index"
    - Channel (TEXT): Sales channel, e.g. 'Wholesale', 'Distributor', 'Export'
    - Currency Code (TEXT): Currency, e.g. 'USD'
    - Warehouse Code (TEXT): Warehouse location code
    - Delivery Region Index (INTEGER): Foreign key to regions."id"
    - Product Description Index (INTEGER): Foreign key to products."Index"
    - Order Quantity (INTEGER): Units purchased
    - Unit Price (REAL): Price per unit in USD
    - Line Total (REAL): Total transaction amount (revenue) in USD
    - Total Unit Cost (REAL): Cost per unit in USD

- customers: 175 customer companies.
  Columns:
    - Customer Index (INTEGER): Primary key
    - Customer Names (TEXT): Company name, e.g. 'Geiss Company', 'Jaxbean Group'

- products: 30 products catalog.
  Columns:
    - Index (INTEGER): Primary key
    - Product Name (TEXT): Name of product, e.g. 'Product 1', 'Product 12'

- regions: 994 geographic regions and counties.
  Columns:
    - id (INTEGER): Primary key
    - name (TEXT): City / locality name, e.g. 'Auburn', 'Birmingham'
    - county (TEXT): County name
    - state_code (TEXT): Two-letter state code, e.g. 'AL', 'CA'
    - state (TEXT): State name, e.g. 'Alabama', 'California'
    - population (INTEGER): Population
    - median_income (REAL): Median household income
    - time_zone (TEXT): Timezone string

- state_regions: 48 US states mapped to major sales regions.
  Columns:
    - State Code (TEXT): Two-letter code, e.g. 'AL'
    - State (TEXT): State name, e.g. 'Alabama'
    - Region (TEXT): Major US sales region: 'South', 'Midwest', 'Northeast', 'West'

- budgets_2017 (also aliased as 2017_budgets): 30 product annual budget targets.
  Columns:
    - Product Name (TEXT): e.g. 'Product 1', 'Product 12'
    - 2017 Budgets (REAL): Budget target in USD
"""

SQLITE_SYNTAX_RULES = """
SQLITE GUIDELINES:
- Output ONLY valid SQLite SELECT queries.
- Column names with spaces MUST be enclosed in double quotes or square brackets, e.g. "Customer Names", "Line Total", [Product Name].
- Dates are stored as ISO 'YYYY-MM-DD' strings. Use strftime('%Y', OrderDate) or strftime('%Y-%m', OrderDate) for date filtering and grouping.
- Do NOT use MySQL specific syntax like CURDATE() or backticks for quoting when double quotes or brackets are standard SQLite.
- Always include appropriate JOIN clauses when querying across multiple tables.
- Return ONLY the executable SQL query.
"""


def get_schema_prompt_context() -> str:
    """Generate the full schema context for LLM prompt insertion."""
    return f"{SCHEMA_RELATIONSHIPS}\n\n{SQLITE_SYNTAX_RULES}"


def get_table_sample(table_name: str, limit: int = 3) -> pd.DataFrame:
    """Retrieve sample rows from a table."""
    conn = sqlite3.connect(f"file:{DB_PATH.resolve().as_posix()}?mode=ro", uri=True)
    try:
        query = f'SELECT * FROM "{table_name}" LIMIT {limit};'
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def get_schema_summary() -> List[Dict[str, Any]]:
    """Get metadata summary of all tables for the UI."""
    conn = sqlite3.connect(f"file:{DB_PATH.resolve().as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [r[0] for r in cur.fetchall()]

        summaries = []
        for tbl in tables:
            cur.execute(f'PRAGMA table_info("{tbl}");')
            cols = [{"name": c[1], "type": c[2]} for c in cur.fetchall()]
            cur.execute(f'SELECT COUNT(*) FROM "{tbl}";')
            count = cur.fetchone()[0]
            summaries.append({
                "table_name": tbl,
                "row_count": count,
                "columns": cols
            })
        return summaries
    finally:
        conn.close()
