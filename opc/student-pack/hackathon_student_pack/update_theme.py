import re
from pathlib import Path

fpath = Path('interface.py')
content = fpath.read_text()

# 1. Update _dark function
new_dark = '''def _dark(fig, title=""):
    is_dark = st.session_state.get("dark_theme", True)
    tc = "#c8c8e0" if is_dark else "#334155"
    gc = "rgba(255,255,255,.05)" if is_dark else "rgba(0,0,0,.05)"
    tpl = "plotly_dark" if is_dark else "plotly_white"
    
    fig.update_layout(template=tpl, paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      title=dict(text=title, font=dict(size=14, color=tc)),
                      margin=dict(l=40,r=20,t=40,b=30), height=300,
                      font=dict(family="Inter", color=tc),
                      legend=dict(font=dict(size=10)))
    fig.update_xaxes(gridcolor=gc)
    fig.update_yaxes(gridcolor=gc)'''
content = re.sub(r'def _dark\(fig, title=""\):.*?fig\.update_yaxes\(gridcolor="rgba\(255,255,255,\.05\)"\)', new_dark, content, flags=re.DOTALL)

# 2. Page config and theme initialization
page_cfg = '''st.set_page_config(page_title="Race AI Engineer", layout="wide")

if "dark_theme" not in st.session_state:
    st.session_state.dark_theme = True

is_dark = st.session_state.dark_theme
icon_color = "ffffff" if is_dark else "000000"

if is_dark:
    css_vars = """
    :root { --bg-main: #0e1117; --bg-header: linear-gradient(135deg,#0f0f23,#1a1a3e,#2d1b4e); --bg-card: linear-gradient(145deg,#15152a,#1e1e3a); --bg-desc: linear-gradient(145deg,rgba(21,21,42,.7),rgba(30,30,58,.7)); --text-primary: #ffffff; --text-secondary: #c8c8e0; --text-muted: rgba(200,200,224,.8); --border-color: rgba(255,255,255,.07); --border-hover: rgba(99,102,241,.5); --accent: #6366f1; --accent-bg: linear-gradient(145deg,#1a1a3e,#2d1b4e); }
    """
else:
    css_vars = """
    :root { --bg-main: #f0f2f6; --bg-header: linear-gradient(135deg,#ffffff,#f1f5f9,#e2e8f0); --bg-card: #ffffff; --bg-desc: #ffffff; --text-primary: #0f172a; --text-secondary: #334155; --text-muted: #475569; --border-color: rgba(0,0,0,.1); --border-hover: rgba(99,102,241,.6); --accent: #4f46e5; --accent-bg: #e0e7ff; }
    """
'''
content = content.replace('st.set_page_config(page_title="Race AI Engineer", layout="wide")', page_cfg)

# 3. Sidebar toggle and layout
sidebar_old = '''    # Show description for selected mode
    st.markdown(f\'<div style="background:linear-gradient(145deg,#15152a,#1e1e3a);border:1px solid rgba(99,102,241,.25);border-radius:10px;padding:.7rem .9rem;margin-top:.5rem;"><span style="color:rgba(200,200,224,.75);font-size:.8rem;line-height:1.4;">{MODE_INFO[app_mode]}</span></div>\', unsafe_allow_html=True)'''
sidebar_new = '''    # Show description for selected mode
    st.markdown(f\'<div style="background:var(--bg-card);border:1px solid var(--border-hover);border-radius:10px;padding:.7rem .9rem;margin-top:.5rem;"><span style="color:var(--text-muted);font-size:.8rem;line-height:1.4;">{MODE_INFO[app_mode]}</span></div>\', unsafe_allow_html=True)

    st.markdown("---")
    theme_switch = st.toggle("Tema Scuro", value=st.session_state.dark_theme)
    if theme_switch != st.session_state.dark_theme:
        st.session_state.dark_theme = theme_switch
        st.rerun()'''
content = content.replace(sidebar_old, sidebar_new)

# 4. Replace CSS block
css_old = '''st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
*, *::before, *::after {{ box-sizing: border-box; }}
html,body,[class*="st-"]{{font-family:'Inter',sans-serif}}
html,body {{ max-width: 100%; overflow-x: hidden; }}
.main-header{{background:linear-gradient(135deg,#0f0f23,#1a1a3e,#2d1b4e);padding:1.2rem 2rem;border-radius:16px;margin-bottom:1.5rem;box-shadow:0 8px 32px rgba(0,0,0,.3);width:100%}}
.main-header h1{{color:#fff;font-size:1.6rem;font-weight:800;margin:0;letter-spacing:-.5px}}
.main-header .subtitle{{color:rgba(255,255,255,.55);font-size:.85rem;margin:0}}
.mini-card{{background:linear-gradient(145deg,#15152a,#1e1e3a);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.2rem;box-shadow:0 4px 20px rgba(0,0,0,.25)}}
.mini-card h3{{color:#e0e0ff;font-size:1rem;font-weight:700;margin:0 0 .8rem 0}}
.answer-box{{background:linear-gradient(145deg,#15152a,#1e1e3a);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:1.5rem;min-height:80px;color:#c8c8e0;font-size:.95rem;line-height:1.6;box-shadow:0 4px 20px rgba(0,0,0,.25);margin-bottom:1rem}}
.flaticon-icon{{width:18px;height:18px;vertical-align:middle;margin-right:6px}}
.flaticon-icon-large{{width:24px;height:24px;vertical-align:middle;margin-right:8px}}

/* Lab styles */
.lab-hero{{position:relative;border-radius:16px;overflow:hidden;margin-bottom:1.5rem;box-shadow:0 8px 40px rgba(0,0,0,.5)}}
.lab-hero img{{width:100%;display:block;filter:brightness(0.45) contrast(1.1)}}
.lab-hero-overlay{{position:absolute;bottom:0;left:0;right:0;padding:2rem;background:linear-gradient(transparent,rgba(8,12,30,.95))}}
.lab-hero-overlay h2{{color:#e0f0ff;font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;margin:0;letter-spacing:1px}}
.lab-hero-overlay p{{color:rgba(180,210,255,.7);font-family:'JetBrains Mono',monospace;font-size:.75rem;margin:.4rem 0 0 0;letter-spacing:.5px}}
.lab-section-title{{color:#8ba4c4;font-family:'JetBrains Mono',monospace;font-size:.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin:1rem 0 .6rem 0;padding-bottom:.4rem;border-bottom:1px solid rgba(100,140,200,.2)}}

/* Sidebar mode selector */
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label {{cursor:pointer;background:linear-gradient(145deg,#15152a,#1e1e3a);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:0.65rem 1rem;margin-bottom:6px;transition:all .2s ease}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:hover {{border-color:rgba(99,102,241,.5);box-shadow:0 0 12px rgba(99,102,241,.15)}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label[data-checked="true"] {{border-color:#6366f1;background:linear-gradient(145deg,#1a1a3e,#2d1b4e);box-shadow:0 0 16px rgba(99,102,241,.2)}}

/* Section description */
.section-desc{{background:linear-gradient(145deg,rgba(21,21,42,.7),rgba(30,30,58,.7));border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:1rem 1.2rem;margin-bottom:1.2rem;color:rgba(200,200,224,.8);font-size:.88rem;line-height:1.55}}
.section-desc strong{{color:#c8c8e0}}
</style>"""'''
css_new = '''st.markdown(f"""<style>
{css_vars}
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');
*, *::before, *::after {{ box-sizing: border-box; }}
html,body,[class*="st-"]{{font-family:'Inter',sans-serif; color: var(--text-primary);}}
html,body {{ max-width: 100%; overflow-x: hidden; }}
[data-testid="stAppViewContainer"] {{ background-color: var(--bg-main); transition: background-color 0.3s; }}
[data-testid="stSidebar"] {{ background-color: var(--bg-main); border-right: 1px solid var(--border-color); }}
[data-testid="stHeader"] {{ background: transparent; }}
.main-header{{background:var(--bg-header);padding:1.2rem 2rem;border-radius:16px;margin-bottom:1.5rem;box-shadow:0 8px 32px rgba(0,0,0,.1);width:100%}}
.main-header h1{{color:var(--text-primary);font-size:1.6rem;font-weight:800;margin:0;letter-spacing:-.5px}}
.main-header .subtitle{{color:var(--text-muted);font-size:.85rem;margin:0}}
.mini-card{{background:var(--bg-card);border:1px solid var(--border-color);border-radius:14px;padding:1.2rem;box-shadow:0 4px 20px rgba(0,0,0,.1)}}
.mini-card h3{{color:var(--text-secondary);font-size:1rem;font-weight:700;margin:0 0 .8rem 0}}
.answer-box{{background:var(--bg-card);border:1px solid var(--border-color);border-radius:14px;padding:1.5rem;min-height:80px;color:var(--text-secondary);font-size:.95rem;line-height:1.6;box-shadow:0 4px 20px rgba(0,0,0,.1);margin-bottom:1rem}}
.flaticon-icon{{width:18px;height:18px;vertical-align:middle;margin-right:6px}}
.flaticon-icon-large{{width:24px;height:24px;vertical-align:middle;margin-right:8px}}

/* Lab styles */
.lab-hero{{position:relative;border-radius:16px;overflow:hidden;margin-bottom:1.5rem;box-shadow:0 8px 40px rgba(0,0,0,.2)}}
.lab-hero img{{width:100%;display:block;filter:brightness(0.45) contrast(1.1)}}
.lab-hero-overlay{{position:absolute;bottom:0;left:0;right:0;padding:2rem;background:linear-gradient(transparent,rgba(8,12,30,.95))}}
.lab-hero-overlay h2{{color:#e0f0ff;font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;margin:0;letter-spacing:1px}}
.lab-hero-overlay p{{color:rgba(180,210,255,.7);font-family:'JetBrains Mono',monospace;font-size:.75rem;margin:.4rem 0 0 0;letter-spacing:.5px}}
.lab-section-title{{color:var(--text-muted);font-family:'JetBrains Mono',monospace;font-size:.85rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin:1rem 0 .6rem 0;padding-bottom:.4rem;border-bottom:1px solid var(--border-color)}}

/* Sidebar mode selector */
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label {{cursor:pointer;background:var(--bg-card);border:1px solid var(--border-color);border-radius:12px;padding:0.65rem 1rem;margin-bottom:6px;transition:all .2s ease; color: var(--text-primary);}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label:hover {{border-color:var(--border-hover);box-shadow:0 0 12px rgba(99,102,241,.15)}}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > label[data-checked="true"] {{border-color:var(--accent);background:var(--accent-bg);box-shadow:0 0 16px rgba(99,102,241,.1)}}

/* Section description */
.section-desc{{background:var(--bg-desc);border:1px solid var(--border-color);border-radius:12px;padding:1rem 1.2rem;margin-bottom:1.2rem;color:var(--text-muted);font-size:.88rem;line-height:1.55}}
.section-desc strong{{color:var(--text-secondary)}}
</style>"""'''
content = content.replace(css_old, css_new)

# 5. Replace ffffff with {icon_color} where applicable
# Be careful to only replace icons8 paths
content = re.sub(r'https://img\.icons8\.com/ios-filled/100/ffffff/(.*?\.png)', r'https://img.icons8.com/ios-filled/100/{icon_color}/\1', content)

# 6. Some literal strings might need the "f" prefix if they didn't have it
content = re.sub(r'(st\.markdown\(\'### <img src="https://img\.icons8\.com)', r'st.markdown(f\'### <img src="https://img.icons8.com', content)

fpath.write_text(content)
print("Updated successfully")
