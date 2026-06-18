import os

from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class QueryRewriter:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )

        # Configurable via .env; defaults to a small, high-limit model
        # since rewriting is a lightweight task.
        self.model_name = os.getenv(
            "GROQ_REWRITE_MODEL",
            "llama-3.1-8b-instant"
        )

        self.reference_words = [

            "it",
            "its",
            "they",
            "them",
            "their",
            "this",
            "that",
            "these",
            "those",
            "he",
            "she",
            "his",
            "her",
            "him",

            "more",
            "summary",
            "summarise",
            "summarize",
            "describe",
            "details",
            "detail",
            "elaborate",
            "continue",
            "explain",
            "expand",
            "briefly",
            "deeply"
        ]

    def needs_rewrite(
        self,
        query
    ):

        query_lower = query.lower()

        followup_patterns = [

            "tell me more",
            "explain more",
            "elaborate more",
            "give more details",
            "summarise it",
            "summarize it",
            "describe it",
            "what about it",
            "what are its",
            "what are their",
            "continue",
            "expand",
            "give summary",
            "give a summary"
        ]

        if any(
            pattern in query_lower
            for pattern in followup_patterns
        ):
            return True

        return any(
            word in query_lower
            for word in self.reference_words
        )

    def rewrite(
        self,
        query,
        history
    ):

        if (
            not history
            or
            not self.needs_rewrite(
                query
            )
        ):
            return query

        conversation = ""

        for msg in history[-10:]:

            conversation += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

        prompt = f"""
You are a query rewriting assistant for a RAG chatbot.

Your job is to convert follow-up questions into
fully standalone retrieval questions.

Rules:

1. Resolve all references:
   - it
   - its
   - they
   - them
   - their
   - this
   - that
   - these
   - those
   - he
   - she

2. Resolve vague follow-up requests:
   - explain more
   - elaborate more
   - tell me more
   - continue
   - describe it
   - summarise it
   - give details

3. Preserve the user's intent.

4. Output ONLY the rewritten query.

Examples:

User: What is DNA?
User: Explain its structure.

Output:
Explain the structure of DNA

---

User: What is mutation?
User: Tell me more.

Output:
Tell me more about mutation

---

User: What is the Snake and the Mirror?
User: Summarise it.

Output:
Summarise the story The Snake and the Mirror

Conversation:

{conversation}

Current Question:

{query}
"""

        try:

            response = (
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0
                )
            )

            rewritten = (
                response
                .choices[0]
                .message
                .content
                .strip()
            )

            return rewritten

        except Exception:

            return query