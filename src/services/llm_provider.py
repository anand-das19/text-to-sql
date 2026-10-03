"""LLM Provider adapter for Text-to-SQL generation using Google Gemini.

Supports environment variables, Streamlit Secrets, and UI-level API keys.
Includes Demo Mode fallback for keyless presentation.
"""
import logging
import os
import re
from typing import Dict, Any, Optional, Tuple

from src.config import DEFAULT_MODEL
from src.database.schema import get_schema_prompt_context
from src.database.reference_queries import get_reference_by_question
from src.services.safety import extract_sql_from_response, validate_and_sanitize_sql, SQLSecurityError

logger = logging.getLogger(__name__)


def get_api_key(explicit_key: Optional[str] = None) -> Optional[str]:
    """Retrieve API key with prioritized fallbacks:

    1. Explicit key passed from UI sidebar
    2. Streamlit secrets (if running in Streamlit)
    3. Environment variable (GEMINI_API_KEY, GOOGLE_API_KEY)
    """
    if explicit_key and explicit_key.strip():
        return explicit_key.strip()

    # Try Streamlit Secrets
    try:
        import streamlit as st
        if hasattr(st, "secrets"):
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
            if "GOOGLE_API_KEY" in st.secrets:
                return st.secrets["GOOGLE_API_KEY"]
    except Exception:
        pass

    # Try Environment variables
    for var_name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        val = os.getenv(var_name)
        if val and val.strip():
            return val.strip()

    return None


SYSTEM_PROMPT = """You are an expert Text-to-SQL assistant specializing in SQLite analytics for sales databases.
Your objective is to generate accurate, safe, SQLite-compatible read-only SELECT queries based on the user's natural language question.

DATABASE SCHEMA AND RELATIONSHIPS:
{schema_context}

RULES AND CONSTRAINTS:
1. Generate ONLY read-only SELECT statements. Do NOT use DDL (CREATE, DROP, ALTER) or DML (INSERT, UPDATE, DELETE).
2. SQLite Syntax:
   - Column names containing spaces MUST be enclosed in double quotes (e.g. "Customer Names", "Line Total", "Product Description Index", "2017 Budgets").
   - For dates ('YYYY-MM-DD'), use SQLite functions like strftime('%Y', OrderDate).
   - Use standard SQLite JOIN clauses referencing the appropriate primary and foreign keys documented above.
3. Output format:
   - Provide the SQL query inside a ```sql ... ``` markdown code block.
   - Follow with a concise 1-2 sentence explanation of how the query resolves the user's request.
"""


def generate_sql(
    question: str,
    api_key: Optional[str] = None,
    model_name: str = DEFAULT_MODEL
) -> Dict[str, Any]:
    """Generate SQL query from natural language question.

    Returns dict with keys:
        - sql: Sanitized SQL string or None
        - raw_response: Full LLM response or explanation
        - explanation: Clean explanation string
        - is_fallback: Boolean indicating if fallback/demo mode was used
        - error: Error message if failed
    """
    resolved_key = get_api_key(api_key)

    # If no API key is available, check for prebuilt reference query
    if not resolved_key:
        ref = get_reference_by_question(question)
        if ref:
            sanitized = validate_and_sanitize_sql(ref["sql"])
            return {
                "sql": sanitized,
                "raw_response": ref["sql"],
                "explanation": f"💡 (Demo Mode) {ref['explanation']}",
                "is_fallback": True,
                "error": None
            }
        else:
            return {
                "sql": None,
                "raw_response": None,
                "explanation": None,
                "is_fallback": True,
                "error": (
                    "No Gemini API key detected. Please provide your Google/Gemini API key "
                    "in the sidebar or environment, or click one of the suggested sample questions "
                    "to test the system in Demo Mode."
                )
            }

    # Initialize Google GenAI client
    try:
        from google import genai
        client = genai.Client(api_key=resolved_key)
    except Exception as e:
        logger.error(f"Failed to initialize GenAI client: {e}")
        return {
            "sql": None,
            "raw_response": None,
            "explanation": None,
            "is_fallback": False,
            "error": f"Failed to initialize AI Client: {str(e)}"
        }

    schema_context = get_schema_prompt_context()
    prompt = (
        f"{SYSTEM_PROMPT.format(schema_context=schema_context)}\n\n"
        f"USER QUESTION: {question}\n\n"
        f"Generate the SQLite query:"
    )

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        raw_text = response.text or ""

        # Extract SQL from response
        extracted_sql = extract_sql_from_response(raw_text)

        # Validate through safety layer
        sanitized_sql = validate_and_sanitize_sql(extracted_sql)

        # Extract explanation if present after code block
        explanation_parts = re.split(r"```(?:sql)?[\s\S]*?```", raw_text, flags=re.IGNORECASE)
        explanation = ""
        if len(explanation_parts) > 1:
            explanation = explanation_parts[-1].strip()
        if not explanation:
            explanation = f"Generated SQL query for: '{question}'"

        return {
            "sql": sanitized_sql,
            "raw_response": raw_text,
            "explanation": explanation,
            "is_fallback": False,
            "error": None
        }

    except SQLSecurityError as se:
        return {
            "sql": None,
            "raw_response": None,
            "explanation": None,
            "is_fallback": False,
            "error": f"Security Guardrail Violation: {str(se)}"
        }
    except Exception as e:
        logger.exception("LLM generation error")
        return {
            "sql": None,
            "raw_response": None,
            "explanation": None,
            "is_fallback": False,
            "error": f"AI Generation Error: {str(e)}"
        }
