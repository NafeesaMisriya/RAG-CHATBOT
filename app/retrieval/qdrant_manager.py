import os
from uuid import UUID

from dotenv import load_dotenv

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    MatchAny,
    PayloadSchemaType
)

load_dotenv()


class QdrantManager:

    def __init__(self):

        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=120

        )

    def create_collection(
        self,
        collection_name: str,
        vector_size: int
    ):

        collections = self.client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if collection_name in existing_collections:

            existing_info = (
                self.client.get_collection(
                    collection_name
                )
            )

            existing_dim = (
                existing_info
                .config
                .params
                .vectors
                .size
            )

            if existing_dim != vector_size:

                raise ValueError(
                    f"Collection dimension mismatch.\n"
                    f"Existing: {existing_dim}\n"
                    f"Requested: {vector_size}\n"
                    f"Delete and recreate collection."
                )

            print(
                f"Collection '{collection_name}' "
                f"already exists."
            )

            return

        self.client.create_collection(
            collection_name=collection_name,

            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        self.ensure_payload_indexes(
            collection_name
        )

        print(
            f"Collection '{collection_name}' "
            f"created successfully."
        )

    def ensure_payload_indexes(
        self,
        collection_name: str
    ):

        """Create the payload indexes needed to filter figures by page and
        node type. Idempotent: indexes that already exist are ignored."""

        indexes = [
            ("metadata.node_type", PayloadSchemaType.KEYWORD),
            ("page", PayloadSchemaType.INTEGER),
        ]

        for field_name, schema in indexes:

            try:

                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema=schema
                )

            except Exception:

                # Index already exists (or is being built) — safe to skip.
                pass

    def recreate_collection(
        self,
        collection_name: str,
        vector_size: int
    ):

        collections = self.client.get_collections()

        existing_collections = [
            collection.name
            for collection in collections.collections
        ]

        if collection_name in existing_collections:

            self.client.delete_collection(
                collection_name
            )

            print(
                f"Deleted existing "
                f"collection '{collection_name}'."
            )

        self.client.create_collection(
            collection_name=collection_name,

            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

        print(
            f"Created collection "
            f"'{collection_name}'."
        )

    def delete_collection(
        self,
        collection_name: str
    ):

        self.client.delete_collection(
            collection_name
        )

        print(
            f"Collection '{collection_name}' "
            f"deleted."
        )

    def insert_vectors(
        self,
        collection_name: str,
        vector_records,
        batch_size: int = 50
    ):

        total = len(vector_records)

        for start in range(
            0,
            total,
            batch_size
        ):

            batch = vector_records[
                start:start + batch_size
            ]

            points = []

            for record in batch:

                point = PointStruct(
                    id=UUID(
                        record.chunk_id
                    ),

                    vector=record.vector,

                    payload={
                        "content":
                        record.content,

                        "page":
                        record.page,

                        "source_document":
                        record.source_document,

                        "metadata":
                        record.metadata
                    }
                )

                points.append(
                    point
                )

            self.client.upsert(
                collection_name=
                collection_name,

                points=
                points
            )

            print(
                f"Uploaded "
                f"{min(start + batch_size, total)}"
                f"/{total}"
            )
    def search(
        self,
        collection_name: str,
        query_vector,
        limit: int = 5
    ):

        results = self.client.query_points(
            collection_name=collection_name,

            query=query_vector,

            limit=limit
        )

        return results

    def get_image_nodes_by_pages(
        self,
        collection_name: str,
        pages: list,
        limit: int = 256
    ):

        """Fetch image nodes that live on the given pages.

        Image captions are too thin to surface reliably through vector
        search, so figures are discovered by page instead: once we know
        which pages the answer is grounded in, we pull every image node on
        those pages and let the reranker pick the ones related to the query.
        Returns a list of context dicts shaped like Retriever.retrieve()."""

        if not pages:

            return []

        page_values = [
            p for p in pages
            if p is not None
        ]

        if not page_values:

            return []

        scroll_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.node_type",
                    match=MatchValue(value="image")
                ),
                FieldCondition(
                    key="page",
                    match=MatchAny(any=page_values)
                )
            ]
        )

        points, _ = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=scroll_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        contexts = []

        for point in points:

            payload = point.payload or {}

            metadata = payload.get(
                "metadata",
                {}
            ) or {}

            contexts.append(
                {
                    "content":
                    payload.get("content", ""),

                    "page":
                    payload.get("page"),

                    "source_document":
                    payload.get("source_document"),

                    "score":
                    0.0,

                    "metadata":
                    metadata,

                    "title":
                    metadata.get("title"),

                    "unit":
                    metadata.get("unit"),

                    "node_type":
                    "image",

                    "image_path":
                    metadata.get("image_path")
                }
            )

        return contexts

    def get_all_image_nodes(
        self,
        collection_name: str,
        limit: int = 512
    ):

        """Fetch every image node in the collection.

        Used for explicit image queries ('give the periodic table image',
        'show figure 1.5') where the relevant image may be on a different
        page than the text that discusses it. After fetching, the caller
        reranks all candidates against the query and picks the best match."""

        scroll_filter = Filter(
            must=[
                FieldCondition(
                    key="metadata.node_type",
                    match=MatchValue(value="image")
                )
            ]
        )

        points, _ = self.client.scroll(
            collection_name=collection_name,
            scroll_filter=scroll_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        contexts = []

        for point in points:

            payload = point.payload or {}

            metadata = payload.get(
                "metadata",
                {}
            ) or {}

            contexts.append(
                {
                    "content":
                    payload.get("content", ""),

                    "page":
                    payload.get("page"),

                    "source_document":
                    payload.get("source_document"),

                    "score":
                    0.0,

                    "metadata":
                    metadata,

                    "title":
                    metadata.get("title"),

                    "unit":
                    metadata.get("unit"),

                    "node_type":
                    "image",

                    "image_path":
                    metadata.get("image_path")
                }
            )

        return contexts

    def get_collection_info(
        self,
        collection_name: str
    ):

        return self.client.get_collection(
            collection_name
        )

    def list_collections(self):

        return self.client.get_collections()

    def count_points(
        self,
        collection_name: str
    ):

        collection_info = (
            self.client.get_collection(
                collection_name
            )
        )

        return (
            collection_info.points_count
        )