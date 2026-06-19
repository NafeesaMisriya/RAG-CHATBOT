import os

from dotenv import load_dotenv

from app.llm.llm_factory import (
    LLMFactory
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

        self.llm = (
            LLMFactory
            .get_generation_llm()
        )

        self.prompt = (
            ChatPromptTemplate
            .from_template(
                """
You are ConteXora, an educational document intelligence assistant.
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

            payload = {

                "history":
                history_text,

                "context":
                context_text,

                "question":
                query
            }

            try:

                return (
                    self.chain.invoke(
                        payload
                    )
                )

            except Exception as e:

                print(
                    f"\nPrimary LLM Failed: {e}"
                )

                try:

                    print(
                        "\nTrying Fallback LLM..."
                    )

                    fallback_llm = (
                        LLMFactory
                        .get_alternate_llm()
                    )

                    fallback_chain = (
                        self.prompt
                        |
                        fallback_llm
                        |
                        self.parser
                    )

                    return (
                        fallback_chain.invoke(
                            payload
                        )
                    )

                except Exception as e2:

                    print(
                        f"\nFallback Failed: {e2}"
                    )

                    return (
                        "⚠️ All language "
                        "model providers are "
                        "currently unavailable."
                    )
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

        payload = {

            "history":
            history_text,

            "context":
            context_text,

            "question":
            query
        }

        try:

            for chunk in (
                self.chain.stream(
                    payload
                )
            ):

                yield chunk

        except Exception as e:

            print(
                f"\nPrimary Stream Failed: {e}"
            )

            try:

                print(
                    "\nTrying Fallback Stream..."
                )

                fallback_llm = (
                    LLMFactory
                    .get_alternate_llm()
                )

                fallback_chain = (
                    self.prompt
                    |
                    fallback_llm
                    |
                    self.parser
                )

                for chunk in (
                    fallback_chain.stream(
                        payload
                    )
                ):

                    yield chunk

            except Exception as e2:

                print(
                    f"\nFallback Stream Failed: {e2}"
                )

                yield (
                    "⚠️ All language "
                    "model providers are "
                    "currently unavailable."
                )