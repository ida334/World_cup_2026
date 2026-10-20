"""
World Cup 2026 Prediction Dashboard — main entry point.
Run with: python -m streamlit run dashboard/app.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(
    page_title="World Cup 2026",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dashboard.theme import inject_css, C_GOLD

inject_css(st)


st.sidebar.markdown(f"""
<div style="padding:8px 0 20px 0; text-align:center;">
  <div style="font-size:2rem;">⚽</div>
  <div style="font-size:1.1rem; font-weight:700; color:{C_GOLD};">World Cup 2026</div>
  <div style="font-size:0.75rem; color:#8b949e;">USA · Canada · Mexico</div>
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("---")

_p = os.path.join(os.path.dirname(__file__), "views")

pg = st.navigation([
    st.Page(os.path.join(_p, "00_about.py"),         title="About App"),
    st.Page(os.path.join(_p, "01_historical.py"),    title="Historical Overview"),
    st.Page(os.path.join(_p, "02_head_to_head.py"),  title="Head to Head"),
    st.Page(os.path.join(_p, "03_predictions.py"),   title="2026 Predictions"),
    st.Page(os.path.join(_p, "04_data_explorer.py"), title="Data Explorer"),
])
pg.run()
