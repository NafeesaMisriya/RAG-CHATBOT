class PageFusion:

    def fuse(
        self,
        nodes
    ):

        page_map = {}

        for node in nodes:

            page = node.page

            if page not in page_map:

                page_map[page] = {

                    "text": [],

                    "captions": [],

                    "tables": [],

                    "unit": node.unit,

                    "title": node.title,

                    "source_document":
                    node.source_document
                }

            if node.node_type == "text":

                page_map[page][
                    "text"
                ].append(
                    node.content
                )

            elif node.node_type == "image":

                if node.caption:

                    page_map[page][
                        "captions"
                    ].append(
                        node.caption
                    )

            elif node.node_type == "table":

                if node.table_data:

                    page_map[page][
                        "tables"
                    ].append(
                        node.table_data
                    )

        fused_nodes = []

        from app.models.node import Node
        import uuid

        for page, data in (
            page_map.items()
        ):

            sections = []

            if data["text"]:

                sections.append(
                    "TEXT:\n"
                    + "\n".join(
                        data["text"]
                    )
                )

            if data["captions"]:

                sections.append(
                    "IMAGE DESCRIPTIONS:\n"
                    + "\n".join(
                        data["captions"]
                    )
                )

            if data["tables"]:

                sections.append(
                    "TABLES:\n"
                    + "\n\n".join(
                        data["tables"]
                    )
                )

            fused_content = (
                "\n\n".join(
                    sections
                )
            )

            fused_node = Node(

                node_id=str(
                    uuid.uuid4()
                ),

                node_type="text",

                page=page,

                content=fused_content,

                source_document=
                data[
                    "source_document"
                ],

                unit=data["unit"],

                title=data["title"]
            )

            fused_nodes.append(
                fused_node
            )

        return fused_nodes