"""
Shared design system for the World Cup 2026 dashboard.
Import get_css() and inject_css() in every page.
"""
import plotly.graph_objects as go
import plotly.io as pio

# ── Colour palette ─────────────────────────────────────────────────────────────
C_BG         = "#0d1117"
C_SURFACE    = "#161b22"
C_SURFACE2   = "#1c2333"
C_BORDER     = "#30363d"
C_GOLD       = "#e6a817"
C_GREEN      = "#26c281"
C_RED        = "#e05252"
C_BLUE       = "#4f9cf9"
C_TEXT       = "#e6edf3"
C_SUBTEXT    = "#8b949e"
C_ACCENT_1   = "#e6a817"   # gold  — winner / champion
C_ACCENT_2   = "#26c281"   # green — advancing / positive
C_ACCENT_3   = "#4f9cf9"   # blue  — neutral info
C_ACCENT_4   = "#e05252"   # red   — danger / exit

TEAM_COLORS  = [C_GOLD, C_GREEN, C_BLUE, C_RED,
                "#a371f7", "#f78166", "#56d364", "#79c0ff"]

# ── Global CSS ─────────────────────────────────────────────────────────────────
_CSS = f"""
<style>
/* ── App shell ── */
html, body, [data-testid="stAppViewContainer"], .stApp {{
    background-color: {C_BG};
    color: {C_TEXT};
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}}
[data-testid="stHeader"] {{ background: transparent; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: {C_SURFACE};
    border-right: 1px solid {C_BORDER};
}}
[data-testid="stSidebar"] * {{ color: {C_TEXT} !important; }}
[data-testid="stSidebar"] .stMarkdown a {{ color: {C_GOLD} !important; }}

/* ── Headings ── */
h1 {{ color: {C_TEXT}; font-weight: 700; letter-spacing: -0.5px; }}
h2, h3 {{ color: {C_TEXT}; font-weight: 600; }}

/* ── Metric cards ── */
[data-testid="stMetric"] {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
    padding: 16px 20px;
}}
[data-testid="stMetricLabel"] {{ color: {C_SUBTEXT} !important; font-size: 0.8rem; }}
[data-testid="stMetricValue"] {{ color: {C_TEXT} !important; font-size: 1.6rem; font-weight: 700; }}

/* ── Tabs ── */
div[data-baseweb="tab-list"] {{
    background: {C_SURFACE} !important;
    border-radius: 14px !important;
    padding: 8px 16px !important;
    border: 1px solid {C_BORDER} !important;
    gap: 0 !important;
}}
div[data-baseweb="tab-list"] button[data-baseweb="tab"] {{
    background: transparent !important;
    color: {C_SUBTEXT} !important;
    border-radius: 24px !important;
    font-weight: 500 !important;
    padding: 12px 40px !important;
    margin: 0 14px !important;
    min-height: 46px !important;
    min-width: 160px !important;
}}
div[data-baseweb="tab-list"] button[aria-selected="true"] {{
    background: #3d85c8 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border-radius: 24px !important;
    padding: 12px 48px !important;
    margin: 0 14px !important;
    min-height: 46px !important;
    min-width: 160px !important;
}}

/* ── Selectbox / inputs ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {{
    background: {C_SURFACE2};
    border: 1px solid {C_BORDER};
    border-radius: 8px;
    color: {C_TEXT};
}}

/* ── DataFrames / tables ── */
[data-testid="stDataFrame"] iframe,
.stDataFrame {{
    background: {C_SURFACE};
    border-radius: 8px;
}}

/* ── Expanders ── */
[data-testid="stExpander"] {{
    background: {C_SURFACE};
    border: 1px solid {C_BORDER};
    border-radius: 10px;
}}
[data-testid="stExpander"] summary {{ color: {C_TEXT}; font-weight: 600; }}

/* ── Buttons ── */
[data-testid="stDownloadButton"] button,
.stButton button {{
    background: #3d85c8;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}}
.stButton button:hover {{ background: #4a96dc; }}

/* ── Alerts ── */
[data-testid="stAlert"] {{
    background: {C_SURFACE2};
    border-left: 4px solid {C_GOLD};
    border-radius: 8px;
}}

/* ── Divider ── */
hr {{ border-color: {C_BORDER}; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: {C_BG}; }}
::-webkit-scrollbar-thumb {{ background: {C_BORDER}; border-radius: 3px; }}

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] {{ background: {C_SURFACE2}; }}
[data-testid="stSlider"] {{
    padding-top: 100px !important;
    padding-bottom: 60px !important;
    padding-left: 16px !important;
    padding-right: 16px !important;
    overflow: visible !important;
}}
[data-testid="column"] {{
    overflow: visible !important;
}}
</style>
"""


def inject_css(st_module):
    st_module.markdown(_CSS, unsafe_allow_html=True)


# ── Reusable HTML components ───────────────────────────────────────────────────

def hero_html(title: str, subtitle: str, emoji: str = "⚽") -> str:
    return f"""
<div style="
  background: linear-gradient(135deg, #1a2340 0%, #0d1117 60%, #1a1a2e 100%);
  border: 1px solid {C_BORDER};
  border-radius: 16px;
  padding: 48px 40px;
  margin-bottom: 32px;
  text-align: center;
  position: relative;
  overflow: hidden;
">
  <div style="font-size: 3.5rem; margin-bottom: 12px;">{emoji}</div>
  <h1 style="
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, {C_GOLD}, #f5d76e, {C_GOLD});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 12px 0;
    letter-spacing: -1px;
  ">{title}</h1>
  <p style="color: {C_SUBTEXT}; font-size: 1.05rem; margin: 0;">{subtitle}</p>
</div>
"""


def section_header_html(text: str, accent: str = C_GOLD) -> str:
    return f"""
<div style="display:flex; align-items:center; gap:12px; margin: 28px 0 16px 0;">
  <div style="width:4px; height:24px; background:{accent}; border-radius:2px;"></div>
  <h3 style="margin:0; font-size:1.15rem; font-weight:700; color:{C_TEXT};">{text}</h3>
</div>
"""


def stat_card_html(label: str, value: str, sub: str = "", color: str = C_GOLD) -> str:
    return f"""
<div style="
  background: {C_SURFACE};
  border: 1px solid {C_BORDER};
  border-top: 3px solid {color};
  border-radius: 10px;
  padding: 20px;
  text-align: center;
">
  <div style="color:{C_SUBTEXT}; font-size:0.75rem; text-transform:uppercase;
              letter-spacing:1px; margin-bottom:8px;">{label}</div>
  <div style="color:{C_TEXT}; font-size:2rem; font-weight:800;">{value}</div>
  {"" if not sub else f'<div style="color:{C_SUBTEXT}; font-size:0.8rem; margin-top:4px;">{sub}</div>'}
</div>
"""


def matchup_card_html(team_a: str, score_a: str, score_b: str, team_b: str,
                      subtitle: str = "") -> str:
    sub_html = (f'<br><span style="color:{C_SUBTEXT}; font-size:0.75rem;">{subtitle}</span>'
                if subtitle else "")
    return f"""
<div style="background:linear-gradient(90deg,#1a2340,{C_SURFACE},#1a2340);
            border:1px solid {C_BORDER}; border-radius:12px;
            padding:14px 20px; margin:8px 0;">
  <table style="width:100%; border-collapse:collapse;">
    <tr>
      <td style="width:38%; text-align:right; padding:0 10px 0 0; vertical-align:middle;">
        <span style="font-size:1.05rem; font-weight:700; color:{C_TEXT};">{team_a}</span>
      </td>
      <td style="width:24%; text-align:center; padding:0; vertical-align:middle;">
        <span style="font-size:1.6rem; font-weight:800; color:{C_GOLD}; letter-spacing:2px;">{score_a} – {score_b}</span>
        {sub_html}
      </td>
      <td style="width:38%; text-align:left; padding:0 0 0 10px; vertical-align:middle;">
        <span style="font-size:1.05rem; font-weight:700; color:{C_TEXT};">{team_b}</span>
      </td>
    </tr>
  </table>
</div>
"""


def prob_bar_html(label: str, value: float, color: str = C_GREEN,
                  max_val: float = 1.0) -> str:
    pct = min(value / max_val, 1.0) * 100
    return f"""
<div style="margin-bottom: 10px;">
  <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
    <span style="color:{C_TEXT}; font-size:0.9rem; font-weight:500;">{label}</span>
    <span style="color:{color}; font-size:0.9rem; font-weight:700;">{value:.1%}</span>
  </div>
  <div style="background:{C_SURFACE2}; border-radius:4px; height:8px; overflow:hidden;">
    <div style="background:{color}; width:{pct:.1f}%; height:100%;
                border-radius:4px; transition:width 0.3s;"></div>
  </div>
</div>
"""


# ── Plotly dark template ───────────────────────────────────────────────────────
_PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=C_SURFACE,
        plot_bgcolor=C_SURFACE,
        font=dict(family="Inter, Segoe UI, system-ui", color=C_TEXT, size=12),
        title=dict(font=dict(size=14, color=C_TEXT)),
        xaxis=dict(
            gridcolor=C_BORDER, linecolor=C_BORDER,
            tickcolor=C_SUBTEXT, tickfont=dict(color=C_SUBTEXT),
            zerolinecolor=C_BORDER,
        ),
        yaxis=dict(
            gridcolor=C_BORDER, linecolor=C_BORDER,
            tickcolor=C_SUBTEXT, tickfont=dict(color=C_SUBTEXT),
            zerolinecolor=C_BORDER,
        ),
        legend=dict(
            bgcolor=C_SURFACE2, bordercolor=C_BORDER,
            borderwidth=1, font=dict(color=C_TEXT),
        ),
        colorway=TEAM_COLORS,
        hoverlabel=dict(
            bgcolor=C_SURFACE2, bordercolor=C_BORDER,
            font=dict(color=C_TEXT),
        ),
    )
)

pio.templates["wc2026"] = _PLOTLY_TEMPLATE
pio.templates.default  = "wc2026"


def apply_chart_defaults(fig: go.Figure, height: int = 360,
                         margin: dict | None = None) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=margin if margin is not None else dict(l=40, r=24, t=24, b=40),
        paper_bgcolor=C_SURFACE,
        plot_bgcolor=C_SURFACE,
    )
    return fig
