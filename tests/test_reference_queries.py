"""Tests verifying that all reference/benchmark queries execute cleanly on SQLite."""
from src.database.reference_queries import REFERENCE_QUERIES
from src.services.safety import validate_and_sanitize_sql
from src.services.query_engine import execute_query


def test_all_reference_queries_execute():
    """Verify that every reference query in the catalog runs cleanly and returns rows."""
    for ref in REFERENCE_QUERIES:
        question = ref["question"]
        raw_sql = ref["sql"]

        # Validate through safety layer
        sanitized_sql = validate_and_sanitize_sql(raw_sql)
        assert sanitized_sql is not None

        # Execute against database
        result = execute_query(sanitized_sql)
        assert result.is_success, f"Reference query for '{question}' failed: {result.error}\nSQL: {sanitized_sql}"
        assert result.row_count > 0, f"Reference query for '{question}' returned 0 rows"
        assert result.execution_time_ms < 500.0, f"Query took too long: {result.execution_time_ms} ms"
