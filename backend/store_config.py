"""Store Configuration for Aditya Retail"""

STORES = {
    "BNS": {
        "code": "BNS",
        "name": "Banaswadi Store",
        "type": "Siemens and Bosch Brand Store",
        "address": "No.5AC, 927, 5th 'A' Cross, HRBR Layout I Block, Kalyanagar",
        "city": "Bangalore",
        "pincode": "560043",
        "phone": "080 25422525 / 080 43365877",
        "whatsapp": "6362629159",
        "email": "banaswadi.adityaretail@gmail.com",
        "invoice_prefix": "BNS",
        "so_prefix": "BNSSO"
    },
    "ARM": {
        "code": "ARM",
        "name": "Malleswaram Store",
        "type": "Bosch Brand Store",
        "address": "No 21/1, 16th Cross, Sampige Road, Malleswaram",
        "city": "Bangalore",
        "pincode": "560003",
        "phone": "080 23563499 / 080 40972295",
        "whatsapp": "7676574938",
        "email": "bosch.adityaretail@gmail.com",
        "invoice_prefix": "ARM",
        "so_prefix": "ARMSO"
    },
    "DAS": {
        "code": "DAS",
        "name": "Dasarahalli Store",
        "type": "Bosch Brand Store",
        "address": "No 628 NR Complex, 3rd Cross, Nethaji Nagar, Dasarahalli, T Dasarahalli, Near Jalahalli Cross",
        "city": "Bangalore",
        "pincode": "560057",
        "phone": "080 29917499",
        "whatsapp": "9482403499",
        "email": "dasarahalli.adityaretail@gmail.com",
        "invoice_prefix": "DAS",
        "so_prefix": "DASSO"
    },
    "HRBR": {
        "code": "HRBR",
        "name": "Electrolux HRBR Store",
        "type": "Electrolux Brand Store",
        "address": "HRBR Layout, Banaswadi",
        "city": "Bangalore",
        "pincode": "560043",
        "phone": "080 25422525",
        "whatsapp": "9876543210",
        "email": "hrbr.adityaretail@gmail.com",
        "invoice_prefix": "HRBR",
        "so_prefix": "HRBRSO"
    }
}

# Company Details
COMPANY = {
    "name": "Aditya Retail",
    "tagline": "Premium Bosch, Siemens & Hindware Home Appliances",
    "website": "www.adityaretail.com",
    "gst_number": "29AAAAA0000A1Z5",  # Update with actual GST
    "primary_email": "info@adityaretail.com",
    "support_phone": "080 25422525"
}

def get_store(store_code: str):
    """Get store configuration by code"""
    return STORES.get(store_code)

def get_all_stores():
    """Get all stores"""
    return STORES

def get_financial_year():
    """Get current financial year in format YY-YY"""
    from datetime import datetime
    now = datetime.now()
    
    if now.month >= 4:  # April to March
        fy_start = now.year
        fy_end = now.year + 1
    else:
        fy_start = now.year - 1
        fy_end = now.year
    
    return f"{str(fy_start)[2:]}-{str(fy_end)[2:]}"

def generate_invoice_number(store_code: str, document_type: str, sequence: int):
    """Generate invoice number with store code and financial year"""
    store = get_store(store_code)
    if not store:
        raise ValueError(f"Invalid store code: {store_code}")
    
    fy = get_financial_year()
    
    if document_type == "sales_order":
        prefix = store["so_prefix"]
    else:  # invoice
        prefix = store["invoice_prefix"]
    
    return f"{prefix}{fy}/{sequence:04d}"


# ---- Header branding for Sales Order / Invoice preview + PDF ----
# NOTE: ARH and ART are not in STORES above, so this is a standalone map keyed by store code.
HEADER_TITLE = "Aditya Retail"

STORE_HEADER_SUBTITLES = {
    "DAS": "Dasarahalli Bosch Brand Store",
    "ARM": "Malleswaram Bosch Brand Store",
    "BNS": "Banaswadi Siemens And Bosch Brand Store",
    "ARH": "Malleswaram Haier Experience Center",
    "ART": "RT Nagar Bosch Brand Store",
    "HRBR": "HRBR Electrolux Exclusive Store",
}

def get_store_header_subtitle(store_code=None, doc_number=""):
    """Store-specific line under 'Aditya Retail'. Falls back to the doc number prefix (e.g. DASSO0204/26-27 -> DAS)."""
    code = (store_code or "").upper()
    if code not in STORE_HEADER_SUBTITLES:
        for c in sorted(STORE_HEADER_SUBTITLES, key=len, reverse=True):
            if (doc_number or "").upper().startswith(c):
                code = c
                break
    return STORE_HEADER_SUBTITLES.get(code, "")
