"""
Email Lead Auto-Capture Service
Parses emails from JustDial, SingleInterface, BSH and auto-creates leads
"""
import re
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid

class EmailLeadCaptureService:
    
    def __init__(self):
        self.store_emails = {
            "banaswadi.adityaretail@gmail.com": "Banaswadi Store",
            "bosch.adityaretail@gmail.com": "Bosch Store",
            "dasarahalli.adityaretail@gmail.com": "Dasarahalli Store"
        }
    
    def parse_justdial_email(self, email_body: str, subject: str, from_email: str) -> Optional[Dict[str, Any]]:
        """
        Parse JustDial lead email format
        
        Common JustDial formats:
        Format 1:
        Hi, A new lead for your business
        Name: [name]
        Mobile: [phone]
        City: [city]
        Query: [query]
        
        Format 2 (Premium Lead):
        Lead Details:
        Customer Name: [name]
        Contact No: [phone]
        Email: [email]
        Location: [location]
        Requirement: [requirement]
        """
        
        try:
            lead_data = {}
            
            # Extract Name (various formats)
            name_patterns = [
                r'Name:\s*(.+)',
                r'Customer Name:\s*(.+)',
                r'Contact Person:\s*(.+)'
            ]
            for pattern in name_patterns:
                name_match = re.search(pattern, email_body, re.IGNORECASE)
                if name_match:
                    lead_data['name'] = name_match.group(1).strip()
                    break
            
            # Extract Phone (various formats)
            phone_patterns = [
                r'Mobile:\s*(\+?\d[\d\s-]{9,})',
                r'Contact No[.:]?\s*(\+?\d[\d\s-]{9,})',
                r'Phone:\s*(\+?\d[\d\s-]{9,})',
                r'Number:\s*(\+?\d[\d\s-]{9,})'
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, email_body, re.IGNORECASE)
                if phone_match:
                    phone = re.sub(r'[^\d+]', '', phone_match.group(1))
                    if len(phone) == 10:
                        lead_data['phone'] = f"+91{phone}"
                    else:
                        lead_data['phone'] = phone if phone.startswith('+') else f"+{phone}"
                    break
            
            # Extract Email
            email_match = re.search(r'Email:\s*([^\s@]+@[^\s@]+\.[^\s@]+)', email_body, re.IGNORECASE)
            if email_match:
                lead_data['email'] = email_match.group(1).strip()
            
            # Extract City/Location
            location_patterns = [
                r'City:\s*(.+)',
                r'Location:\s*(.+)',
                r'Area:\s*(.+)'
            ]
            for pattern in location_patterns:
                loc_match = re.search(pattern, email_body, re.IGNORECASE)
                if loc_match:
                    lead_data['city'] = loc_match.group(1).strip()
                    break
            
            # Extract Query/Requirement
            query_patterns = [
                r'Query:\s*(.+)',
                r'Requirement:\s*(.+)',
                r'Looking for:\s*(.+)',
                r'Interest:\s*(.+)'
            ]
            for pattern in query_patterns:
                query_match = re.search(pattern, email_body, re.IGNORECASE)
                if query_match:
                    query = query_match.group(1).strip()
                    lead_data['interested_products'] = [query]
                    lead_data['query'] = query
                    break
            
            # Determine priority based on JustDial lead type
            if 'premium lead' in subject.lower() or 'verified lead' in subject.lower():
                lead_data['priority'] = 'high'
                lead_data['status'] = 'hot'
            elif 'new lead' in subject.lower():
                lead_data['priority'] = 'medium'
                lead_data['status'] = 'warm'
            else:
                lead_data['priority'] = 'medium'
                lead_data['status'] = 'new'
            
            # Set source
            lead_data['source'] = 'justdial'
            lead_data['store_location'] = self.store_emails.get(from_email, "Main Store")
            
            return lead_data if lead_data.get('name') or lead_data.get('phone') else None
            
        except Exception as e:
            print(f"Error parsing JustDial email: {e}")
            return None
    
    def parse_singleinterface_email(self, email_body: str, from_email: str) -> Optional[Dict[str, Any]]:
        """
        Parse SingleInterface email format
        
        Format:
        Dear Alfred,
        You have just received a contact query on your website. The following are the details:
        User Name: [name]
        Mobile: [phone]
        Email: [email]
        Interest In: [product]
        Query Type: [type]
        Planning Time: [timeline]
        """
        
        try:
            lead_data = {}
            
            # Extract User Name
            name_match = re.search(r'User Name:\s*(.+)', email_body, re.IGNORECASE)
            if name_match:
                lead_data['name'] = name_match.group(1).strip()
            
            # Extract Mobile
            mobile_match = re.search(r'Mobile:\s*(.+)', email_body, re.IGNORECASE)
            if mobile_match:
                phone = mobile_match.group(1).strip()
                # Clean phone number
                phone = re.sub(r'[^\d+]', '', phone)
                lead_data['phone'] = phone
            
            # Extract Email
            email_match = re.search(r'Email:\s*(.+)', email_body, re.IGNORECASE)
            if email_match:
                lead_data['email'] = email_match.group(1).strip()
            
            # Extract Interest In
            interest_match = re.search(r'Interest In:\s*(.+)', email_body, re.IGNORECASE)
            if interest_match:
                lead_data['interested_products'] = [interest_match.group(1).strip()]
            
            # Extract Query Type
            query_match = re.search(r'Query Type:\s*(.+)', email_body, re.IGNORECASE)
            if query_match:
                query_type = query_match.group(1).strip()
                lead_data['query_type'] = query_type
            
            # Extract Planning Time
            timeline_match = re.search(r'Planning Time:\s*(.+)', email_body, re.IGNORECASE)
            if timeline_match:
                timeline = timeline_match.group(1).strip().lower()
                if 'immediately' in timeline or 'urgent' in timeline:
                    lead_data['buying_timeline'] = 'immediate'
                elif 'week' in timeline:
                    lead_data['buying_timeline'] = 'this_week'
                elif 'month' in timeline:
                    lead_data['buying_timeline'] = 'this_month'
                else:
                    lead_data['buying_timeline'] = 'exploring'
            
            # Extract location from "Query from"
            location_match = re.search(r'Query from,?\s*(.+)', email_body, re.IGNORECASE)
            if location_match:
                lead_data['location'] = location_match.group(1).strip()
            
            # Determine store from receiving email
            store_name = self.store_emails.get(from_email, "Unknown Store")
            lead_data['store_location'] = store_name
            lead_data['source'] = f"brand_singleinterface_{store_name.lower().replace(' ', '_')}"
            
            return lead_data if lead_data else None
            
        except Exception as e:
            print(f"Error parsing SingleInterface email: {e}")
            return None
    
    def parse_bsh_email(self, email_body: str, subject: str, from_email: str) -> Optional[Dict[str, Any]]:
        """
        Parse BSH Direct email format
        
        Format:
        Subject: New Lead Notification to BOSCH Brand Store - Aditya Retail
        Lead Details:
        Name: [name]
        Mob: p:+91[phone]
        Product Inquiry: [product]
        Buying Intent: [intent]
        City: [city]
        Pin Code: [pincode]
        """
        
        try:
            lead_data = {}
            
            # Extract Name
            name_match = re.search(r'Name:\s*(.+)', email_body, re.IGNORECASE)
            if name_match:
                lead_data['name'] = name_match.group(1).strip()
            
            # Extract Mobile (handles format "p:+919876543210")
            mobile_match = re.search(r'Mob:\s*p?:?\+?(\d{10,12})', email_body, re.IGNORECASE)
            if mobile_match:
                phone = mobile_match.group(1)
                if len(phone) == 10:
                    lead_data['phone'] = f"+91{phone}"
                else:
                    lead_data['phone'] = f"+{phone}"
            
            # Extract Product Inquiry
            product_match = re.search(r'Product Inquiry:\s*(.+)', email_body, re.IGNORECASE)
            if product_match:
                product_inquiry = product_match.group(1).strip()
                lead_data['interested_products'] = [product_inquiry]
                lead_data['product_inquiry'] = product_inquiry
            
            # Extract Buying Intent
            intent_match = re.search(r'Buying Intent:\s*(.+)', email_body, re.IGNORECASE)
            if intent_match:
                intent = intent_match.group(1).strip().lower()
                if 'immediately' in intent or 'urgent' in intent or 'ready' in intent:
                    lead_data['buying_timeline'] = 'immediate'
                    lead_data['status'] = 'hot'  # Mark as HOT lead
                elif 'week' in intent or 'soon' in intent:
                    lead_data['buying_timeline'] = 'this_week'
                    lead_data['status'] = 'warm'
                elif 'exploring' in intent or 'just_exploring' in intent:
                    lead_data['buying_timeline'] = 'exploring'
                    lead_data['status'] = 'new'
                else:
                    lead_data['buying_timeline'] = 'this_month'
                    lead_data['status'] = 'warm'
            
            # Extract City
            city_match = re.search(r'City:\s*(.+)', email_body, re.IGNORECASE)
            if city_match:
                lead_data['city'] = city_match.group(1).strip()
            
            # Extract Pin Code
            pincode_match = re.search(r'Pin Code:\s*(\d+)', email_body, re.IGNORECASE)
            if pincode_match:
                lead_data['pincode'] = pincode_match.group(1).strip()
            
            # Check if it's a hot lead from subject
            if 'hot lead' in subject.lower():
                lead_data['status'] = 'hot'
                lead_data['priority'] = 'high'
            
            # Determine store from receiving email or subject
            store_name = self.store_emails.get(from_email, "Unknown Store")
            lead_data['store_location'] = store_name
            lead_data['source'] = f"brand_bsh_hot_{store_name.lower().replace(' ', '_')}"
            
            return lead_data if lead_data else None
            
        except Exception as e:
            print(f"Error parsing BSH email: {e}")
            return None
    
    async def create_lead_from_email(
        self,
        email_data: Dict[str, Any],
        email_type: str,
        db
    ) -> Optional[str]:
        """
        Create lead in database from parsed email data
        """
        
        try:
            lead_id = str(uuid.uuid4())
            
            # Build notes from all available info
            notes_parts = []
            if email_data.get('query_type'):
                notes_parts.append(f"Query Type: {email_data['query_type']}")
            if email_data.get('product_inquiry'):
                notes_parts.append(f"Product Inquiry: {email_data['product_inquiry']}")
            if email_data.get('location'):
                notes_parts.append(f"Location: {email_data['location']}")
            if email_data.get('city'):
                notes_parts.append(f"City: {email_data['city']}")
            if email_data.get('pincode'):
                notes_parts.append(f"Pincode: {email_data['pincode']}")
            
            notes = ". ".join(notes_parts) if notes_parts else "Lead from brand email"
            
            lead = {
                "id": lead_id,
                "name": email_data.get('name', 'Customer'),
                "email": email_data.get('email'),
                "phone": email_data.get('phone'),
                "source": email_data.get('source', f'email_{email_type}'),
                "store_location": email_data.get('store_location', 'Unknown'),
                "status": email_data.get('status', 'new'),
                "interested_products": email_data.get('interested_products', []),
                "notes": notes,
                "buying_timeline": email_data.get('buying_timeline', 'exploring'),
                "priority": email_data.get('priority', 'medium'),
                "expected_value": 0,
                "assigned_to": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "last_contact_date": None,
                "next_follow_up": None,
                "interactions": [{
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "email_capture",
                    "source": email_type,
                    "content": f"Lead captured from {email_type} email"
                }],
                "follow_ups": [],
                "email_sequence_status": "pending",
                "emails_sent": [],
                "city": email_data.get('city'),
                "pincode": email_data.get('pincode')
            }
            
            await db.leads.insert_one(lead)
            print(f"✅ Created lead from email: {lead_id} - {email_data.get('name')} - Store: {email_data.get('store_location')}")
            
            # Send welcome email if email address available
            if email_data.get('email'):
                await self.send_email_capture_welcome(lead, db)
            
            return lead_id
            
        except Exception as e:
            print(f"❌ Error creating lead from email: {e}")
            return None
    
    async def send_email_capture_welcome(self, lead: Dict[str, Any], db):
        """
        Send welcome email to leads captured from brand emails
        """
        
        try:
            from sendgrid_email_service import sendgrid_email_service
            
            email = lead.get('email')
            if not email:
                return
            
            name = lead.get('name', 'Valued Customer')
            first_name = name.split()[0]
            store = lead.get('store_location', 'Aditya Retail')
            interested_products = lead.get('interested_products', [])
            
            products_section = ""
            if interested_products:
                products_section = f"\n\n🛍️ YOU SHOWED INTEREST IN:\n" + "\n".join([f"• {p}" for p in interested_products])
            
            subject = f"Hi {first_name}, Thank You for Your Interest! 🙏"
            
            body = f"""Hi {first_name},

Thank you for reaching out to us at {store}!

We received your inquiry and we're excited to help you find the perfect appliance for your home.
{products_section}

🎯 WHY CHOOSE ADITYA RETAIL:
✅ Authorized Dealer - Bosch, Siemens & Hindware
✅ 10,000+ Happy Customers in Bangalore
✅ Same Day Delivery Available
✅ 2-Year Warranty on All Products
✅ FREE Installation & Demo

🎁 SPECIAL OFFERS FOR YOU:
• 15% OFF on orders above ₹1,00,000
• FREE Installation worth ₹2,000
• 0% EMI available on all credit cards
• Extended warranty at special rates

📞 LET'S TALK!
One of our product experts will contact you within 24 hours.
For immediate assistance:

📱 Call/WhatsApp: +91-9844577440
📧 Email: service.adityaretail@gmail.com
🌐 Browse Catalog: https://adityaretail.com

📍 VISIT OUR STORE - {store}:
Mon-Sat: 10 AM - 8 PM
Sunday: By Appointment

Looking forward to serving you!

Warm Regards,
Rohit Upadhyaya
Sales Manager
Aditya Retail - {store}
"""
            
            result = sendgrid_email_service.send_email(
                to_email=email,
                subject=subject,
                body=body,
                from_agent="sales",
                html=False
            )
            
            if result.get('status') == 'success':
                await db.leads.update_one(
                    {"id": lead['id']},
                    {
                        "$push": {
                            "emails_sent": {
                                "type": "email_capture_welcome",
                                "sent_at": datetime.now(timezone.utc).isoformat(),
                                "status": "sent"
                            }
                        },
                        "$set": {
                            "email_sequence_status": "active",
                            "status": "contacted" if lead.get('status') == 'new' else lead.get('status'),
                            "last_contact_date": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
                print(f"✅ Email capture welcome sent to {email}")
            
        except Exception as e:
            print(f"❌ Error sending email capture welcome: {e}")

# Global instance
email_lead_capture_service = EmailLeadCaptureService()
