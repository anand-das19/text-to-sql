"""Database query execution engine with read-only connection and timing metrics."""
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd

from src.config import DB_PATH
from src.database.build_db import ensure_database


class QueryExecutionResult:
    """Encapsulates the result of a database query execution."""

    def __init__(
        self,
        dataframe: pd.DataFrame,
        sql: str,
        execution_time_ms: float,
        row_count: int,
        columns: list,
        error: Optional[str] = None
    ):
        self.dataframe = dataframe
        self.sql = sql
        self.execution_time_ms = execution_time_ms
        self.row_count = row_count
        self.columns = columns
        self.error = error

    @property
    def is_success(self) -> bool:
        return self.error is None


def execute_query(sql_query: str, db_path: Optional[Path] = None) -> QueryExecutionResult:
    """Execute a validated SQL query against the SQLite database in read-only mode.

    Args:
        sql_query: Validated, safe SQLite query string.
        db_path: Path to database file.

    Returns:
        QueryExecutionResult with DataFrame and execution statistics.
    """
    db_path = Path(db_path or DB_PATH)

    if not db_path.exists():
        ensure_database()

    # Read-only URI connection string
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"

    start_time = time.perf_counter()
    try:
        conn = sqlite3.connect(uri, uri=True)
        try:
            # Execute with pandas for fast tabular loading
            df = pd.read_sql_query(sql_query, conn)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return QueryExecutionResult(
                dataframe=df,
                sql=sql_query,
                execution_time_ms=round(elapsed_ms, 2),
                row_count=len(df),
                columns=list(df.columns),
                error=None
            )
        finally:
            conn.close()

    except sqlite3.OperationalError as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return QueryExecutionResult(
            dataframe=pd.DataFrame(),
            sql=sql_query,
            execution_time_ms=round(elapsed_ms, 2),
            row_count=0,
            columns=[],
            error=f"SQL Syntax / Database Error: {e}"
        )
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return QueryExecutionResult(
            dataframe=pd.DataFrame(),
            sql=sql_query,
            execution_time_ms=round(elapsed_ms, 2),
            row_count=0,
            columns=[],
            error=f"Query Execution Failed: {str(e)}"
        )
