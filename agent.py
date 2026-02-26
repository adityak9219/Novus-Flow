import streamlit as st
import requests
import time
import json
import io
from bs4 import BeautifulSoup

# Import libraries for HR Resume Parsing
try:
    import PyPDF2
    from docx import Document
except ImportError:
    pass

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
# 3. CINEMATIC CSS ENGINE (FIXED LOGO POSITION)
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

    #MainMenu, footer, header {visibility: hidden;}

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

    @keyframes thunderPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }

    .hero-subtitle-scroll { 
        font-family: 'Space Grotesk'; 
        color: #94a3b8; 
        margin-top: 30px; 
        letter-spacing: 4px; 
        animation: fadeIn 3s ease-in 2s forwards; 
        opacity: 0; 
    }

    .holo-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 15px; backdrop-filter: blur(10px); }
    .portal-container { max-width: 400px; margin: auto; padding: 2px; background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 15px; }
    .portal-inner { background: #000; border-radius: 13px; padding: 30px; text-align: center; }
    @keyframes fadeIn { to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown('<svg style="width:0;height:0;position:absolute;"><defs><linearGradient id="grad1"><stop offset="0%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient></defs></svg>', unsafe_allow_html=True)

# ==========================================
# 4. LOGIC ENGINE (AUTO-RECOVERY MODELS)
# ==========================================

def scrape_website(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            text = ""
            for tag in soup.find_all(['h1', 'h2', 'p']): 
                text += tag.get_text(strip=True) + " "
            return text[:3000]
        return ""
    except: return ""

def extract_text_from_file(uploaded_file):
    text = ""
    try:
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
        return text
    except: return ""

def run_ai_agent(prompt, api_key):
    # This list tries multiple models to bypass the 404 error
    models_to_try = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
    
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = { "contents": [{ "parts": [{"text": prompt}] }] }
        try:
            response = requests.post(url, json=payload, timeout=15)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
        except:
            continue
    return "Error: Could not connect to AI. Please verify your API Key in Streamlit Secrets."

# ==========================================
# 5. DASHBOARD UI
# ==========================================
def show_main_app():
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
                web_content = scrape_website(url)
                if web_content:
                    res = run_ai_agent(f"Analyze this content: {web_content}. Write a short cold email for AI services.", st.session_state['api_key'])
                    st.markdown(f'<div class="holo-card">{res}</div>', unsafe_allow_html=True)
                else:
                    st.error("Could not read website. Please check the URL.")

    with t2:
        st.subheader("BIOMETRIC RESUME PARSING")
        uploaded_file = st.file_uploader("Upload Candidate CV", type=['pdf', 'docx'])
        if uploaded_file and st.button("EXECUTE NEURAL EVALUATION"):
            with st.spinner("ANALYZING DNA SEQUENCE..."):
                resume_text = extract_text_from_file(uploaded_file)
                res = run_ai_agent(f"Summarize this resume and match skills: {resume_text[:3000]}", st.session_state['api_key'])
                st.markdown(f'<div class="holo-card">{res}</div>', unsafe_allow_html=True)

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
            <svg class="thunder-svg-hero" viewBox="0 0 24 24" fill="url(#grad1)"><path d="M13 2L3 14H12L11 22L21 10H12L13 2Z"/></svg>
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
