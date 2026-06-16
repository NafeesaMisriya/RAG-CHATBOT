import requests
import uuid
import streamlit as st

API_URL = "http://127.0.0.1:8000"

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
}

.subtitle{
    text-align:center;
    color:#888;
    margin-bottom:2rem;
}

</style>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:

    st.session_state.messages = []

if "session_id" not in st.session_state:

    st.session_state.session_id = (
        str(
            uuid.uuid4()
        )
    )
# --------------------------------------------------
# LOAD DOCUMENTS FROM API
# --------------------------------------------------

try:

    response = requests.get(
        f"{API_URL}/documents",
        timeout=10
    )

    if response.status_code == 200:

        documents = response.json()

    else:

        documents = []

except Exception:

    documents = []

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

    # -------------------------
    # DOCUMENT SELECTOR
    # -------------------------

    document_names = [
        doc["name"]
        for doc in documents
    ]

    selected_document = None

    if documents:

        selected_document = (
            st.selectbox(
                "📚 Available Documents",
                document_names
            )
        )

        if (
            "active_document"
            not in st.session_state
        ):

            st.session_state.active_document = (
                selected_document
            )

        if (
            st.session_state.active_document
            !=
            selected_document
        ):

            st.session_state.messages = []

            st.session_state.session_id = (
                str(uuid.uuid4())
            )

            st.session_state.active_document = (
                selected_document
            )

        selected_collection = next(
            doc["collection"]
            for doc in documents
            if doc["name"]
            ==
            selected_document
        )

        if st.button(
            "❌ Delete Document"
        ):

            requests.delete(
                f"http://127.0.0.1:8000/documents/{selected_collection}"
            )

            st.success(
                "Deleted successfully"
            )

            st.rerun()
    else:

        st.info(
            "No documents uploaded."
        )

    st.divider()

    # -------------------------
    # PDF UPLOAD
    # -------------------------

    st.subheader(
        "Upload PDF"
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

            with st.spinner(
                "Uploading..."
            ):

                files = {
                    "file": (
                        uploaded_pdf.name,
                        uploaded_pdf.getvalue(),
                        "application/pdf"
                    )
                }

                response = requests.post(
                    f"{API_URL}/upload",
                    files=files
                )

                result = response.json()

                if (
                    result["message"]
                    ==
                    "Document already indexed."
                ):

                    st.warning(
                        "Document already indexed."
                    )

                else:

                    st.success(
                        "Document uploaded successfully."
                    )

                    st.rerun()

                
    st.divider()

    st.subheader(
        "Indexed Documents"
    )

    if documents:

        for doc in documents:

            st.markdown(
                f"📄 {doc['name']}"
            )

    else:

        st.caption(
            "No documents indexed."
        )

    st.divider()

    if st.button(
        "🗑 Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.session_state.session_id = (
            str(
                uuid.uuid4()
            )
        )

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
# NO DOCUMENT
# --------------------------------------------------

if not selected_document:

    st.info(
        "Upload a PDF to begin."
    )

    st.stop()


# --------------------------------------------------
# ACTIVE DOCUMENT
# --------------------------------------------------

st.success(
    f"📖 Current Document: "
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
# CHAT INPUT
# --------------------------------------------------

question = st.chat_input(
    "Ask a question..."
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

        placeholder = st.empty()

        try:

            response = requests.post(
                f"{API_URL}/chat/stream",

                json={
                    "question":
                    question,

                    "collection_name":
                    selected_collection,

                    "session_id":
                    st.session_state.session_id
                },

                stream=True,
                timeout=150
            )

            if (
                response.status_code
                != 200
            ):

                st.error(
                    response.text
                )

                st.stop()

            answer = ""

            for chunk in (
                response.iter_content(
                    chunk_size=None,
                    decode_unicode=True
                )
            ):

                if chunk:

                    answer += chunk

                    placeholder.markdown(
                        answer + "▌"
                    )
            placeholder.markdown(
                answer 
            )

            st.session_state.messages.append(
                {
                    "role":
                    "assistant",

                    "content":
                    answer
                }
            )

        except Exception as e:

            st.error(
                str(e)
            )
# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "DocuMind • AI-Powered Document Intelligence"
)