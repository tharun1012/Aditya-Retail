import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection with connection timeout
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'startup_template')

# Create client with timeout settings for faster failure detection
client = AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=5000,  # 5 second timeout for server selection
    connectTimeoutMS=5000,  # 5 second connection timeout
    socketTimeoutMS=10000,  # 10 second socket timeout
)
db = client[DB_NAME]

async def get_db():
    """Get database instance"""
    return db

# Initialize collections and indexes
async def init_db():
    """Initialize database collections and indexes"""
    
    # Create indexes for better performance
    await db.products.create_index("category")
    await db.products.create_index("brand") 
    await db.products.create_index("price")
    await db.products.create_index("stock")
    
    await db.orders.create_index("order_id", unique=True)
    await db.orders.create_index("customer_email")
    await db.orders.create_index("status")
    await db.orders.create_index("created_at")
    
    await db.chat_messages.create_index([("session_id", 1), ("timestamp", 1)])
    await db.chat_messages.create_index("agent_type")
    
    await db.chat_sessions.create_index("session_id")
    await db.chat_sessions.create_index("agent_type")
    
    await db.service_requests.create_index("request_id", unique=True)
    await db.service_requests.create_index("status")
    await db.service_requests.create_index("customer_email")
    
    await db.inventory_alerts.create_index("product_id")
    await db.inventory_alerts.create_index("status")
    await db.inventory_alerts.create_index("priority")

    # perf indexes (safe: failures are logged, never block startup)
    for _coll, _spec in [
        ("offline_invoices", [("document_type", 1), ("customer.email", 1), ("created_at", -1)]),
        ("offline_invoices", [("document_type", 1), ("customer.phone", 1), ("created_at", -1)]),
        ("users", "email"),
        ("users", "id"),
        ("users", "user_id"),
        ("service_tickets", "ticket_number"),
        ("notifications", [("user_id", 1), ("created_at", -1)]),
    ]:
        try:
            await db[_coll].create_index(_spec, background=True)
        except Exception as _e:
            print(f"index skipped on {_coll}: {_e}")
    
    print("Database initialized with indexes")

# Sample data seeding
async def seed_sample_data():
    """Seed database with sample product data"""
    
    # Check if products already exist
    existing_products = await db.products.count_documents({})
    if existing_products > 0:
        print(f"Database already has {existing_products} products")
        return
    
    sample_products = [
        {
            "id": "1",
            "name": "Hindware Built-In Microwave LORETO 25L",
            "category": "Built-In Microven",
            "price": 33990,
            "original_price": None,
            "image": "https://adityaretail.com/wp-content/uploads/2024/08/1080_hindware_built_in_microwave_loreto_25l-300x300.webp",
            "brand": "Hindware",
            "description": "25L Built-in Microwave with advanced cooking functions",
            "features": ["25L Capacity", "Built-in Design", "Multi-stage Cooking", "LED Display"],
            "stock": 15,
            "fast_moving": True
        },
        {
            "id": "2", 
            "name": "Hindware Built-In Microwave SPIRO 22L",
            "category": "Built-In Microven",
            "price": 29990,
            "original_price": None,
            "image": "https://adityaretail.com/wp-content/uploads/2024/08/1080_hindware_built_in_microwave_spiro_22l-300x300.webp",
            "brand": "Hindware",
            "description": "22L Built-in Microwave with stylish design",
            "features": ["22L Capacity", "Sleek Design", "Touch Controls", "Child Lock"],
            "stock": 8,
            "fast_moving": False
        },
        {
            "id": "3",
            "name": "iQ700 Built-in Microwave Oven Black",
            "category": "Microwave",
            "price": 112690,
            "original_price": 132490,
            "image": "https://adityaretail.com/wp-content/uploads/2024/08/18113214_BE732L1B1_STP_def-1-300x300.webp",
            "brand": "Siemens",
            "description": "Premium built-in microwave with advanced features",
            "features": ["Premium Quality", "Smart Sensors", "Auto Programs", "Black Finish"],
            "stock": 5,
            "fast_moving": True
        },
        {
            "id": "4",
            "name": "Dona FB 4B 60 Cooking Range",
            "category": "Cooking Range", 
            "price": 59990,
            "original_price": None,
            "image": "https://adityaretail.com/wp-content/uploads/2024/08/DONA-4B-60-picture-1-300x300.webp",
            "brand": "Dona",
            "description": "4 Burner cooking range with oven",
            "features": ["4 Burners", "Built-in Oven", "Auto Ignition", "Safety Features"],
            "stock": 12,
            "fast_moving": True
        },
        {
            "id": "5",
            "name": "Dino Induction Cooktop",
            "category": "Induction",
            "price": 4490,
            "original_price": None, 
            "image": "https://adityaretail.com/wp-content/uploads/2024/08/dino-induction-min-300x300.webp",
            "brand": "Dino",
            "description": "Efficient induction cooktop for modern kitchens",
            "features": ["2000W Power", "Touch Controls", "Energy Efficient", "Compact Design"],
            "stock": 25,
            "fast_moving": True
        },
        {
            "id": "6",
            "name": "iQ700 Flex Induction Cooktop 30 Cm Black",
            "category": "Induction",
            "price": 109640,
            "original_price": 128990,
            "image": "https://adityaretail.com/wp-content/uploads/2024/08/MCSA02951092_EX375FXB5I_ElectricHob_Siemens_STP_def-300x300.webp",
            "brand": "Siemens",
            "description": "Premium flex induction with advanced technology",
            "features": ["FlexInduction Zone", "Touch Control", "30cm Width", "Premium Black"],
            "stock": 3,
            "fast_moving": False
        },
        {
            "id": "7",
            "name": "Series 6 Washing Machine Top Loader 680 RPM",
            "category": "10 KG TOP LOAD WM",
            "price": 48390,
            "original_price": None,
            "image": "https://adityaretail.com/wp-content/uploads/2024/07/19574348_WOI105B0IN_STP_def.webp",
            "brand": "Bosch",
            "description": "10kg top loading washing machine with multiple programs",
            "features": ["10kg Capacity", "680 RPM", "Multiple Programs", "Digital Display"],
            "stock": 7,
            "fast_moving": True
        },
        {
            "id": "8",
            "name": "Series 4 Free-standing Fridge 147.4 X 53.8 Cm Mid Night Blue",
            "category": "226 Liters Single Door Fridge",
            "price": 30490,
            "original_price": None,
            "image": "https://adityaretail.com/wp-content/uploads/2024/07/23139045_CST22U14PI_STP_def-300x300.webp",
            "brand": "Bosch",
            "description": "226L single door refrigerator in midnight blue", 
            "features": ["226L Capacity", "Single Door", "Energy Efficient", "Midnight Blue"],
            "stock": 10,
            "fast_moving": True
        },
        {
            "id": "9",
            "name": "Series 4 Wall-mounted Cooker Hood 90 Cm Flat Black",
            "category": "Hood",
            "price": 58990,
            "original_price": None,
            "image": "https://adityaretail.com/wp-content/uploads/2024/07/21089725_DWKA98H60I_STP_def-300x300.webp",
            "brand": "Bosch",
            "description": "90cm wall mounted cooker hood with LED controls",
            "features": ["90cm Width", "LED Controls", "Air Extraction", "Touch Control"],
            "stock": 6,
            "fast_moving": False
        }
    ]
    
    await db.products.insert_many(sample_products)
    print(f"Seeded {len(sample_products)} sample products")

# TDS (Tax Deducted at Source) rates seeding
TDS_TABLE_TITLE = "Master TDS Rate Chart TY 2026-27 and Reference Table"

TDS_RAW_ROWS = [
    ("192 old Section / 392 New Section Table Sl No 1", "Salary", "-", "Based on taxable salary income", "text", "Slab Based"),
    ("192A Old Section / 392(7)", "EPF Withdrawal", "1004", "50000", "percentage", 0.10),
    ("194D Old Section / 393(1) New Section Table Sl No 1(i)", "Insurance Commission", "1005", "Applicable threshold", "text", "Applicable"),
    ("194H Old Section / 393(1) New Section Table Sl No 1(ii)", "Commission / Brokerage", "1006", "20000", "percentage", 0.02),
    ("194I Old Section / 393(1) New Section Table Sl No 2(ii)D(a)", "Rent – Machinery / Plant / Equipment", "1008", "Applicable threshold – ₹50,000 per month", "percentage", 0.02),
    ("194I Old Section / 393(1) New Section Table Sl no 2(ii)D(b)", "Rent – Land / Building / Furniture", "1009", "Applicable threshold – ₹50,000 per month", "percentage", 0.10),
    ("194IC Old Section / 393(1) New Section Table Sl no 3(ii)", "Joint Development Agreement", "1011", "As applicable", "percentage", 0.10),
    ("194LA Old Section / 393(1)  New Section Table Sl no 3(iii)", "Acquisition Compensation", "1012", "500000", "percentage", 0.10),
    ("194K Old Section / 393(1) New Section Table Sl no 4(i)", "Mutual Fund / Unit Income", "1013", "10000", "percentage", 0.10),
    ("194LBA Old Section / 393(1) New Section Table Sl no 4(ii)", "Business Trust – Interest", "1014", "As applicable", "text", "Applicable"),
    ("194LBA Old Section / 393(1) New Section Table Sl no 4(ii)", "Business Trust – Dividend", "1015", "As applicable", "text", "Applicable"),
    ("194LBA Old Section / 393(1) New Section Table Sl no 4(ii)", "REIT Rental Distribution", "1016", "As applicable", "text", "Applicable"),
    ("194LBB Old Section / 393(1) New Section Table Sl no 4(iii)", "Investment Fund Income", "1017", "As applicable", "text", "Applicable"),
    ("194LBC Old Section / 393(1) New Section Table Sl no 4(iv)", "Securitisation Trust Income", "1018", "As applicable", "text", "Applicable"),
    ("193 Old Section / 393(1) New Section Table Sl no 5(i)", "Interest on Securities", "1019", "10000", "percentage", 0.10),
    ("194A Old Section / 393(1) New Section Table Sl no 5(ii)D(a)", "Interest – Senior Citizen", "1020", "100000", "percentage", 0.10),
    ("194A Old Section / 393(1) New Section Table Sl no 5(ii)D(b)", "Interest – Others", "1021", "50000", "percentage", 0.10),
    ("194A Old Section / 393(1) New Section Table Sl no 5(iii)", "Other Interest Cases", "1022", "10000", "percentage", 0.10),
    ("194C Old Section / 393(1) New Section Table Sl no 6(i)D(a)", "Contractor – Individual / HUF", "1023", "₹30,000 single / ₹1,00,000 aggregate", "percentage", 0.01),
    ("194C Old Section / 393(1) New Section Table Sl no 6(i)D(b)", "Contractor – Others", "1024", "₹30,000 single / ₹1,00,000 aggregate", "percentage", 0.02),
    ("194J(a) Old Section / 393(1) New Section Table Sl no 6(iii)D(a)", "Technical Services", "1026", "50000", "percentage", 0.02),
    ("194J(b) Old Section / 393(1) New Section Table Sl no 6(iii)D(b)", "Professional Services", "1027", "50000", "percentage", 0.10),
    ("194J Old Section / 393(1) New Section Table Sl no 6(iii)D(b)", "Director Fees / Commission", "1028", "Generally no standard threshold", "text", "Applicable"),
    ("194 Old Section / 393(1) New Section Table Sl no 7", "Dividend", "1029", "10000", "percentage", 0.10),
    ("194DA Old Section / 393(1) New Section Table Sl no 8(i)", "Life Insurance Payout (Taxable Cases)", "1030", "100000", "percentage", 0.02),
    ("194Q Old Section / 393(1) New Section Table Sl no 8(ii)", "Purchase of Goods", "1031", "Buyer turnover > ₹10 crore + purchases > ₹50 lakh", "percentage", 0.001),
    ("194R  Old Section / 393(1) New Section Table Sl no 8(iv)", "Benefit / Perquisite", "1033", "20000", "percentage", 0.10),
    ("194O Old Section / 393(1) New Section Table Sl no 8(v)", "E-commerce Transactions", "1035", "Applicable threshold", "percentage", 0.01),
    ("194S Old Section / 393(1) New Section Table Sl no 8(vi)", "Virtual Digital Asset Transfer", "1037", "Category based", "percentage", 0.01),
    ("194B Old Section / 393(1) New Section Table Sl no 1", "Lottery / Game Winnings", "1058", "10000", "percentage", 0.30),
    ("194BA Old Section / 393(1) New Section Table Sl no 2", "Online Gaming Winnings", "1060", "As applicable", "percentage", 0.30),
    ("194BB Old Section / 393(1) New Section Table Sl no 3", "Horse Race Winnings", "1062", "10000", "percentage", 0.30),
    ("194G Old Section / 393(1) New Section Table Sl no 4", "Lottery Commission", "1063", "20000", "percentage", 0.02),
    ("194N Old Section / 393(1) New Section Table Sl no 5", "Cash Withdrawal", "1064 / 1065", "Depends on filer status", "text", "Applicable"),
    ("194T Old Section / 393(1) New Section Table Sl no 5", "Partner Payment by Firm", "1067", "20000", "percentage", 0.10),
]

async def seed_tds_rates():
    """Idempotent: upserts the master TDS rate chart into tds_rates on every startup."""
    upserted = 0
    for old_section, nature, code, threshold, rate_type, rate_val in TDS_RAW_ROWS:
        doc = {
            "table_title": TDS_TABLE_TITLE,
            "old_section": old_section,
            "nature_of_payment": nature,
            "code": code,
            "threshold": str(threshold),
            "rate_type": rate_type,
            "rate_value": rate_val if rate_type == "percentage" else None,
            "rate_text": rate_val if rate_type == "text" else None,
        }
        result = await db.tds_rates.update_one(
            {"code": code, "nature_of_payment": nature},
            {"$set": doc},
            upsert=True
        )
        if result.upserted_id or result.modified_count:
            upserted += 1
    total = await db.tds_rates.count_documents({})
    print(f"TDS rates seeded/updated: {upserted}. Total tds_rates documents: {total}")