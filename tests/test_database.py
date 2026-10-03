"""Tests for SQLite database creation, views, and data integrity."""
import sqlite3
import pytest
from src.database.build_db import build_database, get_table_counts
from src.config import DB_PATH, CSV_DIR


def test_database_build(tmp_path):
    """Verify that build_database successfully creates tables and loads data from CSVs."""
    test_db = tmp_path / "test_sales.sqlite"
    counts = build_database(csv_dir=CSV_DIR, db_path=test_db, force_rebuild=True)

    expected_tables = [
        "sales_order",
        "customers",
        "products",
        "regions",
        "state_regions",
        "budgets_2017"
    ]

    for tbl in expected_tables:
        assert tbl in counts, f"Missing table: {tbl}"
        assert counts[tbl] > 0, f"Table {tbl} has 0 rows"

    assert counts["sales_order"] == 64104
    assert counts["customers"] == 175
    assert counts["products"] == 30
    assert counts["regions"] == 994
    assert counts["state_regions"] == 48
    assert counts["budgets_2017"] == 30


def test_views_and_read_only_access():
    """Verify compatibility views and read-only connection behavior."""
    conn = sqlite3.connect(f"file:{DB_PATH.resolve().as_posix()}?mode=ro", uri=True)
    try:
        cur = conn.cursor()

        # Check view sales_orders
        cur.execute("SELECT COUNT(*) FROM sales_orders;")
        count_view = cur.fetchone()[0]
        assert count_view == 64104

        # Check view 2017_budgets
        cur.execute('SELECT COUNT(*) FROM "2017_budgets";')
        count_budgets = cur.fetchone()[0]
        assert count_budgets == 30

        # Verify write operations fail in read-only mode
        with pytest.raises(sqlite3.OperationalError):
            cur.execute("INSERT INTO customers VALUES (9999, 'Malicious Corp');")

    finally:
        conn.close()
