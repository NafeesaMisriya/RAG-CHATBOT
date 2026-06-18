import json
import os
import requests
import uuid
import streamlit as st

API_URL = "http://127.0.0.1:8000"


def absolute_url(url):

    """Turn a server-relative '/files/...' path into a full URL the
    browser/Streamlit can fetch."""

    if not url:

        return None

    if url.startswith("http"):

        return url

    return f"{API_URL}{url}"


def clean_source_text(text):

    cleaned = []

    for line in text.splitlines():

        upper = line.strip().upper()

        if (
            upper.startswith("TITLE:")
            or
            upper.startswith("UNIT:")
            or
            upper.startswith("PAGE:")
        ):
            continue

        cleaned.append(line)

    return "\n".join(cleaned)
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

if "document_chats" not in st.session_state:

    st.session_state.document_chats = {}

if "session_ids" not in st.session_state:

    st.session_state.session_ids = {}

if "messages" not in st.session_state:

    st.session_state.messages = []

if "session_id" not in st.session_state:

    st.session_state.session_id = str(
        uuid.uuid4()
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


        selected_collection = next(
            doc["collection"]
            for doc in documents
            if doc["name"]
            ==
            selected_document
        )

        if (
            selected_collection
            not in st.session_state.document_chats
        ):

            st.session_state.document_chats[
                selected_collection
            ] = []

        if (
            selected_collection
            not in st.session_state.session_ids
        ):

            st.session_state.session_ids[
                selected_collection
            ] = str(
                uuid.uuid4()
            )

        st.session_state.messages = (
            st.session_state.document_chats[
                selected_collection
            ]
        )

        st.session_state.session_id = (
            st.session_state.session_ids[
                selected_collection
            ]
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

                print("Status Code:", response.status_code)
                print("Response Text:", response.text)

                if response.status_code != 200:

                    st.error(response.text)

                else:

                    result = response.json()

                    if (
                        result.get("message")
                        ==
                        "Document already exists."
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

        if documents:

            current_collection = next(
                doc["collection"]
                for doc in documents
                if doc["name"] ==
                selected_document
            )

            st.session_state.document_chats[
                current_collection
            ] = []

            st.session_state.session_ids[
                current_collection
            ] = str(
                uuid.uuid4()
            )

            st.session_state.messages = []

            st.session_state.session_id = (
                st.session_state.session_ids[
                    current_collection
                ]
            )


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

            # ----------------------------------------------------
            # Single SSE stream carries the answer tokens AND the
            # source/image metadata. No second /chat call, so the
            # answer is generated and stored exactly once.
            # ----------------------------------------------------

            answer = ""

            images = []

            sources = []

            for line in (
                response.iter_lines(
                    decode_unicode=True
                )
            ):

                if not line:

                    continue

                if not line.startswith("data: "):

                    continue

                payload = json.loads(
                    line[len("data: "):]
                )

                event_type = payload.get("type")

                if event_type == "token":

                    answer += payload["data"]

                    placeholder.markdown(
                        answer + "▌"
                    )

                elif event_type == "sources":

                    sources = payload["data"]

                elif event_type == "images":

                    images = payload["data"]

            placeholder.markdown(
                answer
            )

            # -------------------
            # DISPLAY IMAGES
            # -------------------

            if images:

                st.markdown(
                    "### 🖼 Retrieved Images"
                )

                for image in images:

                    # Prefer the local file (same machine as the
                    # Streamlit process); fall back to the server URL.
                    local_path = image.get("image_path")

                    if (
                        local_path
                        and
                        os.path.exists(local_path)
                    ):

                        image_src = local_path

                    else:

                        image_src = absolute_url(
                            image.get("image_url")
                        )

                    if image_src:

                        try:

                            st.image(
                                image_src,
                                use_container_width=True
                            )

                            st.caption(
                                f"Page {image['page']}"
                            )

                        except Exception:

                            st.warning(
                                f"Image not found: "
                                f"{image_src}"
                            )

            # -------------------
            # DISPLAY SOURCES
            # -------------------

            if sources:

                # Show only the single most relevant source (sources
                # are already ordered by rerank relevance) and link to
                # that page, instead of listing every retrieved chunk.
                source = sources[0]

                with st.expander(
                    "📖 Source"
                ):

                    title = (
                        source.get("title")
                        or
                        "Document Source"
                    )

                    cleaned_content = (
                        clean_source_text(
                            source.get("content")
                            or ""
                        )
                    )

                    snippet = (
                        cleaned_content[:500]
                    )

                    st.markdown(
                        f"### {title}"
                    )

                    source_url = (
                        absolute_url(
                            source.get("source_url")
                        )
                    )

                    if source_url:

                        st.markdown(
                            f"📄 [Open page "
                            f"{source['page']}]"
                            f"({source_url})"
                        )

                    else:

                        st.markdown(
                            f"📄 Page "
                            f"{source['page']}"
                        )

                    st.markdown(
                        f"{snippet}..."
                    )

            assistant_message = {
                "role":
                "assistant",

                "content":
                answer
            }

            # NOTE: st.session_state.messages and
            # document_chats[selected_collection] are the SAME list
            # object (assigned by reference above), so a single append
            # updates both. Appending to both duplicated every answer.
            st.session_state.messages.append(
                assistant_message
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