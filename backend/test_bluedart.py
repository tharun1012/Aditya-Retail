import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env')

from bluedart_integration import bluedart_service

test_order = {
    "order_number": "TEST-ORDER-001",
    "shipping_address": {
        "name": "Test Customer",
        "address": "123 Test Street, Koramangala",
        "pincode": "560034",
        "phone": "9999999999",
    },
    "weight": 1.0,
    "cod_amount": 0,
    "declared_value": 500,
    "shipper_name": "Aditya Retail",
    "shipper_address": "REPLACE_WITH_REAL_PICKUP_ADDRESS",
    "shipper_pincode": "560058",
    "shipper_phone": "9686229746",
}

print("Configured:", bluedart_service.is_configured())
result = bluedart_service.generate_waybill(test_order)
print("Result:", result)
