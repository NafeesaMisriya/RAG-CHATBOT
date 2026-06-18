"""Diagnostic: verify query-relevant image selection.

Run:  ./venv/Scripts/python.exe -m tests.diag_images
"""
from app.chat.rag_chatbot import RAGChatbot

bot = RAGChatbot()

CASES = [
    ("biology_txt", "give labelled image of brain"),
    ("biology_txt", "Explain parts of brain and its functions with figure"),
    ("biology_txt", "show all the diagrams of the brain"),
    ("biology_txt", "what is the recipe to cook pasta"),  # out-of-context
    ("real_image_test_pdf", "show me all the images"),
]


def run(collection, question):
    print("\n" + "=" * 70)
    print(f"Q: {question!r}   [{collection}]")
    print("=" * 70)

    contexts = bot._get_contexts(
        question=question,
        collection_name=collection,
        history=[],
    )

    wants_all = bot._wants_all_images(question)
    anchor = bot._anchor_pages(
        contexts,
        relax=wants_all,
        broad=wants_all,
    )
    print(f"Top text page/score: "
          f"{contexts[0].get('page')} / {contexts[0].get('rerank_score'):.3f}")
    print(f"Anchor (grounded) pages: {anchor}")

    images = bot._select_images(
        question=question,
        contexts=contexts,
        collection_name=collection,
    )

    print(f"Selected images: {len(images)}")
    for im in images:
        print(f"  img page={im['page']} score={im['rerank_score']:.3f} "
              f"{im['image_path']}")

    sources = bot._select_sources(contexts)
    print(f"Selected sources: {len(sources)}")
    for s in sources:
        print(f"  src page={s['page']}  {(s['title'] or '')[:40]}")


for col, q in CASES:
    try:
        run(col, q)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR on {q!r}: {e}")
