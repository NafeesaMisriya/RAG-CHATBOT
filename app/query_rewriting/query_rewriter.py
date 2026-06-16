"""import re


class QueryRewriter:

    def __init__(self):

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
            "him"
        ]

    def _extract_topic(
        self,
        history
    ):

        user_messages = [
            msg["content"]
            for msg in history
            if msg["role"] == "user"
        ]

        if not user_messages:
            return None

        for message in reversed(
            user_messages
        ):

            lower = message.lower()

            patterns = [
                r"what is (.+)",
                r"who is (.+)",
                r"define (.+)",
                r"explain (.+)",
                r"tell me about (.+)"
            ]

            for pattern in patterns:

                match = re.search(
                    pattern,
                    lower
                )

                if match:

                    topic = (
                        match.group(1)
                        .strip(" ?.")
                    )

                    if (
                        len(topic.split())
                        <= 8
                    ):

                        return topic

        return (
            user_messages[-1]
            .strip(" ?.")
        )

    def rewrite(
        self,
        query,
        history
    ):

        if not history:

            return query

        topic = self._extract_topic(
            history
        )

        if not topic:

            return query

        q = query.lower()

        if not any(
            ref in q
            for ref in self.reference_words
        ):

            return query

        rewritten = query

        replacements = {
            "its": f"{topic}'s",
            "it": topic,
            "they": topic,
            "them": topic,
            "their": f"{topic}'s",
            "this": topic,
            "that": topic,
            "these": topic,
            "those": topic,
            "he": topic,
            "she": topic,
            "his": f"{topic}'s",
            "her": f"{topic}'s",
            "him": topic
        }

        for old, new in (
            replacements.items()
        ):

            rewritten = re.sub(
                rf"\b{old}\b",
                new,
                rewritten,
                flags=re.IGNORECASE
            )

        return rewritten"""

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

        self.model_name = (
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
            "him"
        ]

    def needs_rewrite(
        self,
        query
    ):

        query_lower = (
            query.lower()
        )

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

        for msg in history[-6:]:

            conversation += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

        prompt = f"""
You are a query rewriting assistant.

Convert the current question into a
fully standalone question.

Use conversation history to resolve:

- it
- its
- they
- them
- their
- this
- that
- elaborate more
- explain more
- tell me more

Return ONLY the rewritten query.

Conversation:

{conversation}

Current Question:

{query}
"""

        try:

            response = (
                self.client.chat.completions.create(
                    model=
                    self.model_name,

                    messages=[
                        {
                            "role":
                            "user",

                            "content":
                            prompt
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