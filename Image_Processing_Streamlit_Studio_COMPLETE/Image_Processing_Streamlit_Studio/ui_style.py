"""App-wide presentation. The icon switch uses a session CSS palette, not an unsupported
Streamlit runtime theme API. Keep the accessible widget labels in the DOM.
"""


def theme_css(dark: bool) -> str:
    palettes = {
        True: dict(
            bg="#081321", sidebar="#0D1B2D", surface="#13253B", surface2="#1C314B",
            surface3="#223B59", text="#F0F5FC", muted="#A8BCD3", border="#2E4965",
            accent="#75B6FF", strong="#3169D7", onstrong="#FFFFFF", input="#152940",
            soft="#18355A", success="#6FD4B2", warning="#FFD18B", shadow="0 12px 35px rgba(0,0,0,.18)",
        ),
        False: dict(
            bg="#F5F8FD", sidebar="#EBF2FA", surface="#FFFFFF", surface2="#F0F5FC",
            surface3="#E6EFFA", text="#172B46", muted="#536B88", border="#CBD9E9",
            accent="#285EC4", strong="#275BB8", onstrong="#FFFFFF", input="#FFFFFF",
            soft="#E7EFFD", success="#12664F", warning="#825217", shadow="0 12px 36px rgba(25,54,89,.07)",
        ),
    }
    pal = palettes[dark]
    css_vars = "\n".join(f"--ip-{name}: {hex_color};" for name, hex_color in pal.items())
    return f"""
<style>
:root, [data-testid="stAppViewContainer"] {{ {css_vars}
  --st-background-color:var(--ip-bg); --st-secondary-background-color:var(--ip-surface2);
  --st-text-color:var(--ip-text); --st-primary-color:var(--ip-strong);
  --st-border-color:var(--ip-border); --st-link-color:var(--ip-accent);
  color-scheme: {'dark' if dark else 'light'}; }}
html, body, [data-testid="stAppViewContainer"], .stApp, .main {{
  background:var(--ip-bg) !important; color:var(--ip-text) !important;
}}
[data-testid="stHeader"], [data-testid="stToolbar"] {{ background:var(--ip-bg) !important; }}
[data-testid="stSidebar"], [data-testid="stSidebarContent"],
[data-testid="stSidebarNav"] {{
  background:var(--ip-sidebar) !important; color:var(--ip-text) !important;
}}
[data-testid="stSidebar"] {{ border-right:1px solid var(--ip-border) !important; }}
/* Text colors for BOTH theme variants; avoid overriding the icon glyph color. */
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
.stApp p, .stApp label, .stApp li, .stApp pre, .stApp code,
.stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMetricLabel"] p,
.stApp [data-testid="stMetricValue"],
.stApp [data-testid="stMarkdownContainer"] {{ color: var(--ip-text) !important; }}
.stApp [data-testid="stCaptionContainer"] *,
.stApp [data-testid="stCaptionContainer"] p,
.stApp small {{ color:var(--ip-muted) !important; }}
.block-container {{max-width:1480px; padding-top:1.15rem; padding-bottom:3rem;}}
section[data-testid="stSidebar"] .block-container {{padding-top:1.8rem;}}
/* Rounded containers and data components. */
[data-testid="stVerticalBlockBorderWrapper"] > div {{
 background:var(--ip-surface) !important;
 border:1px solid var(--ip-border) !important;
 border-radius:18px !important; box-shadow:var(--ip-shadow);
}}
[data-testid="stMetric"] {{background:var(--ip-surface2) !important; border:1px solid var(--ip-border);
 border-radius:13px; padding:.75rem .95rem;}}
[data-testid="stDataFrame"], [data-testid="stTable"], [data-testid="stVegaLiteChart"] {{
 color:var(--ip-text); border-color:var(--ip-border) !important; border-radius:12px;
}}
[data-testid="stAlert"] {{border-radius:13px !important;}}
[data-testid="stCodeBlock"], pre, code {{background:var(--ip-surface2) !important; color:var(--ip-text) !important;}}
hr {{border-color:var(--ip-border) !important; opacity:.8;}}
/* Streamlit's config theme stays dark; cover interactive widgets in both modes. */
[data-testid="stFileUploaderDropzone"] {{
 background:var(--ip-surface2) !important;
 border:1.5px dashed var(--ip-accent) !important;
 border-radius:16px !important;
}}
[data-testid="stFileUploaderDropzone"] *,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small {{color:var(--ip-text) !important;}}
[data-baseweb="select"] > div,
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSlider"] > div,
[data-testid="stDateInput"] input {{
 background:var(--ip-input) !important;
 color:var(--ip-text) !important;
 border-color:var(--ip-border) !important;
}}
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="listbox"],
[role="listbox"],
[role="option"],
[data-baseweb="popover"] [role="option"],
[data-testid="stTooltipContent"] {{
 background:var(--ip-surface) !important;
 color:var(--ip-text) !important;
 border-color:var(--ip-border) !important;
}}
[data-baseweb="popover"] *, [data-baseweb="menu"] * {{color:var(--ip-text) !important;}}
[role="option"]:hover {{background:var(--ip-surface3) !important;}}
[data-testid="stSlider"] [role="slider"] {{background:var(--ip-strong) !important;}}
[data-testid="stSlider"] [data-baseweb="slider"] > div > div {{color:var(--ip-text);}}
[data-testid="stRadio"] label {{color:var(--ip-text) !important; border-radius:10px; padding:.16rem .4rem;}}
[data-testid="stRadio"] label:hover {{background:var(--ip-surface2) !important;}}
[data-testid="stRadio"] label:has(input:checked) {{background:var(--ip-soft) !important;}}
[data-testid="stRadio"] label span {{color:var(--ip-text) !important;}}
/* Buttons: one coherent style across day/night. */
div.stButton > button, div.stDownloadButton > button {{
 background:var(--ip-surface2) !important;
 color:var(--ip-text) !important;
 border:1px solid var(--ip-border) !important;
 border-radius:12px !important;
 font-weight:650 !important; min-height:2.65rem;
 box-shadow:0 1px 1px rgba(13,35,60,.04);
 transition:background 140ms ease,border-color 140ms ease,transform 140ms ease;
}}
div.stButton > button *,div.stDownloadButton > button * {{color:inherit !important;}}
div.stButton > button:hover, div.stDownloadButton > button:hover {{
 background:var(--ip-surface3) !important;
 border-color:var(--ip-accent) !important;
 transform:translateY(-1px);
}}
div.stButton > button[kind="primary"],div.stDownloadButton > button[kind="primary"] {{
 background:var(--ip-strong) !important;
 color:var(--ip-onstrong) !important;
 border-color:var(--ip-strong) !important;
}}
div.stButton > button[kind="primary"]:hover {{filter:brightness(1.08);}}
div.stButton > button:focus-visible, div.stDownloadButton > button:focus-visible {{outline:2px solid var(--ip-accent) !important; outline-offset:2px;}}
/* Icon-only theme button: label remains in DOM as an accessible name. */
.st-key-theme_toggle button {{width:2.8rem !important; height:2.8rem !important;
 border-radius:50% !important; padding:0 !important; display:flex !important; justify-content:center !important; align-items:center !important;}}
.st-key-theme_toggle button p {{font-size:0 !important; line-height:0 !important;}}
.st-key-theme_toggle button span[data-testid="stIconMaterial"] {{font-size:1.4rem !important;}}
.st-key-theme_toggle button:hover {{transform:rotate(15deg) !important;}}
/* Navigation and final all-results button. */
.st-key-nav_colors button, .st-key-nav_points button, .st-key-nav_contrast button,
.st-key-nav_filters button {{min-height:3.2rem; border-radius:13px !important;}}
.st-key-compare_all_button button {{min-height:3.15rem !important;
 border-style:solid !important; font-weight:750 !important;}}
.ip-eyebrow {{color:var(--ip-accent) !important; font-size:.72rem; font-weight:800;
 text-transform:uppercase; letter-spacing:.16em; margin:0 0 .4rem;}}
.ip-headline {{color:var(--ip-text) !important; font-size:clamp(1.85rem,2.9vw,2.65rem);
 font-weight:810; letter-spacing:-.045em; line-height:1.08; margin:0 0 .4rem;}}
.ip-muted {{color:var(--ip-muted) !important; margin:.4rem 0 0; font-size:.95rem; line-height:1.6;}}
.ip-mini-title {{font-size:.73rem; letter-spacing:.13em; text-transform:uppercase;
 color:var(--ip-muted) !important; font-weight:780; margin: .4rem 0 .5rem;}}
.ip-chip {{display:inline-block; margin:.1rem .5rem .1rem 0; padding:.36rem .7rem;
 font-size:.79rem; font-weight:700; border-radius:999px; color:var(--ip-text);
 border:1px solid var(--ip-border); background:var(--ip-surface2);}}
.ip-decision {{background:var(--ip-surface); border:1px solid var(--ip-border);
 border-left:4px solid var(--ip-accent); border-radius:15px; padding:1.1rem 1.2rem;
 margin:1rem 0; box-shadow:var(--ip-shadow);}}
.ip-decision.no-winner {{border-left-color:var(--ip-warning);}}
.ip-decision-title {{font-size:1.13rem; font-weight:790; color:var(--ip-text); margin:0 0 .3rem;}}
.ip-decision-desc {{font-size:.93rem; line-height:1.65; color:var(--ip-muted);}}
.ip-evidence {{display:inline-block; padding:.4rem .7rem; font-size:.8rem; margin:.65rem .55rem 0 0;
 color:var(--ip-text); border:1px solid var(--ip-border);
 background:var(--ip-surface2); border-radius:10px;}}
.ip-section-line {{display:flex;align-items:center;gap:.7rem; margin:.8rem 0;}}
.ip-section-line::before {{content:"";width:7px;height:7px;border-radius:50%;background:var(--ip-accent);}}
.ip-footer {{color:var(--ip-muted);font-size:.8rem;margin-top:1.2rem;}}
/* Custom comparison tables and inline SVG plots use the same palette in both modes. */
.ip-table-wrap {{overflow-x:auto; border:1px solid var(--ip-border); border-radius:14px;
 background:var(--ip-surface); margin:.7rem 0 1rem;}}
.ip-data-table {{width:100%;border-collapse:collapse; font-size:.84rem;}}
.ip-data-table th {{text-align:left; white-space:nowrap; padding:.78rem .82rem; font-weight:790;
 color:var(--ip-muted); background:var(--ip-surface2);border-bottom:1px solid var(--ip-border);}}
.ip-data-table td {{padding:.76rem .82rem; border-bottom:1px solid var(--ip-border);
 color:var(--ip-text);white-space:nowrap;}}
.ip-data-table tr:last-child td {{border-bottom:none;}}
.ip-data-table tbody tr:hover {{background:var(--ip-surface2);}}
.ip-histogram {{display:block;width:100%;height:auto;background:var(--ip-surface2);
 border:1px solid var(--ip-border);border-radius:14px;}}
.ip-chart-legend {{font-size:.82rem;color:var(--ip-muted);margin:.45rem 0 1rem;}}
.ip-chart-dot {{display:inline-block;width:.65rem;height:.65rem;border-radius:99px;margin:0 .4rem 0 .9rem;}}

</style>
"""
