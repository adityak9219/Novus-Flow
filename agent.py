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
    st.session_state['api_key'] = ''
# Check for Secret Key in Cloud
if 'GEMINI_API_KEY' in st.secrets:
    st.session_state['api_key'] = st.secrets['GEMINI_API_KEY']

if 'leads_db' not in st.session_state:
    st.session_state['leads_db'] = []
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 3. CINEMATIC CSS ENGINE
# ==========================================
st.markdown("""
<style>
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
    
    /* NEBULA BACKGROUND */
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
    @keyframes nebulaMove { 0% { transform: rotate(0deg) scale(1); } 100% { transform: rotate(5deg) scale(1.1); } }

    /* HERO ANIMATIONS */
    .hero-container { min-height: 70vh; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; z-index: 10; }
    
    /* THE THUNDERBOLT LOGO */
    .thunder-main { 
        font-size: 80px; 
        filter: drop-shadow(0 0 30px #00d4ff); 
        animation: pulseBolt 2s infinite ease-in-out;
        margin-bottom: 20px;
        cursor: pointer;
    }
    @keyframes pulseBolt { 0% { transform: scale(1); filter: drop-shadow(0 0 20px #00d4ff); } 50% { transform: scale(1.1); filter: drop-shadow(0 0 50px #ffffff); } 100% { transform: scale(1); filter: drop-shadow(0 0 20px #00d4ff); } }

    /* TEXT STYLES */
    .hero-text { font-family: 'Syncopate', sans-serif; font-weight: 700; font-size: 5rem; color: #ffffff; letter-spacing: -5px; text-shadow: 0 0 30px rgba(255, 255, 255, 0.2); line-height: 1; }
    .hero-sub { color: #94a3b8; font-size: 1.2rem; letter-spacing: 5px; margin-top: 20px; text-transform: uppercase; }

    /* CARDS (RESTORED) */
    .card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; width: 80%; margin: 50px auto; z-index: 20; position: relative; }
    .holo-card { 
        background: rgba(255, 255, 255, 0.03); 
        border: 1px solid rgba(255, 255, 255, 0.1); 
        padding: 30px; 
        border-radius: 15px; 
        backdrop-filter: blur(10px); 
        text-align: center;
        transition: all 0.3s ease; 
    }
    .holo-card:hover { transform: translateY(-10px); border-color: #00d4ff; box-shadow: 0 0 30px rgba(0, 212, 255, 0.1); }
    .holo-card h3 { font-family: 'Syncopate'; font-size: 1.2rem; margin-bottom: 10px; }
    .holo-card p { color: #94a3b8; font-size: 0.9rem; }

    /* LOGIN PORTAL */
    .portal-container { max-width: 400px; margin: 40px auto; padding: 2px; background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 30px; }
    .portal-inner { background: #000; border-radius: 28px; padding: 30px; text-align: center; }

    /* UI OVERRIDES */
    .stTextInput input { background: #111827 !important; border: 1px solid #334155 !important; color: white !important; text-align: center; }
    .stButton button { background: white; color: black; font-weight: 700; border-radius: 50px; height: 50px; border: none; width: 100%; font-family: 'Syncopate'; }
    .stButton button:hover { box-shadow: 0 0 20px white; transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. LOGIC (SELF HEALING BRAIN)
# ==========================================
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
        return f"Error: Status Code {response.status_code}"
    except Exception as e: return f"Connection Error: {str(e)}"

def find_working_model(api_key):
    """Auto-detects available Google Model."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for model in data.get('models', []):
                if 'generateContent' in model.get('supportedGenerationMethods', []):
                    return model['name'].replace('models/', '')
    except: pass
    return "gemini-pro"

def ask_ai(prompt, api_key):
    if not api_key: return "⚠️ I am offline. Please connect API Key."
    api_key = api_key.strip()
    model_name = find_working_model(api_key)
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = { "contents": [{ "parts": [{"text": prompt}] }] }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"System Error: {str(e)}"

# ==========================================
# 5. DASHBOARD UI
# ==========================================
def show_main_app():
    c_title, c_log = st.columns([4, 1])
    with c_title:
        st.markdown("""<div style="display:flex;align-items:center;"><h2 style="font-family:Syncopate;margin:0;">NOVUS CORE</h2><span style="color:#4ade80;margin-left:15px;border:1px solid #4ade80;padding:2px 8px;border-radius:10px;font-size:0.7rem;">● ONLINE</span></div>""", unsafe_allow_html=True)
    with c_log:
        if st.button("DISCONNECT"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown("<hr style='border:1px solid #334155; margin-bottom:20px;'>", unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["[ SALES ]", "[ HR ]", "[ FINANCE ]", "[ NOVUS AI ]"])

    with t1:
        st.subheader("TARGET ACQUISITION")
        url = st.text_input("URL TARGET", placeholder="https://")
        if st.button("EXECUTE SCAN"):
            with st.spinner("NEURAL AGENT DEPLOYED..."):
                data = scrape_website(url)
                final_prompt = f"Analyze website: '{data[:2000]}'. Act as sales expert. Write cold email pitching AI services. <150 words."
                res = ask_ai(final_prompt, st.session_state['api_key'])
                st.session_state['current_result'] = res
                st.session_state['current_url'] = url
                st.markdown(f"""<div style="background:rgba(255,255,255,0.05);padding:20px;border-radius:10px;">{res}</div>""", unsafe_allow_html=True)
        if 'current_result' in st.session_state:
            if st.button("💾 SAVE LEAD"):
                st.session_state['leads_db'].append({"Company": st.session_state['current_url'], "Status": "Ready", "Timestamp": time.strftime("%H:%M")})
                st.success("SAVED")
        if len(st.session_state['leads_db']) > 0:
            st.dataframe(st.session_state['leads_db'], use_container_width=True)

    with t2:
        st.subheader("BIOMETRIC PARSING (SIMULATION)")
        st.file_uploader("UPLOAD RESUME")
    
    with t3:
        st.subheader("GLOBAL LEDGER (SIMULATION)")
        st.metric("REVENUE", "$482K", "+14%")

    with t4:
        st.subheader("NOVUS NEURAL INTERFACE")
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
        if prompt := st.chat_input("Query Novus AI..."):
            with st.chat_message("user"): st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                resp = ask_ai(prompt, st.session_state['api_key'])
                st.markdown(resp)
            st.session_state.messages.append({"role": "assistant", "content": resp})

# ==========================================
# 6. LANDING PAGE (RESTORED & UPGRADED)
# ==========================================
def show_landing_page():
    # 1. HERO SECTION WITH THUNDERBOLT
    st.markdown("""
    <div class="hero-container">
        <div class="thunder-main">⚡</div>
        <div class="hero-text">NOVUS FLOW</div>
        <div class="hero-sub">THE SINGULARITY IS HERE</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. RESTORED CARDS (SALES, TALENT, RISK) + NEW AI CARD
    st.markdown("""
    <div class="card-grid">
        <div class="holo-card">
            <h3 style="color:#60a5fa;">SALES</h3>
            <p>Autonomous Outreach Agent.</p>
        </div>
        <div class="holo-card">
            <h3 style="color:#a78bfa;">TALENT</h3>
            <p>Neural Candidate Matching.</p>
        </div>
        <div class="holo-card">
            <h3 style="color:#f472b6;">NOVUS AI</h3>
            <p>Direct Neural Link.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. LOGIN PORTAL
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown('<div class="portal-container"><div class="portal-inner">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-family:Syncopate; letter-spacing:2px; margin-bottom:15px; color:white;">ESTABLISH LINK</h3>', unsafe_allow_html=True)
        password = st.text_input("ACCESS KEY", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        st.write("")
        if st.button("CONNECT SYSTEM"):
            if password == "aditya123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown("<br><div style='text-align:center; color:#334155; padding-bottom:50px;'>NOVUS TECHNOLOGIES © 2026</div>", unsafe_allow_html=True)

# ==========================================
# 7. EXECUTION
# ==========================================
if st.session_state['logged_in']:
    show_main_app()
else:
    show_landing_page()
