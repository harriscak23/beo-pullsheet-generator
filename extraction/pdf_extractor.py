import pdfplumber


def extract_pdf(pdf_path):
    """
    Extract raw text and tables from a BEO PDF.

    Args:
        pdf_path (str): Path to the BEO PDF.

    Returns:
        dict: Raw extracted BEO data.
    """

    beo_data = {
        "file": pdf_path,
        "page_count": 0,
        "pages": []
    }

    with pdfplumber.open(pdf_path) as pdf:

        beo_data["page_count"] = len(pdf.pages)

        for page_number, page in enumerate(pdf.pages, start=1):

            page_data = {
                "page": page_number,
                "text": page.extract_text() or "",
                "tables": []
            }

            tables = page.extract_tables()

            for table in tables:

                cleaned_table = []

                for row in table:

                    if row is None:
                        continue

                    cleaned_row = []

                    for cell in row:

                        if cell is None:
                            cleaned_row.append(None)
                        else:
                            cell = str(cell).strip()

                            if cell == "":
                                cell = None

                            cleaned_row.append(cell)

                    cleaned_table.append(cleaned_row)

                page_data["tables"].append(cleaned_table)

            beo_data["pages"].append(page_data)

    return beo_data