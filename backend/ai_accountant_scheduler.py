"""
Scheduler for AI Accounting Agents
Runs autonomous accounting tasks on schedule
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import asyncio
from ai_daily_accountant import DailyAccountantAgent
from database import db

scheduler = AsyncIOScheduler()

async def run_daily_accountant():
    """Run the daily accountant agent"""
    print(f"⏰ Scheduled: Running Daily AI Accountant at {datetime.now()}")
    
    try:
        agent = DailyAccountantAgent(db)
        results = await agent.run_daily_accounting()
        print(f"✅ Daily accounting completed: {results.get('transactions_processed', 0)} transactions")
        return results
    except Exception as e:
        print(f"❌ Daily accountant failed: {str(e)}")
        return {"error": str(e)}

def start_scheduler():
    """Start the scheduler with all accounting jobs"""
    
    # Schedule daily accountant to run every night at 2:00 AM
    scheduler.add_job(
        run_daily_accountant,
        CronTrigger(hour=2, minute=0),  # 2:00 AM every day
        id='daily_accountant',
        name='Daily AI Accountant',
        replace_existing=True
    )
    
    print("📅 AI Accounting Scheduler initialized")
    print("   - Daily Accountant: 2:00 AM every day")
    
    scheduler.start()
    print("✅ Scheduler started successfully")

def stop_scheduler():
    """Stop the scheduler"""
    scheduler.shutdown()
    print("🛑 Scheduler stopped")
