#!/usr/bin/env python3
"""
Quick Email Test Script
Run this to test if your SendGrid email is working

Usage:
  python3 /app/test_email.py your-email@example.com
"""

import sys
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def send_test_email(to_email):
    """Send a test email"""
    
    api_key = os.getenv("SENDGRID_API_KEY")
    from_email = os.getenv("SALES_EMAIL", "sales.aronline@gmail.com")
    
    print("=" * 60)
    print("📧 SENDGRID EMAIL TEST")
    print("=" * 60)
    print(f"From Email: {from_email}")
    print(f"To Email: {to_email}")
    print(f"API Key: {'✓ Present' if api_key else '✗ Missing'}")
    print("-" * 60)
    
    if not api_key:
        print("❌ ERROR: SENDGRID_API_KEY not found in /app/backend/.env")
        print("\nTo fix:")
        print("1. Add SENDGRID_API_KEY=your-key to /app/backend/.env")
        print("2. Run this script again")
        return False
    
    # Create email message
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject='✅ Test Email from Aditya Retail AI Agent',
        html_content='''
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2563eb;">🎉 Email System Test Successful!</h1>
                
                <div style="background: #f0fdf4; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #10b981;">✅ What's Working:</h3>
                    <ul>
                        <li>SendGrid API connection ✓</li>
                        <li>Email delivery ✓</li>
                        <li>HTML rendering ✓</li>
                    </ul>
                </div>
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #2563eb;">Next Steps:</h3>
                    <ol>
                        <li><strong>Verify Sender Email:</strong> Go to SendGrid dashboard and verify your sender email</li>
                        <li><strong>Domain Authentication:</strong> Set up SPF/DKIM for better deliverability</li>
                        <li><strong>Start Campaigns:</strong> Your AI Marketing Agent is ready!</li>
                    </ol>
                </div>
                
                <p>Your AI Marketing Agent will now automatically send:</p>
                <ul>
                    <li>Welcome emails to new leads (1 hour after capture)</li>
                    <li>Product demo invitations (Day 2)</li>
                    <li>Special offers (Day 5)</li>
                    <li>Order confirmations</li>
                    <li>Delivery updates</li>
                    <li>Follow-up emails</li>
                </ul>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                
                <p style="color: #6b7280; font-size: 12px;">
                    This is a test email from Aditya Retail AI Marketing System<br>
                    If you received this, your email system is working perfectly!
                </p>
            </div>
        '''
    )
    
    try:
        print("\n📤 Sending test email...")
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        print(f"\n✅ SUCCESS! Email sent successfully!")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.body.decode() if response.body else 'Email accepted for delivery'}")
        print(f"\n📬 Check your inbox at: {to_email}")
        print("   (Also check spam/junk folder)")
        print("\n" + "=" * 60)
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: Email sending failed!")
        print(f"   Error: {error_msg}")
        print("\n" + "=" * 60)
        
        # Provide specific help based on error
        if "does not contain a valid address" in error_msg or "not verified" in error_msg.lower():
            print("\n🔧 FIX: Sender email not verified")
            print("   1. Go to: https://app.sendgrid.com/settings/sender_auth/senders")
            print(f"   2. Add and verify: {from_email}")
            print("   3. Check email inbox for verification link")
            print("   4. Run this test again")
            
        elif "Unauthorized" in error_msg or "authentication" in error_msg.lower():
            print("\n🔧 FIX: Invalid API Key")
            print("   1. Go to: https://app.sendgrid.com/settings/api_keys")
            print("   2. Create new API key with 'Mail Send' permission")
            print("   3. Update /app/backend/.env with new key")
            print("   4. Run this test again")
            
        else:
            print("\n🔧 HELP:")
            print("   1. Check SendGrid documentation: https://docs.sendgrid.com/")
            print("   2. Verify API key has 'Mail Send' permission")
            print("   3. Check SendGrid account status")
        
        print("\n" + "=" * 60)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n❌ ERROR: Please provide a recipient email address")
        print("\nUsage:")
        print(f"  python3 {sys.argv[0]} your-email@example.com")
        print("\nExample:")
        print(f"  python3 {sys.argv[0]} john@example.com")
        sys.exit(1)
    
    recipient_email = sys.argv[1]
    
    # Validate email format (basic check)
    if "@" not in recipient_email or "." not in recipient_email:
        print(f"\n❌ ERROR: '{recipient_email}' doesn't look like a valid email address")
        sys.exit(1)
    
    success = send_test_email(recipient_email)
    sys.exit(0 if success else 1)
