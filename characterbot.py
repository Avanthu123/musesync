import streamlit as st
import ollama
from PIL import Image

# -----------------------------
# Page Setup
# -----------------------------
st.set_page_config(page_title="I Am Iron Man", layout="wide")

# -----------------------------
# Custom CSS for Iron Man Theme
# -----------------------------
st.markdown("""
    <style>
    /* Global */
    body, .stApp {
        background-color: #000;
        color: #f5f5f5;
        overflow: hidden !important;
        height: 100vh !important;
    }

    /* Lock down ALL Streamlit scroll containers */
    .main, [data-testid="stMain"],
    .block-container,
    [data-testid="stMainBlockContainer"],
    .stMainBlockContainer {
        overflow: hidden !important;
        height: 100vh !important;
        max-height: 100vh !important;
        padding: 0 !important;
    }

    /* Animated background for the whole app */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(255, 30, 0, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 50%, rgba(255, 30, 0, 0.05) 0%, transparent 50%);
        z-index: 0;
        pointer-events: none;
    }

    /* Style header to blend with dark theme but keep menu button */
    header[data-testid="stHeader"] {
        background: transparent !important;
        color: #fff !important;
    }
    footer { display: none !important; }

    /* Left column: fixed in place */
    div[data-testid="stColumns"] > div:first-child {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 50vw !important;
        height: 100vh !important;
        overflow: hidden !important;
        z-index: 10;
        background: radial-gradient(circle at center, #111 0%, #000 100%);
        border-right: 3px solid #ff1e00;
        box-shadow: 0 0 25px #ff1e00;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 1rem;
    }

    /* Arc reactor pulsing glow on left panel */
    div[data-testid="stColumns"] > div:first-child::before {
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        width: 400px; height: 400px;
        transform: translate(-50%, -50%);
        background: radial-gradient(circle, rgba(255, 30, 0, 0.15) 0%, rgba(255, 30, 0, 0.05) 40%, transparent 70%);
        animation: arcPulse 3s ease-in-out infinite;
        pointer-events: none;
        z-index: 0;
    }

    /* Scan line effect on left panel */
    div[data-testid="stColumns"] > div:first-child::after {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(255, 30, 0, 0.03) 2px,
            rgba(255, 30, 0, 0.03) 4px
        );
        pointer-events: none;
        z-index: 1;
    }

    @keyframes arcPulse {
        0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
        50% { opacity: 1; transform: translate(-50%, -50%) scale(1.15); }
    }

    /* Image inside left panel */
    div[data-testid="stColumns"] > div:first-child img {
        width: 80%;
        max-width: 600px;
        filter: drop-shadow(0 0 30px #ff1e00);
        animation: imgFloat 6s ease-in-out infinite;
        position: relative;
        z-index: 2;
    }

    @keyframes imgFloat {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* Title styling */
    .iron-title {
        color: #ff1e00;
        text-shadow: 0 0 20px #ff1e00, 0 0 40px rgba(255, 30, 0, 0.4);
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 2;
        animation: titleGlow 2s ease-in-out infinite alternate;
    }

    @keyframes titleGlow {
        0% { text-shadow: 0 0 20px #ff1e00, 0 0 40px rgba(255, 30, 0, 0.3); }
        100% { text-shadow: 0 0 30px #ff1e00, 0 0 60px rgba(255, 30, 0, 0.6), 0 0 80px rgba(255, 30, 0, 0.2); }
    }

    /* Right column: fixed to right half */
    div[data-testid="stColumns"] > div:last-child {
        position: fixed !important;
        top: 0 !important;
        left: 50vw !important;
        right: 0 !important;
        width: 50vw !important;
        height: 100vh !important;
        display: flex;
        flex-direction: column;
        overflow: hidden !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Force the columns container to not scroll */
    div[data-testid="stColumns"] {
        overflow: hidden !important;
        height: 100vh !important;
    }

    /* HUD grid overlay on right panel */
    div[data-testid="stColumns"] > div:last-child::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            linear-gradient(rgba(255, 30, 0, 0.04) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 30, 0, 0.04) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
        animation: gridScroll 20s linear infinite;
    }

    @keyframes gridScroll {
        0% { background-position: 0 0; }
        100% { background-position: 0 400px; }
    }

    /* Chat bubbles */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 12px 16px;
        margin: 10px 0;
        background: linear-gradient(135deg, #111 0%, #1a1a1a 100%);
        box-shadow: 0 0 12px #ff1e00;
        color: #fff;
        border: 1px solid rgba(255, 30, 0, 0.2);
        animation: bubbleFadeIn 0.4s ease-out;
        position: relative;
        z-index: 1;
        overflow-wrap: break-word;
        word-wrap: break-word;
        word-break: break-word;
        max-width: 100%;
    }

    div[data-testid="stChatMessage"]:hover {
        box-shadow: 0 0 20px #ff1e00, 0 0 40px rgba(255, 30, 0, 0.3);
        border-color: rgba(255, 30, 0, 0.5);
        transition: all 0.3s ease;
    }

    @keyframes bubbleFadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* Scrollable chat container styling */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border: none !important;
    }

    /* Allow the chat container to scroll */
    div[data-testid="stColumns"] > div:last-child div[data-testid="stVerticalBlockBorderWrapper"][style*="height"] {
        overflow-y: auto !important;
        overflow-x: hidden !important;
        border: none !important;
    }

    /* Ensure chat messages container has bottom padding so last msg visible */
    div[data-testid="stColumns"] > div:last-child div[data-testid="stVerticalBlockBorderWrapper"][style*="height"] > div {
        padding-bottom: 20px !important;
        padding-right: 10px !important;
    }

    /* Custom scrollbar for chat */
    div[data-testid="stVerticalBlockBorderWrapper"][style*="height"]::-webkit-scrollbar {
        width: 6px;
    }
    div[data-testid="stVerticalBlockBorderWrapper"][style*="height"]::-webkit-scrollbar-track {
        background: #111;
    }
    div[data-testid="stVerticalBlockBorderWrapper"][style*="height"]::-webkit-scrollbar-thumb {
        background: #ff1e00;
        border-radius: 3px;
    }

    /* Typing indicator */
    .typing-dots {
        display: inline-flex;
        gap: 4px;
        padding: 8px 0;
    }
    .typing-dots span {
        width: 8px; height: 8px;
        background: #ff1e00;
        border-radius: 50%;
        animation: dotBounce 1.4s ease-in-out infinite;
    }
    .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
    .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes dotBounce {
        0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Input bar: fixed at bottom of right half */
    .stChatInput {
        position: fixed !important;
        bottom: 0 !important;
        left: 50vw !important;
        right: 0 !important;
        width: 50vw !important;
        background: rgba(0, 0, 0, 0.95);
        padding: 0.75rem 1.5rem;
        z-index: 30;
        backdrop-filter: blur(10px);
        border-top: 1px solid rgba(255, 30, 0, 0.3);
    }
    .stChatInput textarea {
        border: 2px solid #ff1e00 !important;
        border-radius: 10px;
        background-color: rgba(17, 17, 17, 0.9) !important;
        color: white !important;
        box-shadow: 0 0 10px rgba(255, 30, 0, 0.2) !important;
    }
    .stChatInput textarea:focus {
        box-shadow: 0 0 20px rgba(255, 30, 0, 0.5) !important;
        border-color: #ff4400 !important;
    }

    /* Left panel animated border glow */
    div[data-testid="stColumns"] > div:first-child {
        border-right: 3px solid #ff1e00;
        box-shadow: 0 0 25px #ff1e00, inset 0 0 60px rgba(255, 30, 0, 0.05);
        animation: borderPulse 4s ease-in-out infinite;
    }

    @keyframes borderPulse {
        0%, 100% { box-shadow: 0 0 25px #ff1e00, inset 0 0 60px rgba(255, 30, 0, 0.05); }
        50% { box-shadow: 0 0 40px #ff1e00, 0 0 80px rgba(255, 30, 0, 0.15), inset 0 0 80px rgba(255, 30, 0, 0.08); }
    }

    /* Style sidebar to match theme */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #111 !important;
    }

    /* Fix Streamlit main block padding */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        overflow: hidden !important;
    }

    /* CSS-only floating particles */
    .particle {
        position: fixed;
        width: 3px; height: 3px;
        background: radial-gradient(circle, #ff1e00, transparent);
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        animation: particleRise linear infinite;
    }
    .particle:nth-child(1)  { left:  5%; animation-duration: 18s; animation-delay: 0s;   opacity: 0.4; width: 2px; height: 2px; }
    .particle:nth-child(2)  { left: 12%; animation-duration: 22s; animation-delay: 2s;   opacity: 0.3; width: 4px; height: 4px; }
    .particle:nth-child(3)  { left: 20%; animation-duration: 15s; animation-delay: 4s;   opacity: 0.5; }
    .particle:nth-child(4)  { left: 28%; animation-duration: 20s; animation-delay: 1s;   opacity: 0.2; width: 2px; height: 2px; }
    .particle:nth-child(5)  { left: 35%; animation-duration: 25s; animation-delay: 3s;   opacity: 0.4; width: 4px; height: 4px; }
    .particle:nth-child(6)  { left: 42%; animation-duration: 17s; animation-delay: 5s;   opacity: 0.3; }
    .particle:nth-child(7)  { left: 48%; animation-duration: 21s; animation-delay: 0.5s; opacity: 0.5; width: 2px; height: 2px; }
    .particle:nth-child(8)  { left: 55%; animation-duration: 19s; animation-delay: 3.5s; opacity: 0.4; }
    .particle:nth-child(9)  { left: 62%; animation-duration: 23s; animation-delay: 1.5s; opacity: 0.2; width: 4px; height: 4px; }
    .particle:nth-child(10) { left: 68%; animation-duration: 16s; animation-delay: 4.5s; opacity: 0.5; }
    .particle:nth-child(11) { left: 75%; animation-duration: 24s; animation-delay: 2.5s; opacity: 0.3; width: 2px; height: 2px; }
    .particle:nth-child(12) { left: 82%; animation-duration: 18s; animation-delay: 0.8s; opacity: 0.4; }
    .particle:nth-child(13) { left: 88%; animation-duration: 20s; animation-delay: 3.2s; opacity: 0.3; width: 4px; height: 4px; }
    .particle:nth-child(14) { left: 93%; animation-duration: 22s; animation-delay: 1.8s; opacity: 0.5; }
    .particle:nth-child(15) { left:  8%; animation-duration: 26s; animation-delay: 5.5s; opacity: 0.2; width: 2px; height: 2px; }
    .particle:nth-child(16) { left: 38%; animation-duration: 14s; animation-delay: 2.8s; opacity: 0.4; }
    .particle:nth-child(17) { left: 52%; animation-duration: 19s; animation-delay: 4.2s; opacity: 0.3; width: 4px; height: 4px; }
    .particle:nth-child(18) { left: 72%; animation-duration: 21s; animation-delay: 0.3s; opacity: 0.5; }
    .particle:nth-child(19) { left: 85%; animation-duration: 17s; animation-delay: 3.8s; opacity: 0.2; width: 2px; height: 2px; }
    .particle:nth-child(20) { left: 15%; animation-duration: 23s; animation-delay: 1.2s; opacity: 0.4; }

    @keyframes particleRise {
        0%   { bottom: -10px; opacity: 0; transform: translateX(0); }
        10%  { opacity: 0.6; }
        50%  { transform: translateX(20px); }
        90%  { opacity: 0.2; }
        100% { bottom: 105vh; opacity: 0; transform: translateX(-15px); }
    }

    /* Sidebar styling */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {
        background-color: #0a0a0a !important;
        border-right: 2px solid rgba(255, 30, 0, 0.3) !important;
    }
    [data-testid="stSidebar"] * {
        color: #f5f5f5 !important;
    }
    [data-testid="stSidebar"] .stSlider > div > div > div {
        background: #ff1e00 !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #111 !important;
        border-color: #ff1e00 !important;
    }
    </style>
""", unsafe_allow_html=True)

# CSS-only floating particles (no JS needed)
particles_html = '<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;pointer-events:none;z-index:0;overflow:hidden;">'
for i in range(20):
    particles_html += '<div class="particle"></div>'
particles_html += '</div>'
st.markdown(particles_html, unsafe_allow_html=True)

# -----------------------------
# Sidebar: Model & Temperature
# -----------------------------
with st.sidebar:
    st.markdown('<div class="iron-title" style="font-size:1.5rem;">STARK LABS</div>', unsafe_allow_html=True)
    st.markdown("---")
    model_choice = st.selectbox("AI Model", ["gemma3:latest", "llama3:latest", "mistral:latest", "phi3:latest"], index=0)
    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.8, step=0.1)
    st.markdown("---")
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Greetings, human. Tony Stark here \u2014 let's see what genius question you've got today."}
        ]
        st.session_state.waiting = False
        st.rerun()

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1, 1], gap="small")

with left:
    st.markdown('<div class="iron-title">I am Iron Man.</div>', unsafe_allow_html=True)
    st.image("ironman.png")

with right:
    # Chat container - scrollable with explicit height
    chat_container = st.container(height=600)

    with chat_container:
        # Initialize chat state
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Greetings, human. Tony Stark here \u2014 let's see what genius question you've got today."}
            ]
        if "waiting" not in st.session_state:
            st.session_state.waiting = False

        # Render chat history
        for msg in st.session_state.messages:
            avatar = "ironman_icon.png" if msg["role"] == "assistant" else None
            with st.chat_message(msg["role"], avatar=avatar):
                st.write(msg["content"])

        # Show typing indicator while waiting for response
        if st.session_state.waiting:
            with st.chat_message("assistant", avatar="ironman_icon.png"):
                st.markdown('<div class="typing-dots"><span></span><span></span><span></span></div>', unsafe_allow_html=True)

    # Chat input - stays fixed below the scrollable chat
    user_input = st.chat_input("Type your message, genius...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.waiting = True
        st.rerun()

    # Generate response if waiting
    if st.session_state.get("waiting", False):
        # Add Iron Man persona system prompt
        system_prompt = {
            "role": "system",
            "content": (
                "You are Iron Man (Tony Stark). Respond with confidence, wit, sarcasm, "
                "and charm. Stay in character at all times."
            )
        }

        messages = [system_prompt] + st.session_state.messages

        # Generate response
        response = ollama.chat(
            model=model_choice,
            messages=messages,
            options={"temperature": temperature}
        )

        reply = response["message"]["content"]

        # Append, stop waiting, and rerun
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.waiting = False
        st.rerun()
