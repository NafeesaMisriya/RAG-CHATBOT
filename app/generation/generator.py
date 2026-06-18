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

Rules:

1. Answer using the information found in the document context.

2. If the user asks to "explain more", "elaborate", "give details",
   "simplify", "summarize", or "provide examples", you MAY expand the
   explanation using general educational knowledge, but ONLY to clarify
   or deepen concepts that are already present in the document context.

3. Never introduce completely new topics that are not related to the
   document context. Stay within the subject matter of the document.

4. If the answer cannot be found in the document AND is not a request to
   expand on a concept already in the document, respond exactly:

   "I could not find the answer in the document."

5. Structure your answer clearly using, where useful:
   - A short explanation
   - Key Points (bullet list)
   - Examples (when they aid understanding)

6. Use the conversation history to resolve references such as it, its,
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