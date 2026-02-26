import streamlit as st
import requests
import time
import json
import random
from bs4 import BeautifulSoup

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="NOVUS FLOW | The Singularity",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. SESSION STATE
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = st.secrets.get('GEMINI_API_KEY', '')

if 'leads_db' not in st.session_state:
    st.session_state['leads_db'] = []

# ==========================================
# 3. CINEMATIC CSS ENGINE
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #e2e8f0;
        background-color: #030712;
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #111827 0%, #000000 100%);
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .hero-container { 
        height: 80vh; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        position: relative;
        width: 100%;
    }
    
    .title-wrapper { 
        display: flex; 
        align-items: center; 
        justify-content: center;
        position: relative;
        z-index: 10;
        gap: 15px;
    }

    .thunder-svg-hero { 
        width: clamp(80px, 15vw, 150px);
        filter: drop-shadow(0 0 50px rgba(59, 130, 246, 0.8)); 
        z-index: 20;
        animation: thunderPulse 4s infinite ease-in-out;
    }

    .hero-text { 
        font-family: 'Syncopate', sans-serif; 
        font-weight: 700; 
        font-size: clamp(40px, 10vw, 110px); 
        color: #ffffff; 
        letter-spacing: -2px; 
        opacity: 0; 
        white-space: nowrap;
    }

    #text-left { animation: slideOutLeft 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }
    #text-right { animation: slideOutRight 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }

    @keyframes slideOutLeft { 
        0% { transform: translateX(50%) scale(0.5); opacity: 0; filter: blur(20px); } 
        100% { transform: translateX(0%) scale(1); opacity: 1; filter: blur(0px); margin-right: 20px; } 
    }
    @keyframes slideOutRight { 
        0% { transform: translateX(-50%) scale(0.5); opacity: 0; filter: blur(20px); } 
        100% { transform: translateX(0%) scale(1); opacity: 1; filter: blur(0px); margin-left: 20px; } 
    }

    @keyframes thunderPulse { 0% { transform: scale(1); } 50% { transform: scale(1.1); } 100% { transform: scale(1); } }

    .hero-subtitle-scroll { 
        font-family: 'Space Grotesk', monospace; 
        color: #94a3b8; 
        margin-top: 30px; 
        letter-spacing: 3px; 
        font-size: clamp(0.7rem, 2vw, 1rem); 
        animation: fadeIn 3s ease-in 2s forwards; 
        opacity: 0; 
    }

    .holo-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); }
    .portal-container { position: relative; width: 100%; max-width: 450px; margin: 50px auto; padding: 3px; background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 30px; }
    .portal-inner { background: #000; border-radius: 28px; padding: 50px; text-align: center; }

    @keyframes fadeIn { to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<svg style="width:0;height:0;position:absolute;"><defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" /><stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" /></linearGradient></defs></svg>', unsafe_allow_html=True)

# ==========================================
# 4. LOGIC ENGINE
# ==========================================

def run_ai_agent(prompt, api_key):
    # Updated to gemini-1.5-flash to fix the 404 error
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = { "contents": [{ "parts": [{"text": prompt}] }] }
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: {response.status_code}. Check your API Key."
    except Exception as e:
        return f"System Error: {str(e)}"

# ==========================================
# 5. DASHBOARD UI
# ==========================================
def show_main_app():
    # --- RESTORED HEADER WITH TERMINATE LINK ---
    c_title, c_log = st.columns([4, 1])
    with c_title:
        st.markdown("""
        <div style="display:flex; align-items:center;">
            <h2 style="font-family:Syncopate; margin:0; font-size:2rem;">NOVUS CORE</h2>
            <div style="color:#4ade80; margin-left:15px; border:1px solid #4ade80; padding:2px 10px; border-radius:10px; font-size:0.8rem;">● ONLINE</div>
        </div>
        """, unsafe_allow_html=True)
    with c_log:
        if st.button("TERMINATE LINK"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown("<hr style='border:1px solid #334155; margin-bottom:30px;'>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["[ SALES ]", "[ HR ]", "[ FINANCE ]"])

    with t1:
        st.subheader("TARGET ACQUISITION")
        url = st.text_input("Enter Company URL")
        if st.button("EXECUTE SCAN"):
            with st.spinner("NEURAL AGENT DEPLOYED..."):
                res = run_ai_agent(f"Analyze this company {url} and write a cold email.", st.session_state['api_key'])
                st.write(res)

    with t2:
        st.subheader("BIOMETRIC RESUME PARSING")
        if st.button("EXECUTE NEURAL EVALUATION"):
            with st.spinner("ANALYZING..."):
                res = run_ai_agent("Analyze the uploaded resume.", st.session_state['api_key'])
                st.write(res)

    with t3:
        st.metric("REVENUE", "$482,000", "+14%")

# ==========================================
# 6. LANDING PAGE
# ==========================================
def show_landing_page():
    st.markdown(f"""
    <div class="hero-container">
        <div class="title-wrapper">
            <div id="text-left" class="hero-text">NOVUS</div>
            <svg class="thunder-svg-hero" viewBox="0 0 24 24" fill="url(#grad1)" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/>
            </svg>
            <div id="text-right" class="hero-text">FLOW</div>
        </div>
        <div class="hero-subtitle-scroll">SCROLL TO INITIALIZE NEURAL LINK</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 4])
    with c2:
        st.markdown("""<div style="padding: 100px 0; font-size: 1.5rem; color: #94a3b8;">WE DO NOT BUILD TOOLS.<br>WE BUILD <span style="color:#3b82f6;">AGENCY.</span><br><br>Traditional software waits for input. Novus Flow anticipates intent.</div>""", unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a: st.markdown("""<div class="holo-card"><h3 style="color:#60a5fa;">01 // SALES</h3><p>Autonomous Outreach.</p></div>""", unsafe_allow_html=True)
    with col_b: st.markdown("""<div class="holo-card"><h3 style="color:#a78bfa;">02 // TALENT</h3><p>Neural Matching.</p></div>""", unsafe_allow_html=True)
    with col_c: st.markdown("""<div class="holo-card"><h3 style="color:#f472b6;">03 // RISK</h3><p>Sentinel Mode.</p></div>""", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    _, c_center, _ = st.columns([1, 1, 1])
    with c_center:
        st.markdown('<div class="portal-container"><div class="portal-inner">', unsafe_allow_html=True)
        password = st.text_input("ENCRYPTION KEY", type="password", placeholder="ENTER KEY")
        if st.button("CONNECT"):
            if password == "aditya123":
                st.session_state['logged_in'] = True
                st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

if st.session_state['logged_in']:
    show_main_app()
else:
    show_landing_page()
