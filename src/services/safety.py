"""SQL safety, validation, extraction, and sanitization layer.

Enforces strict read-only execution, rejects DDL/DML/multi-statement queries,
disallows SQL comments, and enforces row limits.
"""
import re
from typing import Tuple, Optional
from src.config import DEFAULT_ROW_LIMIT, MAX_ROW_LIMIT

# Keywords that are strictly prohibited in the generated SQL
FORBIDDEN_KEYWORDS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bINSERT\b",
    r"\bUPDATE\b",
    r"\bALTER\b",
    r"\bTRUNCATE\b",
    r"\bCREATE\b",
    r"\bREPLACE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
    r"\bPRAGMA\b",
    r"\bATTACH\b",
    r"\bDETACH\b",
    r"\bVACUUM\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bINTO\s+OUTFILE\b",
    r"\bLOAD_FILE\b",
]

# Prohibited comment patterns that could hide malicious payloads
COMMENT_PATTERNS = [
    r"--",        # Single line comment
    r"/\*.*?\*/", # Multi-line comment
]


class SQLSecurityError(ValueError):
    """Raised when an SQL query violates security guardrails."""
    pass


def extract_sql_from_response(response_text: str) -> str:
    """Extract SQL query from an LLM response string.

    Handles ```sql ... ``` code blocks, plain code blocks, or bare queries.
    """
    if not response_text:
        return ""

    # Look for ```sql ... ``` block
    sql_match = re.search(r"```(?:sql)?\s*([\s\S]*?)\s*```", response_text, re.IGNORECASE)
    if sql_match:
        return sql_match.group(1).strip()

    # If no markdown block, return stripped text
    return response_text.strip()


def validate_and_sanitize_sql(
    query: str,
    default_limit: int = DEFAULT_ROW_LIMIT,
    max_limit: int = MAX_ROW_LIMIT
) -> str:
    """Validate that the SQL query is a safe, single-statement read query,

    and ensure an appropriate row limit is applied.

    Args:
        query: Raw SQL query string.
        default_limit: Default LIMIT value to append if none present.
        max_limit: Maximum allowed LIMIT value.

    Returns:
        Sanitized, validated SQL query string.

    Raises:
        SQLSecurityError: If the query fails any security check.
    """
    clean_query = query.strip()

    if not clean_query:
        raise SQLSecurityError("The SQL query is empty.")

    # 1. Reject SQL comments (prevent injection obfuscation)
    for pattern in COMMENT_PATTERNS:
        if re.search(pattern, clean_query, re.DOTALL):
            raise SQLSecurityError(
                "SQL comments ('--' or '/* */') are not permitted for security reasons."
            )

    # 2. Reject multi-statement queries
    # Remove trailing semicolon if present
    trimmed = clean_query.rstrip(";").strip()
    if ";" in trimmed:
        raise SQLSecurityError(
            "Multi-statement queries separated by ';' are strictly forbidden."
        )

    # 3. Must begin with SELECT or WITH (for CTEs)
    # Match the first word (ignoring leading whitespace and parentheses)
    first_word_match = re.match(r"^\s*\(?\s*([A-Za-z]+)", trimmed)
    if not first_word_match:
        raise SQLSecurityError("Unable to identify query command.")

    first_word = first_word_match.group(1).upper()
    if first_word not in ("SELECT", "WITH"):
        raise SQLSecurityError(
            f"Only read-only SELECT queries are permitted (received '{first_word}')."
        )

    # 4. Check for forbidden keywords anywhere in query
    for kw_pattern in FORBIDDEN_KEYWORDS:
        if re.search(kw_pattern, trimmed, re.IGNORECASE):
            match = re.search(kw_pattern, trimmed, re.IGNORECASE).group(0)
            raise SQLSecurityError(
                f"Potentially destructive operation '{match.upper()}' detected and blocked."
            )

    # 5. Enforce automatic row limit
    limit_match = re.search(r"\bLIMIT\s+(\d+)\b", trimmed, re.IGNORECASE)
    if limit_match:
        current_limit = int(limit_match.group(1))
        if current_limit > max_limit:
            # Clamp to max_limit
            trimmed = re.sub(
                r"\bLIMIT\s+\d+\b",
                f"LIMIT {max_limit}",
                trimmed,
                flags=re.IGNORECASE
            )
    else:
        # Append default limit
        trimmed = f"{trimmed}\nLIMIT {default_limit}"

    return trimmed.strip() + ";"
