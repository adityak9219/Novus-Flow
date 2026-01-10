import streamlit as st
import time
import random
from openai import OpenAI

# ==========================================
# 1. PAGE CONFIGURATION & SETUP
# ==========================================
st.set_page_config(
    page_title="Novus Flow | AI Agency",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize Session State for Animation
if "first_load" not in st.session_state:
    st.session_state.first_load = True

# ==========================================
# 2. NOVUS "BRAIN" SETTINGS (SYSTEM PROMPT)
# ==========================================
NOVUS_SYSTEM_PROMPT = """
You are NOVUS FLOW, an advanced AI Agency Manager. 
You are NOT a standard assistant. You are an architect of workflows.

YOUR PERSONA:
- Name: Novus
- Tone: Professional, Futuristic, Concise, "Cyberpunk-Corporate".
- Goal: To help the user build, design, and execute complex tasks.
- Style: You speak in terms of "deploying agents", "initializing workflows", and "analyzing parameters".

GUIDELINES:
1. If the user says "Hello", welcome them to the Neural Link.
2. If asked to build something, break it down into steps (Strategy -> Design -> Code).
3. Keep responses high-impact. Avoid fluff.
4. If you don't have a tool for a request yet, state that you are "simulating" the output for now.
"""

# ==========================================
# 3. HIGH-END CSS STYLING (THE UI ENGINE)
# ==========================================
st.markdown("""
    <style>
        /* --- GLOBAL RESET --- */
        .stApp {
            background-color: #050510; /* Deep Space Black */
            color: #e0e0e0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Hide Default Streamlit Clutter */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div[data-testid="stToolbar"] {visibility: hidden;}
        div[data-testid="stDecoration"] {display: none;}

        /* --- HERO SECTION (ANIMATIONS) --- */
        .hero-container {
            position: fixed;
            top: 40%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            width: 100%;
            z-index: 1;
            pointer-events: none;
            transition: opacity 1s ease-in-out;
        }

        .thunderbolt {
            font-size: 80px;
            color: #ffffff;
            text-shadow: 0 0 30px #3b82f6, 0 0 60px #8b5cf6;
            margin-bottom: 0px;
            opacity: 0;
            animation: boltStrike 1.2s ease-out forwards;
            position: relative;
            z-index: 10;
        }

        .hero-title {
            font-size: 100px;
            font-weight: 900;
            letter-spacing: -4px;
            text-transform: uppercase;
            background: linear-gradient(to bottom, #ffffff, #888888);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-top: -30px;
            opacity: 0;
            filter: blur(20px);
            animation: textEmergence 1.8s cubic-bezier(0.19, 1, 0.22, 1) forwards;
            animation-delay: 0.3s;
        }

        .hero-subtitle {
            font-family: 'Courier New', monospace;
            font-size: 14px;
            color: #666;
            letter-spacing: 6px;
            margin-top: 25px;
            text-transform: uppercase;
            opacity: 0;
            animation: fadeInSimple 2s ease forwards;
            animation-delay: 1.5s;
        }

        /* --- ANIMATIONS --- */
        @keyframes boltStrike {
            0% { transform: scale(0) translateY(-50px); opacity: 0; }
            40% { opacity: 1; transform: scale(1.2) translateY(0); }
            100% { opacity: 1; transform: scale(1); }
        }

        @keyframes textEmergence {
            0% { opacity: 0; transform: scale(3.5); filter: blur(30px); }
            100% { opacity: 1; transform: scale(1); filter: blur(0px); }
        }

        @keyframes fadeInSimple {
            to { opacity: 0.8; }
        }

        /* --- AGENCY WATERMARK --- */
        .agency-text {
            position: fixed;
            bottom: 30px;
            left: 40px;
            font-family: 'Arial', sans-serif;
            font-size: 11px;
            color: #333;
            line-height: 1.6;
            z-index: 2;
            pointer-events: none;
        }
        .agency-highlight { color: #3b82f6; font-weight: bold; }

        /* --- CHAT INPUT (THE FLOATING CAPSULE) --- */
        div[data-testid="stChatInput"] {
            position: fixed;
            bottom: 40px;
            left: 50%;
            transform: translateX(-50%);
            width: 600px !important;
            max-width: 90%;
            z-index: 1000;
            background: transparent;
        }

        div[data-testid="stChatInput"] div[class*="stTextInput"] input {
            background: rgba(15, 15, 25, 0.8) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 50px !important;
            color: white !important;
            padding: 1.5rem 1.5rem 1.5rem 3.5rem !important; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
            backdrop-filter: blur(15px);
        }

        div[data-testid="stChatInput"] div[class*="stTextInput"] input:focus {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3) !important;
        }

        /* Logo Overlay inside Input */
        .input-logo-overlay {
            position: fixed;
            bottom: 53px;
            left: calc(50% - 270px);
            width: 28px;
            height: 28px;
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            border-radius: 50%;
            z-index: 1002;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 12px;
            pointer-events: none;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
        }

        @media (max-width: 700px) {
            div[data-testid="stChatInput"] { width: 90% !important; }
            .input-logo-overlay { left: 8%; }
        }

        /* --- MESSAGE BUBBLES --- */
        div[data-testid="stChatMessageContent"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.05);
        }
    </style>

    <div class="hero-container" id="hero-area">
        <div class="thunderbolt">⚡</div>
        <div class="hero-title">NOVUS FLOW</div>
        <div class="hero-subtitle">INITIALIZE NEURAL LINK</div>
    </div>

    <div class="agency-text">
        WE DO NOT BUILD TOOLS.<br>
        WE BUILD <span class="agency-highlight">AGENCY.</span>
    </div>
    
    <div class="input-logo-overlay">N</div>
""", unsafe_allow_html=True)


# ==========================================
# 4. SIDEBAR (API KEY CONFIGURATION)
# ==========================================
with st.sidebar:
    st.title("Novus Settings")
    
    # Secure API Key Input
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
    
    st.markdown("---")
    st.caption("Agency Status: ONLINE")
    
    if st.button("Reboot System (Clear Chat)"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.info("Instructions: Enter your API key above to activate the Neural Link.")


# ==========================================
# 5. AGENT LOGIC (REAL OPENAI BRAIN)
# ==========================================

def get_openai_client(key):
    """Initializes the OpenAI client securely."""
    if not key:
        return None
    return OpenAI(api_key=key)

def process_stream(client, messages):
    """
    Connects to OpenAI and streams the response chunk by chunk.
    This creates the 'typing' effect naturally.
    """
    try:
        # We append the System Prompt to guide the behavior
        full_history = [{"role": "system", "content": NOVUS_SYSTEM_PROMPT}] + messages
        
        stream = client.chat.completions.create(
            model="gpt-4o", # Or "gpt-3.5-turbo" if you want cheaper
            messages=full_history,
            stream=True,
        )
        return stream
    except Exception as e:
        return f"Error: {str(e)}"

# ==========================================
# 6. MAIN EXECUTION FLOW
# ==========================================

# 1. Render Chat History
# We create a container so messages stack cleanly
chat_container = st.container()

with chat_container:
    # Spacer to push content down initially
    st.write("") 
    st.write("")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 2. Input Handling
if prompt := st.chat_input("Command Novus..."):
    
    # A. Visual Clean-up: Fade out the big logo when typing starts
    if st.session_state.first_load:
        st.markdown("""
            <style>
                .hero-container { opacity: 0; pointer-events: none; }
            </style>
        """, unsafe_allow_html=True)
        st.session_state.first_load = False

    # B. Add User Message to State
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # C. Display User Message Immediately
    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # D. GENERATE RESPONSE
    with chat_container:
        with st.chat_message("assistant"):
            
            # Check for API Key
            if not api_key:
                st.warning("⚠️ NEURAL LINK DISCONNECTED: Please enter your OpenAI API Key in the sidebar.")
                response_text = "Please configure the system in the sidebar settings."
            else:
                # Initialize Client
                client = get_openai_client(api_key)
                
                # Create a placeholder for the streaming text
                message_placeholder = st.empty()
                full_response = ""
                
                # Get the Stream
                stream = process_stream(client, st.session_state.messages)
                
                # Check if it returned an error string
                if isinstance(stream, str):
                    message_placeholder.error(stream)
                    full_response = stream
                else:
                    # Stream the chunks
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            # Update UI with cursor effect
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Final clean update
                    message_placeholder.markdown(full_response)
    
    # E. Save Assistant Response to State
    if api_key:
        st.session_state.messages.append({"role": "assistant", "content": full_response})
