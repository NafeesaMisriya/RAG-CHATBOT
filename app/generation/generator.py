import os

from dotenv import load_dotenv

from langchain_groq import (
    ChatGroq
)

from langchain_core.prompts import (
    ChatPromptTemplate
)

from langchain_core.output_parsers import (
    StrOutputParser
)

load_dotenv()


class Generator:

    def __init__(self):

        self.llm = ChatGroq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            ),

            # Configurable via .env so dev can use a higher-limit/cheaper
            # model (e.g. llama-3.1-8b-instant) without code changes.
            model=os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            ),

            temperature=0.2
        )

        self.prompt = (
            ChatPromptTemplate
            .from_template(
                """
You are DocuMind, an educational document intelligence assistant.
Your primary source of truth is the provided document context.

RULES

1. Answer using the information found in the document context.

2. If the user asks to "explain more", "elaborate", "give details",
   "simplify", "summarize", or "provide examples", you MAY expand the
   explanation using general educational knowledge - but ONLY to clarify
   or deepen a concept that is ALREADY present in the document context.
   Keep the expansion tightly connected to that concept.

3. Never introduce completely new topics that are unrelated to the
   document. Stay within the subject matter of the document.

4. If the answer cannot be found in the document, and the question is not
   a request to expand on a concept already in the document, respond with
   EXACTLY this sentence and nothing else:

   "I could not find the answer in the document."

5. Structure the answer for a student, using only the parts that help:
   - **Explanation** - a short, plain-language overview
   - **Key Points** - a concise bullet list of the essentials
   - **Examples** - simple examples or analogies, when they aid learning

6. Prefer clear, friendly, student-friendly language. Define difficult
   terms in simple words. Be accurate and concise; do not pad the answer.

7. Use the conversation history to resolve references such as it, its,
   they, them, this, that, these, those.

Conversation History:
{history}

Document Context:
{context}

Question:
{question}

Answer:
"""
            )
        )

        self.parser = (
            StrOutputParser()
        )

        self.chain = (
            self.prompt
            |
            self.llm
            |
            self.parser
        )

    def _build_context_text(
        self,
        contexts
    ):

        context_text = ""

        for context in contexts:

            context_text += (
                f"\n\nPage "
                f"{context['page']}:\n"
                f"{context['content']}"
            )

        return context_text

    def _build_history_text(
        self,
        history
    ):

        history_text = ""

        for msg in history:

            history_text += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

        return history_text

    def generate(
        self,
        query,
        contexts,
        history=None
    ):

        if history is None:

            history = []

        context_text = (
            self._build_context_text(
                contexts
            )
        )

        history_text = (
            self._build_history_text(
                history
            )
        )

        response = (
            self.chain.invoke(
                {
                    "history":
                    history_text,

                    "context":
                    context_text,

                    "question":
                    query
                }
            )
        )

        return response

    def stream_generate(
        self,
        query,
        contexts,
        history=None
    ):

        if history is None:

            history = []

        context_text = (
            self._build_context_text(
                contexts
            )
        )

        history_text = (
            self._build_history_text(
                history
            )
        )

        for chunk in (
            self.chain.stream(
                {
                    "history":
                    history_text,

                    "context":
                    context_text,

                    "question":
                    query
                }
            )
        ):

            yield chunk