import os
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
import requests
import streamlit as st
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv(Path(__file__).with_name(".env"), override=True)
SERVER_URL = os.environ["FILE_SEARCH_SERVER_URL"].rstrip("/")
TELEMETRY_SERVER_URL = "http://127.0.0.1:8100"
CAR_IMAGE_PATH = Path(__file__).resolve().parent / "images" / "car.png"
TELEMETRY_JSON = Path(__file__).resolve().parent / "telemetry" / "race_session_telemetry.json"

# ---------------------------------------------------------------------------
# Backend helpers
# ---------------------------------------------------------------------------
def call_server(query: str, endpoint: str) -> str:
    try:
        r = requests.post(f"{SERVER_URL}{endpoint}", json={"query": query}, timeout=120)
        r.raise_for_status()
        answer = r.json().get("answer")
        return answer if answer else "Non sono riuscito a generare una risposta. Riprova con una domanda più specifica."
    except requests.exceptions.RequestException as e:
        return f"Errore: {e}"

def call_server_dashboard(query: str, active_chips: list) -> dict:
    try:
        r = requests.post(f"{SERVER_URL}/query_telemetria_dashboard",
                          json={"query": query, "active_chips": active_chips}, timeout=120)
        r.raise_for_status()
        d = r.json()
        return {"answer": d.get("answer", ""), "chart_config": d.get("chart_config")}
    except requests.exceptions.RequestException as e:
        return {"answer": f"Errore: {e}", "chart_config": None}

def fetch_telemetry(tool_name: str, params: dict) -> dict:
    try:
        r = requests.get(f"{TELEMETRY_SERVER_URL}/tools/{tool_name}", params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# ---------------------------------------------------------------------------
# Shared helpers (used by In-Race Analyzer)
# ---------------------------------------------------------------------------
def _dark(fig, title=""):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                      plot_bgcolor="rgba(0,0,0,0)",
                      title=dict(text=title, font=dict(size=14, color="#c8c8e0")),
                      margin=dict(l=40,r=20,t=40,b=30), height=300,
                      font=dict(family="Inter", color="#a0a0c0"),
                      legend=dict(font=dict(size=10)))
    fig.update_xaxes(gridcolor="rgba(255,255,255,.05)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,.05)")

@st.cache_data
def load_telemetry_data():
    """Load the full telemetry JSON for in-race analysis."""
    with open(TELEMETRY_JSON, "r", encoding="utf-8") as fh:
        return json.load(fh)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Race AI Engineer", layout="wide")

# Load car image as base64 for CSS background
car_b64 = ""
if CAR_IMAGE_PATH.exists():
    car_b64 = base64.b64encode(CAR_IMAGE_PATH.read_bytes()).decode()

st.markdown(f"""<style>
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
.attribution-footer{{text-align:center;font-size:0.7rem;color:rgba(255,255,255,0.3);margin-top:3rem;padding-top:1rem;border-top:1px solid rgba(255,255,255,0.05)}}
.attribution-footer a{{color:rgba(255,255,255,0.4);text-decoration:none}}
.attribution-footer a:hover{{color:rgba(255,255,255,0.7)}}
</style>""", unsafe_allow_html=True)



# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
MODE_INFO = {
    "Experimental Lab": "Verifica componenti, regolamento e specifiche tecniche della vettura.",
    "In-Race Analyzer": "Scorri la gara giro per giro, analizza i delta e chiedi consigli all'AI.",
    "Post-Race Analyzer": "Dashboard completa con grafici, chip e analisi AI della sessione.",
}

with st.sidebar:
    st.markdown('<p style="font-family:\'JetBrains Mono\',monospace;font-size:.75rem;letter-spacing:2px;color:#8ba4c4;text-transform:uppercase;margin-bottom:.6rem;">Seleziona Modalita</p>', unsafe_allow_html=True)
    app_mode = st.radio(
        "Seleziona Modalita",
        list(MODE_INFO.keys()),
        index=0,
        label_visibility="collapsed"
    )
    # Show description for selected mode
    st.markdown(f'<div style="background:linear-gradient(145deg,#15152a,#1e1e3a);border:1px solid rgba(99,102,241,.25);border-radius:10px;padding:.7rem .9rem;margin-top:.5rem;"><span style="color:rgba(200,200,224,.75);font-size:.8rem;line-height:1.4;">{MODE_INFO[app_mode]}</span></div>', unsafe_allow_html=True)

# Reset state on mode switch + scroll to top
if "prev_mode" not in st.session_state:
    st.session_state.prev_mode = app_mode
if st.session_state.prev_mode != app_mode:
    st.session_state.prev_mode = app_mode
    for k in ["messages", "lab_messages", "inrace_messages", "inrace_lap",
              "dashboard_answer", "dashboard_chart_config"]:
        st.session_state.pop(k, None)
    # Scroll to top on mode change
    st.components.v1.html('<script>window.parent.document.querySelector("section.main").scrollTo(0,0);</script>', height=0)

# ═══════════════════════════════════════════════════════════════════════════
# EXPERIMENT MODE — Laboratorio Tecnico
# ═══════════════════════════════════════════════════════════════════════════
if app_mode == "Experimental Lab":
    # Hero image (replaces the header banner)
    if car_b64:
        st.markdown(f"""<div class="lab-hero">
<img src="data:image/png;base64,{car_b64}" alt="STV-E26"/>
<div class="lab-hero-overlay">
<h2>LABORATORIO TECNICO</h2>
<p>STV-E26 // Analisi Componenti // Conformita Regolamento</p>
</div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('### <img src="https://img.icons8.com/ios-filled/100/ffffff/mechanic.png" class="flaticon-icon-large" /> Laboratorio Tecnico — STV-E26', unsafe_allow_html=True)

    st.markdown('<div class="section-desc">Usa questa sezione per <strong>verificare componenti</strong>, controllare la <strong>conformita al regolamento</strong> e simulare modifiche alle specifiche tecniche della STV-E26. Puoi fare domande all\'AI sul regolamento, dimensioni, materiali e configurazioni sperimentali.</div>', unsafe_allow_html=True)

    # Example technical questions
    st.markdown('<div class="lab-section-title">Analisi Rapide</div>', unsafe_allow_html=True)

    LAB_EXAMPLES = [
        "L'ala posteriore RW-26C e conforme al regolamento?",
        "Il contenitore batteria BAT-X9 e ammesso?",
        "Il fairing SA-LF-OPT rispetta i limiti dimensionali?",
        "Cosa succede se aumento il chord dell'ala a 310 mm?",
        "Il wheelbase di 1605 mm e conforme alla Sezione 8.2?",
        "Posso usare magnesio-litio per l'accumulator container?",
    ]

    ex_cols = st.columns(3)
    clicked_lab = None
    for i, q in enumerate(LAB_EXAMPLES):
        if ex_cols[i % 3].button(q, key=f"lab_{i}", use_container_width=True):
            clicked_lab = q

    st.markdown("---")
    st.markdown('<div class="lab-section-title">Consulta l\'Ingegnere</div>', unsafe_allow_html=True)

    # Chat state
    if "lab_messages" not in st.session_state:
        st.session_state.lab_messages = [
            {"role": "assistant", "content": "Benvenuto nel Laboratorio Tecnico. Puoi chiedermi informazioni su componenti sperimentali, conformita al regolamento, dimensioni, materiali e specifiche tecniche della STV-E26."}
        ]

    for msg in st.session_state.lab_messages:
        avatar = "https://api.dicebear.com/9.x/bottts/svg?seed=engineer" if msg["role"] == "assistant" else "https://api.dicebear.com/9.x/initials/svg?seed=U"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("Domanda tecnica sulla vettura...")
    if clicked_lab:
        user_input = clicked_lab

    if user_input:
        st.session_state.lab_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="https://api.dicebear.com/9.x/initials/svg?seed=U"):
            st.markdown(user_input)
        with st.chat_message("assistant", avatar="https://api.dicebear.com/9.x/bottts/svg?seed=engineer"):
            with st.spinner("Analisi documenti tecnici in corso..."):
                answer = call_server(user_input, "/query")
            st.markdown(answer)
        st.session_state.lab_messages.append({"role": "assistant", "content": answer})



# ═══════════════════════════════════════════════════════════════════════════
# IN-RACE ANALYZER — Debugger Giro per Giro
# ═══════════════════════════════════════════════════════════════════════════
elif app_mode == "In-Race Analyzer":
    # TODO(security): All HTML below is static with no user input injection
    st.markdown("""<div class="main-header"><div>
<h1>In-Race Analyzer</h1>
<p class="subtitle">STV-E26 · Debugger Giro per Giro · Analisi Delta e Trend</p>
</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-desc">Scorri la gara <strong>giro per giro</strong> come un debugger. Per ogni lap puoi vedere i <strong>delta</strong> rispetto al giro precedente (tempi, gomme, energia, freni), monitorare i <strong>trend</strong> nei grafici e chiedere all\'<strong>AI Race Engineer</strong> un\'analisi specifica del giro selezionato.</div>', unsafe_allow_html=True)

    # Load telemetry data (cached)
    tel_data = load_telemetry_data()
    all_laps = tel_data["laps"]
    total_laps = len(all_laps)
    lap_idx = {l["lap"]: l for l in all_laps}
    race_events = {e["lap"]: e for e in tel_data.get("race_control_events", [])}
    pit_events = {p["lap"]: p for p in tel_data.get("pit_stop_history", [])}

    # --- Lap Navigator ---
    if "inrace_lap" not in st.session_state:
        st.session_state.inrace_lap = 1

    current_lap = st.slider(
        "Seleziona Giro", 1, total_laps,
        key="inrace_lap",
        help="Usa le frecce della tastiera per avanzare giro per giro"
    )

    curr = lap_idx[current_lap]
    prev = lap_idx.get(current_lap - 1)

    # --- Lap Info Badge ---
    _sc = "#10b981" if curr.get("track_status") == "green" else "#eab308" if "yellow" in str(curr.get("track_status","")) else "#ef4444"
    _sl = str(curr.get("track_status", "unknown")).upper()
    _si = f"Stint {curr.get('stint_number', '?')} / Lap {curr.get('stint_lap', '?')}"
    _cp = str(curr.get("tires", {}).get("compound", "?"))
    _fb = str(curr.get("driver_feedback", ""))[:80]
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin:0.5rem 0 1rem 0;flex-wrap:wrap;">'
        f'<span style="background:{_sc};color:#000;font-weight:700;padding:4px 12px;border-radius:20px;font-size:.8rem;">{_sl}</span>'
        f'<span style="color:#c8c8e0;font-size:.9rem;font-weight:600;">{_si}</span>'
        f'<span style="color:#8ba4c4;font-size:.8rem;">Compound: {_cp}</span>'
        f'<span style="color:rgba(200,200,224,.6);font-size:.75rem;font-style:italic;">{_fb}</span>'
        f'</div>', unsafe_allow_html=True)

    # --- Race control / pit events for this lap ---
    if current_lap in race_events:
        ev = race_events[current_lap]
        st.warning(f"Race Control — {str(ev.get('type','')).replace('_',' ').title()}: {ev.get('message','')}")
    if current_lap in pit_events:
        pit = pit_events[current_lap]
        st.info(f"Pit Stop — Fermo: {pit.get('stationary_time_s',0)}s | {', '.join(str(a) for a in pit.get('actions',[]))} | {pit.get('reason','')}")

    st.markdown("---")

    # --- Delta helper ---
    def _dv(cv, pv):
        """Compute delta between current and previous value."""
        if cv is None or pv is None:
            return None
        return round(cv - pv, 3)

    # ---- PERFORMANCE METRICS ----
    st.markdown('<div class="lab-section-title">Performance</div>', unsafe_allow_html=True)
    pm1, pm2, pm3, pm4 = st.columns(4)

    _lt = curr.get("lap_time_s")
    _plt = prev.get("lap_time_s") if prev else None
    pm1.metric("Tempo Giro", f"{_lt:.3f}s" if _lt else "N/A",
               delta=f"{_dv(_lt,_plt):+.3f}s" if _dv(_lt,_plt) is not None else None,
               delta_color="inverse")

    _pos = curr.get("position")
    _ppos = prev.get("position") if prev else None
    pm2.metric("Posizione", f"P{_pos}" if _pos else "N/A",
               delta=f"{_dv(_pos,_ppos):+.0f}" if _dv(_pos,_ppos) is not None else None,
               delta_color="inverse")

    _soc = curr.get("energy_system",{}).get("battery_state_of_charge_pct")
    _psoc = prev.get("energy_system",{}).get("battery_state_of_charge_pct") if prev else None
    pm3.metric("SoC Batteria", f"{_soc:.1f}%" if _soc else "N/A",
               delta=f"{_dv(_soc,_psoc):+.1f}%" if _dv(_soc,_psoc) is not None else None)

    _ga = curr.get("race_context",{}).get("gap_to_car_ahead_s")
    _pga = prev.get("race_context",{}).get("gap_to_car_ahead_s") if prev else None
    pm4.metric("Gap Davanti", f"{_ga:.2f}s" if _ga else "N/A",
               delta=f"{_dv(_ga,_pga):+.2f}s" if _dv(_ga,_pga) is not None else None,
               delta_color="inverse")

    # ---- SECTORS ----
    st.markdown('<div class="lab-section-title">Settori</div>', unsafe_allow_html=True)
    sc1, sc2, sc3 = st.columns(3)
    for idx, (sk, scol) in enumerate(zip(["sector_1","sector_2","sector_3"],[sc1,sc2,sc3])):
        sv = curr.get("sector_times_s",{}).get(sk)
        spv = prev.get("sector_times_s",{}).get(sk) if prev else None
        scol.metric(f"Settore {idx+1}", f"{sv:.3f}s" if sv else "N/A",
                    delta=f"{_dv(sv,spv):+.3f}s" if _dv(sv,spv) is not None else None,
                    delta_color="inverse")

    # ---- TYRES ----
    st.markdown('<div class="lab-section-title">Gomme</div>', unsafe_allow_html=True)
    _C = ["front_left","front_right","rear_left","rear_right"]
    _CL = ["Ant. SX","Ant. DX","Post. SX","Post. DX"]

    st.caption("Usura (%)")
    wc = st.columns(4)
    for i,(cn,cl) in enumerate(zip(_C,_CL)):
        w = curr.get("tires",{}).get("wear_pct",{}).get(cn)
        ew = curr.get("tires",{}).get("expected_wear_pct",{}).get(cn)
        pw = prev.get("tires",{}).get("wear_pct",{}).get(cn) if prev else None
        hlp = f"Atteso: {ew:.1f}% | Gap: {(w-ew):+.1f}pp" if w is not None and ew is not None else None
        wc[i].metric(cl, f"{w:.1f}%" if w else "N/A",
                     delta=f"{_dv(w,pw):+.1f}%" if _dv(w,pw) is not None else None,
                     delta_color="inverse", help=hlp)

    st.caption("Temperatura (C)")
    tc = st.columns(4)
    for i,(cn,cl) in enumerate(zip(_C,_CL)):
        t = curr.get("tires",{}).get("temperature_c",{}).get(cn)
        pt = prev.get("tires",{}).get("temperature_c",{}).get(cn) if prev else None
        tc[i].metric(cl, f"{t:.1f}C" if t else "N/A",
                     delta=f"{_dv(t,pt):+.1f}C" if _dv(t,pt) is not None else None,
                     delta_color="inverse")

    # ---- BRAKES ----
    st.markdown('<div class="lab-section-title">Temperature Freni</div>', unsafe_allow_html=True)
    bc = st.columns(4)
    for i,(cn,cl) in enumerate(zip(_C,_CL)):
        b = curr.get("brake_temperatures_c",{}).get(cn)
        pb = prev.get("brake_temperatures_c",{}).get(cn) if prev else None
        bc[i].metric(cl, f"{b:.1f}C" if b else "N/A",
                     delta=f"{_dv(b,pb):+.1f}C" if _dv(b,pb) is not None else None,
                     delta_color="inverse")

    # ---- ENERGY ----
    st.markdown('<div class="lab-section-title">Sistema Energetico</div>', unsafe_allow_html=True)
    ec = st.columns(4)

    _kwh = curr.get("energy_system",{}).get("energy_remaining_kwh")
    _pkwh = prev.get("energy_system",{}).get("energy_remaining_kwh") if prev else None
    ec[0].metric("Energia Residua", f"{_kwh:.2f} kWh" if _kwh else "N/A",
                 delta=f"{_dv(_kwh,_pkwh):+.2f} kWh" if _dv(_kwh,_pkwh) is not None else None)

    _ers = curr.get("energy_system",{}).get("ers_deployment_kj")
    _pers = prev.get("energy_system",{}).get("ers_deployment_kj") if prev else None
    ec[1].metric("ERS Deploy", f"{_ers:.1f} kJ" if _ers else "N/A",
                 delta=f"{_dv(_ers,_pers):+.1f} kJ" if _dv(_ers,_pers) is not None else None)

    _dm = str(curr.get("energy_system",{}).get("deployment_mode","N/A"))
    ec[2].metric("Modalita", _dm.capitalize())

    _gb = curr.get("race_context",{}).get("gap_to_car_behind_s")
    _pgb = prev.get("race_context",{}).get("gap_to_car_behind_s") if prev else None
    ec[3].metric("Gap Dietro", f"{_gb:.2f}s" if _gb else "N/A",
                 delta=f"{_dv(_gb,_pgb):+.2f}s" if _dv(_gb,_pgb) is not None else None)

    # ---- STRATEGY ----
    st.markdown('<div class="lab-section-title">Contesto Strategico</div>', unsafe_allow_html=True)
    _strat = curr.get("strategy_context", {})
    stc = st.columns(4)
    stc[0].metric("Giri Rimanenti", _strat.get("laps_remaining","?"))
    stc[1].metric("Pit Window", str(_strat.get("pit_window_status","?")).replace("_"," ").title())
    stc[2].metric("Proiezione (no pit)", f"P{_strat.get('projected_finish_position_if_no_stop','?')}")
    stc[3].metric("Proiezione (pit now)", f"P{_strat.get('projected_finish_position_if_pit_now','?')}")

    # ---- TREND CHARTS ----
    st.markdown("---")
    st.markdown('<div class="lab-section-title">Trend fino al Giro Corrente</div>', unsafe_allow_html=True)

    trend_laps = [lap_idx[n] for n in range(1, current_lap + 1) if n in lap_idx]
    trend_x = [l["lap"] for l in trend_laps]

    ch1, ch2 = st.columns(2)
    with ch1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend_x, y=[l.get("lap_time_s") for l in trend_laps],
                                 name="Tempo Giro", line=dict(color="#6366f1",width=2),
                                 mode="lines+markers", marker=dict(size=4)))
        if _lt is not None:
            fig.add_trace(go.Scatter(x=[current_lap], y=[_lt], mode="markers",
                                     marker=dict(color="#f97316",size=10,symbol="diamond"),
                                     showlegend=False))
        _dark(fig, "Tempo Giro (s)")
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=trend_x,
                                  y=[l.get("energy_system",{}).get("battery_state_of_charge_pct") for l in trend_laps],
                                  name="SoC %", fill="tozeroy",
                                  line=dict(color="#22d3ee",width=2),
                                  fillcolor="rgba(34,211,238,.15)"))
        if _soc is not None:
            fig2.add_trace(go.Scatter(x=[current_lap], y=[_soc], mode="markers",
                                      marker=dict(color="#f97316",size=10,symbol="diamond"),
                                      showlegend=False))
        _dark(fig2, "SoC Batteria (%)")
        st.plotly_chart(fig2, use_container_width=True)

    ch3, ch4 = st.columns(2)
    with ch3:
        _wcolors = ["#6366f1","#a855f7","#ec4899","#f97316"]
        fig3 = go.Figure()
        for cn,cl,co in zip(_C,_CL,_wcolors):
            fig3.add_trace(go.Scatter(x=trend_x,
                                      y=[l.get("tires",{}).get("wear_pct",{}).get(cn) for l in trend_laps],
                                      name=cl, line=dict(color=co,width=2), mode="lines"))
        fig3.add_hline(y=80, line_dash="dot", line_color="rgba(239,68,68,.4)",
                       annotation_text="Limite 80%")
        _dark(fig3, "Usura Gomme (%)")
        st.plotly_chart(fig3, use_container_width=True)

    with ch4:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(x=trend_x, y=[l.get("position") for l in trend_laps],
                                  name="Posizione", line=dict(color="#10b981",width=3),
                                  mode="lines+markers", marker=dict(size=5)))
        if _pos is not None:
            fig4.add_trace(go.Scatter(x=[current_lap], y=[_pos], mode="markers",
                                      marker=dict(color="#f97316",size=10,symbol="diamond"),
                                      showlegend=False))
        fig4.update_yaxes(autorange="reversed")
        _dark(fig4, "Posizione in Gara")
        st.plotly_chart(fig4, use_container_width=True)

    # ---- AI CHAT ----
    st.markdown("---")
    st.markdown('<div class="lab-section-title">Chiedi all\'AI su questo Giro</div>', unsafe_allow_html=True)

    if "inrace_messages" not in st.session_state:
        st.session_state.inrace_messages = []

    for msg in st.session_state.inrace_messages:
        _av = "https://api.dicebear.com/9.x/bottts/svg?seed=engineer" if msg["role"] == "assistant" else "https://api.dicebear.com/9.x/initials/svg?seed=U"
        with st.chat_message(msg["role"], avatar=_av):
            st.markdown(msg["content"])

    inrace_input = st.chat_input("Chiedi all'AI di analizzare questo giro...")

    if inrace_input:
        lap_ctx = json.dumps(curr, indent=2, default=str)
        prev_ctx = json.dumps(prev, indent=2, default=str) if prev else "Nessun giro precedente (primo giro)."
        enriched = (
            f"Sto analizzando il GIRO {current_lap} della sessione di endurance a Vallelunga.\n\n"
            f"DATI GIRO CORRENTE (Lap {current_lap}):\n{lap_ctx}\n\n"
            f"DATI GIRO PRECEDENTE (Lap {current_lap - 1}):\n{prev_ctx}\n\n"
            f"DOMANDA DELL'INGEGNERE: {inrace_input}\n\n"
            f"Rispondi come AI Race Engineer analizzando i dati del giro, "
            f"evidenziando i cambiamenti rispetto al giro precedente e dando consigli operativi."
        )
        st.session_state.inrace_messages.append({"role": "user", "content": inrace_input})
        with st.chat_message("user", avatar="https://api.dicebear.com/9.x/initials/svg?seed=U"):
            st.markdown(inrace_input)
        with st.chat_message("assistant", avatar="https://api.dicebear.com/9.x/bottts/svg?seed=engineer"):
            with st.spinner("Analisi giro in corso..."):
                answer = call_server(enriched, "/query_telemetria")
            st.markdown(answer)
        st.session_state.inrace_messages.append({"role": "assistant", "content": answer})



# ═══════════════════════════════════════════════════════════════════════════
# POST-RACE ANALYZER — Telemetria Completa
# ═══════════════════════════════════════════════════════════════════════════
elif app_mode == "Post-Race Analyzer":
    # Show header banner
    st.markdown("""<div class="main-header"><div>
<h1>Post-Race Analyzer</h1>
<p class="subtitle">STV-E26 · Vallelunga Endurance Session · Analisi Completa</p>
</div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-desc">Analizza l\'<strong>intera sessione di gara</strong> con dashboard interattive. Attiva le <strong>chip</strong> (Gomme, Energia, Freni, Posizione) per visualizzare grafici dettagliati, oppure fai domande all\'AI Race Engineer per ottenere <strong>analisi strategiche</strong> e consigli di setup.</div>', unsafe_allow_html=True)

    CHIPS = {
        "gomme":     {"icon": "<img src='https://img.icons8.com/ios-filled/100/ffffff/tire.png' class='flaticon-icon'/>", "label": "Gomme",     "prompt": "Mostra lo stato delle gomme"},
        "energia":   {"icon": "<img src='https://img.icons8.com/ios-filled/100/ffffff/battery.png' class='flaticon-icon'/>",   "label": "Energia",   "prompt": "Mostra lo stato dell'energia"},
        "freni":     {"icon": "<img src='https://img.icons8.com/ios-filled/100/ffffff/abs.png' class='flaticon-icon'/>", "label": "Freni",     "prompt": "Mostra le temperature dei freni"},
        "posizione": {"icon": "<img src='https://img.icons8.com/ios-filled/100/ffffff/map-marker.png' class='flaticon-icon'/>", "label": "Posizione", "prompt": "Mostra la posizione in gara"},
    }
    for key in CHIPS:
        if f"chip_{key}" not in st.session_state:
            st.session_state[f"chip_{key}"] = False
    if "dashboard_answer" not in st.session_state:
        st.session_state.dashboard_answer = None
    if "dashboard_chart_config" not in st.session_state:
        st.session_state.dashboard_chart_config = None

    st.markdown("#### Chiedi al tuo Race Engineer")

    # Telemetry example questions
    TEL_EXAMPLES = [
        "Qual è lo stato attuale delle gomme?",
        "Quanta energia rimane nella batteria?",
        "Temperature freni negli ultimi 10 giri?",
        "Qual è la mia posizione in gara?",
        "Confronta usura gomme osservata vs attesa",
        "Consiglio strategia pit stop",
    ]
    ex_cols = st.columns(3)
    clicked_tel = None
    for i, q in enumerate(TEL_EXAMPLES):
        if ex_cols[i % 3].button(q, key=f"tel_{i}", use_container_width=True):
            clicked_tel = q

    st.markdown("---")

    # Chip row
    chip_cols = st.columns(len(CHIPS))
    for i, (key, info) in enumerate(CHIPS.items()):
        with chip_cols[i]:
            st.markdown(f"<div style='margin-bottom:-10px;'>{info['icon']} <b style='color:#c8c8e0;'>{info['label']}</b></div>", unsafe_allow_html=True)
            st.session_state[f"chip_{key}"] = st.toggle(
                "Attiva " + info['label'],
                value=st.session_state[f"chip_{key}"],
                key=f"toggle_{key}",
                label_visibility="collapsed")

    active_chips = [k for k in CHIPS if st.session_state.get(f"chip_{k}")]
    prompt = st.chat_input("Scrivi la tua domanda oppure attiva le chip qui sopra...")
    if clicked_tel:
        prompt = clicked_tel

    if prompt:
        if active_chips:
            auto_parts = [CHIPS[k]["prompt"] for k in active_chips]
            full_prompt = ". ".join(auto_parts) + ". " + prompt
            with st.spinner("L'AI sta preparando la dashboard..."):
                result = call_server_dashboard(full_prompt, active_chips)
            st.session_state.dashboard_answer = result["answer"]
            st.session_state.dashboard_chart_config = result["chart_config"]
        else:
            st.session_state.dashboard_answer = None
            st.session_state.dashboard_chart_config = None
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            with st.spinner("Analisi in corso..."):
                answer = call_server(prompt, "/query_telemetria")
            st.markdown(answer)
            st.markdown("</div>", unsafe_allow_html=True)

    # --- Plotly + metric helpers ---
    def _dark(fig, title=""):
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)",
                          title=dict(text=title, font=dict(size=14, color="#c8c8e0")),
                          margin=dict(l=40,r=20,t=40,b=30), height=300,
                          font=dict(family="Inter", color="#a0a0c0"),
                          legend=dict(font=dict(size=10)))
        fig.update_xaxes(gridcolor="rgba(255,255,255,.05)")
        fig.update_yaxes(gridcolor="rgba(255,255,255,.05)")

    def _metric(values, mtype):
        clean = [v for v in values if v is not None]
        if not clean: return None
        if mtype == "average": return sum(clean)/len(clean)
        if mtype == "max": return max(clean)
        if mtype == "min": return min(clean)

    CORNERS = ["front_left","front_right","rear_left","rear_right"]
    CLABELS = ["Ant. Sinistra","Ant. Destra","Post. Sinistra","Post. Destra"]

    # --- Render functions ---
    def render_gomme(cfg=None):
        sl,el = (cfg.get("start_lap",1),cfg.get("end_lap",50)) if cfg else (1,50)
        ms = cfg.get("metrics",[]) if cfg else []
        data = fetch_telemetry("get_lap_window",{"start_lap":sl,"end_lap":el,"fields":"tires.wear_pct,tires.temperature_c,tires.pressure_bar"})
        if "error" in data: st.error(data["error"]); return
        laps = data.get("laps",[]); ln = [l["lap"] for l in laps]
        colors = ["#6366f1","#a855f7","#ec4899","#f97316"]
        st.markdown(f'<div class="mini-card"><h3><img src="https://img.icons8.com/ios-filled/100/ffffff/tire.png" class="flaticon-icon"/> Gomme — Lap {sl}-{el}</h3></div>', unsafe_allow_html=True)
        if ms:
            mc = st.columns(4); ci=0
            for m in ms:
                dk = "tires.temperature_c" if "temp" in m.get("field","") else "tires.wear_pct" if "wear" in m.get("field","") else "tires.pressure_bar"
                u = "°C" if "temp" in m.get("field","") else "%" if "wear" in m.get("field","") else "bar"
                for c,lb in zip(CORNERS,CLABELS):
                    vs=[l.get(dk,{}).get(c) if isinstance(l.get(dk),dict) else None for l in laps]
                    r=_metric(vs,m.get("type","average"))
                    if r: mc[ci%4].metric(f"{m.get('label','')} {lb}",f"{r:.1f}{u}"); ci+=1
        for cf,tt in [("tires.wear_pct","Usura (%)"),("tires.temperature_c","Temp (°C)")]:
            fig=go.Figure()
            for c,lb,co in zip(CORNERS,CLABELS,colors):
                vs=[l.get(cf,{}).get(c) if isinstance(l.get(cf),dict) else None for l in laps]
                fig.add_trace(go.Scatter(x=ln,y=vs,name=lb,line=dict(color=co,width=2),mode="lines"))
                for m in ms:
                    if m.get("type")=="average" and (("temp" in m.get("field","") and "temp" in cf) or ("wear" in m.get("field","") and "wear" in cf)):
                        avg=_metric(vs,"average")
                        if avg: fig.add_hline(y=avg,line_dash="dash",line_color=co,annotation_text=f"Media {lb}: {avg:.1f}",annotation_font_size=9,opacity=.5)
            if "wear" in cf: fig.add_hline(y=80,line_dash="dot",line_color="rgba(239,68,68,.4)",annotation_text="Limite 80%")
            _dark(fig,f"{tt} — Lap {sl}-{el}"); st.plotly_chart(fig,use_container_width=True)

    def render_energia(cfg=None):
        sl,el = (cfg.get("start_lap",1),cfg.get("end_lap",50)) if cfg else (1,50)
        ms = cfg.get("metrics",[]) if cfg else []
        data = fetch_telemetry("get_lap_window",{"start_lap":sl,"end_lap":el,"fields":"energy_system"})
        if "error" in data: st.error(data["error"]); return
        laps = data.get("laps",[]); ln = [l["lap"] for l in laps]
        soc=[l.get("energy_system",{}).get("battery_state_of_charge_pct") if isinstance(l.get("energy_system"),dict) else None for l in laps]
        ers=[l.get("energy_system",{}).get("ers_deployment_kj") if isinstance(l.get("energy_system"),dict) else None for l in laps]
        kwh=[l.get("energy_system",{}).get("energy_remaining_kwh") if isinstance(l.get("energy_system"),dict) else None for l in laps]
        st.markdown(f'<div class="mini-card"><h3><img src="https://img.icons8.com/ios-filled/100/ffffff/battery.png" class="flaticon-icon"/> Energia — Lap {sl}-{el}</h3></div>', unsafe_allow_html=True)
        if ms:
            mc=st.columns(min(len(ms),4))
            for i,m in enumerate(ms):
                f=m.get("field",""); vs,u=(soc,"%") if "soc" in f or "charge" in f else (kwh," kWh") if "kwh" in f or "remain" in f else (ers," kJ") if "ers" in f else (soc,"%")
                r=_metric(vs,m.get("type","average"))
                if r: mc[i%len(mc)].metric(m.get("label",""),f"{r:.1f}{u}")
        else:
            if soc and soc[-1] is not None:
                m1,m2=st.columns(2)
                m1.metric("SoC",f"{soc[-1]:.1f}%",delta=f"{(soc[-1]-soc[-2]):.1f}%" if len(soc)>1 and soc[-2] else None)
                m2.metric("Rimanente",f"{kwh[-1]:.1f} kWh" if kwh and kwh[-1] else "N/A")
        fig=go.Figure(); fig.add_trace(go.Scatter(x=ln,y=soc,name="SoC %",fill="tozeroy",line=dict(color="#22d3ee",width=2),fillcolor="rgba(34,211,238,.15)"))
        _dark(fig,f"SoC (%) — Lap {sl}-{el}"); st.plotly_chart(fig,use_container_width=True)
        fig2=go.Figure(); fig2.add_trace(go.Bar(x=ln,y=ers,name="ERS kJ",marker_color="rgba(168,85,247,.7)"))
        _dark(fig2,f"ERS (kJ) — Lap {sl}-{el}"); st.plotly_chart(fig2,use_container_width=True)

    def render_freni(cfg=None):
        sl,el = (cfg.get("start_lap",1),cfg.get("end_lap",50)) if cfg else (1,50)
        ms = cfg.get("metrics",[]) if cfg else []
        data = fetch_telemetry("get_lap_window",{"start_lap":sl,"end_lap":el,"fields":"brake_temperatures_c"})
        if "error" in data: st.error(data["error"]); return
        laps = data.get("laps",[]); ln = [l["lap"] for l in laps]
        colors=["#ef4444","#f97316","#eab308","#84cc16"]
        st.markdown(f'<div class="mini-card"><h3><img src="https://img.icons8.com/ios-filled/100/ffffff/abs.png" class="flaticon-icon"/> Freni — Lap {sl}-{el}</h3></div>', unsafe_allow_html=True)
        if ms:
            mc=st.columns(4); ci=0
            for m in ms:
                for c,lb in zip(CORNERS,CLABELS):
                    vs=[l.get("brake_temperatures_c",{}).get(c) if isinstance(l.get("brake_temperatures_c"),dict) else None for l in laps]
                    r=_metric(vs,m.get("type","average"))
                    if r: mc[ci%4].metric(f"{m.get('label','')} {lb}",f"{r:.1f}°C"); ci+=1
        fig=go.Figure()
        for c,lb,co in zip(CORNERS,CLABELS,colors):
            vs=[l.get("brake_temperatures_c",{}).get(c) if isinstance(l.get("brake_temperatures_c"),dict) else None for l in laps]
            fig.add_trace(go.Scatter(x=ln,y=vs,name=lb,line=dict(color=co,width=2),mode="lines"))
            for m in ms:
                if m.get("type")=="average":
                    avg=_metric(vs,"average")
                    if avg: fig.add_hline(y=avg,line_dash="dash",line_color=co,annotation_text=f"Media {lb}: {avg:.1f}°C",annotation_font_size=9,opacity=.5)
        _dark(fig,f"Temp Freni (°C) — Lap {sl}-{el}"); st.plotly_chart(fig,use_container_width=True)

    def render_posizione(cfg=None):
        sl,el = (cfg.get("start_lap",1),cfg.get("end_lap",50)) if cfg else (1,50)
        ms = cfg.get("metrics",[]) if cfg else []
        data = fetch_telemetry("get_lap_window",{"start_lap":sl,"end_lap":el,"fields":"position,lap_time_s"})
        if "error" in data: st.error(data["error"]); return
        laps = data.get("laps",[]); ln = [l["lap"] for l in laps]
        pos=[l.get("position") for l in laps]; lt=[l.get("lap_time_s") for l in laps]
        st.markdown(f'<div class="mini-card"><h3><img src="https://img.icons8.com/ios-filled/100/ffffff/map-marker.png" class="flaticon-icon"/> Posizione — Lap {sl}-{el}</h3></div>', unsafe_allow_html=True)
        if ms:
            mc=st.columns(min(len(ms),4))
            for i,m in enumerate(ms):
                vs,u=(pos,"") if "position" in m.get("field","") else (lt,"s")
                r=_metric(vs,m.get("type","average"))
                if r: mc[i%len(mc)].metric(m.get("label",""),f"{r:.2f}{u}")
        else:
            if pos and pos[-1] is not None:
                m1,m2=st.columns(2); m1.metric("Posizione",f"P{pos[-1]}")
                best=min([t for t in lt if t],default=0); m2.metric("Best Lap",f"{best:.3f}s" if best else "N/A")
        fig=go.Figure(); fig.add_trace(go.Scatter(x=ln,y=pos,name="Pos",line=dict(color="#10b981",width=3),mode="lines+markers",marker=dict(size=5)))
        fig.update_yaxes(autorange="reversed"); _dark(fig,f"Posizione — Lap {sl}-{el}"); st.plotly_chart(fig,use_container_width=True)
        fig2=go.Figure(); fig2.add_trace(go.Scatter(x=ln,y=lt,name="Lap Time",line=dict(color="#f59e0b",width=2),mode="lines+markers",marker=dict(size=4)))
        _dark(fig2,f"Tempi Giro (s) — Lap {sl}-{el}"); st.plotly_chart(fig2,use_container_width=True)

    # --- Render dashboards ---
    RENDERERS = {"gomme":render_gomme,"energia":render_energia,"freni":render_freni,"posizione":render_posizione}

    if st.session_state.dashboard_answer:
        st.markdown("---")
        st.markdown(f'<div class="answer-box">{st.session_state.dashboard_answer}</div>', unsafe_allow_html=True)

    cfg = st.session_state.dashboard_chart_config
    if active_chips:
        st.markdown("---")
        cols = st.columns(len(active_chips))
        for i, ck in enumerate(active_chips):
            with cols[i]:
                if cfg:
                    # Backward compat: support both "category" (str) and "categories" (list)
                    cats = cfg.get("categories", [])
                    if not cats and cfg.get("category"):
                        cats = [cfg.get("category")]
                    # If this chip is in the categories list → full config (metrics + lap range)
                    if not cats or ck in cats:
                        RENDERERS[ck](cfg)
                    else:
                        # Apply start_lap/end_lap globally even if chip not in categories
                        RENDERERS[ck]({"start_lap": cfg.get("start_lap", 1),
                                       "end_lap": cfg.get("end_lap", 50)})
                else:
                    RENDERERS[ck](None)
    elif not prompt and not st.session_state.dashboard_answer:
        st.markdown("---")
        st.info("Attiva le chip qui sopra per visualizzare le dashboard, oppure scrivi una domanda.")
