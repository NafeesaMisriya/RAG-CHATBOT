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

            model=
            "llama-3.3-70b-versatile",

            temperature=0.2
        )

        self.prompt = (
            ChatPromptTemplate
            .from_template(
                """
You are DocuMind,
an educational document assistant.

Answer ONLY using the provided context.

Use the conversation history to resolve references such as:

- it
- its
- they
- them
- this
- that
- these
- those

If the answer cannot be found
inside the provided context, respond exactly:

"I could not find the answer in the document."

Conversation History:
{history}

Context:
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