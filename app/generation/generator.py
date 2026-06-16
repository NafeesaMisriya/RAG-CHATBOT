import os
import time
from groq import Groq 
from dotenv import load_dotenv

load_dotenv()


class Generator:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )
        
        

        self.model_name = (
            "llama-3.3-70b-versatile"
        )

    def build_prompt(
        self,
        query,
        contexts,
        history=None
    ):

        if history is None:
            history = []

        history_text = ""

        for msg in history:

            history_text += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

        context_text = ""

        for context in contexts:

            context_text += (
                f"\n\nPage "
                f"{context['page']}:\n"
                f"{context['content']}"
            )

        prompt = f"""
You are a helpful educational assistant.

Answer ONLY using the provided context.

Use the conversation history when resolving references
such as "it", "they", "that structure", etc.

If the answer is not found in the context,
say:

"I could not find the answer in the document."

Conversation History:
{history_text}

Context:
{context_text}

Question:
{query}

Answer:
"""

        return prompt

    def generate(
        self,
        query,
        contexts,
        history=None
    ):

        if history is None:
            history = []

        prompt = self.build_prompt(
            query,
            contexts,
            history
        )

        response = (
            self.client.chat.completions.create(
                model=self.model_name,

                messages=[
                    {
                        "role":
                        "user",

                        "content":
                        prompt
                    }
                ],

                temperature=0.2
            )
        )

        return (
            response
            .choices[0]
            .message
            .content
        )