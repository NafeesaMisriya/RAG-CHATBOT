import re

class QueryRouter:
    # Match standalone greetings (case-insensitive, allowing trailing spaces/punctuation)
    GREETINGS = re.compile(
        r'^\s*(hi+|hello+|hey+|hy+|yo+|good\s+morning|good\s+evening|good\s+afternoon|how\s+are\s+you(\s+doing)?|how\'s\s+it\s+going|what\'s\s+up)\s*[,\.\!\?]*\s*$',
        re.IGNORECASE
    )

    # Match standalone identity/who/what questions
    IDENTITY = re.compile(
        r'^\s*(who|what)\s+are\s+you\s*[,\.\!\?]*\s*$',
        re.IGNORECASE
    )

    # Match standalone capabilities / help requests
    CAPABILITIES = re.compile(
        r'^\s*(what\s+can\s+you\s+do|help|how\s+do\s+i\s+use\s+this(\s+chatbot)?|how\s+to\s+use\s+this(\s+chatbot)?)\s*[,\.\!\?]*\s*$',
        re.IGNORECASE
    )

    # Match standalone gratitude
    GRATITUDE = re.compile(
        r'^\s*(thanks|thank\s+you(\s+very\s+much)?)\s*[,\.\!\?]*\s*$',
        re.IGNORECASE
    )

    # Match standalone farewells
    FAREWELLS = re.compile(
        r'^\s*(bye|goodbye|bye\s+bye)\s*[,\.\!\?]*\s*$',
        re.IGNORECASE
    )

    @classmethod
    def classify_and_respond(cls, query: str):
        if not query:
            return "DOCUMENT_QUERY", None

        normalized = query.strip()

        if cls.GREETINGS.match(normalized):
            return (
                "GENERAL_CHAT",
                "Hello! How can I help you today? I can answer questions about your uploaded documents or help guide you through using the chatbot."
            )
        elif cls.IDENTITY.match(normalized):
            return (
                "GENERAL_CHAT",
                "I am ConteXora, your educational document intelligence assistant. I am designed to help you analyze and understand uploaded PDF documents by extracting text, tables, and figures, and answering your questions based on them."
            )
        elif cls.CAPABILITIES.match(normalized):
            return (
                "GENERAL_CHAT",
                "I can help you extract knowledge from PDF documents. You can upload one or more PDFs, select a document, and ask questions. I will locate the relevant text, tables, or figures, and provide a grounded explanation with sources and figures. To start, select a document from the sidebar and type your question!"
            )
        elif cls.GRATITUDE.match(normalized):
            return (
                "GENERAL_CHAT",
                "You're very welcome! Let me know if you have any other questions about your documents."
            )
        elif cls.FAREWELLS.match(normalized):
            return (
                "GENERAL_CHAT",
                "Goodbye! Have a great day, and feel free to ask for help whenever you need it."
            )

        return "DOCUMENT_QUERY", None
