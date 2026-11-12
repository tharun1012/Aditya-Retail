"""
Background scheduler for automated lead email follow-ups
Runs every hour to check and send scheduled emails
"""
import asyncio
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from lead_automation_service import lead_automation

async def process_email_sequences():
    """Process all pending email sequences"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'startup_template')
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"\n{'='*60}")
        print(f"🤖 Lead Email Automation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        # Get all leads with active email sequences
        leads = await db.leads.find({
            "email": {"$exists": True, "$ne": None},
            "status": {"$nin": ["won", "lost"]}  # Don't email converted/lost leads
        }).to_list(1000)
        
        print(f"📊 Found {len(leads)} active leads to process\n")
        
        for lead in leads:
            try:
                lead_id = lead.get('id')
                email = lead.get('email')
                created_at = datetime.fromisoformat(lead.get('created_at').replace('Z', '+00:00'))
                emails_sent = lead.get('emails_sent', [])
                
                # Calculate days since lead creation
                days_since_creation = (datetime.now(timezone.utc) - created_at).days
                
                # Check which emails have been sent
                sent_types = [e.get('type') for e in emails_sent]
                
                # Day 0: Welcome email (should already be sent on creation)
                if 'welcome' not in sent_types:
                    print(f"📧 Sending welcome email to {email}")
                    await lead_automation.send_welcome_email(lead, db)
                    await asyncio.sleep(1)  # Rate limit
                
                # Day 2: Follow-up email
                elif days_since_creation >= 2 and 'day2' not in sent_types:
                    print(f"📧 Sending Day 2 follow-up to {email}")
                    await lead_automation.send_follow_up_email(lead, 'day2', db)
                    await asyncio.sleep(1)
                
                # Day 4: Nurture email
                elif days_since_creation >= 4 and 'day4' not in sent_types:
                    print(f"📧 Sending Day 4 nurture email to {email}")
                    await lead_automation.send_follow_up_email(lead, 'day4', db)
                    await asyncio.sleep(1)
                
                # Day 7: Urgency email
                elif days_since_creation >= 7 and 'day7' not in sent_types:
                    print(f"📧 Sending Day 7 urgency email to {email}")
                    await lead_automation.send_follow_up_email(lead, 'day7', db)
                    await asyncio.sleep(1)
                
                # Update lead score after each check
                await lead_automation.update_lead_status_by_score(lead_id, db)
                
            except Exception as e:
                print(f"❌ Error processing lead {lead.get('id')}: {e}")
                continue
        
        # Check for hot leads that need escalation
        print(f"\n{'='*60}")
        print("🔥 Checking for hot leads...")
        print(f"{'='*60}\n")
        
        escalations = await lead_automation.check_and_escalate_hot_leads(db)
        
        if escalations:
            print(f"🚨 Found {len(escalations)} hot leads needing attention:\n")
            for esc in escalations:
                print(f"   🔥 {esc['name']} (Score: {esc['score']})")
                print(f"      📧 {esc['email']}")
                print(f"      📝 {esc['notes'][:100]}")
                print()
        else:
            print("✅ No new hot leads to escalate\n")
        
        print(f"{'='*60}")
        print(f"✅ Email automation cycle complete")
        print(f"{'='*60}\n")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error in email scheduler: {e}")

async def run_scheduler():
    """Run the scheduler continuously"""
    print("🚀 Lead Email Scheduler Started")
    print("📧 Will check for pending emails every hour\n")
    
    while True:
        try:
            await process_email_sequences()
            
            # Wait 1 hour before next check
            print(f"⏰ Next check in 1 hour...\n")
            await asyncio.sleep(3600)  # 1 hour
            
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            print("⏰ Retrying in 5 minutes...\n")
            await asyncio.sleep(300)  # 5 minutes on error

if __name__ == "__main__":
    # For testing: run once immediately
    asyncio.run(process_email_sequences())
