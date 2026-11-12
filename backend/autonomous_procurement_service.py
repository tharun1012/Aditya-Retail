"""
Autonomous Procurement Service - Phase 2
Automatically monitors inventory and generates purchase orders
"""
from datetime import datetime, timezone
from typing import List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

class AutonomousProcurementService:
    """Service to automatically monitor stock levels and generate POs"""
    
    def __init__(self, db):
        self.db = db
        
    async def check_low_stock_items(self) -> List[Dict[str, Any]]:
        """
        Check for products below reorder level
        Returns list of low-stock products
        """
        try:
            low_stock_products = await self.db.products.find(
                {
                    "$expr": {
                        "$lte": ["$stock_quantity", "$reorder_level"]
                    }
                },
                {"_id": 0}
            ).to_list(None)
            
            logger.info(f"Found {len(low_stock_products)} low-stock items")
            return low_stock_products
            
        except Exception as e:
            logger.error(f"Error checking low stock: {str(e)}")
            return []
    
    async def calculate_order_quantity(self, product: Dict[str, Any]) -> int:
        """
        Calculate optimal order quantity based on:
        - Current stock level
        - Reorder level
        - Average sales velocity (if available)
        - Safety stock buffer
        """
        current_stock = product.get('stock_quantity', 0)
        reorder_level = product.get('reorder_level', 10)
        
        # Calculate deficit
        deficit = max(0, reorder_level - current_stock)
        
        # Add 50% buffer for safety stock
        buffer_quantity = int(reorder_level * 0.5)
        
        # Minimum order quantity
        min_order_qty = 5
        
        optimal_qty = max(min_order_qty, deficit + buffer_quantity)
        
        return optimal_qty
    
    async def generate_auto_draft_po(
        self, 
        product: Dict[str, Any], 
        quantity: int,
        reason: str = "Automatic reorder - Low stock detected"
    ) -> Dict[str, Any]:
        """
        Generate a draft purchase order for a low-stock product
        """
        try:
            draft_po_id = str(uuid.uuid4())
            draft_number = f"AUTO-DRAFT-PO-{datetime.now().strftime('%Y%m%d')}-{draft_po_id[:8].upper()}"
            
            # Calculate amounts
            rate = product.get('price', 0)
            item_subtotal = rate * quantity
            tax_rate = 18.0  # Default GST
            tax_amount = (item_subtotal * tax_rate) / 100
            total_amount = item_subtotal + tax_amount
            
            # Get product brand as vendor preference (if available)
            vendor_name = product.get('brand', 'TO BE DECIDED')
            
            draft_po = {
                "id": draft_po_id,
                "draft_number": draft_number,
                "po_number": None,
                "status": "draft",
                "po_date": datetime.now(timezone.utc).isoformat(),
                "expected_delivery_date": datetime.now(timezone.utc).isoformat(),
                "vendor": {
                    "name": vendor_name,
                    "phone": "",
                    "email": "",
                    "gst_number": "",
                    "address": "",
                    "city": "",
                    "state": "",
                    "pincode": ""
                },
                "items": [{
                    "product_id": product.get('id'),
                    "product_name": product.get('name'),
                    "hsn_code": product.get('hsn_code', ''),
                    "quantity": quantity,
                    "rate": rate,
                    "discount": 0,
                    "tax_rate": tax_rate
                }],
                "payment_mode": "cash",
                "discount": 0,
                "shipping_charges": 0,
                "round_off": 0,
                "subtotal": item_subtotal,
                "total_amount": total_amount,
                "notes": f"{reason}. Current stock: {product.get('stock_quantity', 0)} units, Reorder level: {product.get('reorder_level', 10)} units.",
                "created_by": "autonomous_system",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "auto_generated": True,
                "auto_reason": reason,
                "priority": "medium"
            }
            
            # Save draft to database
            await self.db.purchase_drafts.insert_one(draft_po)
            
            logger.info(f"Auto-generated draft PO: {draft_number} for {product.get('name')}")
            return draft_po
            
        except Exception as e:
            logger.error(f"Error generating auto draft PO: {str(e)}")
            return None
    
    async def run_autonomous_procurement_check(self) -> Dict[str, Any]:
        """
        Main function to run autonomous procurement check
        Returns summary of actions taken
        """
        try:
            logger.info("🤖 Starting autonomous procurement check...")
            
            # Step 1: Find low-stock items
            low_stock_items = await self.check_low_stock_items()
            
            if not low_stock_items:
                logger.info("✅ No low-stock items found. All inventory levels healthy.")
                return {
                    "status": "success",
                    "message": "No action needed. All inventory levels healthy.",
                    "low_stock_count": 0,
                    "drafts_created": 0,
                    "drafts": []
                }
            
            # Step 2: Check which items don't already have pending draft POs
            items_needing_po = []
            for product in low_stock_items:
                # Check if there's already a pending draft for this product
                existing_draft = await self.db.purchase_drafts.find_one({
                    "status": "draft",
                    "items.product_id": product.get('id')
                })
                
                if not existing_draft:
                    items_needing_po.append(product)
            
            logger.info(f"📦 {len(items_needing_po)} items need new draft POs")
            
            # Step 3: Generate draft POs for items needing reorder
            created_drafts = []
            for product in items_needing_po:
                quantity = await self.calculate_order_quantity(product)
                draft_po = await self.generate_auto_draft_po(product, quantity)
                
                if draft_po:
                    created_drafts.append({
                        "draft_number": draft_po["draft_number"],
                        "product_name": product.get('name'),
                        "quantity": quantity,
                        "total_amount": draft_po["total_amount"]
                    })
            
            logger.info(f"✅ Created {len(created_drafts)} auto-generated draft POs")
            
            # Step 4: Create notification for purchase manager
            if created_drafts:
                await self.create_purchase_manager_notification(created_drafts)
            
            return {
                "status": "success",
                "message": f"Created {len(created_drafts)} draft POs for low-stock items",
                "low_stock_count": len(low_stock_items),
                "drafts_created": len(created_drafts),
                "drafts": created_drafts,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in autonomous procurement check: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "low_stock_count": 0,
                "drafts_created": 0,
                "drafts": []
            }
    
    async def create_purchase_manager_notification(self, drafts: List[Dict[str, Any]]):
        """
        Create notification for purchase manager about new draft POs
        """
        try:
            notification = {
                "id": str(uuid.uuid4()),
                "type": "auto_draft_po_created",
                "title": f"🤖 {len(drafts)} Auto-Generated Draft POs Ready for Review",
                "message": f"The autonomous procurement system has created {len(drafts)} draft purchase orders for low-stock items. Please review and approve.",
                "drafts": drafts,
                "priority": "high",
                "read": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "target_roles": ["admin", "purchase_manager"]
            }
            
            await self.db.notifications.insert_one(notification)
            logger.info(f"📧 Created notification for purchase manager")
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
    
    async def parse_vendor_stock_report(
        self, 
        vendor_name: str, 
        report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse vendor stock report and match with our inventory needs
        
        Args:
            vendor_name: Name of the vendor (e.g., "Bosch", "Siemens")
            report_data: Dict with vendor products and their availability
                        Format: {"product_name": {"available": qty, "price": amount}}
        
        Returns:
            Matching recommendations for draft PO generation
        """
        try:
            logger.info(f"📊 Parsing vendor stock report from {vendor_name}")
            
            # Get our low-stock items
            low_stock_items = await self.check_low_stock_items()
            
            # Filter by vendor/brand
            vendor_low_stock = [
                item for item in low_stock_items 
                if item.get('brand', '').lower() == vendor_name.lower()
            ]
            
            # Match vendor availability with our needs
            matches = []
            for product in vendor_low_stock:
                product_name = product.get('name', '')
                
                # Try to find matching product in vendor report
                for vendor_product, details in report_data.items():
                    # Simple name matching (can be enhanced with fuzzy matching)
                    if vendor_product.lower() in product_name.lower():
                        matches.append({
                            "our_product": product.get('name'),
                            "our_current_stock": product.get('stock_quantity'),
                            "our_reorder_level": product.get('reorder_level'),
                            "vendor_product": vendor_product,
                            "vendor_available_qty": details.get('available', 0),
                            "vendor_price": details.get('price', 0),
                            "recommended_order_qty": await self.calculate_order_quantity(product),
                            "product_id": product.get('id')
                        })
            
            logger.info(f"✅ Found {len(matches)} matching products from {vendor_name}")
            
            return {
                "status": "success",
                "vendor": vendor_name,
                "matches_found": len(matches),
                "matches": matches,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing vendor report: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "matches_found": 0,
                "matches": []
            }
    
    async def generate_po_from_vendor_match(
        self, 
        matches: List[Dict[str, Any]], 
        vendor_name: str
    ) -> List[Dict[str, Any]]:
        """
        Generate draft POs from vendor stock report matches
        """
        created_drafts = []
        
        for match in matches:
            # Check if vendor has enough stock
            if match['vendor_available_qty'] >= match['recommended_order_qty']:
                product = await self.db.products.find_one(
                    {"id": match['product_id']},
                    {"_id": 0}
                )
                
                if product:
                    draft_po = await self.generate_auto_draft_po(
                        product,
                        match['recommended_order_qty'],
                        f"Vendor stock report match - {vendor_name} has stock available"
                    )
                    
                    if draft_po:
                        created_drafts.append(draft_po)
        
        return created_drafts
