from app.generation.generator import (
    Generator
)

generator = Generator()

contexts = [
    {
        "page": 10,
        "content":
        "DNA consists of two strands "
        "forming a double helix. "
        "The strands are held together "
        "by complementary base pairing."
    }
]

history = [
    {
        "role": "user",
        "content": "Tell me about DNA"
    },
    {
        "role": "assistant",
        "content": "DNA stores genetic information."
    }
]

answer = generator.generate(
    query="What shape does it have?",
    contexts=contexts,
    history=history
)

print("\nANSWER:\n")

print(answer)