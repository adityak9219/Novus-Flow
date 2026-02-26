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
    pass # Streamlit will handle the error if requirements.txt isn't updated

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="NOVUS FLOW | The Singularity",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= =========================
# 2. SESSION STATE
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'api_key' not in st.session_state:
    # Attempt to pull from Streamlit Secrets
    st.session_state['api_key'] = st.secrets.get('GEMINI_API_KEY', '')

if 'leads_db' not in st.session_state:
    st.session_state['leads_db'] = []

# ==========================================
# 3. CINEMATIC CSS ENGINE (REFINED ANIMATIONS)
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Space+Grotesk:wght@300;500;700&display=swap');
    
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
    
    /* HERO CONTAINER */
    .hero-container { 
        height: 80vh; 
        display: flex; 
        flex-direction: column; 
        justify-content: center; 
        align-items: center; 
        position: relative;
        width: 100%;
        overflow: hidden;
    }
    
    .title-wrapper { 
        display: flex; 
        align-items: center; 
        justify-content: center;
        position: relative;
        z-index: 10;
    }
    
    .thunder-svg-hero { 
        width: clamp(70px, 12vw, 120px);
        filter: drop-shadow(0 0 50px rgba(59, 130, 246, 0.8)); 
        z-index: 20; /* Keep bolt on top of sliding text */
        animation: thunderPulse 4s infinite ease-in-out;
    }
    
    .hero-text { 
        font-family: 'Syncopate', sans-serif; 
        font-weight: 700; 
        font-size: clamp(40px, 9vw, 110px); 
        color: #ffffff; 
        opacity: 0; 
        white-space: nowrap; 
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.2); 
    }
    
    /* ANIMATION: TEXT SLIDES OUT FROM BEHIND THE BOLT */
    #text-left { 
        animation: slideOutLeft 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; 
    }
    #text-right { 
        animation: slideOutRight 2s cubic-bezier(0.2, 0.8, 0.2, 1) 0.5s forwards; 
    }
    
    @keyframes slideOutLeft { 
        0% { transform: translateX(60%); opacity: 0; filter: blur(15px); } 
        100% { transform: translateX(0); opacity: 1; filter: blur(0px); margin-right: 25px; } 
    }
    @keyframes slideOutRight { 
        0% { transform: translateX(-60%); opacity: 0; filter: blur(15px); } 
        100% { transform: translateX(0); opacity: 1; filter: blur(0px); margin-left: 25px; } 
    }
    
    @keyframes thunderPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
    
    .hero-subtitle-scroll { 
        font-family: 'Space Grotesk', monospace; 
        color: #94a3b8; 
        margin-top: 30px; 
        letter-spacing: 4px; 
        font-size: clamp(0.7rem, 2vw, 0.9rem); 
        text-align: center;
        animation: fadeIn 3s ease-in 2s forwards; 
        opacity: 0; 
    }

    /* CARDS & PORTAL */
    .holo-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 30px; border-radius: 20px; backdrop-filter: blur(10px); transition: 0.3s; }
    .holo-card:hover { border-color: #3b82f6; background: rgba(255, 255, 255, 0.07); }
    
    .portal-container { max-width: 450px; margin: 50px auto; padding: 2px; background: linear-gradient(90deg, #2563eb, #d946ef); border-radius: 20px; }
    .portal-inner { background: #000; border-radius: 18px; padding: 40px; text-align: center; }

    .stTextInput input { background: #111827 !important; color: white !important; border-radius: 10px !important; }
    .stButton button { border-radius: 50px; font-family: 'Syncopate'; transition: 0.3s; }
    
    @keyframes fadeIn { to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# Define the Gradient for the SVG Bolt
st.markdown('<svg style="width:0;height:0;position:absolute;"><defs><linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" /><stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" /></linearGradient></defs></svg>', unsafe_allow_html=True)

# ==========================================
# 4. LOGIC ENGINE (REAL HR & SALES)
# ==========================================

def extract_text_from_file(uploaded_file):
    """Real file parsing for HR section."""
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
    except Exception as e:
        return f"Error reading file: {e}"

def run_ai_agent(prompt_text, api_key):
    """Core AI call to Gemini."""
    if not api_key: return "⚠️ Missing API Key"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Connection Failed: {e}"

# ==========================================
# 5. DASHBOARD UI
# ==========================================
def show_main_app():
    st.markdown('<h2 style="font-family:Syncopate; letter-spacing:2px;">NOVUS CORE</h2>', unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #334155; margin-bottom:30px;'>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["[ SALES ]", "[ HR ]", "[ FINANCE ]"])

    with t1:
        st.subheader("TARGET ACQUISITION")
        target_url = st.text_input("Enter Company URL", placeholder="https://example.com")
        if st.button("RUN OUTREACH AGENT"):
            with st.spinner("Analyzing target..."):
                time.sleep(1)
                st.info("Sales Agent is currently scanning domain structure...")

    with t2:
        st.subheader("BIOMETRIC RESUME PARSING")
        uploaded_file = st.file_uploader("Upload Candidate CV", type=['pdf', 'docx'])
        
        if uploaded_file and st.session_state['api_key']:
            if st.button("EXECUTE NEURAL EVALUATION"):
                with st.spinner("Extracting DNA Data..."):
                    resume_text = extract_text_from_file(uploaded_file)
                    # Prompt for AI analysis
                    analysis_prompt = f"""
                    Act as an expert technical recruiter. Analyze this resume:
                    {resume_text[:4000]}
                    
                    Provide:
                    1. Candidate Name
                    2. Top 3 Skills
                    3. Match Score (0-100%)
                    4. Brief Verdict
                    Format the output nicely with emojis.
                    """
                    result = run_ai_agent(analysis_prompt, st.session_state['api_key'])
                    st.markdown(f'<div class="holo-card">{result}</div>', unsafe_allow_html=True)
        elif not st.session_state['api_key']:
            st.warning("Please ensure GEMINI_API_KEY is set in your Secrets to use AI features.")

    with t3:
        st.subheader("GLOBAL LEDGER")
        st.metric("NET PROFIT", "$370,000", "+22%")
        st.line_chart({"Revenue": [45, 52, 47, 55, 64, 72]})

# ==========================================
# 6. LANDING PAGE
# ==========================================
def show_landing_page():
    # Centered Cinematic Logo with Restored Animation
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

    # Portal Login
    st.markdown('<br><br>', unsafe_allow_html=True)
    _, c_center, _ = st.columns([1, 1.5, 1])
    with c_center:
        st.markdown('<div class="portal-container"><div class="portal-inner">', unsafe_allow_html=True)
        st.markdown('<h3 style="font-family:Syncopate; letter-spacing:2px; margin-bottom:20px;">ESTABLISH LINK</h3>', unsafe_allow_html=True)
        password = st.text_input("ENCRYPTION KEY", type="password", label_visibility="collapsed", placeholder="ENTER KEY")
        if st.button("CONNECT"):
            if password == "aditya123":
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br><div style='text-align:center; color:#334155; font-size:0.8rem;'>NOVUS TECHNOLOGIES © 2026 // SINGULARITY READY</div>", unsafe_allow_html=True)

# ==========================================
# 7. EXECUTION
# ==========================================
if st.session_state['logged_in']:
    show_main_app()
else:
    show_landing_page()
