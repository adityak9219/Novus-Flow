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
# 2. SESSION STATE & DATABASE
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

# Initialize Chat History for the Assistant
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
    
    @keyframes nebulaMove {
        0% { transform: rotate(0deg) scale(1); }
        100% { transform: rotate(5deg) scale(1.1); }
    }

    /* HERO ANIMATIONS */
    .hero-container { height: 80vh; display: flex; flex-direction: column; justify-content: center; align-items: center; position: relative; perspective: 1000px; z-index: 10; }
    .thunder-wrapper { position: absolute; z-index: 20; animation: thunderPulse 4s infinite ease-in-out; }
    .thunder-svg-hero { width: 150px; height: 150px; filter: drop-shadow(0 0 50px rgba(59, 130, 246, 0.8)); }
    .title-wrapper { display: flex; align-items: center; gap: 20px; z-index: 10; overflow: hidden; }
    
    .hero-text { font-family: 'Syncopate', sans-serif; font-weight: 700; font-size: 6rem; color: #ffffff; letter-spacing: -5px; opacity: 0; text-shadow: 0 0 30px rgba(255, 255, 255, 0.2); }
    
    #text-left { animation: slideOutLeft 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }
    #text-right { animation: slideOutRight 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; }
    
    @keyframes slideOutLeft { 0% { transform: translateX(100%) scale(0.5); opacity: 0; filter: blur(20px); } 100% { transform: translateX(0%) scale(1); opacity: 1; filter: blur(0px); margin-right: 80px; } }
    @keyframes slideOutRight { 0% { transform: translateX(-100%) scale(0.5); opacity: 0; filter: blur(20px); } 100% { transform: translateX(0%) scale(1); opacity: 1; filter: blur(0px); margin-left: 80px; } }
    @keyframes thunderPulse { 0% { transform: scale(1); filter: drop-shadow(0 0 30px #2563eb); } 50% { transform: scale(1.1); filter: drop-shadow(0 0 80px #06b6d4); } 100% { transform: scale(1); filter: drop-shadow(0 0 30px #2563eb); } }
    
    .hero-subtitle-scroll { font-family: 'Space Grotesk', monospace; color: #94a3b8; margin-top: 50px; letter-spacing: 5px; font-size: 1rem; animation: fadeIn 3s ease-in 2s forwards; opacity: 0; }

    /* CARDS */
    .holo-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); transform: rotateX(10deg) scale(0.9); transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1); position: relative; overflow: hidden; }
    .holo-card:hover { transform: rotateX(0deg) scale(1.05) translateY(-20px); background: rgba(255, 255, 255, 0.07); box-shadow: 0 30px 60px -10px rgba(0, 200, 255, 0.2); border-color: #00d4ff; }
    
    /* LOGIN PORTAL */
    .portal-container { position: relative; width: 100%; max-width: 450px; margin: 50px auto; padding: 3px; background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 30px; animation: borderRotate 4s linear infinite; box-shadow: 0 0 50px rgba(37, 99, 235, 0.4); }
    .portal-inner { background: #000; border-radius: 28px; padding: 50px; text-align: center; }

    /* UI ELEMENTS */
    .stTextInput input { background: #111827 !important; border: 1px solid #334155 !important; color: white !important; text-align: center; letter-spacing: 3px; font-family: 'Space Grotesk'; }
    .stButton button { background: white; color: black; font-weight: 700; border-radius: 50px; height: 50px; border: none; width: 100%; font-family: 'Syncopate'; letter-spacing: 1px; }
    .stButton button:hover { transform: scale(1.05); box-shadow: 0 0 30px white; }
    
    @keyframes fadeIn { to { opacity: 1; } }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
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
        return f"Error: Status Code {response.status_code}"
    except Exception as e: return f"Connection Error: {str(e)}"

# --- AUTO-FIND WORKING MODEL ---
def find_working_model(api_key):
    """Asks Google which models are available and picks the first valid one."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for model in data.get('models', []):
                if 'generateContent' in model.get('supportedGenerationMethods', []):
                    return model['name'].replace('models/', '')
    except:
        pass
    return "gemini-pro"

# --- UNIVERSAL AI CALL ---
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

    if st.session_state['api_key'] and len(st.session_state['api_key']) > 10:
         st.success("SYSTEM ONLINE: NEURAL LINK ESTABLISHED")
    else:
         st.warning("⚠️ SYSTEM OFFLINE: CHECK API KEY")

    st.markdown("<hr style='border:1px solid #334155; margin-bottom:30px;'>", unsafe_allow_html=True)

    # --- TABS (NOW 4 TABS) ---
    t1, t2, t3, t4 = st.tabs(["[ SALES ]", "[ HR ]", "[ FINANCE ]", "[ NOVUS AI ]"])

    # 1. SALES TAB
    with t1:
        st.subheader("TARGET ACQUISITION")
        url = st.text_input("URL TARGET", placeholder="https://")
        if st.button("EXECUTE SCAN"):
            with st.spinner("NEURAL AGENT DEPLOYED..."):
                data = scrape_website(url)
                # Specialized Prompt for Sales
                final_prompt = f"Analyze website content: '{data[:2000]}'. Act as a sales expert. Write a cold email pitching AI automation. Under 150 words."
                res = ask_ai(final_prompt, st.session_state['api_key'])
                
                st.session_state['current_result'] = res
                st.session_state['current_url'] = url
                
                st.markdown(f"""<div style="background:rgba(255,255,255,0.05); padding:25px; border-radius:15px; border:1px solid #334155;">{res}</div>""", unsafe_allow_html=True)

        if 'current_result' in st.session_state:
            if st.button("💾 SAVE LEAD"):
                st.session_state['leads_db'].append({"Company": st.session_state['current_url'], "Status": "Ready", "Timestamp": time.strftime("%H:%M")})
                st.success("SECURED")
        if len(st.session_state['leads_db']) > 0:
            st.dataframe(st.session_state['leads_db'], use_container_width=True)

    # 2. HR TAB (Simulated)
    with t2:
        st.subheader("BIOMETRIC PARSING")
        if st.file_uploader("UPLOAD CANDIDATE DATA"):
            with st.spinner("ANALYZING..."): time.sleep(2)
            st.success("MATCH FOUND")
            st.metric("MATCH SCORE", "98.4%", "ELITE TIER")

    # 3. FINANCE TAB (Simulated)
    with t3:
        st.subheader("GLOBAL LEDGER")
        m1, m2 = st.columns(2)
        m1.metric("REVENUE", "$482,000", "+14%")
        m2.metric("PROFIT", "$370,000", "+22%")
        st.line_chart([45, 48, 47, 52, 55, 59, 64, 61, 68, 72])

    # 4. NEW: ASSISTANT TAB (REAL AI CHAT)
    with t4:
        st.subheader("NOVUS NEURAL INTERFACE")
        st.markdown("<div style='color:#94a3b8; margin-bottom:20px;'>Ask me anything. I am connected to the global network.</div>", unsafe_allow_html=True)

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Enter command or query..."):
            # 1. Show User Message
            with st.chat_message("user"):
                st.markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            # 2. Get AI Response
            with st.chat_message("assistant"):
                response_text = ask_ai(prompt, st.session_state['api_key'])
                st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# ==========================================
# 6. LANDING PAGE
# ==========================================
def show_landing_page():
    st.markdown("""
    <div class="hero-container">
        <div class="thunder-wrapper">
            <svg class="thunder-svg-hero" viewBox="0 0 24 24" fill="url(#grad1)" xmlns="http://www.w3.org/2000/svg"><path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/></svg>
        </div>
        <div class="title-wrapper">
            <div id="text-left" class="hero-text">NOVUS</div>
            <div id="text-right" class="hero-text">FLOW</div>
        </div>
        <div class="hero-subtitle-scroll">SCROLL TO INITIALIZE NEURAL LINK</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 4])
    with c2: st.markdown("""<div style="padding: 100px 0; font-size: 1.5rem; color: #94a3b8;">WE BUILD <span style="color:#3b82f6;">AGENCY.</span></div>""", unsafe_allow_html=True)

    c_center = st.columns([1, 1, 1])[1]
    with c_center:
        st.markdown('<div class="portal-container"><div class="portal-inner">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-family:Syncopate; letter-spacing:2px; margin-bottom:20px;">ESTABLISH LINK</h3>', unsafe_allow_html=True)
        password = st.text_input("ENCRYPTION KEY", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        st.write("")
        if st.button("CONNECT"):
            if password == "aditya123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br><div style='text-align:center; color:#334155;'>NOVUS TECHNOLOGIES © 2026</div>", unsafe_allow_html=True)

# ==========================================
# 7. EXECUTION
# ==========================================
if st.session_state['logged_in']:
    show_main_app()
else:
    show_landing_page()
