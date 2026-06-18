import pdfplumber


class TableExtractor:

    def extract_tables(
        self,
        pdf_path,
        page_number
    ):

        tables_text = []

        try:

            with pdfplumber.open(
                pdf_path
            ) as pdf:

                page = pdf.pages[
                    page_number - 1
                ]

                tables = (
                    page.extract_tables()
                )

                for idx, table in enumerate(
                    tables,
                    start=1
                ):

                    table_text = (
                        f"TABLE {idx}\n"
                    )

                    for row in table:

                        row = [
                            str(cell).strip()
                            if cell
                            else ""
                            for cell in row
                        ]

                        table_text += (
                            " | ".join(row)
                            + "\n"
                        )

                    tables_text.append(
                        table_text
                    )

        except Exception as e:

            print(
                f"Table extraction error: "
                f"{e}"
            )

        return tables_text