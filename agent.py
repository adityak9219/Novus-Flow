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

# ==========================================
# 3. CINEMATIC CSS ENGINE (SMART RESPONSIVE FIX)
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
    
    /* HIDE STREAMLIT UI */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* HERO CONTAINER - FORCED CENTERING */
    .hero-container { 
        height: 80vh; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        text-align: center;
        width: 100%;
        margin: 0 auto;
    }
    
    .title-wrapper { 
        display: flex; 
        align-items: center; 
        justify-content: center;
        gap: 20px; 
        width: 100%;
        position: relative;
    }
    
    .thunder-svg-hero { 
        width: clamp(60px, 10vw, 100px);
        filter: drop-shadow(0 0 50px rgba(59, 130, 246, 0.8)); 
        animation: thunderPulse 4s infinite ease-in-out;
    }
    
    .hero-text { 
        font-family: 'Syncopate', sans-serif; 
        font-weight: 700; 
        font-size: clamp(40px, 8vw, 110px); 
        color: #ffffff; 
        letter-spacing: -2px; 
        opacity: 0; 
        white-space: nowrap; 
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.2); 
    }
    
    #text-left { animation: slideInLeft 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }
    #text-right { animation: slideInRight 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }
    
    @keyframes slideInLeft { 
        0% { transform: translateX(30px); opacity: 0; filter: blur(10px); } 
        100% { transform: translateX(0); opacity: 1; filter: blur(0px); } 
    }
    @keyframes slideInRight { 
        0% { transform: translateX(-30px); opacity: 0; filter: blur(10px); } 
        100% { transform: translateX(0); opacity: 1; filter: blur(0px); } 
    }
    
    @keyframes thunderPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.15); } }
    
    .hero-subtitle-scroll { 
        font-family: 'Space Grotesk', monospace; 
        color: #94a3b8; 
        margin-top: 40px; 
        letter-spacing: 5px; 
        font-size: clamp(0.7rem, 1.5vw, 0.9rem); 
        animation: fadeIn 3s ease-in 2s forwards; 
        opacity: 0; 
    }

    /* Portal & Card Styles */
    .holo-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); transition: all 0.5s ease; }
    .holo-card:hover { transform: translateY(-10px); border-color: #3b82f6; background: rgba(255, 255, 255, 0.07); }
    
    .portal-container { width: 100%; max-width: 400px; margin: 50px auto; padding: 2px; background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 20px; }
    .portal-inner { background: #000; border-radius: 18px; padding: 40px; text-align: center; }

    @keyframes fadeIn { to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<svg style="width:0;height:0;position:absolute;"><defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" /><stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" /></linearGradient></defs></svg>', unsafe_allow_html=True)

# ==========================================
# 4. LOGIC ENGINE
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
        return f"Error: {response.status_code}"
    except Exception as e: return f"Error: {str(e)}"

def find_working_model(api_key):
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

def run_ai_agent_universal(content, api_key):
    if not api_key: return "⚠️ API KEY MISSING"
    model_name = find_working_model(api_key)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    prompt = f"Analyze: '{content[:2000]}'. Write a professional cold email for AI automation services under 150 words."
    payload = { "contents": [{ "parts": [{"text": prompt}] }] }
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=payload)
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except: return "⚠️ ENGINE ERROR"

# ==========================================
# 5. DASHBOARD UI
# ==========================================
def show_main_app():
    c_title, c_log = st.columns([4, 1])
    with c_title:
        st.markdown('<div style="display:flex; align-items:center;"><h2 style="font-family:Syncopate; margin:0;">NOVUS CORE</h2><div style="color:#4ade80; margin-left:15px; border:1px solid #4ade80; padding:2px 10px; border-radius:10px; font-size:0.8rem;">● ONLINE</div></div>', unsafe_allow_html=True)
    with c_log:
        if st.button("TERMINATE LINK"):
            st.session_state['logged_in'] = False
            st.rerun()

    st.markdown("<hr style='border:1px solid #334155; margin-bottom:30px;'>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["[ SALES ]", "[ HR ]", "[ FINANCE ]"])

    with t1:
        url = st.text_input("URL TARGET", placeholder="https://")
        if st.button("EXECUTE SCAN"):
            with st.spinner("SCANNING..."):
                res = run_ai_agent_universal(scrape_website(url), st.session_state['api_key'])
                st.session_state['current_result'] = res
                st.markdown(f'<div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:10px;">{res}</div>', unsafe_allow_html=True)

    with t2: st.info("HR Module Ready")
    with t3: st.info("Finance Module Ready")

# ==========================================
# 6. LANDING PAGE (CENTRAL LOGO FIX)
# ==========================================
def show_landing_page():
    # Centered Logo and Text
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

    # Feature Cards
    col_a, col_b, col_c = st.columns(3)
    with col_a: st.markdown('<div class="holo-card"><h3>01 // SALES</h3><p>Autonomous Outreach.</p></div>', unsafe_allow_html=True)
    with col_b: st.markdown('<div class="holo-card"><h3>02 // TALENT</h3><p>Neural Matching.</p></div>', unsafe_allow_html=True)
    with col_c: st.markdown('<div class="holo-card"><h3>03 // RISK</h3><p>Sentinel Mode.</p></div>', unsafe_allow_html=True)

    # Portal Login
    st.markdown('<br><br>', unsafe_allow_html=True)
    _, c_center, _ = st.columns([1, 1, 1])
    with c_center:
        st.markdown('<div class="portal-container"><div class="portal-inner">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-family:Syncopate; margin-bottom:20px;">ESTABLISH LINK</h3>', unsafe_allow_html=True)
        password = st.text_input("KEY", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        if st.button("CONNECT"):
            if password == "aditya123":
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("DENIED")
        st.markdown('</div></div>', unsafe_allow_html=True)

# ==========================================
# 7. EXECUTION
# ==========================================
if st.session_state['logged_in']:
    show_main_app()
else:
    show_landing_page()
