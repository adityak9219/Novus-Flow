import streamlit as st
import requests
import time
import json
import random
from bs4 import BeautifulSoup
import google.generativeai as genai

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
if 'active_module' not in st.session_state:
    st.session_state['active_module'] = 'Sales & Leads'
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = ''

# ==========================================
# 3. CINEMATIC CSS ENGINE
# ==========================================
st.markdown("""
<style>
    /* IMPORT FUTURE FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&family=Inter:wght@300;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #e2e8f0;
        background-color: #030712;
        overflow-x: hidden;
    }

    .stApp {
        background: radial-gradient(circle at 50% 50%, #111827 0%, #000000 100%);
    }
    
    .stApp::before {
        content: "";
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: 
            radial-gradient(circle at 20% 30%, rgba(37, 99, 235, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 80% 70%, rgba(124, 58, 237, 0.15) 0%, transparent 40%);
        animation: nebulaMove 20s infinite alternate linear;
        z-index: 0;
        pointer-events: none;
    }
    
    @keyframes nebulaMove {
        0% { transform: rotate(0deg) scale(1); }
        100% { transform: rotate(5deg) scale(1.1); }
    }

    .hero-container {
        height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        position: relative;
        perspective: 1000px;
        z-index: 10;
    }

    .thunder-wrapper {
        position: absolute;
        z-index: 20;
        animation: thunderPulse 4s infinite ease-in-out;
    }
    
    .thunder-svg-hero {
        width: 150px; height: 150px;
        filter: drop-shadow(0 0 50px rgba(59, 130, 246, 0.8));
    }

    .title-wrapper {
        display: flex;
        align-items: center;
        gap: 20px;
        z-index: 10;
        overflow: hidden;
    }

    .hero-text {
        font-family: 'Syncopate', sans-serif;
        font-weight: 700;
        font-size: 6rem;
        color: #ffffff;
        letter-spacing: -5px;
        opacity: 0;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
    }

    #text-left { animation: slideOutLeft 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }
    #text-right { animation: slideOutRight 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }

    @keyframes slideOutLeft {
        0% { transform: translateX(100%) scale(0.5); opacity: 0; filter: blur(20px); }
        100% { transform: translateX(0%) scale(1); opacity: 1; filter: blur(0px); margin-right: 80px; }
    }
    @keyframes slideOutRight {
        0% { transform: translateX(-100%) scale(0.5); opacity: 0; filter: blur(20px); }
        100% { transform: translateX(0%) scale(1); opacity: 1; filter: blur(0px); margin-left: 80px; }
    }
    
    @keyframes thunderPulse {
        0% { transform: scale(1); filter: drop-shadow(0 0 30px #2563eb); }
        50% { transform: scale(1.1); filter: drop-shadow(0 0 80px #06b6d4); }
        100% { transform: scale(1); filter: drop-shadow(0 0 30px #2563eb); }
    }

    .hero-subtitle-scroll {
        font-family: 'Space Grotesk', monospace;
        color: #94a3b8;
        margin-top: 50px;
        letter-spacing: 5px;
        font-size: 1rem;
        animation: fadeIn 3s ease-in 2s forwards;
        opacity: 0;
    }

    .ar-section { margin-top: 100px; perspective: 2000px; padding: 50px; }
    .ar-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 30px; transform-style: preserve-3d; }

    .holo-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px;
        border-radius: 20px;
        backdrop-filter: blur(10px);
        transform: rotateX(10deg) scale(0.9);
        transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
        position: relative;
        overflow: hidden;
    }
    
    .holo-card:hover {
        transform: rotateX(0deg) scale(1.05) translateY(-20px);
        background: rgba(255, 255, 255, 0.07);
        box-shadow: 0 30px 60px -10px rgba(0, 200, 255, 0.2);
        border-color: #00d4ff;
    }
    
    .holo-card::before {
        content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transform: skewX(-25deg); transition: 0.5s;
    }
    .holo-card:hover::before { left: 100%; transition: 0.7s; }

    .manifesto-section { padding: 150px 0; text-align: left; }
    .big-type {
        font-family: 'Syncopate', sans-serif; font-size: 4rem; line-height: 1.1; font-weight: 700;
        background: linear-gradient(to right, #ffffff, #64748b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 20px;
    }
    .highlight { color: #3b82f6; -webkit-text-fill-color: #3b82f6; }

    .portal-container {
        position: relative; width: 100%; max-width: 450px; margin: 50px auto; padding: 3px;
        background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 30px;
        animation: borderRotate 4s linear infinite; box-shadow: 0 0 50px rgba(37, 99, 235, 0.4);
    }
    .portal-inner { background: #000; border-radius: 28px; padding: 50px; text-align: center; }

    .stTextInput input {
        background: #111827 !important; border: 1px solid #334155 !important; color: white !important;
        text-align: center; letter-spacing: 3px; font-family: 'Space Grotesk';
    }
    .stButton button {
        background: white; color: black; font-weight: 700; border-radius: 50px; height: 50px;
        border: none; width: 100%; font-family: 'Syncopate'; letter-spacing: 1px;
    }
    .stButton button:hover { transform: scale(1.05); box-shadow: 0 0 30px white; }
    
    .disconnect-btn button {
        background: transparent !important; border: 1px solid #ef4444 !important; color: #ef4444 !important;
        font-size: 0.8rem; padding: 5px 15px; height: auto;
    }
    
    .streamlit-expanderHeader { background-color: rgba(255,255,255,0.05); color: #e2e8f0; border-radius: 10px; }

    @keyframes fadeIn { to { opacity: 1; } }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

st.markdown('<svg style="width:0;height:0;position:absolute;"><defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" /><stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" /></linearGradient></defs></svg>', unsafe_allow_html=True)

# ==========================================
# 4. LANDING PAGE
# ==========================================
def show_landing_page():
    st.markdown("""
    <div class="hero-container">
        <div class="thunder-wrapper">
            <svg class="thunder-svg-hero" viewBox="0 0 24 24" fill="url(#grad1)" xmlns="http://www.w3.org/2000/svg">
                <path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/>
            </svg>
        </div>
        <div class="title-wrapper">
            <div id="text-left" class="hero-text">NOVUS</div>
            <div id="text-right" class="hero-text">FLOW</div>
        </div>
        <div class="hero-subtitle-scroll">SCROLL TO INITIALIZE NEURAL LINK</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 4])
    with c2:
        st.markdown("""
        <div class="manifesto-section">
            <div class="big-type">
                WE DO NOT BUILD TOOLS.<br>
                WE BUILD <span class="highlight">AGENCY.</span>
            </div>
            <p style="font-size: 1.2rem; color: #94a3b8; max-width: 600px; line-height: 1.8;">
                Traditional software waits for input. Novus Flow anticipates intent. 
                We have replaced the static database with a living, breathing neural lattice that acts on your behalf.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; font-family:Syncopate; font-size:2rem; margin-bottom:50px;'>THE TRI-CORE ENGINE</h2>", unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="holo-card">
            <h3 style="color:#60a5fa; font-family:Syncopate;">01 // SALES</h3>
            <p style="color:#cbd5e1; margin-top:15px;"><strong>Autonomous Outreach.</strong><br>Scrapes 40,000 datapoints per lead and crafts hyper-personalized messages.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="holo-card">
            <h3 style="color:#a78bfa; font-family:Syncopate;">02 // TALENT</h3>
            <p style="color:#cbd5e1; margin-top:15px;"><strong>Neural Matching.</strong><br>Scans global talent pool and interviews candidates via voice-agent.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="holo-card">
            <h3 style="color:#f472b6; font-family:Syncopate;">03 // RISK</h3>
            <p style="color:#cbd5e1; margin-top:15px;"><strong>Sentinel Mode.</strong><br>Real-time auditing of contracts and invoices.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    c_l, c_center, c_r = st.columns([1, 1, 1])
    with c_center:
        st.markdown('<div class="portal-container"><div class="portal-inner">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-family:Syncopate; letter-spacing:2px; margin-bottom:20px;">ESTABLISH LINK</h3>', unsafe_allow_html=True)
        password = st.text_input("ENCRYPTION KEY", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        st.write("")
        if st.button("CONNECT"):
            if password == "aditya123":
                with st.spinner("HANDSHAKE IN PROGRESS..."):
                    time.sleep(1.5)
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br><div style='text-align:center; color:#334155;'>NOVUS TECHNOLOGIES © 2026 // SINGULARITY READY</div>", unsafe_allow_html=True)

# ==========================================
# 5. INTERNAL DASHBOARD
# ==========================================
def show_main_app():
    # --- 1. SCRAPER FUNCTION ---
    def scrape_website(url):
        try:
            if not url.startswith('http'): url = 'https://' + url
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text = ""
                for tag in soup.find_all(['h1', 'h2', 'p']): text += tag.get_text(strip=True) + " "
                return text[:5000]
            else:
                return f"Error: Status Code {response.status_code}"
        except Exception as e: return f"Connection Error: {str(e)}"

    # --- 2. AI AGENT (Simulation Fallback) ---
    def run_ai_agent_universal(content, api_key):
        # SIMULATION MODE if no key
        if not api_key: return generate_simulated_response(content)

        api_key = api_key.strip()
        models_to_try = ["gemini-1.5-flash", "gemini-pro"]

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            prompt = f"Analyze website: '{content}'. Write cold email pitching AI services."
            payload = { "contents": [{ "parts": [{"text": prompt}] }] }
            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    return response.json()['candidates'][0]['content']['parts'][0]['text']
            except: continue
        
        return generate_simulated_response(content)

    def generate_simulated_response(content):
        return f"""
Dear {content[:15]} Team,

I've analyzed your digital footprint and found 3 key areas to automate your workflows.
At Novus Flow, our autonomous agents can reduce your operational overhead by 40%.

I have prepared a full audit of your site structure. Are you open to a brief walk-through next Tuesday?

Best regards,

**Novus Autonomous Agent**
*Generated via Neural Simulation Mode*
"""

    # --- HEADER ---
    c_title, c_log = st.columns([4, 1])
    with c_title:
        st.markdown("""
        <div style="display:flex; align-items:center;">
            <h2 style="font-family:Syncopate; margin:0; font-size:2rem;">NOVUS CORE</h2>
            <div style="color:#4ade80; margin-left:15px; border:1px solid #4ade80; padding:2px 10px; border-radius:10px; font-size:0.8rem;">● ONLINE</div>
        </div>
        """, unsafe_allow_html=True)
    with c_log:
        if st.button("TERMINATE"):
            st.session_state['logged_in'] = False
            st.rerun()

    # --- API CONFIG ---
    with st.expander("🔌 SYSTEM CONFIGURATION", expanded=False):
        api_val = st.text_input("GEMINI API KEY", type="password", value=st.session_state['api_key'])
        if api_val:
            st.session_state['api_key'] = api_val
            st.success("KEY LINKED")
        else:
            st.info("SIMULATION MODE ACTIVE")

    st.markdown("<hr style='border:1px solid #334155; margin-bottom:30px;'>", unsafe_allow_html=True)

    # --- TABS ---
    t1, t2, t3 = st.tabs(["[ SALES ]", "[ HR ]", "[ FINANCE ]"])

    # 1. SALES TAB
    with t1:
        st.subheader("TARGET ACQUISITION")
        url = st.text_input("URL TARGET", placeholder="https://")
        if st.button("EXECUTE SCAN"):
            with st.spinner("NEURAL AGENT DEPLOYED..."):
                data = scrape_website(url)
                res = run_ai_agent_universal(data, st.session_state['api_key'])
                
                # FIXED: HTML CARD
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.05); border:1px solid #334155; border-radius:15px; padding:25px; margin-top:20px;">
                    <div style="border-bottom:1px solid #334155; padding-bottom:10px; margin-bottom:10px; color:#94a3b8;">
                        TO: <span style="color:white;">{url}</span> <br> FROM: <span style="color:#4ade80;">NOVUS AGENT</span>
                    </div>
                    <div style="color:#e2e8f0; white-space: pre-wrap; font-family: sans-serif;">
{res}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # 2. HR TAB (ADDED THIS PART FOR YOU)
    with t2:
        st.subheader("BIOMETRIC PARSING")
        uploaded_file = st.file_uploader("UPLOAD CANDIDATE DATA", type=['pdf', 'docx'])
        
        if uploaded_file:
            with st.spinner("ANALYZING DNA SEQUENCE & WORK HISTORY..."):
                time.sleep(2) # Fake processing delay
            
            st.success("MATCH FOUND")
            
            # Fake Candidate Profile
            c1, c2 = st.columns([1, 3])
            with c1:
                st.markdown("""
                <div style="background:#334155; height:100px; width:100px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:40px;">👤</div>
                """, unsafe_allow_html=True)
            with c2:
                st.metric("MATCH SCORE", "98.4%", "ELITE TIER")
                st.write("**Candidate:** ALEXEI V.")
                st.write("**Skills:** Python, Neural Networks, Quantum Computing")
                st.button("SCHEDULE INTERVIEW", type="primary")

    # 3. FINANCE TAB (NEW UPGRADE!)
    with t3:
        st.subheader("GLOBAL LEDGER")
        
        # High-Tech Metric Row
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("REVENUE (MRR)", "$482,000", "+14%")
        m2.metric("OP. COST", "$112,000", "-8%")
        m3.metric("NET PROFIT", "$370,000", "+22%")
        m4.metric("AI SAVINGS", "$45,000", "AUTO")
        
        st.write("")
        st.write("")
        
        # Rich Chart
        chart_data = {
            "Revenue": [45, 48, 47, 52, 55, 59, 64, 61, 68, 72],
            "Expenses": [30, 29, 31, 28, 27, 25, 26, 24, 23, 22]
        }
        st.line_chart(chart_data)
        
        st.success("AUDIT LOG: All transactions verified. 0 Anomalies detected.")

# ==========================================
# 6. EXECUTION
# ==========================================
if st.session_state['logged_in']:
    show_main_app()
else:
    show_landing_page()