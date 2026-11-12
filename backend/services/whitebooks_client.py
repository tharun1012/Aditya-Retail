"""
Whitebooks GSP API client — E-Way Bill + E-Invoice generation.
CONFIRMED against the official Postman collections downloaded from
developer.whitebooks.in/resources.

CONFIRMED (from Postman collections):
  E-Way Bill:
    Auth:     GET  /ewaybillapi/v1.03/authenticate?email=&username=&password=
              headers: ip_address, client_id, client_secret, gstin, Accept
    Generate: POST /ewaybillapi/v1.03/ewayapi/genewaybill?email=
              headers: ip_address, client_id, client_secret, gstin, Content-Type, Accept
              -> no auth-token header needed on generate. Plain JSON body.

  E-Invoice:
    Auth:     GET  /einvoice/authenticate?email=
              headers: username, password, ip_address, client_id, client_secret, gstin
    Generate: POST /einvoice/type/GENERATE/version/V1_03?email=
              headers: ip_address, client_id, client_secret, username, auth-token, gstin
              -> DOES require the auth-token from the auth call.

STILL UNCONFIRMED: exact token field name in e-invoice auth response, and
exact shape of "data" in responses (Postman only had placeholder examples).
"""
import os
import time
import json
from pathlib import Path
import requests
from dotenv import load_dotenv
from typing import Optional

load_dotenv(Path(__file__).resolve().parent.parent / '.env')


class WhitebooksAuthError(Exception):
    pass


class WhitebooksAPIError(Exception):
    def __init__(self, message, response_body=None):
        super().__init__(message)
        self.response_body = response_body


class WhitebooksClient:
    def __init__(self):
        self.base_url = os.getenv("WHITEBOOKS_BASE_URL", "https://apisandbox.whitebooks.in")
        self.ip_address = os.getenv("WHITEBOOKS_IP_ADDRESS", "127.0.0.1")
        self.email = os.getenv("WHITEBOOKS_EMAIL")
        self.gstin = os.getenv("WHITEBOOKS_GSTIN")
        self.username = os.getenv("WHITEBOOKS_USERNAME")
        self.password = os.getenv("WHITEBOOKS_PASSWORD")

        self.ewb_client_id = os.getenv("WHITEBOOKS_EWAYBILL_CLIENT_ID")
        self.ewb_client_secret = os.getenv("WHITEBOOKS_EWAYBILL_CLIENT_SECRET")

        self.einv_client_id = os.getenv("WHITEBOOKS_EINVOICE_CLIENT_ID")
        self.einv_client_secret = os.getenv("WHITEBOOKS_EINVOICE_CLIENT_SECRET")

        self.gst_client_id = os.getenv("WHITEBOOKS_GST_CLIENT_ID")
        self.gst_client_secret = os.getenv("WHITEBOOKS_GST_CLIENT_SECRET")

        self._einv_token_cache = {}

    def _ewb_common_headers(self, extra=None):
        headers = {
            "ip_address": self.ip_address,
            "client_id": self.ewb_client_id,
            "client_secret": self.ewb_client_secret,
            "gstin": self.gstin,
            "Accept": "application/json",
        }
        if extra:
            headers.update(extra)
        return headers

    def authenticate_ewaybill(self) -> dict:
        url = f"{self.base_url}/ewaybillapi/v1.03/authenticate"
        params = {"email": self.email, "username": self.username, "password": self.password}
        resp = requests.get(url, headers=self._ewb_common_headers(), params=params, timeout=30)
        data = self._safe_json(resp)
        if resp.status_code != 200 or str(data.get("status_cd", "1")) == "0":
            raise WhitebooksAuthError(f"E-Way Bill auth failed ({resp.status_code}): {data}")
        return data

    def generate_ewaybill(self, payload: dict) -> dict:
        url = f"{self.base_url}/ewaybillapi/v1.03/ewayapi/genewaybill"
        headers = self._ewb_common_headers({"Content-Type": "application/json"})
        params = {"email": self.email}

        resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
        data = self._safe_json(resp)

        if resp.status_code != 200 or str(data.get("status_cd", "1")).lower() in ("0", "fail", "failure"):
            raise WhitebooksAPIError(f"E-Way Bill generation failed: {data}", response_body=data)

        inner = self._unwrap_data(data)
        return {
            "ewb_no": inner.get("ewayBillNo") or inner.get("ewbNo"),
            "ewb_date": inner.get("ewayBillDate"),
            "valid_upto": inner.get("validUpto"),
            "raw": data,
        }

    def build_ewaybill_payload(self, invoice: dict, transporter: Optional[dict] = None) -> dict:
        transporter = transporter or {}
        same_state = invoice.get("store_state_code") == invoice.get("shipping_state_code")
        return {
            "supplyType": "O",
            "subSupplyType": "1",
            "subSupplyDesc": " ",
            "docType": "INV",
            "docNo": invoice.get("invoice_number"),
            "docDate": invoice.get("invoice_date"),
            "fromGstin": self.gstin,
            "fromTrdName": invoice.get("store_name"),
            "fromAddr1": invoice.get("store_address_line1", ""),
            "fromAddr2": invoice.get("store_address_line2", ""),
            "fromPlace": invoice.get("store_city", ""),
            "fromPincode": invoice.get("store_pincode"),
            "fromStateCode": invoice.get("store_state_code"),
            "actFromStateCode": invoice.get("store_state_code"),
            "toGstin": invoice.get("customer_gstin", "URP"),
            "toTrdName": invoice.get("customer_name"),
            "toAddr1": invoice.get("shipping_address_line1", ""),
            "toAddr2": invoice.get("shipping_address_line2", ""),
            "toPlace": invoice.get("shipping_city", ""),
            "toPincode": invoice.get("shipping_pincode"),
            "toStateCode": invoice.get("shipping_state_code"),
            "actToStateCode": invoice.get("shipping_state_code"),
            "transactionType": 1 if same_state else 2,
            "dispatchFromGSTIN": self.gstin,
            "dispatchFromTradeName": invoice.get("store_name"),
            "shipToGSTIN": invoice.get("customer_gstin", "URP"),
            "shipToTradeName": invoice.get("customer_name"),
            "totalValue": invoice.get("taxable_amount"),
            "cgstValue": invoice.get("cgst_total", 0),
            "sgstValue": invoice.get("sgst_total", 0),
            "igstValue": invoice.get("igst_total", 0),
            "totInvValue": invoice.get("total_amount"),
            "transMode": transporter.get("mode", "1"),
            "transDistance": transporter.get("distance"),
            "transporterName": transporter.get("name"),
            "transporterId": transporter.get("gstin_or_id"),
            "transDocNo": transporter.get("doc_no"),
            "transDocDate": transporter.get("doc_date"),
            "vehicleNo": transporter.get("vehicle_number"),
            "vehicleType": transporter.get("vehicle_type", "R"),
            "itemList": [
                {
                    "productName": item.get("product_name"),
                    "productDesc": item.get("product_name"),
                    "hsnCode": int(item.get("hsn_code")) if item.get("hsn_code") else None,
                    "quantity": item.get("quantity"),
                    "qtyUnit": item.get("unit", "NOS"),
                    "taxableAmount": item.get("taxable_amount"),
                    "sgstRate": item.get("sgst_rate", 0),
                    "cgstRate": item.get("cgst_rate", 0),
                    "igstRate": item.get("igst_rate", 0),
                }
                for item in invoice.get("items", [])
            ],
        }

    def _authenticate_einvoice(self) -> str:
        if self._einv_token_cache.get("token") and self._einv_token_cache.get("expires_at", 0) > time.time() + 30:
            return self._einv_token_cache["token"]

        url = f"{self.base_url}/einvoice/authenticate"
        headers = {
            "username": self.username,
            "password": self.password,
            "ip_address": self.ip_address,
            "client_id": self.einv_client_id,
            "client_secret": self.einv_client_secret,
            "gstin": self.gstin,
        }
        params = {"email": self.email}

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        data = self._safe_json(resp)
        if resp.status_code != 200:
            raise WhitebooksAuthError(f"E-Invoice auth failed ({resp.status_code}): {data}")

        inner = self._unwrap_data(data)
        token = inner.get("AuthToken") or inner.get("authtoken") or inner.get("TokenId") or inner.get("token")
        if not token:
            raise WhitebooksAuthError(f"No token found in e-invoice auth response: {data}")

        self._einv_token_cache["token"] = token
        self._einv_token_cache["expires_at"] = time.time() + 21600
        return token

    def generate_einvoice(self, payload: dict) -> dict:
        token = self._authenticate_einvoice()
        url = f"{self.base_url}/einvoice/type/GENERATE/version/V1_03"
        headers = {
            "ip_address": self.ip_address,
            "client_id": self.einv_client_id,
            "client_secret": self.einv_client_secret,
            "username": self.username,
            "auth-token": token,
            "gstin": self.gstin,
            "Content-Type": "application/json",
        }
        params = {"email": self.email}

        resp = requests.post(url, headers=headers, params=params, json=payload, timeout=30)
        data = self._safe_json(resp)

        if resp.status_code != 200 or str(data.get("status_cd", "1")).lower() in ("0", "fail", "failure"):
            raise WhitebooksAPIError(f"E-Invoice generation failed: {data}", response_body=data)

        inner = self._unwrap_data(data)
        return {
            "irn": inner.get("Irn") or inner.get("irn"),
            "ack_no": inner.get("AckNo"),
            "ack_date": inner.get("AckDt"),
            "signed_qr_code": inner.get("SignedQRCode"),
            "raw": data,
        }

    def build_einvoice_payload(self, invoice: dict) -> dict:
        return {
            "Version": "1.1",
            "TranDtls": {"TaxSch": "GST", "SupTyp": "B2B", "RegRev": "N", "IgstOnIntra": "N"},
            "DocDtls": {
                "Typ": "INV",
                "No": invoice.get("invoice_number"),
                "Dt": invoice.get("invoice_date"),
            },
            "SellerDtls": {
                "Gstin": self.gstin,
                "LglNm": invoice.get("store_name"),
                "Addr1": invoice.get("store_address_line1", ""),
                "Loc": invoice.get("store_city", ""),
                "Pin": invoice.get("store_pincode"),
                "Stcd": invoice.get("store_state_code"),
            },
            "BuyerDtls": {
                "Gstin": invoice.get("customer_gstin"),
                "LglNm": invoice.get("customer_name"),
                "Pos": invoice.get("shipping_state_code"),
                "Addr1": invoice.get("shipping_address_line1", ""),
                "Loc": invoice.get("shipping_city", ""),
                "Pin": invoice.get("shipping_pincode"),
                "Stcd": invoice.get("shipping_state_code"),
            },
            "ItemList": [
                {
                    "SlNo": str(idx + 1),
                    "IsServc": "N",
                    "PrdDesc": item.get("product_name"),
                    "HsnCd": item.get("hsn_code"),
                    "Qty": item.get("quantity"),
                    "Unit": item.get("unit", "NOS"),
                    "UnitPrice": item.get("rate"),
                    "TotAmt": item.get("taxable_amount"),
                    "AssAmt": item.get("taxable_amount"),
                    "GstRt": item.get("tax_rate", 18),
                    "CgstAmt": item.get("cgst_amount", 0),
                    "SgstAmt": item.get("sgst_amount", 0),
                    "IgstAmt": item.get("igst_amount", 0),
                    "TotItemVal": item.get("line_total"),
                }
                for idx, item in enumerate(invoice.get("items", []))
            ],
            "ValDtls": {
                "AssVal": invoice.get("taxable_amount"),
                "CgstVal": invoice.get("cgst_total", 0),
                "SgstVal": invoice.get("sgst_total", 0),
                "IgstVal": invoice.get("igst_total", 0),
                "TotInvVal": invoice.get("total_amount"),
            },
        }

    @staticmethod
    def _safe_json(resp):
        try:
            return resp.json()
        except ValueError:
            return {"raw_text": resp.text}

    @staticmethod
    def _unwrap_data(response_json: dict) -> dict:
        raw_data = response_json.get("data")
        if isinstance(raw_data, dict):
            return raw_data
        if isinstance(raw_data, str):
            try:
                return json.loads(raw_data)
            except (ValueError, TypeError):
                return {}
        return response_json


    def _gst_common_headers(self, extra=None):
        headers = {
            "client_id": self.gst_client_id,
            "client_secret": self.gst_client_secret,
        }
        if extra:
            headers.update(extra)
        return headers

    def search_taxpayer(self, gstin: str) -> dict:
        """
        GST API - Search Taxpayer (GSTIN validation/lookup).
        GET /public/search?email=&gstin=
        headers: client_id, client_secret
        Confirmed via Whitebooks Playground: no separate auth/token step needed.
        """
        if not gstin:
            raise WhitebooksAPIError("GSTIN is required")

        url = f"{self.base_url}/public/search"
        headers = self._gst_common_headers({"Accept": "application/json"})
        params = {"email": self.email, "gstin": gstin.strip().upper()}

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        data = self._safe_json(resp)

        if resp.status_code == 404:
            return {"valid": False, "reason": "not_found", "raw": data}

        if resp.status_code != 200:
            raise WhitebooksAPIError(
                f"GST Search Taxpayer failed ({resp.status_code}): {data}",
                response_body=data,
            )

        # Response shape wasn't documented with a live example on Whitebooks'
        # docs page - unwrap defensively and log raw payload for inspection.
        inner = data.get("data", data) if isinstance(data, dict) else data
        status_flag = str(
            inner.get("status_cd", inner.get("sts", "1"))
        ).lower() if isinstance(inner, dict) else "1"

        if status_flag in ("0", "fail", "failure", "inactive"):
            return {"valid": False, "reason": "inactive_or_invalid", "raw": data}

        pradr = inner.get("pradr", {}) if isinstance(inner, dict) else {}
        state = None
        if isinstance(pradr, dict):
            addr = pradr.get("addr", {})
            if isinstance(addr, dict):
                state = addr.get("stcd")

        return {
            "valid": True,
            "gstin": inner.get("gstin") or params["gstin"],
            "legal_name": inner.get("lgnm") or inner.get("legal_name"),
            "trade_name": inner.get("tradeNam") or inner.get("trade_name"),
            "status": inner.get("sts") or inner.get("status"),
            "state": state,
            "raw": data,
        }

whitebooks_client = WhitebooksClient()
