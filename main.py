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

/* Background */
.stApp {
    background: #0a0a0a;
    color: white;
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
    margin-bottom: 10px;
    border: 1px solid rgba(29,185,84,0.15);
    backdrop-filter: blur(8px);
    transition: all 0.25s ease;
    text-align: left;
    white-space: pre-line;
    font-weight: 500;
    min-height: 70px;
    line-height: 1.6;
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
# LLM CHAIN
# ----------------------------------
@st.cache_resource
def get_chain():
    model = OllamaLLM(model="gemma3:latest")
    prompt = ChatPromptTemplate.from_template("""
You are MuseSync — a chill, music-obsessed AI with great taste and real personality.
You're talking to someone who just described their mood or vibe.

Their vibe: "{question}"

You have these tracks lined up for them:
{tracks}

Respond like a friend who knows music inside out. Be warm, maybe a bit poetic.
Briefly react to their vibe (1 sentence), then naturally weave in the song picks — 
don't just list them, *say something* about why they fit.
Keep it short (3-5 sentences max). No bullet lists. Sound human.
""")
    return prompt | model

chain = get_chain()

def format_tracks(docs):
    lines = []
    for d in docs:
        m = d.metadata
        lines.append(f"{m.get('track_name', '?')} by {m.get('artists', '?')}")
    return ", ".join(lines)

# ----------------------------------
left, right = st.columns([1,1], gap="large")

# ================= CHAT SIDE =================
with left:

    col1, col2 = st.columns([3,1])
    with col2:
        if st.button("🎲 Lucky"):
            random_docs = get_random_tracks()
            st.session_state.recommendations = random_docs
            lucky_q = "something random and exciting"
            reply = chain.invoke({"question": lucky_q, "tracks": format_tracks(random_docs)})
            st.session_state.messages.append({"role": "assistant", "content": reply})
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

        reply = chain.invoke({"question": last_user, "tracks": format_tracks(docs)})

        st.session_state.messages.append({"role": "assistant", "content": reply})
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
            genre = meta.get("track_genre", meta.get("genre", ""))

            # Build a multi-line label: bold song name, then artist + genre below
            genre_tag = f"  ·  {genre}" if genre else ""
            label = f"▶  {name}\n · {artist}{genre_tag}"

            if st.button(label, key=f"{i}_{tid}", use_container_width=True):
                st.session_state.current_track_id = tid
                st.rerun()
