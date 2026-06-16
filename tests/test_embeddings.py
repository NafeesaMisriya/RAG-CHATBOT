from app.embedding.embedding_manager import (
    EmbeddingManager
)

embedding_manager = (
    EmbeddingManager()
)

vector = embedding_manager.embed_text(
    "What is a neural network?"
)

print(len(vector))

print(vector[:10])
