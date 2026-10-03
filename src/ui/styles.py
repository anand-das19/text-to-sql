"""Custom CSS styles and UI themes for Text-to-SQL Streamlit application."""

CUSTOM_CSS = """
<style>
/* Main typography and headers */
h1, h2, h3 {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    letter-spacing: -0.02em;
}

/* Header banner */
.hero-header {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    color: #F8FAFC;
    padding: 1.75rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
}

.hero-header h1 {
    color: #FFFFFF;
    font-size: 2.1rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
}

.hero-header p {
    color: #94A3B8;
    font-size: 1.05rem;
    margin: 0;
}

/* Feature badges */
.badge-pill {
    display: inline-block;
    padding: 0.25rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 600;
    border-radius: 9999px;
    margin-right: 0.5rem;
    background-color: #EEF2F6;
    color: #334155;
    border: 1px solid #CBD5E1;
}

.badge-pill.success {
    background-color: #ECFDF5;
    color: #065F46;
    border-color: #A7F3D0;
}

.badge-pill.info {
    background-color: #EFF6FF;
    color: #1E40AF;
    border-color: #BFDBFE;
}

/* Suggestion pills styling */
div.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.15s ease;
}

/* Metric card */
.stat-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
}

.stat-box .num {
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F172A;
}

.stat-box .label {
    font-size: 0.75rem;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Results container */
.result-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.25rem;
    margin-top: 1rem;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}
</style>
"""
