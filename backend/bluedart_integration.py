"""
Blue Dart Direct API Integration
==================================
Direct SOAP-based integration with Blue Dart's Waybill Generation service.
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from zeep import Client, Settings
    from zeep.exceptions import Fault
except ImportError:
    raise ImportError(
        "zeep is required for Blue Dart SOAP integration. "
        "Install with: pip install zeep --break-system-packages"
    )

logger = logging.getLogger("bluedart_integration")

BLUEDART_LICENCE_KEY = os.environ.get("BLUEDART_LICENCE_KEY", "")
BLUEDART_LOGIN_ID = os.environ.get("BLUEDART_LOGIN_ID", "")
BLUEDART_VERSION = os.environ.get("BLUEDART_VERSION", "1.3")
BLUEDART_CUSTOMER_CODE = os.environ.get("BLUEDART_CUSTOMER_CODE", "")
BLUEDART_ORIGIN_AREA = os.environ.get("BLUEDART_ORIGIN_AREA", "")

WAYBILL_WSDL_URL = (
    "https://netconnect.bluedart.com/Ver1.10/ShippingAPI/WayBill/WayBillGeneration.svc?wsdl"
)


class BlueDartError(Exception):
    pass


class BlueDartService:
    def __init__(self):
        self._client: Optional[Client] = None
        self._configured = bool(
            BLUEDART_LICENCE_KEY and BLUEDART_LOGIN_ID and BLUEDART_CUSTOMER_CODE
        )
        if not self._configured:
            logger.warning(
                "Blue Dart credentials are not fully configured. "
                "Set BLUEDART_LICENCE_KEY, BLUEDART_LOGIN_ID, and "
                "BLUEDART_CUSTOMER_CODE as backend secrets."
            )

    def _get_client(self) -> Client:
        if self._client is None:
            settings = Settings(strict=False, xml_huge_tree=True)
            self._client = Client(WAYBILL_WSDL_URL, settings=settings)
        return self._client

    def _profile(self) -> Dict[str, Any]:
        return {
            "Api_type": "S",
            "LicenceKey": BLUEDART_LICENCE_KEY,
            "LoginID": BLUEDART_LOGIN_ID,
            "Version": BLUEDART_VERSION,
        }

    def is_configured(self) -> bool:
        return self._configured

    def generate_waybill(self, order: Dict[str, Any]) -> Dict[str, Any]:
        if not self._configured:
            return {
                "status": "error",
                "awb_number": None,
                "message": (
                    "Blue Dart credentials not configured. Set "
                    "BLUEDART_LICENCE_KEY, BLUEDART_LOGIN_ID, BLUEDART_CUSTOMER_CODE."
                ),
            }

        addr = order.get("shipping_address", {})
        is_cod = float(order.get("cod_amount", 0) or 0) > 0

        request_payload = {
            "Consignee": {
                "ConsigneeName": addr.get("name", ""),
                "ConsigneeAddress1": addr.get("address", "")[:30],
                "ConsigneeAddress2": addr.get("address", "")[30:60],
                "ConsigneeAddress3": addr.get("address", "")[60:90],
                "ConsigneePincode": addr.get("pincode", ""),
                "ConsigneeMobile": addr.get("phone", ""),
                "ConsigneeTelephone": "",
                "ConsigneeAttention": addr.get("name", ""),
            },
            "Shipper": {
                "CustomerCode": BLUEDART_CUSTOMER_CODE,
                "CustomerName": order.get("shipper_name", ""),
                "CustomerAddress1": order.get("shipper_address", ""),
                "CustomerPincode": order.get("shipper_pincode", ""),
                "CustomerMobile": order.get("shipper_phone", ""),
                "OriginArea": BLUEDART_ORIGIN_AREA,
                "Sender": "1",
                "IsToPayCustomer": False,
                "IsForcePickup": False,
            },
            "Services": {
                "ProductCode": "A",
                "SubProductCode": "P",
                "ActualWeight": order.get("weight", 0.5),
                "CreditReferenceNo": order.get("order_number", ""),
                "DeclaredValue": order.get("declared_value", 0),
                "InvoiceNo": order.get("invoice_number", order.get("order_number", "")),
                "InvoiceDate": order.get("invoice_date", datetime.utcnow().strftime("%Y-%m-%d")),
                "PieceCount": order.get("piece_count", 1),
                "CollectableAmount": order.get("cod_amount", 0) if is_cod else 0,
                "PickupDate": order.get("pickup_date", datetime.utcnow().strftime("%Y-%m-%d")),
                "PickupTime": order.get("pickup_time", "1400"),
            },
        }

        try:
            client = self._get_client()
            response = client.service.GenerateWayBill(
                Request=request_payload,
                Profile=self._profile(),
            )

            result = response.GenerateWayBillResult if hasattr(response, "GenerateWayBillResult") else response

            status_info = getattr(getattr(result, "Status", None), "WayBillGenerationStatus", None)
            status_text = getattr(status_info, "StatusInformation", "") if status_info else ""

            awb_no = getattr(result, "AWBNo", None)

            if awb_no:
                return {
                    "status": "success",
                    "awb_number": awb_no,
                    "token_number": getattr(result, "TokenNumber", None),
                    "destination_location": getattr(result, "DestinationLocation", None),
                    "destination_area": getattr(result, "DestinationArea", None),
                    "message": status_text or "Waybill generated successfully",
                }
            else:
                return {
                    "status": "error",
                    "awb_number": None,
                    "message": status_text or "Waybill generation failed with no AWB returned",
                }

        except Fault as e:
            logger.error(f"Blue Dart SOAP fault: {e}")
            return {"status": "error", "awb_number": None, "message": f"SOAP error: {str(e)}"}
        except Exception as e:
            logger.error(f"Blue Dart waybill generation error: {e}")
            return {"status": "error", "awb_number": None, "message": str(e)}

    def cancel_waybill(self, awb_number: str) -> Dict[str, Any]:
        if not self._configured:
            return {"status": "error", "message": "Blue Dart credentials not configured"}

        try:
            client = self._get_client()
            response = client.service.CancelWaybill(
                Request={"AWBNo": awb_number},
                Profile=self._profile(),
            )
            return {"status": "success", "message": str(response)}
        except Exception as e:
            logger.error(f"Blue Dart waybill cancellation error: {e}")
            return {"status": "error", "message": str(e)}


bluedart_service = BlueDartService()
