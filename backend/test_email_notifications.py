"""
Test Email Notifications - Send test emails for Order, Delivery, and Service Ticket
"""
import asyncio
import sys
sys.path.insert(0, '/app/backend')

from email_notification_service import email_notification_service

async def test_all_emails():
    test_email = "rohit.gadiya@gmail.com"
    test_name = "Rohit Gadiya"
    
    results = {}
    
    # Test 1: Order Confirmation Email
    print("\n" + "="*50)
    print("📦 TEST 1: Order Confirmation Email")
    print("="*50)
    
    try:
        result = await email_notification_service.send_order_confirmation(
            customer_email=test_email,
            customer_name=test_name,
            order_id="ORD-TEST-20260209-ABCD1234",
            order_items=[
                {
                    "name": "Bosch Series 4 Island Cooker Hood 90 cm",
                    "quantity": 1,
                    "price": 55490
                },
                {
                    "name": "Bosch DWA68IJ60I Wall-Mounted Chimney 60 cm",
                    "quantity": 1,
                    "price": 16200
                }
            ],
            total_amount=71690,
            payment_link="https://acct-workflow-1.preview.emergentagent.com/#/payment-success?test=true",
            shipping_address="123 Test Street, Bangalore, Karnataka - 560001"
        )
        results['order_confirmation'] = result
        print(f"Result: {result}")
    except Exception as e:
        results['order_confirmation'] = {"status": "error", "message": str(e)}
        print(f"Error: {e}")
    
    # Test 2: Delivery Dispatched Email
    print("\n" + "="*50)
    print("🚚 TEST 2: Delivery Dispatched Email")
    print("="*50)
    
    try:
        result = await email_notification_service.send_delivery_dispatched(
            customer_email=test_email,
            customer_name=test_name,
            order_id="ORD-TEST-20260209-ABCD1234",
            tracking_number="AWB123456789",
            delivery_partner="Delhivery",
            expected_date="February 12, 2026"
        )
        results['delivery_dispatched'] = result
        print(f"Result: {result}")
    except Exception as e:
        results['delivery_dispatched'] = {"status": "error", "message": str(e)}
        print(f"Error: {e}")
    
    # Test 3: Service Ticket Email
    print("\n" + "="*50)
    print("🔧 TEST 3: Service Ticket Created Email")
    print("="*50)
    
    try:
        result = await email_notification_service.send_service_ticket_confirmation(
            customer_email=test_email,
            customer_name=test_name,
            ticket_number="ADR-SRV-20260209-TEST1234",
            issue_description="Chimney making unusual noise during operation. The motor seems to be running louder than usual and there's a slight vibration.",
            product_name="Bosch DWA68IJ60I Series 4 Wall-Mounted Chimney",
            brand="Bosch",
            priority="Normal"
        )
        results['service_ticket'] = result
        print(f"Result: {result}")
    except Exception as e:
        results['service_ticket'] = {"status": "error", "message": str(e)}
        print(f"Error: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 EMAIL TEST SUMMARY")
    print("="*50)
    
    for email_type, result in results.items():
        status = "✅ SUCCESS" if result.get('status') == 'success' else "❌ FAILED"
        print(f"{email_type}: {status}")
        if result.get('status') != 'success':
            print(f"   Error: {result.get('message', 'Unknown error')}")
    
    return results

# Run the test
if __name__ == "__main__":
    results = asyncio.run(test_all_emails())
    print("\n✅ Email test completed!")
