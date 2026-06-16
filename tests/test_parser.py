from app.parsing.pdf_parser import PDFParser


def main():

    parser = PDFParser(
        pdf_path="data/raw/book.pdf"
    )

    nodes = parser.parse()

    print(
        f"\nTotal Nodes:"
        f" {len(nodes)}\n"
    )

    for node in nodes[:10]:

        print(node)


if __name__ == "__main__":
    main()