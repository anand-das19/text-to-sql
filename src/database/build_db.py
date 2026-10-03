"""SQLite database builder for regional sales dataset.

Imports CSV files from Data_CSV into an optimized SQLite database with indexes
and compatibility views.
"""
import logging
import sqlite3
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from src.config import CSV_DIR, DB_PATH

logger = logging.getLogger(__name__)

# Canonical table mapping: CSV filename -> Table Name
TABLE_MAPPING = {
    "sales_order.csv": "sales_order",
    "Customers.csv": "customers",
    "Products.csv": "products",
    "Regions.csv": "regions",
    "State_Regions.csv": "state_regions",
    "2017_Budgets.csv": "budgets_2017",
}

# Indexes to accelerate common text-to-SQL joins and filters
INDEX_DEFINITIONS = [
    ("idx_so_cust", "sales_order", '"Customer Name Index"'),
    ("idx_so_prod", "sales_order", '"Product Description Index"'),
    ("idx_so_region", "sales_order", '"Delivery Region Index"'),
    ("idx_so_date", "sales_order", '"OrderDate"'),
    ("idx_cust_idx", "customers", '"Customer Index"'),
    ("idx_prod_idx", "products", '"Index"'),
    ("idx_regions_id", "regions", '"id"'),
    ("idx_sr_state_code", "state_regions", '"State Code"'),
]

# Compatibility views so both naming conventions work seamlessly
COMPATIBILITY_VIEWS = [
    ('CREATE VIEW IF NOT EXISTS sales_orders AS SELECT * FROM sales_order;'),
    ('CREATE VIEW IF NOT EXISTS "2017_budgets" AS SELECT * FROM budgets_2017;'),
]


def build_database(
    csv_dir: Optional[Path] = None,
    db_path: Optional[Path] = None,
    force_rebuild: bool = False
) -> Dict[str, int]:
    """Build SQLite database from CSV source files.

    Args:
        csv_dir: Path to directory containing CSV files.
        db_path: Target path for the SQLite database.
        force_rebuild: If True, delete and rebuild existing database.

    Returns:
        Dict mapping table names to their row counts.
    """
    csv_dir = Path(csv_dir or CSV_DIR)
    db_path = Path(db_path or DB_PATH)

    if not csv_dir.exists():
        raise FileNotFoundError(f"Source CSV directory not found: {csv_dir}")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    if db_path.exists() and not force_rebuild:
        # Check if all tables exist and have data
        try:
            counts = get_table_counts(db_path)
            if all(tbl in counts and counts[tbl] > 0 for tbl in TABLE_MAPPING.values()):
                logger.info(f"Database already exists and verified at {db_path}")
                return counts
        except Exception:
            logger.warning("Existing database check failed, rebuilding...")

    if db_path.exists():
        try:
            db_path.unlink()
        except Exception as e:
            logger.warning(f"Could not delete old database file {db_path}: {e}")

    logger.info(f"Building SQLite database at {db_path} from {csv_dir}...")
    table_counts = {}

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        # Import each table
        for csv_filename, table_name in TABLE_MAPPING.items():
            csv_path = csv_dir / csv_filename
            if not csv_path.exists():
                raise FileNotFoundError(f"Required CSV file missing: {csv_path}")

            df = pd.read_csv(csv_path)
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            table_counts[table_name] = len(df)
            logger.info(f"Loaded {table_name}: {len(df):,} rows")

        # Create performance indexes
        for idx_name, table_name, column_name in INDEX_DEFINITIONS:
            try:
                cur.execute(
                    f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name} ({column_name});"
                )
            except Exception as e:
                logger.warning(f"Failed to create index {idx_name}: {e}")

        # Create compatibility views
        for view_sql in COMPATIBILITY_VIEWS:
            try:
                cur.execute(view_sql)
            except Exception as e:
                logger.warning(f"Failed to create view: {e}")

        conn.commit()
    finally:
        conn.close()

    logger.info(f"Successfully built SQLite database at {db_path}")
    return table_counts


def get_table_counts(db_path: Optional[Path] = None) -> Dict[str, int]:
    """Retrieve row counts for all base tables in the database."""
    db_path = Path(db_path or DB_PATH)
    if not db_path.exists():
        return {}

    counts = {}
    conn = sqlite3.connect(f"file:{db_path.resolve().as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cur.fetchall()]
        for table in tables:
            cur.execute(f'SELECT COUNT(*) FROM "{table}";')
            counts[table] = cur.fetchone()[0]
    finally:
        conn.close()
    return counts


def ensure_database(force_rebuild: bool = False) -> Path:
    """Ensure database exists, building it if needed.

    Returns the Path to the database.
    """
    build_database(force_rebuild=force_rebuild)
    return DB_PATH


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    stats = build_database(force_rebuild=True)
    print("Database build complete. Table summary:")
    for tbl, count in stats.items():
        print(f" - {tbl}: {count:,} rows")
