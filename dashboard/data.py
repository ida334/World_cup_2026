"""
Cached data loaders shared by the dashboard pages.

Kept apart from app.py so pages can import them without re-running the
app's st.navigation / pg.run(), which rendered the page twice on first load.
"""
import os

import streamlit as st

from src.db_loader import get_connection
from src.model import load_model
from src.simulator import load_simulation, SIM_PATH


@st.cache_resource
def get_db():
    return get_connection()


@st.cache_resource
def get_model_cached():
    try:
        return load_model()
    except FileNotFoundError:
        return None


@st.cache_data
def get_simulation():
    if not os.path.exists(SIM_PATH):
        return None
    return load_simulation()
