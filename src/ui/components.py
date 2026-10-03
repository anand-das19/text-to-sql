"""Reusable UI components for Streamlit Text-to-SQL application."""
import streamlit as st
import pandas as pd
from typing import Callable, Optional

from src.database.schema import get_schema_summary
from src.database.reference_queries import REFERENCE_QUERIES
from src.services.llm_provider import get_api_key
from src.services.query_engine import QueryExecutionResult


def render_header():
    """Render the application hero header."""
    st.markdown("""
    <div class="hero-header">
        <h1>📊 SalesIQ: Natural Language SQL Assistant</h1>
        <p>Convert plain English sales and customer questions into validated, safe SQLite queries with instant visual results.</p>
        <div style="margin-top: 1rem;">
            <span class="badge-pill success">✓ Safe Read-Only Queries</span>
            <span class="badge-pill info">⚡ Embedded SQLite Data Layer</span>
            <span class="badge-pill">✨ Powered by Google Gemini</span>
            <span class="badge-pill">🛡️ Auto Row Limits (100 Max)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar() -> dict:
    """Render the sidebar with API settings, schema inspector, and guardrails."""
    with st.sidebar:
        st.subheader("⚙️ Engine Configuration")

        # Check existing environment/secrets key
        env_key = get_api_key()
        has_env_key = bool(env_key)

        api_key_input = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get("custom_api_key", ""),
            placeholder="Paste your key or use env var" if not has_env_key else "Loaded from Environment / Secrets",
            help="Get an API key at https://aistudio.google.com/. If empty, the app runs in Demo Mode on verified queries."
        )
        if api_key_input:
            st.session_state["custom_api_key"] = api_key_input

        # Active key status
        active_key = get_api_key(api_key_input)
        if active_key:
            st.success("🟢 **Live Gemini AI Active**")
        else:
            st.info("💡 **Demo Mode Active**\nSelect any prebuilt question below to explore data without an API key.")

        model_name = st.selectbox(
            "AI Model",
            options=["gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-flash"],
            index=0
        )

        st.divider()

        # Database Schema Explorer
        st.subheader("📁 Database Schema (6 Tables)")
        try:
            summaries = get_schema_summary()
            total_records = sum(t["row_count"] for t in summaries)
            st.caption(f"Connected to local SQLite database with **{total_records:,} total records**.")

            for tbl in summaries:
                with st.expander(f"**{tbl['table_name']}** ({tbl['row_count']:,} rows)"):
                    cols_df = pd.DataFrame(tbl["columns"])
                    st.dataframe(cols_df, hide_index=True, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not load schema summary: {e}")

        st.divider()

        # Security guardrails note
        st.subheader("🛡️ Safety & Guardrails")
        st.markdown("""
        - **Read-Only Mode**: SQLite connection uses `mode=ro`.
        - **Query Filter**: Destructive commands (`DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`) are blocked.
        - **Comment Stripping**: Disallows comment injection (`--`, `/* */`).
        - **Single Statement**: Blocks chained queries separated by `;`.
        - **Auto Limit**: Appends `LIMIT 100` to prevent memory exhaustion.
        """)

        st.caption("SalesIQ v2.0 • Internship Portfolio Project")

        return {
            "api_key": active_key,
            "model_name": model_name
        }


def render_sample_queries_selector(on_select: Callable[[str], None]):
    """Render curated clickable sample questions by category."""
    st.markdown("##### 💡 Try Suggested Business Questions")

    categories = list(dict.fromkeys(q["category"] for q in REFERENCE_QUERIES))
    tabs = st.tabs(["All"] + categories)

    with tabs[0]:
        cols = st.columns(2)
        for i, ref in enumerate(REFERENCE_QUERIES):
            col = cols[i % 2]
            with col:
                if st.button(f"📌 {ref['question']}", key=f"q_all_{i}", use_container_width=True):
                    on_select(ref["question"])

    for tab_idx, cat in enumerate(categories, 1):
        with tabs[tab_idx]:
            cat_queries = [q for q in REFERENCE_QUERIES if q["category"] == cat]
            for i, ref in enumerate(cat_queries):
                if st.button(f"📌 {ref['question']}", key=f"q_{cat}_{i}", use_container_width=True):
                    on_select(ref["question"])


def render_results_section(
    question: str,
    sql: str,
    explanation: Optional[str],
    result: QueryExecutionResult,
    is_fallback: bool = False
):
    """Render the query results, explanation, SQL code, and visualization."""
    st.markdown("---")
    st.subheader("📋 Query Results")

    if is_fallback:
        st.info("ℹ️ **Notice:** Result generated using the curated reference catalog (Demo Mode).")

    if explanation:
        st.markdown(f"**Insight:** {explanation}")

    # Metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows Returned", f"{result.row_count:,}")
    with col2:
        st.metric("Execution Latency", f"{result.execution_time_ms:.1f} ms")
    with col3:
        st.metric("Columns", len(result.columns))

    # Tabs for Data View, SQL Query, and Charts
    tab_data, tab_sql, tab_viz = st.tabs(["📊 Data Table", "💻 Generated SQL", "📈 Quick Chart"])

    with tab_data:
        if result.row_count > 0:
            st.dataframe(result.dataframe, use_container_width=True)
            # CSV Download
            csv_data = result.dataframe.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Export Results as CSV",
                data=csv_data,
                file_name="query_results.csv",
                mime="text/csv",
            )
        else:
            st.warning("Query executed successfully but returned 0 rows.")

    with tab_sql:
        st.code(sql, language="sql")
        st.caption("Executed safely against read-only SQLite database connection.")

    with tab_viz:
        df = result.dataframe
        if df.empty or len(df.columns) < 2:
            st.info("Chart preview is available when results contain at least 2 columns (e.g. 1 category + 1 numeric metric).")
        else:
            # Check for categorical and numeric column candidates
            num_cols = df.select_dtypes(include=["number"]).columns.tolist()
            cat_cols = [c for c in df.columns if c not in num_cols]

            if num_cols and cat_cols:
                cat_col = cat_cols[0]
                num_col = num_cols[0]
                st.caption(f"Visualizing `{num_col}` by `{cat_col}`:")
                chart_df = df[[cat_col, num_col]].set_index(cat_col)
                st.bar_chart(chart_df)
            elif len(num_cols) >= 2:
                st.caption(f"Visualizing `{num_cols[1]}` by `{num_cols[0]}`:")
                chart_df = df[[num_cols[0], num_cols[1]]].set_index(num_cols[0])
                st.line_chart(chart_df)
            else:
                st.info("No numeric columns detected to plot.")
