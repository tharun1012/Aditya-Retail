"""
AI Sales Agent - Order Management & Payment Link Generation
Handles complete order flow from AI chat to payment
"""
import os
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests
import base64
import hashlib
import json

# Import email notification service
try:
    from email_notification_service import email_notification_service
except ImportError:
    email_notification_service = None

class AISalesOrderManager:
    """Manages order creation and payment link generation for AI Sales Agent"""
    
    def __init__(self, db):
        self.db = db
        
        # PhonePe Configuration
        self.phonepe_merchant_id = os.environ.get("PHONEPE_MERCHANT_ID", "M224EIU0W7NHS")
        self.phonepe_salt_key = os.environ.get("PHONEPE_SALT_KEY", "b8063715-a14a-418a-973f-ef6341087184")
        self.phonepe_salt_index = int(os.environ.get("PHONEPE_SALT_INDEX", "1"))
        self.phonepe_environment = os.environ.get("PHONEPE_ENVIRONMENT", "PRODUCTION")
        
        self.phonepe_api_url = "https://api.phonepe.com/apis/hermes" if self.phonepe_environment == "PRODUCTION" else "https://api-preprod.phonepe.com/apis/pg-sandbox"
        self.redirect_url = os.environ.get("REDIRECT_URL", "https://acct-workflow-1.preview.emergentagent.com/#/payment-success")
        self.callback_url = os.environ.get("CALLBACK_URL", "https://acct-workflow-1.preview.emergentagent.com/api/phonepe/callback")
    
    async def create_order_and_payment_link(
        self,
        customer_data: Dict[str, Any],
        product_id: str,
        quantity: int = 1,
        additional_discount: float = 0
    ) -> Dict[str, Any]:
        """
        Create order and generate payment link
        
        Args:
            customer_data: {
                'name': str,
                'phone': str,
                'email': str,
                'address': str,
                'landmark': str (optional),
                'city': str (optional),
                'pincode': str (optional)
            }
            product_id: Product ID to order
            quantity: Quantity to order
            additional_discount: Extra discount offered by AI agent (%)
        
        Returns:
            {
                'success': bool,
                'order_id': str,
                'payment_link': str,
                'amount': float,
                'message': str
            }
        """
        try:
            # 1. Fetch product details
            product = await self.db.products.find_one({"id": product_id}, {"_id": 0})
            if not product:
                return {
                    "success": False,
                    "message": "Product not found"
                }
            
            # 2. Calculate pricing with additional discount
            original_price = product.get('price', 0)
            base_discount = product.get('discount', 0)
            
            # Apply additional AI agent discount
            total_discount = base_discount + additional_discount
            final_price = original_price * (1 - total_discount / 100)
            total_amount = final_price * quantity
            
            # 3. Generate order ID
            order_id = f"ORD-AI-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # 4. Create order document
            order_doc = {
                "order_id": order_id,
                "customer": {
                    "name": customer_data.get('name'),
                    "phone": customer_data.get('phone'),
                    "email": customer_data.get('email'),
                    "address": customer_data.get('address'),
                    "landmark": customer_data.get('landmark', ''),
                    "city": customer_data.get('city', 'Not provided'),
                    "pincode": customer_data.get('pincode', 'Not provided')
                },
                "items": [{
                    "product_id": product_id,
                    "name": product.get('name'),
                    "brand": product.get('brand'),
                    "quantity": quantity,
                    "price": original_price,
                    "discount_percent": total_discount,
                    "final_price": final_price,
                    "subtotal": total_amount
                }],
                "pricing": {
                    "subtotal": total_amount,
                    "discount_amount": (original_price * quantity) - total_amount,
                    "total": total_amount,
                    "ai_discount_applied": additional_discount
                },
                "payment": {
                    "method": "phonepe",
                    "status": "pending",
                    "transaction_id": None
                },
                "status": "pending_payment",
                "source": "ai_sales_agent",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # 5. Save order to database
            await self.db.orders.insert_one(order_doc)
            
            # 6. Generate PhonePe payment link
            payment_result = await self._generate_phonepe_payment_link(
                order_id=order_id,
                amount=int(total_amount * 100),  # Convert to paise
                customer_data=customer_data
            )
            
            if not payment_result['success']:
                return {
                    "success": False,
                    "message": "Failed to generate payment link",
                    "error": payment_result.get('error')
                }
            
            # 7. Send order confirmation email
            if email_notification_service and customer_data.get('email'):
                try:
                    await email_notification_service.send_order_confirmation(
                        customer_email=customer_data['email'],
                        customer_name=customer_data.get('name', 'Valued Customer'),
                        order_id=order_id,
                        order_items=[{
                            'name': product.get('name'),
                            'quantity': quantity,
                            'price': final_price
                        }],
                        total_amount=total_amount,
                        payment_link=payment_result['payment_url'],
                        shipping_address=customer_data.get('address')
                    )
                    print(f"✅ Order confirmation email sent to {customer_data['email']}")
                except Exception as email_error:
                    print(f"⚠️ Failed to send order email: {email_error}")
            
            # 8. Return success with payment link
            return {
                "success": True,
                "order_id": order_id,
                "payment_link": payment_result['payment_url'],
                "amount": total_amount,
                "discount_applied": total_discount,
                "ai_discount": additional_discount,
                "message": f"Order created successfully! Amount: ₹{total_amount:,.2f}",
                "email_sent": bool(customer_data.get('email'))
            }
            
        except Exception as e:
            print(f"Error creating order: {e}")
            return {
                "success": False,
                "message": f"Error creating order: {str(e)}"
            }
    
    async def _generate_phonepe_payment_link(
        self,
        order_id: str,
        amount: int,
        customer_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate PhonePe payment link"""
        try:
            # Generate unique merchant transaction ID
            merchant_transaction_id = f"TXN_{order_id}_{uuid.uuid4().hex[:8]}"
            
            # Create payment payload
            payload = {
                "merchantId": self.phonepe_merchant_id,
                "merchantTransactionId": merchant_transaction_id,
                "merchantUserId": customer_data.get('phone', 'GUEST')[-10:],  # Last 10 digits
                "amount": amount,
                "redirectUrl": self.redirect_url,
                "redirectMode": "REDIRECT",
                "callbackUrl": self.callback_url,
                "mobileNumber": customer_data.get('phone', '9999999999')[-10:],
                "paymentInstrument": {
                    "type": "PAY_PAGE"
                }
            }
            
            # Convert payload to JSON string
            payload_json = json.dumps(payload)
            
            # Encode payload in base64
            payload_base64 = base64.b64encode(payload_json.encode()).decode()
            
            # Generate checksum
            checksum = self._generate_phonepe_checksum(payload_base64, "/pg/v1/pay")
            
            # Make API call to PhonePe
            pay_url = f"{self.phonepe_api_url}/pg/v1/pay"
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "X-VERIFY": checksum
            }
            
            request_body = {
                "request": payload_base64
            }
            
            response = requests.post(pay_url, json=request_body, headers=headers, timeout=10)
            response_data = response.json()
            
            if response_data.get('success'):
                # Extract payment URL from response
                payment_url = response_data['data']['instrumentResponse']['redirectInfo']['url']
                
                # Update order with transaction ID
                await self.db.orders.update_one(
                    {"order_id": order_id},
                    {"$set": {
                        "payment.transaction_id": merchant_transaction_id,
                        "payment.payment_url": payment_url
                    }}
                )
                
                return {
                    "success": True,
                    "payment_url": payment_url,
                    "transaction_id": merchant_transaction_id
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get('message', 'Unknown error')
                }
                
        except Exception as e:
            print(f"PhonePe payment link generation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_phonepe_checksum(self, payload_base64: str, api_path: str) -> str:
        """Generate SHA256 checksum for PhonePe API"""
        string_to_hash = payload_base64 + api_path + self.phonepe_salt_key
        sha256_hash = hashlib.sha256(string_to_hash.encode()).hexdigest()
        return sha256_hash + "###" + str(self.phonepe_salt_index)
    
    def extract_customer_details(self, conversation_history: list) -> Dict[str, Any]:
        """Extract customer details from conversation"""
        customer_data = {
            'name': None,
            'phone': None,
            'email': None,
            'address': None,
            'landmark': None,
            'city': None,
            'pincode': None
        }
        
        # Combine all user messages
        all_messages = " ".join([
            msg.get('message', '') for msg in conversation_history 
            if msg.get('sender') == 'user'
        ])
        
        # Extract name
        name_patterns = [
            r"(?:my name is|i'?m|call me|this is)\s+([A-Za-z\s]+?)(?:\s|$|\.)",
            r"name:\s*([A-Za-z\s]+?)(?:\s|$|\.)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, all_messages, re.IGNORECASE)
            if match:
                customer_data['name'] = match.group(1).strip().title()
                break
        
        # Extract phone (Indian mobile numbers)
        phone_patterns = [
            r"(\+91[\s-]?)?([6-9]\d{9})",
            r"(?:phone|mobile|number)[\s:]*(\+91[\s-]?)?([6-9]\d{9})"
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, all_messages)
            if match:
                phone = match.group(2) if match.group(2) else match.group(1)
                customer_data['phone'] = phone
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, all_messages)
        if email_match:
            customer_data['email'] = email_match.group(0)
        
        # Extract address (look for common address patterns)
        address_patterns = [
            r"(?:address|deliver to|ship to)[\s:]+(.+?)(?:\.|$|landmark|city)",
            r"(\d+[,\s]+.+?(?:street|road|avenue|lane|nagar|colony|block).+?)(?:\.|$|landmark|city)"
        ]
        for pattern in address_patterns:
            match = re.search(pattern, all_messages, re.IGNORECASE)
            if match:
                customer_data['address'] = match.group(1).strip()
                break
        
        # Extract landmark
        landmark_pattern = r"(?:landmark|near)[\s:]+(.+?)(?:\.|$|city|pincode)"
        landmark_match = re.search(landmark_pattern, all_messages, re.IGNORECASE)
        if landmark_match:
            customer_data['landmark'] = landmark_match.group(1).strip()
        
        # Extract city
        city_pattern = r"(?:city|location)[\s:]+([A-Za-z\s]+?)(?:\.|$|pincode)"
        city_match = re.search(city_pattern, all_messages, re.IGNORECASE)
        if city_match:
            customer_data['city'] = city_match.group(1).strip().title()
        
        # Extract pincode
        pincode_pattern = r"\b(\d{6})\b"
        pincode_match = re.search(pincode_pattern, all_messages)
        if pincode_match:
            customer_data['pincode'] = pincode_match.group(1)
        
        return customer_data
    
    def validate_customer_data(self, customer_data: Dict[str, Any]) -> tuple[bool, list]:
        """Validate if all required customer data is present"""
        required_fields = ['name', 'phone', 'email', 'address']
        missing_fields = []
        
        for field in required_fields:
            if not customer_data.get(field):
                missing_fields.append(field)
        
        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields
