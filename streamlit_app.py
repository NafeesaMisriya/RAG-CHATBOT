import os
import streamlit as st

from app.chat.rag_chatbot import (
    RAGChatbot
)

from app.ingestion.document_ingestor import (
    DocumentIngestor
)

from app.utils.document_registry import (
    DocumentRegistry
)

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide"
)

# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
<style>

.block-container{
    padding-top:2rem;
}

.main-title{
    text-align:center;
    font-size:3rem;
    font-weight:700;
    margin-bottom:0;
}

.subtitle{
    text-align:center;
    color:#888;
    margin-bottom:2rem;
}

.source-box{
    padding:12px;
    border-radius:10px;
    border:1px solid #444;
    margin-bottom:10px;
}

</style>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "chatbot" not in st.session_state:

    st.session_state.chatbot = (
        RAGChatbot()
    )

if "messages" not in st.session_state:

    st.session_state.messages = []

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("# 📚 DocuMind")

    st.markdown(
        """
AI-powered document assistant

• PDF Question Answering  
• Semantic Search  
• Conversation Memory  
• Context-Aware Responses
"""
    )

    st.divider()

    # ----------------------------
    # AVAILABLE DOCUMENTS
    # ----------------------------

    documents = (
        DocumentRegistry.get_documents()
    )

    document_names = [
        doc["name"]
        for doc in documents
    ]

    selected_document = None

    if document_names:

        selected_document = (
            st.selectbox(
                "📚 Available Documents",
                document_names
            )
        )

    else:

        st.info(
            "No documents uploaded yet."
        )

    st.divider()

    # ----------------------------
    # UPLOAD PDF
    # ----------------------------

    st.subheader(
        "Upload New PDF"
    )

    uploaded_pdf = st.file_uploader(
        "Choose PDF",
        type=["pdf"]
    )

    if uploaded_pdf:

        if st.button(
            "🚀 Ingest Document",
            use_container_width=True
        ):

            collection_name = (
                uploaded_pdf.name
                .replace(".pdf", "")
                .replace(" ", "_")
                .lower()
            )

            exists = any(
                doc["collection"]
                == collection_name
                for doc in documents
            )

            if exists:

                st.warning(
                    "Document already ingested."
                )

            else:

                with st.spinner(
                    "Processing document..."
                ):

                    os.makedirs(
                        "data/uploads",
                        exist_ok=True
                    )

                    pdf_path = os.path.join(
                        "data/uploads",
                        uploaded_pdf.name
                    )

                    with open(
                        pdf_path,
                        "wb"
                    ) as f:

                        f.write(
                            uploaded_pdf.getbuffer()
                        )

                    ingestor = (
                        DocumentIngestor()
                    )

                    ingestor.ingest(
                        pdf_path=pdf_path,
                        collection_name=
                        collection_name
                    )

                    DocumentRegistry.register(
                        document_name=
                        uploaded_pdf.name,

                        collection_name=
                        collection_name
                    )

                st.success(
                    "Document indexed successfully."
                )

                st.rerun()

    st.divider()

    # ----------------------------
    # CLEAR CHAT
    # ----------------------------

    if st.button(
        "🗑 Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        try:

            st.session_state.chatbot.memory.clear()

        except:
            pass

        st.rerun()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
<div class="main-title">
📚 DocuMind
</div>
""",
    unsafe_allow_html=True
)

st.markdown(
    """
<div class="subtitle">
Chat intelligently with your documents
</div>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# NO DOCUMENT SELECTED
# --------------------------------------------------

if not selected_document:

    st.info(
        """
Upload and ingest a PDF to start chatting.
"""
    )

    st.stop()

# --------------------------------------------------
# CURRENT DOCUMENT
# --------------------------------------------------

st.success(
    f"📖 Currently Chatting With: "
    f"{selected_document}"
)

# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for message in (
    st.session_state.messages
):

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

# --------------------------------------------------
# FIND COLLECTION
# --------------------------------------------------

selected_collection = None

for doc in documents:

    if (
        doc["name"]
        ==
        selected_document
    ):

        selected_collection = (
            doc["collection"]
        )

        break

# --------------------------------------------------
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask something about your document..."
)

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            question
        )

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Thinking..."
        ):

            result = (
                st.session_state
                .chatbot
                .ask(
                    question,
                    collection_name=
                    selected_collection
                )
            )

            answer = (
                result["answer"]
            )

            st.markdown(
                answer
            )

            if (
                "sources"
                in result
                and result["sources"]
            ):

                with st.expander(
                    "📖 View Sources"
                ):

                    for source in (
                        result["sources"]
                    ):

                        st.markdown(
                            f"""
### Page {source['page']}

**Similarity Score:** {source['score']:.4f}

---

{source['content'][:500]}
"""
                        )

                        st.divider()

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "DocuMind • AI-Powered Document Intelligence"
)