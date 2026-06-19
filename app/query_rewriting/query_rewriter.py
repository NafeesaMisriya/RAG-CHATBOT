import os

from dotenv import load_dotenv

load_dotenv()


class QueryRewriter:

    def __init__(self):

        self.provider = os.getenv(
            "LLM_PROVIDER",
            "groq"
        ).lower()

        self.groq_model = os.getenv(
            "GROQ_REWRITE_MODEL",
            "llama-3.1-8b-instant"
        )

        self.gemini_model = os.getenv(
            "GEMINI_REWRITE_MODEL",
            "gemini-2.5-flash-lite"
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
   - his
   - her

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

            # ------------------------
            # GEMINI FIRST
            # ------------------------

            if self.provider == "gemini":

                try:

                    import google.generativeai as genai

                    genai.configure(
                        api_key=os.getenv(
                            "GEMINI_API_KEY"
                        )
                    )

                    model = (
                        genai.GenerativeModel(
                            self.gemini_model
                        )
                    )

                    response = (
                        model.generate_content(
                            prompt
                        )
                    )

                    rewritten = (
                        response.text
                        .strip()
                    )

                    print(
                        "\nRewritten Query (Gemini):",
                        rewritten
                    )

                    return rewritten

                except Exception as e:

                    print(
                        f"\nGemini Rewrite Failed: {e}"
                    )

                    print(
                        "\nTrying Groq..."
                    )

                    from groq import Groq

                    client = Groq(
                        api_key=os.getenv(
                            "GROQ_API_KEY"
                        )
                    )

                    response = (
                        client.chat.completions.create(
                            model=
                            self.groq_model,

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

                    print(
                        "\nRewritten Query (Groq Fallback):",
                        rewritten
                    )

                    return rewritten

            # ------------------------
            # GROQ FIRST
            # ------------------------

            try:

                from groq import Groq

                client = Groq(
                    api_key=os.getenv(
                        "GROQ_API_KEY"
                    )
                )

                response = (
                    client.chat.completions.create(
                        model=
                        self.groq_model,

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

                print(
                    "\nRewritten Query (Groq):",
                    rewritten
                )

                return rewritten

            except Exception as e:

                print(
                    f"\nGroq Rewrite Failed: {e}"
                )

                print(
                    "\nTrying Gemini..."
                )

                import google.generativeai as genai

                genai.configure(
                    api_key=os.getenv(
                        "GEMINI_API_KEY"
                    )
                )

                model = (
                    genai.GenerativeModel(
                        self.gemini_model
                    )
                )

                response = (
                    model.generate_content(
                        prompt
                    )
                )

                rewritten = (
                    response.text
                    .strip()
                )

                print(
                    "\nRewritten Query (Gemini Fallback):",
                    rewritten
                )

                return rewritten

        except Exception as e:

            print(
                f"\nAll Rewrite Providers Failed: {e}"
            )

            return query