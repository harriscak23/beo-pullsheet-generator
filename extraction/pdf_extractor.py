import pdfplumber

pdf_path = "pdf/BEO.pdf"

with pdfplumber.open(pdf_path) as pdf:
    print(f"Number of pages: {len(pdf.pages)}")

    for page_number, page in enumerate(pdf.pages, start=1):
        print(f"\n--- PAGE {page_number} ---")

        text = page.extract_text()

        if text:
            print(text)


with pdfplumber.open(pdf_path) as pdf:

    for page_number, page in enumerate(pdf.pages, start=1):

        tables = page.extract_tables()

        print(f"Page {page_number}: {len(tables)} tables")

        for table in tables:
            for row in table:
                print(row)