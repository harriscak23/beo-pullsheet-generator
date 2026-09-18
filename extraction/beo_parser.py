import re
from datetime import datetime


def get_all_text(beo_data):
    """Join text from every page into one string for simple searches."""
    parts = []
    for page in beo_data.get("pages", []):
        parts.append(page.get("text") or "")
    return "\n".join(parts)


def get_all_tables(beo_data):
    """Flatten every table from every page into one list."""
    tables = []
    for page in beo_data.get("pages", []):
        for table in page.get("tables", []):
            tables.append(table)
    return tables


def parse_contract_number(beo_data):
    """
    Look for: Contract: 00009191
    Return None if not found (do not invent a value).
    """
    text = get_all_text(beo_data)
    match = re.search(r"Contract:\s*(\d+)", text)
    if match:
        return match.group(1)
    return None


def parse_event_date(beo_data):
    """
    Look for: Event Date: Saturday, June 13, 2026
    Convert to MM/DD, e.g. 06/13
    """
    text = get_all_text(beo_data)
    match = re.search(
        r"Event Date:\s*[A-Za-z]+,\s*([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})",
        text,
    )
    if not match:
        return None

    month_name = match.group(1)
    day = match.group(2)
    year = match.group(3)

    try:
        # Parse the full date, then format only month/day
        dt = datetime.strptime(f"{month_name} {day} {year}", "%B %d %Y")
        return dt.strftime("%m/%d")
    except ValueError:
        return None


def find_location_row(beo_data):
    """
    Find the LOCATION AND TIMES data row.
    Expected columns:
    Building Name | Room Name | Guest Count | Guaranteed Count | Start Time | End Time
    """
    for table in get_all_tables(beo_data):
        if not table:
            continue

        # First cell often says "LOCATION AND TIMES"
        first_cell = (table[0][0] or "") if table[0] else ""
        if "LOCATION AND TIMES" not in first_cell:
            continue

        # Data is usually the last row in this small table
        if len(table) >= 3:
            return table[-1]

    return None


def parse_building_name(beo_data):
    row = find_location_row(beo_data)
    if not row or len(row) < 1:
        return None
    return row[0]


def parse_start_time(beo_data):
    """Extract ONLY start time (ignore end time)."""
    row = find_location_row(beo_data)
    if not row or len(row) < 5:
        return None
    return row[4]  # Start Time column


def parse_guest_count(beo_data):
    """
    Read Guest Count and Guaranteed Count.
    final_guest_count = whichever is higher.
    """
    row = find_location_row(beo_data)
    if not row or len(row) < 4:
        return {
            "guest_count": None,
            "guaranteed_count": None,
            "final_guest_count": None,
        }

    def to_int(value):
        if value is None:
            return None
        try:
            return int(str(value).strip())
        except ValueError:
            return None

    guest_count = to_int(row[2])
    guaranteed_count = to_int(row[3])

    counts = [c for c in (guest_count, guaranteed_count) if c is not None]
    final_guest_count = max(counts) if counts else None

    return {
        "guest_count": guest_count,
        "guaranteed_count": guaranteed_count,
        "final_guest_count": final_guest_count,
    }


def is_menu_junk_row(description):
    """Skip headers / section dividers that are not real food items."""
    if not description:
        return True

    cleaned = description.strip()
    junk_exact = {
        "MENU SELECTIONS",
        "Description",
        "~",
    }

    if cleaned in junk_exact:
        return True

    # Section labels like ~Beverages~
    if cleaned.startswith("~") and cleaned.endswith("~"):
        return True

    return False


def is_package_header(description, uom):
    """
    Package rows are NOT menu items.
    Example: "Belgian Waffles Breakfast Package" with UOM "Packages"
    """
    if not description:
        return False

    # Strong signal: Delivery UOM is Packages
    if uom and uom.strip().lower() == "packages":
        return True

    # Backup signal: name ends with "Package"
    if description.strip().lower().endswith("package"):
        return True

    return False


def parse_menu_selections(beo_data):
    """
    Extract menu rows until STAFFING.

    Package inheritance:
    - Package header stores qty + UOM temporarily
    - Next real item with missing UOM inherits those values
    - Package name itself is NOT added to menu_selections
    """
    menu_items = []
    pending_package = None  # {"quantity": ..., "uom": ...}

    for table in get_all_tables(beo_data):
        if not table:
            continue

        first_cell = (table[0][0] or "") if table[0] else ""
        if "MENU SELECTIONS" not in first_cell:
            continue

        for row in table:
            if not row:
                continue

            description = row[0]
            quantity = row[1] if len(row) > 1 else None
            uom = row[2] if len(row) > 2 else None

            # Normalize description newlines into spaces for readability
            if description:
                description = " ".join(str(description).split())

            if is_menu_junk_row(description):
                continue

            # Convert quantity safely
            qty_value = None
            if quantity is not None:
                try:
                    qty_value = int(str(quantity).strip())
                except ValueError:
                    qty_value = None

            # --- PACKAGE HEADER ---
            # Remember qty/UOM for the next real item; do not append this row.
            if is_package_header(description, uom):
                pending_package = {
                    "quantity": qty_value,
                    "uom": uom,
                }
                continue

            # --- REAL MENU ITEM ---
            item_qty = qty_value
            item_uom = uom

            # If this item has no UOM, and a package is pending, inherit.
            if pending_package and not item_uom:
                if item_qty is None:
                    item_qty = pending_package["quantity"]
                item_uom = pending_package["uom"]
                pending_package = None  # consumed

            # If the item already has its own UOM, clear any unused package.
            elif pending_package and item_uom:
                pending_package = None

            menu_items.append({
                "name": description,
                "quantity": item_qty,
                "uom": item_uom,
            })

        # Only one MENU SELECTIONS table expected
        break

    return menu_items


def parse_number_of_tables(beo_data):
    """
    Look in SPECIAL INSTRUCTIONS for patterns like:
    Client responsible for securing (3)-6ft tables...
    Extract the number inside parentheses before 'tables'.
    """
    text = get_all_text(beo_data)

    # Prefer the explicit (3)-6ft tables style first
    match = re.search(r"\((\d+)\)\s*-?\s*\d*\s*ft\s*tables?", text, re.IGNORECASE)
    if match:
        return int(match.group(1))

    return None


def parse_beo(beo_data):
    """
    Main entry point.
    Takes raw extractor output and returns a clean structured dictionary.
    Missing values stay as None — we do not invent data.
    """
    guest_info = parse_guest_count(beo_data)

    return {
        "contract_number": parse_contract_number(beo_data),
        "event_date": parse_event_date(beo_data),
        "start_time": parse_start_time(beo_data),
        "building_name": parse_building_name(beo_data),
        "guest_count": guest_info["guest_count"],
        "guaranteed_count": guest_info["guaranteed_count"],
        "final_guest_count": guest_info["final_guest_count"],
        "menu_selections": parse_menu_selections(beo_data),
        "number_of_tables": parse_number_of_tables(beo_data),
    }