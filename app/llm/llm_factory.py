import os

from dotenv import load_dotenv

load_dotenv()


class LLMFactory:

    @staticmethod
    def get_provider():

        return os.getenv(
            "LLM_PROVIDER",
            "groq"
        ).lower()

    @staticmethod
    def _create_groq():

        from langchain_groq import (
            ChatGroq
        )

        return ChatGroq(

            api_key=
            os.getenv(
                "GROQ_API_KEY"
            ),

            model=
            os.getenv(
                "GROQ_MODEL",
                "llama-3.3-70b-versatile"
            ),

            temperature=0.2
        )

    @staticmethod
    def _create_gemini():

        from langchain_google_genai import (
            ChatGoogleGenerativeAI
        )

        return ChatGoogleGenerativeAI(

            google_api_key=
            os.getenv(
                "GEMINI_API_KEY"
            ),

            model=
            os.getenv(
                "GEMINI_MODEL",
                "gemini-2.5-flash"
            ),

            temperature=0.2
        )

    @staticmethod
    def get_generation_llm():

        provider = (
            LLMFactory.get_provider()
        )

        # ------------------------
        # User selected Gemini
        # ------------------------

        if provider == "gemini":

            try:

                llm = (
                    LLMFactory
                    ._create_gemini()
                )

                llm.invoke(
                    "ping"
                )

                print(
                    "\nUsing Gemini"
                )

                return llm

            except Exception as e:

                print(
                    f"\nGemini unavailable: {e}"
                )

                print(
                    "\nFailing over to Groq..."
                )

                return (
                    LLMFactory
                    ._create_groq()
                )

        # ------------------------
        # User selected Groq
        # ------------------------

        try:

            llm = (
                LLMFactory
                ._create_groq()
            )

            llm.invoke(
                "ping"
            )

            print(
                "\nUsing Groq"
            )

            return llm

        except Exception as e:

            print(
                f"\nGroq unavailable: {e}"
            )

            print(
                "\nFailing over to Gemini..."
            )

            return (
                LLMFactory
                ._create_gemini()
            )
        

    @staticmethod
    def get_alternate_llm():

        provider = (
            LLMFactory.get_provider()
        )

        if provider == "groq":

            return (
                LLMFactory
                ._create_gemini()
            )

        return (
            LLMFactory
            ._create_groq()
        )