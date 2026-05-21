import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.risk_engine import calculate_risk_score, fetch_latest_metrics
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="BondRisk AI", layout="wide")

st.title("🛡️ BondRisk AI: Varthana Credit Analysis")
st.markdown("---")

# 1. Fetch Data
try:
    issuer_id = 1
    score = calculate_risk_score(issuer_id)
    df_metrics = fetch_latest_metrics(issuer_id)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📊 Extracted Financial Metrics")
        # Displaying the raw data extracted by Gemini
        st.dataframe(df_metrics, use_container_width=True)
        
        st.info(f"💡 **Insight:** The model is currently flagging a {score}% risk primarily due to Leverage headroom.")

    with col2:
        st.subheader("🔥 Breach Probability")
        # Visual Gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "black"},
                'steps' : [
                    {'range': [0, 30], 'color': "#00CC96"}, # Green
                    {'range': [30, 70], 'color': "#FFA15A"}, # Orange
                    {'range': [70, 100], 'color': "#EF553B"} # Red
                ],
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error loading dashboard: {e}")