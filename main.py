from extraction.pdf_extractor import extract_pdf
from extraction.beo_parser import parse_beo


pdf_path = "pdf/sample_beo.pdf"

# Step 1: raw PDF extraction (unchanged module)
beo_data = extract_pdf(pdf_path)

# Step 2: interpret BEO meaning
parsed = parse_beo(beo_data)

print("=== PARSED BEO ===")
print()
print(f"Contract Number: {parsed['contract_number']}")
print(f"Event Date: {parsed['event_date']}")
print(f"Start Time: {parsed['start_time']}")
print(f"Building: {parsed['building_name']}")
print(f"Guest Count: {parsed['guest_count']}")
print(f"Guaranteed Count: {parsed['guaranteed_count']}")
print(f"Final Guest Count: {parsed['final_guest_count']}")
print(f"Number of Tables: {parsed['number_of_tables']}")
print()
print("Menu Selections:")

if not parsed["menu_selections"]:
    print("  (none found)")
else:
    for item in parsed["menu_selections"]:
        print(f"- {item['name']}")
        print(f"  Quantity: {item['quantity']}")
        print(f"  UOM: {item['uom']}")
        print()