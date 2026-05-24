import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="U.S. Healthcare Shortage Dashboard",
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
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/RahmaRas/healthcare-ai-dashboard/main/hpsa_data.csv"
    df = pd.read_csv(url)
    return df

st.markdown('<div class="main-header">🏥 U.S. Healthcare Workforce Shortage Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Interactive analysis of 39,000+ real HRSA government records · Built with SQL + Python + Plotly</div>', unsafe_allow_html=True)

df = load_data()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Shortage Areas", f"{df['total_shortage_areas'].sum():,}")
with col2:
    st.metric("States Covered", df['state_name'].nunique())
with col3:
    st.metric("Avg Shortage Score", f"{df['avg_score'].mean():.1f}")
with col4:
    total = df['total_underserved'].sum()
    st.metric("Total Underserved", f"{total/1e6:.0f}M+")

st.markdown("---")

st.sidebar.header("🔍 Filters")
states = ["All States"] + sorted(df['state_name'].unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)
rural_options = ["All"] + sorted(df['rural_status'].dropna().unique().tolist())
selected_rural = st.sidebar.selectbox("Rural Status", rural_options)

filtered = df.copy()
if selected_state != "All States":
    filtered = filtered[filtered['state_name'] == selected_state]
if selected_rural != "All":
    filtered = filtered[filtered['rural_status'] == selected_rural]

tab1, tab2, tab3 = st.tabs(["📊 Charts", "🗺️ State Rankings", "💾 SQL Queries"])

with tab1:
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top 15 States by Underserved Population")
        top_states = filtered.groupby('state_name')['total_underserved'].sum().reset_index()
        top_states = top_states.sort_values('total_underserved', ascending=True).tail(15)
        fig1 = px.bar(top_states, x='total_underserved', y='state_name',
                     orientation='h', color='total_underserved',
                     color_continuous_scale='Oranges',
                     labels={'total_underserved': 'Total Underserved', 'state_name': ''})
        fig1.update_layout(showlegend=False, coloraxis_showscale=False, height=500)
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        st.subheader("Top 15 States by Shortage Score")
        top_score = filtered.groupby('state_name')['avg_score'].mean().reset_index()
        top_score = top_score.sort_values('avg_score', ascending=True).tail(15)
        fig2 = px.bar(top_score, x='avg_score', y='state_name',
                     orientation='h', color='avg_score',
                     color_continuous_scale='Blues',
                     labels={'avg_score': 'Avg Shortage Score', 'state_name': ''})
        fig2.update_layout(showlegend=False, coloraxis_showscale=False, height=500)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Rural vs Non-Rural Shortage Comparison")
    rural = filtered.groupby('rural_status').agg(
        total_underserved=('total_underserved', 'sum'),
        total_areas=('total_shortage_areas', 'sum'),
        avg_score=('avg_score', 'mean')
    ).reset_index()
    fig3 = px.bar(rural, x='rural_status', y='total_underserved',
                 color='rural_status',
                 labels={'total_underserved': 'Total Underserved', 'rural_status': 'Area Type'},
                 color_discrete_sequence=['#059669','#f59e0b','#10b981','#ef4444','#6b7280'])
    fig3.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    st.subheader("Full State Rankings Table")
    state_summary = filtered.groupby('state_name').agg(
        avg_score=('avg_score', 'mean'),
        total_underserved=('total_underserved', 'sum'),
        total_areas=('total_shortage_areas', 'sum'),
        providers_needed=('total_providers_needed', 'sum')
    ).reset_index()
    state_summary['avg_score'] = state_summary['avg_score'].round(1)
    state_summary['total_underserved'] = state_summary['total_underserved'].astype(int)
    state_summary = state_summary.sort_values('avg_score', ascending=False)
    state_summary.columns = ['State', 'Avg Score', 'Total Underserved', 'Shortage Areas', 'Providers Needed']
    st.dataframe(state_summary, use_container_width=True, height=500)

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
st.markdown("Built by [Rahma Ras](https://rahmaras.github.io) · Data: HRSA Open Data (May 2026) · [Tableau Dashboard](https://public.tableau.com/app/profile/rahma.ras/viz/USHealthcareWorkforceShortageTracker/Dashboard2) · [GitHub](https://github.com/RahmaRas/healthcare-ai-dashboard)")
