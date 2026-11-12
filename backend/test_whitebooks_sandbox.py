import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from services.whitebooks_client import whitebooks_client, WhitebooksAuthError

print("--- Testing E-Way Bill auth ---")
try:
    result = whitebooks_client.authenticate_ewaybill()
    print(f"SUCCESS: {result}")
except WhitebooksAuthError as e:
    print(f"FAILED: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

print("\n--- Testing E-Invoice auth ---")
try:
    token = whitebooks_client._authenticate_einvoice()
    print(f"SUCCESS: got token: {token[:20]}...")
except WhitebooksAuthError as e:
    print(f"FAILED: {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
