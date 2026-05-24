import streamlit as st
import pandas as pd
import plotly.express as px
import anthropic

st.set_page_config(
    page_title="U.S. Healthcare Shortage AI",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(120deg, #059669, #f59e0b);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
}
.sub-header {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    border: 1.5px solid rgba(5,150,105,0.15);
    box-shadow: 0 2px 12px rgba(5,150,105,0.08);
}
.sql-box {
    background: #1e1e1e;
    color: #d4d4d4;
    border-radius: 10px;
    padding: 1rem;
    font-family: monospace;
    font-size: 0.85rem;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/RahmaRas/healthcare-ai-dashboard/main/hpsa_data.csv"
    df = pd.read_csv(url)
    return df

st.markdown('<div class="main-header">🏥 U.S. Healthcare Workforce Shortage AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Ask questions about 39,000+ real HRSA shortage records · Built with SQL + Python + Claude AI</div>', unsafe_allow_html=True)

try:
    df = load_data()
    data_loaded = True
except:
    data_loaded = False
    st.error("Data loading... please refresh in a moment.")

if data_loaded:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", f"{len(df):,}")
    with col2:
        st.metric("States Covered", df['state_name'].nunique())
    with col3:
        st.metric("Avg Shortage Score", f"{df['avg_score'].mean():.1f}")
    with col4:
        total = df['total_underserved'].sum()
        st.metric("Total Underserved", f"{total/1e6:.0f}M+")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🤖 Ask AI", "📊 Dashboard", "💾 SQL Queries"])

    with tab1:
        st.subheader("Ask anything about U.S. healthcare shortages")
        question = st.text_input("", placeholder="e.g. Which state has the worst shortage? Why is Kentucky so high?")

        if question and data_loaded:
            with st.spinner("Analyzing data..."):
                summary = df.groupby('state_name').agg({
                    'avg_score': 'mean',
                    'total_underserved': 'sum',
                    'total_shortage_areas': 'sum'
                }).round(1).to_string()

                client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
                message = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    messages=[{
                        "role": "user",
                        "content": f"""You are a healthcare data analyst. Answer this question using the data below.
Be specific, cite actual numbers, and keep your answer to 3-4 sentences.

Question: {question}

Data summary (state, avg_score, total_underserved, total_shortage_areas):
{summary}"""
                    }]
                )
                st.success(message.content[0].text)

    with tab2:
        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("Top States by Underserved Population")
            top_states = df.groupby('state_name')['total_underserved'].sum().reset_index()
            top_states = top_states.sort_values('total_underserved', ascending=True).tail(15)
            fig1 = px.bar(top_states, x='total_underserved', y='state_name',
                         orientation='h', color='total_underserved',
                         color_continuous_scale='Oranges',
                         labels={'total_underserved': 'Total Underserved', 'state_name': ''})
            fig1.update_layout(showlegend=False, coloraxis_showscale=False, height=450)
            st.plotly_chart(fig1, use_container_width=True)

        with col_right:
            st.subheader("Shortage Score by State")
            top_score = df.groupby('state_name')['avg_score'].mean().reset_index()
            top_score = top_score.sort_values('avg_score', ascending=True).tail(15)
            fig2 = px.bar(top_score, x='avg_score', y='state_name',
                         orientation='h', color='avg_score',
                         color_continuous_scale='Blues',
                         labels={'avg_score': 'Avg Shortage Score', 'state_name': ''})
            fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=450)
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Rural vs Non-Rural Shortage Comparison")
        if 'rural_status' in df.columns:
            rural = df.groupby('rural_status')['total_underserved'].sum().reset_index()
            fig3 = px.bar(rural, x='rural_status', y='total_underserved',
                         color='rural_status',
                         labels={'total_underserved': 'Total Underserved', 'rural_status': 'Area Type'},
                         color_discrete_sequence=px.colors.qualitative.Set2)
            fig3.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig3, use_container_width=True)

    with tab3:
        st.subheader("SQL Queries Used in This Analysis")
        st.markdown("**Query 1: Top states by shortage severity**")
        st.code("""SELECT state_name,
       COUNT(*) AS total_shortage_areas,
       ROUND(AVG(hpsa_score), 1) AS avg_shortage_score,
       SUM(estimated_underserved_pop) AS total_underserved
FROM hpsa_shortage
WHERE hpsa_status = 'Designated'
GROUP BY state_name
ORDER BY avg_shortage_score DESC
LIMIT 10;""", language="sql")

        st.markdown("**Query 2: Rural vs Urban comparison**")
        st.code("""SELECT rural_status,
       COUNT(*) AS total_areas,
       ROUND(AVG(hpsa_score), 1) AS avg_score,
       SUM(estimated_underserved_pop) AS total_underserved
FROM hpsa_shortage
WHERE hpsa_status = 'Designated'
GROUP BY rural_status
ORDER BY avg_score DESC;""", language="sql")

        st.markdown("**Query 3: Full state export for visualization**")
        st.code("""SELECT state_name, state_abbr,
       COUNT(*) AS total_shortage_areas,
       ROUND(AVG(hpsa_score), 1) AS avg_score,
       SUM(estimated_underserved_pop) AS total_underserved,
       SUM(hpsa_shortage) AS total_providers_needed,
       rural_status
FROM hpsa_shortage
WHERE hpsa_status = 'Designated'
AND state_name IS NOT NULL
GROUP BY state_name, state_abbr, rural_status
ORDER BY total_underserved DESC;""", language="sql")

    st.markdown("---")
    st.markdown("Built by [Rahma Ras](https://rahmaras.github.io) · Data: HRSA Open Data (May 2026) · [Tableau Dashboard](https://public.tableau.com/app/profile/rahma.ras/viz/USHealthcareWorkforceShortageTracker/Dashboard2)")
