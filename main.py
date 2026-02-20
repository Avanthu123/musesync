import streamlit as st
import random
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector import retriever

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(page_title="MuseSync", layout="wide")

# ----------------------------------
# SESSION STATE
# ----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey. Tell me the vibe and I’ll sync the mood 🎧"}
    ]

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "current_track_id" not in st.session_state:
    st.session_state.current_track_id = None

if "waiting" not in st.session_state:
    st.session_state.waiting = False


# ----------------------------------
# CSS
# ----------------------------------
st.markdown("""
<style>

/* Animated gradient background */
.stApp {
    background: linear-gradient(-45deg, #0a0f0d, #000000, #0d1f18, #00110a);
    background-size: 400% 400%;
    animation: gradientMove 18s ease infinite;
    color: white;
}
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

/* Chat bubbles */
.stChatMessage {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 12px;
    backdrop-filter: blur(6px);
}

/* Typing dots */
.typing-dots {
    display: inline-flex;
    gap: 4px;
}
.typing-dots span {
    width: 8px;
    height: 8px;
    background: #1DB954;
    border-radius: 50%;
    animation: bounce 1.4s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
    40% { transform: scale(1); opacity: 1; }
}

/* Pulse bar */
.pulse-bar {
    height: 6px;
    background: rgba(29,185,84,0.2);
    border-radius: 8px;
    margin-bottom: 10px;
    overflow: hidden;
}
.pulse-bar::after {
    content: "";
    display: block;
    height: 100%;
    width: 30%;
    background: linear-gradient(90deg,#1DB954,#00ff88);
    animation: move 1.5s infinite ease-in-out;
}
@keyframes move {
    0% { transform: translateX(-100%); }
    50% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

/* Playlist buttons styled as cards */
div.row-widget.stButton > button {
    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 12px;
    border: 1px solid rgba(29,185,84,0.15);
    backdrop-filter: blur(8px);
    transition: all 0.25s ease;
    text-align: left;
    white-space: pre-line;
    font-weight: 500;
}

div.row-widget.stButton > button:hover {
    transform: translateX(6px);
    border-color: #1DB954;
    box-shadow: 0 0 20px rgba(29,185,84,0.3);
}

div.row-widget.stButton > button:focus {
    outline: none;
}

header, footer {visibility:hidden;}

</style>
""", unsafe_allow_html=True)


# ----------------------------------
# RANDOM TRACKS (CHROMA SAFE)
# ----------------------------------
def get_random_tracks(n=6):
    data = retriever.vectorstore.get()
    docs = []
    for i in range(len(data["ids"])):
        docs.append(
            type("Doc", (), {
                "page_content": data["documents"][i],
                "metadata": data["metadatas"][i]
            })
        )
    return random.sample(docs, min(n, len(docs)))


# ----------------------------------
# LAYOUT
# ----------------------------------
left, right = st.columns([1,1], gap="large")

# ================= CHAT SIDE =================
with left:

    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("🎲 Lucky"):
            random_docs = get_random_tracks()
            st.session_state.recommendations = random_docs

            text = "Here are some random vibes for you:\n\n"
            for d in random_docs:
                meta = d.metadata
                text += f"- {meta.get('track_name')} — {meta.get('artists')}\n"

            st.session_state.messages.append({
                "role": "assistant",
                "content": text
            })
            st.rerun()

    chat_container = st.container(height=600)

    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if st.session_state.waiting:
            with st.chat_message("assistant"):
                st.markdown(
                    '<div class="typing-dots"><span></span><span></span><span></span></div>',
                    unsafe_allow_html=True
                )

    user_input = st.chat_input("How's the vibe?")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.waiting = True
        st.rerun()

    if st.session_state.waiting:
        last_user = st.session_state.messages[-1]["content"]

        docs = retriever.invoke(last_user)
        st.session_state.recommendations = docs

        response_text = "Here are some tracks matching your vibe:\n\n"
        for d in docs:
            meta = d.metadata
            response_text += f"- {meta.get('track_name')} — {meta.get('artists')}\n"

        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.session_state.waiting = False
        st.rerun()


# ================= PLAYER SIDE =================
with right:
    st.subheader("🎧 Now Playing")

    if st.session_state.current_track_id:
        tid = st.session_state.current_track_id
        embed_url = f"https://open.spotify.com/embed/track/{tid}?autoplay=1"

        st.markdown('<div class="pulse-bar"></div>', unsafe_allow_html=True)

        st.components.v1.html(f"""
        <iframe style="border-radius:12px"
        src="{embed_url}"
        width="100%" height="80"
        frameborder="0"
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture">
        </iframe>
        """, height=100)
    else:
        st.info("No Track Selected")

    st.subheader("📋 Playlist")

    if st.session_state.recommendations:
        for i, doc in enumerate(st.session_state.recommendations):
            meta = doc.metadata
            tid = meta.get("track_id")
            name = meta.get("track_name", "Unknown")
            artist = meta.get("artists", "Unknown")

            label = f"▶ {name}\n{artist}"

            if st.button(label, key=f"{i}_{tid}", use_container_width=True):
                st.session_state.current_track_id = tid
                st.rerun()
