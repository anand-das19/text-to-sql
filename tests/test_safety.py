"""Tests for SQL safety validation, keyword blocking, and row limits."""
import pytest
from src.services.safety import (
    validate_and_sanitize_sql,
    extract_sql_from_response,
    SQLSecurityError
)


def test_extract_sql_markdown():
    """Verify markdown code block extraction."""
    raw = "Here is the query:\n```sql\nSELECT * FROM customers;\n```\nHope this helps!"
    extracted = extract_sql_from_response(raw)
    assert extracted == "SELECT * FROM customers;"

    raw_no_tag = "```\nSELECT * FROM products;\n```"
    assert extract_sql_from_response(raw_no_tag) == "SELECT * FROM products;"

    plain = "SELECT * FROM regions"
    assert extract_sql_from_response(plain) == "SELECT * FROM regions"


def test_valid_select_query():
    """Verify safe SELECT queries pass and receive automatic row limit."""
    query = 'SELECT "Customer Names" FROM customers'
    sanitized = validate_and_sanitize_sql(query, default_limit=50)
    assert "LIMIT 50;" in sanitized
    assert sanitized.startswith('SELECT "Customer Names" FROM customers')


def test_existing_limit_preserved_or_clamped():
    """Verify existing row limits are respected or clamped if excessive."""
    query = 'SELECT * FROM customers LIMIT 25;'
    sanitized = validate_and_sanitize_sql(query, default_limit=100, max_limit=500)
    assert "LIMIT 25;" in sanitized

    query_high = 'SELECT * FROM customers LIMIT 1000;'
    sanitized_high = validate_and_sanitize_sql(query_high, default_limit=100, max_limit=500)
    assert "LIMIT 500;" in sanitized_high


def test_block_destructive_commands():
    """Verify destructive statements (DDL/DML) are blocked."""
    banned = [
        "DROP TABLE customers;",
        "DELETE FROM sales_order;",
        "INSERT INTO customers VALUES (1, 'Test');",
        "UPDATE customers SET name = 'Hacked';",
        "ALTER TABLE regions ADD COLUMN secret TEXT;",
        "TRUNCATE TABLE products;",
        "PRAGMA table_info(customers);",
        "VACUUM;",
    ]
    for q in banned:
        with pytest.raises(SQLSecurityError):
            validate_and_sanitize_sql(q)


def test_block_multi_statement():
    """Verify chained statements separated by semicolons are blocked."""
    chained = "SELECT * FROM customers; DROP TABLE products;"
    with pytest.raises(SQLSecurityError, match="Multi-statement"):
        validate_and_sanitize_sql(chained)


def test_block_sql_comments():
    """Verify SQL comments used for injection or obfuscation are blocked."""
    with pytest.raises(SQLSecurityError, match="comments"):
        validate_and_sanitize_sql("SELECT * FROM customers -- ignore rest")

    with pytest.raises(SQLSecurityError, match="comments"):
        validate_and_sanitize_sql("SELECT * /* comment */ FROM customers")
