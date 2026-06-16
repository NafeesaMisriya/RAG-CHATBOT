import json
import os


REGISTRY_PATH = (
    "data/document_registry.json"
)


class DocumentRegistry:

    @staticmethod
    def load():

        if not os.path.exists(
            REGISTRY_PATH
        ):

            return []

        try:

            with open(
                REGISTRY_PATH,
                "r"
            ) as f:

                content = f.read().strip()

                if not content:

                    return []

                return json.loads(
                    content
                )

        except Exception:

            with open(
                REGISTRY_PATH,
                "w"
            ) as f:

                json.dump(
                    [],
                    f,
                    indent=4
                )

            return []
    @staticmethod
    def save(
        documents
    ):

        with open(
            REGISTRY_PATH,
            "w"
        ) as f:

            json.dump(
                documents,
                f,
                indent=4
            )

    @staticmethod
    def register(
        document_name,
        collection_name
    ):

        docs = (
            DocumentRegistry.load()
        )

        exists = any(
            doc["collection"]
            ==
            collection_name
            for doc in docs
        )

        if not exists:

            docs.append(
                {
                    "name":
                    document_name,

                    "collection":
                    collection_name
                }
            )

            DocumentRegistry.save(
                docs
            )

    @staticmethod
    def get_documents():

        return (
            DocumentRegistry.load()
        )