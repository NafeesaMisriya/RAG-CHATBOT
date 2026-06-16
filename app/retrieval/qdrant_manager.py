import os
from uuid import UUID

from dotenv import load_dotenv

from qdrant_client import QdrantClient

from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
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

        print(
            f"Collection '{collection_name}' "
            f"created successfully."
        )

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
                        record.source_document
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