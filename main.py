import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Updated import: pulling the retriever from gvector.py
from vector import retriever

# Configure the Streamlit page
st.set_page_config(page_title="Mood Music Recommender", page_icon="🎵", layout="centered")
st.title("🎵 Mood-Based Music Recommendation Bot")
st.write("Tell me your mood and I'll recommend the perfect songs for you!")

# --- 1. Setup LLM & Chain (Cached) ---
# We use @st.cache_resource so the model and chain aren't rebuilt on every user interaction
@st.cache_resource
def get_chain():
    model = OllamaLLM(model="gemma3:latest")
    
    template = """
    You are a friendly music recommendation assistant. Your job is to suggest songs based on the user's mood and preferences.

    You must follow these rules:
    - Use ONLY the provided music recommendations from the database
    - Recommend 5-10 songs that match the user's mood and preferences
    - For each recommendation, include: song title, artist, genre, and why it matches their mood
    - Consider audio features like valence (positivity), energy, and danceability
    - If the user's mood matches multiple music tracks, prioritize by popularity (higher is better)
    - Be enthusiastic and explain why each song fits their mood
    - If you cannot find suitable matches, suggest the closest alternatives

    Available music tracks:
    {records}

    User's mood/request:
    {question}
    """
    prompt = ChatPromptTemplate.from_template(template)
    return prompt | model

chain = get_chain()

# --- 2. Manage Chat History ---
# Initialize session state to hold the conversation
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. Handle User Input ---
if question := st.chat_input("Describe your mood (e.g., 'I feel happy and energetic' or 'I need calming music'):"):
    
    # Display the user's question
    with st.chat_message("user"):
        st.markdown(question)
    
    # Save the user's question to state
    st.session_state.messages.append({"role": "user", "content": question})

    # Generate and display the assistant's response
    with st.chat_message("assistant"):
        with st.spinner("Finding the perfect songs for your mood..."):
            
            # Retrieve relevant music tracks based on mood using retriever
            records = retriever.invoke(question)
            
            # Invoke LLM with grounded context
            response = chain.invoke({
                "records": records,
                "question": question
            })
            
            st.markdown(response)
            
            # Display song details in expandable sections
            if records:
                with st.expander("📊 Track Details"):
                    for i, doc in enumerate(records[:5], 1):
                        st.write(f"**Track {i}:**")
                        st.write(f"- {doc.page_content[:200]}...")
                        st.divider()
    
    # Save the assistant's response to state
    st.session_state.messages.append({"role": "assistant", "content": response})