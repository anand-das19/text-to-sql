"""SalesIQ: Natural Language to SQL Analytics Web Application.

A modern, production-ready Streamlit web app converting natural language
business questions into validated read-only SQLite queries.
"""
import logging
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

from src.database.build_db import ensure_database
from src.services.llm_provider import generate_sql
from src.services.query_engine import execute_query
from src.ui.styles import CUSTOM_CSS
from src.ui.components import (
    render_header,
    render_sidebar,
    render_sample_queries_selector,
    render_results_section
)

# Page configuration
st.set_page_config(
    page_title="SalesIQ | Natural Language SQL Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom styling
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Auto-initialize database if not present
try:
    ensure_database()
except Exception as e:
    st.error(f"Failed to initialize SQLite database: {e}")
    st.stop()


def main():
    # Render Hero & Sidebar
    render_header()
    sidebar_config = render_sidebar()

    # Session state initialization
    if "current_question" not in st.session_state:
        st.session_state["current_question"] = ""
    if "active_result" not in st.session_state:
        st.session_state["active_result"] = None

    def on_sample_selected(question_text: str):
        st.session_state["current_question"] = question_text
        st.session_state["auto_submit"] = True

    # Render Sample Questions Picker
    render_sample_queries_selector(on_sample_selected)

    st.markdown("---")
    st.subheader("💬 Ask Your Question")

    # Question Input Form
    with st.form(key="query_form", clear_on_submit=False):
        user_input = st.text_input(
            "Enter a sales, revenue, or customer question:",
            value=st.session_state.get("current_question", ""),
            placeholder="e.g. Which customers had the highest total spend?",
            key="input_box"
        )
        col1, col2 = st.columns([1, 5])
        with col1:
            submitted = st.form_submit_button("🚀 Run Query", use_container_width=True)

    # Check for auto submit from suggestion clicks
    if st.session_state.get("auto_submit", False):
        submitted = True
        st.session_state["auto_submit"] = False
        user_input = st.session_state["current_question"]

    # Process query
    if submitted:
        question = user_input.strip()
        if not question:
            st.warning("Please enter a question or click a suggested query above.")
        else:
            with st.spinner("🤖 Consulting database schema & generating SQL..."):
                gen_result = generate_sql(
                    question=question,
                    api_key=sidebar_config.get("api_key"),
                    model_name=sidebar_config.get("model_name")
                )

            if gen_result.get("error"):
                st.error(f"❌ {gen_result['error']}")
            elif not gen_result.get("sql"):
                st.error("❌ Failed to generate a valid SQL query.")
            else:
                with st.spinner("⚡ Executing query on read-only SQLite database..."):
                    exec_result = execute_query(gen_result["sql"])

                if not exec_result.is_success:
                    st.error(f"❌ {exec_result.error}")
                    st.code(gen_result["sql"], language="sql")
                else:
                    st.session_state["active_result"] = {
                        "question": question,
                        "sql": gen_result["sql"],
                        "explanation": gen_result.get("explanation"),
                        "result": exec_result,
                        "is_fallback": gen_result.get("is_fallback", False)
                    }

    # Display active result if present
    if st.session_state.get("active_result"):
        active = st.session_state["active_result"]
        render_results_section(
            question=active["question"],
            sql=active["sql"],
            explanation=active["explanation"],
            result=active["result"],
            is_fallback=active.get("is_fallback", False)
        )


if __name__ == "__main__":
    main()
