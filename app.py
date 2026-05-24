import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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
.insight-card {
    background: linear-gradient(135deg, #d1fae5, #fef3c7);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border-left: 4px solid #059669;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
    color: #111;
}
.warning-card {
    background: linear-gradient(135deg, #fee2e2, #fef3c7);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    border-left: 4px solid #ef4444;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
    color: #111;
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

# Sidebar filters
st.sidebar.header("🔍 Filters")
states = ["All States"] + sorted(df['state_name'].unique().tolist())
selected_state = st.sidebar.selectbox("Select State", states)
rural_options = ["All"] + sorted(df['rural_status'].dropna().unique().tolist())
selected_rural = st.sidebar.selectbox("Rural Status", rural_options)

st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Compare Two States**")
state_list = sorted(df['state_name'].unique().tolist())
compare_a = st.sidebar.selectbox("State A", state_list, index=state_list.index("Maryland") if "Maryland" in state_list else 0)
compare_b = st.sidebar.selectbox("State B", state_list, index=state_list.index("Kentucky") if "Kentucky" in state_list else 1)

filtered = df.copy()
if selected_state != "All States":
    filtered = filtered[filtered['state_name'] == selected_state]
if selected_rural != "All":
    filtered = filtered[filtered['rural_status'] == selected_rural]

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Shortage Areas", f"{filtered['total_shortage_areas'].sum():,}")
with col2:
    st.metric("States Covered", filtered['state_name'].nunique())
with col3:
    st.metric("Avg Shortage Score", f"{filtered['avg_score'].mean():.1f}")
with col4:
    total = filtered['total_underserved'].sum()
    st.metric("Total Underserved", f"{total/1e6:.0f}M+")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🗺️ Map", "📊 Charts", "💡 Insights", "🏆 Compare States", "💾 SQL + Data"])

with tab1:
    st.subheader("U.S. Healthcare Shortage Map")
    map_data = filtered.groupby(['state_name', 'state_abbr']).agg(
        avg_score=('avg_score', 'mean'),
        total_underserved=('total_underserved', 'sum'),
        providers_needed=('total_providers_needed', 'sum')
    ).reset_index()

    fig_map = px.choropleth(
        map_data,
        locations='state_abbr',
        locationmode='USA-states',
        color='avg_score',
        scope='usa',
        color_continuous_scale='RdYlGn_r',
        labels={'avg_score': 'Shortage Score'},
        hover_name='state_name',
        hover_data={
            'state_abbr': False,
            'avg_score': ':.1f',
            'total_underserved': ':,.0f',
            'providers_needed': ':,.0f'
        },
        title='Average HPSA Shortage Score by State (Higher = Worse)'
    )
    fig_map.update_layout(height=550, geo=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig_map, use_container_width=True)

with tab2:
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

with tab3:
    st.subheader("💡 Key Insights from the Data")
    national_avg = df['avg_score'].mean()
    worst_state = df.groupby('state_name')['avg_score'].mean().idxmax()
    worst_score = df.groupby('state_name')['avg_score'].mean().max()
    most_underserved = df.groupby('state_name')['total_underserved'].sum().idxmax()
    most_underserved_val = df.groupby('state_name')['total_underserved'].sum().max()
    providers_gap = df['total_providers_needed'].sum()
    rural_underserved = df[df['rural_status']=='Non-Rural']['total_underserved'].sum()
    rural_only = df[df['rural_status']=='Rural']['total_underserved'].sum()

    st.markdown(f'<div class="warning-card">🚨 <b>{worst_state}</b> has the worst shortage score at <b>{worst_score:.1f}</b> — that\'s <b>{worst_score/national_avg:.1f}x</b> the national average of {national_avg:.1f}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="warning-card">👥 <b>{most_underserved}</b> has the highest underserved population at <b>{most_underserved_val/1e6:.0f}M people</b> without adequate primary care access</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card">🏙️ Surprising finding: <b>Non-Rural areas</b> have {rural_underserved/1e6:.0f}M underserved vs Rural\'s {rural_only/1e6:.0f}M — urban shortages are often overlooked</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card">👨‍⚕️ The U.S. needs approximately <b>{providers_gap:,.0f} additional providers</b> to eliminate all designated shortage areas</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="insight-card">📊 <b>19,412 shortage areas</b> are currently designated across 60 states and territories — affecting <b>522M+ Americans</b></div>', unsafe_allow_html=True)

    st.subheader("🏥 Job Market Angle")
    st.info("""
**Where healthcare data jobs are growing fastest:**

States with the worst shortages are investing heavily in data infrastructure to track and address these gaps. 
The top hiring states for healthcare data analysts right now are:

- **Texas** — 452 shortage areas, massive health system expansion
- **New York** — highest underserved population, largest hospital networks  
- **California** — tech + healthcare convergence, strong data science demand
- **Kentucky** — worst shortage scores, active state-level intervention programs
- **North Carolina** — Research Triangle, growing biotech + health data sector

**What employers want:** SQL + Tableau/Streamlit + healthcare domain knowledge — exactly your stack.
    """)

with tab4:
    st.subheader(f"🏆 State Comparison: {compare_a} vs {compare_b}")
    def get_state_stats(state):
        s = df[df['state_name'] == state]
        return {
            'Avg Shortage Score': round(s['avg_score'].mean(), 1),
            'Total Underserved': int(s['total_underserved'].sum()),
            'Shortage Areas': int(s['total_shortage_areas'].sum()),
            'Providers Needed': int(s['total_providers_needed'].sum()),
        }

    stats_a = get_state_stats(compare_a)
    stats_b = get_state_stats(compare_b)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"### 🔵 {compare_a}")
        for k, v in stats_a.items():
            st.metric(k, f"{v:,}" if isinstance(v, int) else v)
    with col_b:
        st.markdown(f"### 🟠 {compare_b}")
        for k, v in stats_b.items():
            delta = v - stats_a[k]
            st.metric(k, f"{v:,}" if isinstance(v, int) else v,
                     delta=f"{delta:+,}" if isinstance(v, int) else None)

    categories = list(stats_a.keys())
    vals_a = [stats_a[k] for k in categories]
    vals_b = [stats_b[k] for k in categories]

    fig_compare = go.Figure(data=[
        go.Bar(name=compare_a, x=categories, y=vals_a, marker_color='#059669'),
        go.Bar(name=compare_b, x=categories, y=vals_b, marker_color='#f59e0b')
    ])
    fig_compare.update_layout(barmode='group', height=400, title=f"{compare_a} vs {compare_b} — Side by Side")
    st.plotly_chart(fig_compare, use_container_width=True)

with tab5:
    st.subheader("💾 SQL Queries Used in This Analysis")
    st.code("""SELECT state_name,
       COUNT(*) AS total_shortage_areas,
       ROUND(AVG(hpsa_score), 1) AS avg_shortage_score,
       SUM(estimated_underserved_pop) AS total_underserved
FROM hpsa_shortage
WHERE hpsa_status = 'Designated'
GROUP BY state_name
ORDER BY avg_shortage_score DESC
LIMIT 10;""", language="sql")

    st.code("""SELECT rural_status,
       COUNT(*) AS total_areas,
       ROUND(AVG(hpsa_score), 1) AS avg_score,
       SUM(estimated_underserved_pop) AS total_underserved
FROM hpsa_shortage
WHERE hpsa_status = 'Designated'
GROUP BY rural_status
ORDER BY avg_score DESC;""", language="sql")

    st.subheader("📥 Download Filtered Data")
    csv = filtered.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name="healthcare_shortage_filtered.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("Built by [Rahma Ras](https://rahmaras.github.io) · Data: HRSA Open Data (May 2026) · [Tableau Dashboard](https://public.tableau.com/app/profile/rahma.ras/viz/USHealthcareWorkforceShortageTracker/Dashboard2) · [GitHub](https://github.com/RahmaRas/healthcare-ai-dashboard)")
