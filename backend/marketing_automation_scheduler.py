"""
Autonomous AI Marketing Agent Scheduler
Runs daily automation tasks for campaign management and lead generation
"""
import asyncio
import schedule
import time
from datetime import datetime, timezone
from ai_marketing_automation import AIMarketingAgent
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketingAutomationScheduler:
    """Background scheduler for autonomous marketing automation"""
    
    def __init__(self):
        self.agent = AIMarketingAgent()
        self.is_running = False
        mongo_url = os.environ.get('MONGO_URL')
        db_name = os.environ.get('DB_NAME')
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
    
    async def daily_automation(self):
        """Run daily marketing automation tasks"""
        try:
            logger.info("🤖 Starting daily marketing automation...")
            
            # 1. Generate/Update Campaigns
            logger.info("📊 Generating marketing campaigns...")
            campaigns = await self.agent.generate_marketing_campaigns()
            logger.info(f"✅ Created {len(campaigns)} campaigns")
            
            # 2. Track Progress Towards Targets
            logger.info("🎯 Tracking monthly targets...")
            progress = await self.agent.track_monthly_progress()
            logger.info(f"Progress: {progress['leads_generated']}/{progress['target_leads']} leads")
            
            # 3. Optimize Campaigns
            logger.info("⚡ Optimizing campaign performance...")
            optimizations = await self.agent.optimize_campaigns()
            logger.info(f"✅ Optimized {optimizations['campaigns_updated']} campaigns")
            
            # 4. Send Performance Report
            logger.info("📧 Generating performance report...")
            report = await self.agent.generate_daily_report()
            
            # 5. Save automation log
            await self.db.automation_logs.insert_one({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "daily_automation",
                "campaigns_created": len(campaigns),
                "progress": progress,
                "optimizations": optimizations,
                "status": "success"
            })
            
            logger.info("✅ Daily automation complete!")
            
        except Exception as e:
            logger.error(f"❌ Automation error: {str(e)}")
            await self.db.automation_logs.insert_one({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "daily_automation",
                "status": "failed",
                "error": str(e)
            })
    
    async def weekly_strategy_review(self):
        """Run weekly strategy review and adjustments"""
        try:
            logger.info("📈 Starting weekly strategy review...")
            
            # Analyze performance
            analysis = await self.agent.weekly_performance_analysis()
            
            # Adjust strategies
            adjustments = await self.agent.adjust_weekly_strategy(analysis)
            
            logger.info(f"✅ Weekly review complete: {adjustments['changes_made']} adjustments")
            
        except Exception as e:
            logger.error(f"❌ Weekly review error: {str(e)}")
    
    async def monthly_report(self):
        """Generate comprehensive monthly report"""
        try:
            logger.info("📊 Generating monthly report...")
            
            report = await self.agent.generate_monthly_report()
            
            # Save report
            await self.db.monthly_reports.insert_one(report)
            
            logger.info("✅ Monthly report generated")
            
        except Exception as e:
            logger.error(f"❌ Monthly report error: {str(e)}")
    
    def start_scheduler(self):
        """Start the background scheduler"""
        logger.info("🚀 Starting Marketing Automation Scheduler...")
        
        # Schedule daily automation at 9 AM
        schedule.every().day.at("09:00").do(
            lambda: asyncio.run(self.daily_automation())
        )
        
        # Schedule weekly review every Monday at 10 AM
        schedule.every().monday.at("10:00").do(
            lambda: asyncio.run(self.weekly_strategy_review())
        )
        
        # Schedule monthly report on 1st of month at 11 AM
        schedule.every().day.at("11:00").do(
            lambda: asyncio.run(self._check_and_run_monthly())
        )
        
        self.is_running = True
        logger.info("✅ Scheduler configured:")
        logger.info("   - Daily automation: 9:00 AM")
        logger.info("   - Weekly review: Monday 10:00 AM")
        logger.info("   - Monthly report: 1st of month 11:00 AM")
        
        # Run first automation immediately
        logger.info("🚀 Running initial automation...")
        asyncio.run(self.daily_automation())
        
        # Keep scheduler running
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def _check_and_run_monthly(self):
        """Check if it's the 1st of month and run monthly report"""
        if datetime.now().day == 1:
            await self.monthly_report()
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        logger.info("⏹️  Scheduler stopped")

# Singleton instance
_scheduler_instance = None

def get_scheduler():
    """Get or create scheduler instance"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = MarketingAutomationScheduler()
    return _scheduler_instance

if __name__ == "__main__":
    # Run scheduler
    scheduler = get_scheduler()
    scheduler.start_scheduler()
