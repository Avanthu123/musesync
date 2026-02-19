import os
import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# =========================
# CONFIG
# =========================
CSV_FILE = r"deduplicated_music_data.csv"
DB_LOCATION = "./chroma_music_mood_db"
COLLECTION_NAME = "music_mood_recommendations"
BATCH_SIZE = 1000

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(CSV_FILE)

# =========================
# EMBEDDING MODEL
# =========================
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

# =========================
# VECTOR STORE
# =========================
vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=DB_LOCATION,
    embedding_function=embeddings
)

existing_count = vector_store._collection.count()
print("Existing documents in DB:", existing_count)

# =========================
# PREPARE DOCUMENTS
# =========================
documents = []
ids = []

def categorize_mood(valence, energy, acousticness):
    """Map audio features to mood categories"""
    if valence > 0.6 and energy > 0.6:
        return "upbeat, energetic, happy"
    elif valence > 0.6 and energy <= 0.6:
        return "joyful, peaceful, calm"
    elif valence <= 0.6 and energy > 0.6:
        return "intense, aggressive, powerful"
    else:
        return "sad, melancholic, introspective"

for i, row in df.iterrows():
    mood = categorize_mood(row['valence'], row['energy'], row['acousticness'])
    
    content = (
        f"Track: {row['track_name']} by {row['artists']}. "
        f"Genre: {row['track_genre']}. "
        f"Mood: {mood}. "
        f"Danceability: {row['danceability']:.2f}, "
        f"Energy: {row['energy']:.2f}, "
        f"Valence: {row['valence']:.2f}, "
        f"Acousticness: {row['acousticness']:.2f}, "
        f"Tempo: {row['tempo']:.1f} BPM. "
        f"Popularity: {row['popularity']}/100."
    )
 
    doc = Document(
        page_content=content,
        metadata={
            "track_id": row["track_id"],
            "track_name": row["track_name"],
            "artists": row["artists"],
            "genre": row["track_genre"],
            "mood": mood,
            "valence": float(row["valence"]),
            "energy": float(row["energy"]),
            "danceability": float(row["danceability"]),
            "acousticness": float(row["acousticness"]),
            "popularity": int(row["popularity"]),
            "duration_ms": int(row["duration_ms"])
        },
        id=str(i)
    )

    documents.append(doc)
    ids.append(str(i))

# =========================
# INGEST (ONLY IF EMPTY)
# =========================
if existing_count == 0:
    print("Ingesting documents into Chroma...")

    for i in range(0, len(documents), BATCH_SIZE):
        batch_docs = documents[i:i + BATCH_SIZE]
        batch_ids = ids[i:i + BATCH_SIZE]

        vector_store.add_documents(
            documents=batch_docs,
            ids=batch_ids
        )

        print(f"Inserted documents {i} to {i + len(batch_docs)}")

    print("Final document count:", vector_store._collection.count())
else:
    print("Using existing embeddings. No re-ingestion needed.")

# =========================
# RETRIEVER
# =========================
retriever = vector_store.as_retriever(
    search_kwargs={"k": 15}
)