# Shiprocket Integration for AI Ecommerce Platform
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, JSON
from app.database import Base
import os
import uuid

class ShipmentTracking(Base):
    __tablename__ = "shipment_tracking"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String, nullable=False)
    shiprocket_order_id = Column(String)
    shipment_id = Column(String)
    awb_number = Column(String)
    courier_company = Column(String)
    courier_name = Column(String)
    tracking_url = Column(String(500))
    current_status = Column(String(100))
    expected_delivery_date = Column(DateTime)
    pickup_scheduled_date = Column(DateTime)
    shipped_date = Column(DateTime)
    delivered_date = Column(DateTime)
    tracking_data = Column(JSON)  # Store full tracking response
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ShiprocketService:
    def __init__(self):
        self.base_url = "https://apiv2.shiprocket.in/v1/external"
        self.email = os.getenv("SHIPROCKET_EMAIL", "")
        self.password = os.getenv("SHIPROCKET_PASSWORD", "")
        self.token = None
        self.token_expires_at = None
    
    def authenticate(self) -> bool:
        """Authenticate with Shiprocket and get access token"""
        auth_url = f"{self.base_url}/auth/login"
        
        auth_data = {
            "email": self.email,
            "password": self.password
        }
        
        try:
            response = requests.post(auth_url, json=auth_data, timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and "token" in response_data:
                self.token = response_data["token"]
                # Token typically expires in 10 days
                self.token_expires_at = datetime.now() + timedelta(days=9)
                return True
            else:
                print(f"Shiprocket authentication failed: {response_data}")
                return False
                
        except Exception as e:
            print(f"Shiprocket authentication error: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token"""
        if not self.token or (self.token_expires_at and datetime.now() >= self.token_expires_at):
            if not self.authenticate():
                raise Exception("Shiprocket authentication failed")
        
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
    
    def check_serviceability(self, pickup_pincode: str, delivery_pincode: str, weight: float) -> Dict[str, Any]:
        """Check serviceability and get shipping rates"""
        url = f"{self.base_url}/courier/serviceability/"
        
        params = {
            "pickup_postcode": pickup_pincode,
            "delivery_postcode": delivery_pincode,
            "weight": weight,
            "cod": 1  # Cash on delivery available
        }
        
        try:
            response = requests.get(url, params=params, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and "data" in response_data:
                available_couriers = response_data["data"]["available_courier_companies"]
                
                if available_couriers:
                    # Get the cheapest option
                    cheapest = min(available_couriers, key=lambda x: x["rate"])
                    
                    return {
                        "serviceable": True,
                        "shipping_cost": cheapest["rate"],
                        "estimated_days": cheapest["etd"],
                        "courier_name": cheapest["courier_name"],
                        "courier_company_id": cheapest["courier_company_id"],
                        "all_options": available_couriers
                    }
                else:
                    return {
                        "serviceable": False,
                        "message": "No courier services available for this pincode"
                    }
            else:
                return {
                    "serviceable": False,
                    "message": response_data.get("message", "Serviceability check failed")
                }
                
        except Exception as e:
            return {
                "serviceable": False,
                "message": f"Serviceability check error: {str(e)}"
            }
    
    def create_order(self, order_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create order in Shiprocket"""
        url = f"{self.base_url}/orders/create/adhoc"
        
        try:
            response = requests.post(url, json=order_details, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and "order_id" in response_data:
                return {
                    "success": True,
                    "shiprocket_order_id": response_data["order_id"],
                    "shipment_id": response_data.get("shipment_id"),
                    "message": "Order created successfully in Shiprocket"
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Order creation failed"),
                    "errors": response_data.get("errors", {})
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Order creation error: {str(e)}"
            }
    
    def generate_awb(self, shipment_id: str, courier_company_id: int) -> Dict[str, Any]:
        """Generate AWB for shipment"""
        url = f"{self.base_url}/courier/assign/awb"
        
        awb_data = {
            "shipment_id": shipment_id,
            "courier_company_id": courier_company_id
        }
        
        try:
            response = requests.post(url, json=awb_data, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and "awb_assign_status" in response_data:
                if response_data["awb_assign_status"] == 1:
                    return {
                        "success": True,
                        "awb_number": response_data["response"]["data"]["awb_number"],
                        "courier_name": response_data["response"]["data"]["courier_name"],
                        "courier_company_id": response_data["response"]["data"]["courier_company_id"]
                    }
                else:
                    return {
                        "success": False,
                        "error": "AWB assignment failed",
                        "message": response_data.get("message", "")
                    }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "AWB generation failed")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"AWB generation error: {str(e)}"
            }
    
    def track_shipment(self, awb_number: str) -> Dict[str, Any]:
        """Track shipment using AWB number"""
        url = f"{self.base_url}/courier/track/awb/{awb_number}"
        
        try:
            response = requests.get(url, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200 and "tracking_data" in response_data:
                tracking_data = response_data["tracking_data"]
                
                if tracking_data and "track_status" in tracking_data:
                    current_status = tracking_data["track_status"]
                    
                    # Parse tracking events
                    tracking_events = []
                    if "shipment_track" in tracking_data:
                        for event in tracking_data["shipment_track"]:
                            tracking_events.append({
                                "date": event.get("date"),
                                "status": event.get("sr-status"),
                                "location": event.get("location"),
                                "activity": event.get("activity")
                            })
                    
                    return {
                        "success": True,
                        "current_status": current_status,
                        "delivered_date": tracking_data.get("delivered_date"),
                        "expected_delivery": tracking_data.get("edd"),
                        "tracking_events": tracking_events,
                        "raw_data": response_data
                    }
                else:
                    return {
                        "success": False,
                        "error": "No tracking data available"
                    }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Tracking failed")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Tracking error: {str(e)}"
            }
    
    def get_pickup_schedule(self, shipment_id: str) -> Dict[str, Any]:
        """Schedule pickup for shipment"""
        url = f"{self.base_url}/courier/generate/pickup"
        
        pickup_data = {
            "shipment_id": [shipment_id]
        }
        
        try:
            response = requests.post(url, json=pickup_data, headers=self.get_headers(), timeout=30)
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "pickup_scheduled": True,
                    "message": "Pickup scheduled successfully",
                    "response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": response_data.get("message", "Pickup scheduling failed")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Pickup scheduling error: {str(e)}"
            }

class ShippingCRUD:
    @staticmethod
    def create_shipment_tracking(
        db: Session,
        order_id: str,
        shiprocket_order_id: Optional[str] = None,
        shipment_id: Optional[str] = None,
        awb_number: Optional[str] = None
    ) -> ShipmentTracking:
        """Create shipment tracking record"""
        
        tracking = ShipmentTracking(
            order_id=order_id,
            shiprocket_order_id=shiprocket_order_id,
            shipment_id=shipment_id,
            awb_number=awb_number,
            current_status="created"
        )
        
        db.add(tracking)
        db.commit()
        db.refresh(tracking)
        return tracking
    
    @staticmethod
    def update_shipment_tracking(
        db: Session,
        order_id: str,
        update_data: Dict[str, Any]
    ) -> Optional[ShipmentTracking]:
        """Update shipment tracking information"""
        
        tracking = db.query(ShipmentTracking).filter(
            ShipmentTracking.order_id == order_id
        ).first()
        
        if not tracking:
            return None
        
        for key, value in update_data.items():
            if hasattr(tracking, key):
                setattr(tracking, key, value)
        
        tracking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(tracking)
        return tracking
    
    @staticmethod
    def get_shipment_by_order_id(db: Session, order_id: str) -> Optional[ShipmentTracking]:
        """Get shipment tracking by order ID"""
        return db.query(ShipmentTracking).filter(
            ShipmentTracking.order_id == order_id
        ).first()
    
    @staticmethod
    def get_shipment_by_awb(db: Session, awb_number: str) -> Optional[ShipmentTracking]:
        """Get shipment tracking by AWB number"""
        return db.query(ShipmentTracking).filter(
            ShipmentTracking.awb_number == awb_number
        ).first()

class ShippingService:
    def __init__(self):
        self.shiprocket = ShiprocketService()
        self.default_pickup_pincode = "560001"  # Bangalore - adjust as needed
    
    def calculate_shipping_cost(self, delivery_pincode: str, weight: float) -> Dict[str, Any]:
        """Calculate shipping cost using Shiprocket"""
        
        # First check if we have Shiprocket credentials
        if not self.shiprocket.email or not self.shiprocket.password:
            # Fallback to manual calculation
            return self._manual_shipping_calculation(delivery_pincode, weight)
        
        try:
            result = self.shiprocket.check_serviceability(
                pickup_pincode=self.default_pickup_pincode,
                delivery_pincode=delivery_pincode,
                weight=weight
            )
            
            if result["serviceable"]:
                return {
                    "success": True,
                    "shipping_cost": result["shipping_cost"],
                    "estimated_days": result["estimated_days"],
                    "courier_name": result["courier_name"],
                    "serviceable": True
                }
            else:
                return {
                    "success": False,
                    "serviceable": False,
                    "message": result.get("message", "Not serviceable")
                }
                
        except Exception as e:
            # Fallback to manual calculation on API failure
            return self._manual_shipping_calculation(delivery_pincode, weight)
    
    def _manual_shipping_calculation(self, pincode: str, weight: float) -> Dict[str, Any]:
        """Manual shipping cost calculation as fallback"""
        
        # Define zones based on pincode (simplified)
        metro_pincodes = ['110', '400', '700', '560', '600', '500']  # Delhi, Mumbai, Kolkata, Bangalore, Chennai, Hyderabad
        is_metro = any(pincode.startswith(metro) for metro in metro_pincodes)
        
        base_cost = 40 if is_metro else 60
        per_kg_cost = 15 if is_metro else 25
        
        shipping_cost = base_cost + (weight * per_kg_cost)
        estimated_days = 3 if is_metro else 7
        
        return {
            "success": True,
            "shipping_cost": shipping_cost,
            "estimated_days": estimated_days,
            "courier_name": "Standard Shipping",
            "serviceable": True,
            "fallback": True
        }
    
    def create_shipment(self, db: Session, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create shipment with Shiprocket"""
        
        try:
            # Prepare Shiprocket order data
            shiprocket_data = {
                "order_id": order_data["order_number"],
                "order_date": order_data["order_date"],
                "pickup_location": "Primary",
                "billing_customer_name": order_data["customer_name"],
                "billing_last_name": "",
                "billing_address": order_data["billing_address"]["address"],
                "billing_city": order_data["billing_address"]["city"],
                "billing_pincode": order_data["billing_address"]["pincode"],
                "billing_state": order_data["billing_address"]["state"],
                "billing_country": "India",
                "billing_email": order_data["customer_email"],
                "billing_phone": order_data["customer_phone"],
                "shipping_is_billing": True,
                "order_items": order_data["items"],
                "payment_method": "Prepaid" if order_data.get("payment_method") == "phonepe" else "COD",
                "sub_total": order_data["subtotal"],
                "length": 10,  # Default dimensions
                "breadth": 10,
                "height": 10,
                "weight": order_data.get("weight", 1)
            }
            
            # Create order in Shiprocket
            result = self.shiprocket.create_order(shiprocket_data)
            
            if result["success"]:
                # Create tracking record
                tracking = ShippingCRUD.create_shipment_tracking(
                    db=db,
                    order_id=order_data["order_id"],
                    shiprocket_order_id=result["shiprocket_order_id"],
                    shipment_id=result.get("shipment_id")
                )
                
                return {
                    "success": True,
                    "shiprocket_order_id": result["shiprocket_order_id"],
                    "shipment_id": result.get("shipment_id"),
                    "tracking_id": tracking.id
                }
            else:
                return result
                
        except Exception as e:
            # Create manual tracking record even if Shiprocket fails
            tracking = ShippingCRUD.create_shipment_tracking(
                db=db,
                order_id=order_data["order_id"]
            )
            
            return {
                "success": True,
                "manual_tracking": True,
                "tracking_id": tracking.id,
                "message": "Order created with manual tracking",
                "shiprocket_error": str(e)
            }
    
    def track_shipment(self, db: Session, order_id: str) -> Dict[str, Any]:
        """Track shipment status"""
        
        tracking = ShippingCRUD.get_shipment_by_order_id(db, order_id)
        if not tracking:
            return {"success": False, "error": "Shipment tracking not found"}
        
        if tracking.awb_number:
            # Track using Shiprocket
            try:
                result = self.shiprocket.track_shipment(tracking.awb_number)
                
                if result["success"]:
                    # Update tracking data
                    ShippingCRUD.update_shipment_tracking(
                        db=db,
                        order_id=order_id,
                        update_data={
                            "current_status": result["current_status"],
                            "tracking_data": result["raw_data"],
                            "delivered_date": result.get("delivered_date")
                        }
                    )
                    
                    return result
                else:
                    return result
                    
            except Exception as e:
                return {"success": False, "error": f"Tracking error: {str(e)}"}
        else:
            # Return manual tracking status
            return {
                "success": True,
                "current_status": tracking.current_status,
                "manual_tracking": True,
                "created_at": tracking.created_at.isoformat()
            }

# Initialize shipping service
shipping_service = ShippingService()