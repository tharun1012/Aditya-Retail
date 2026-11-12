from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional
from database import get_db
from ai_daily_accountant import DailyAccountantAgent
from datetime import datetime, timezone

router = APIRouter(prefix="/ai-accountant", tags=["AI Autonomous Accountant"])

@router.post("/run-daily-accounting")
async def trigger_daily_accounting(background_tasks: BackgroundTasks, db = Depends(get_db)):
    """Manually trigger the daily accounting process"""
    try:
        # Run in background
        background_tasks.add_task(run_accounting_task, db)
        
        return {
            "status": "success",
            "message": "Daily accounting process started in background",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start accounting: {str(e)}")

async def run_accounting_task(db):
    """Background task to run accounting"""
    agent = DailyAccountantAgent(db)
    results = await agent.run_daily_accounting()
    print(f"Background accounting completed: {results}")

@router.get("/daily-reports")
async def get_daily_reports(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 30,
    db = Depends(get_db)
):
    """Get daily accounting reports"""
    try:
        query = {}
        
        if from_date and to_date:
            query["report_date"] = {"$gte": from_date, "$lte": to_date}
        
        reports = await db.daily_accounting_reports.find(
            query,
            {"_id": 0}
        ).sort("report_date", -1).limit(limit).to_list(None)
        
        return {
            "status": "success",
            "reports": reports,
            "count": len(reports)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch reports: {str(e)}")

# Maps a transaction's "type" (as stored in daily_accounting_reports)
# to the collection holding its full original document, and the field
# that document uses as its human-readable reference number.
_TRANSACTION_DETAIL_MAP = {
    "sale_online": ("orders", "order_number"),
    "sale_offline": ("offline_invoices", "invoice_number"),
    "purchase": ("purchases", "po_number"),
    "grn": ("grn", "grn_number"),
    "purchase_bill": ("purchase_bills", "bill_number"),
    "journal_voucher": ("journal_vouchers", "voucher_number"),
    "payment_receipt": ("so_payment_receipts", "receipt_number"),
}


@router.get("/transaction-detail")
async def get_transaction_detail(type: str, id: str, db = Depends(get_db)):
    """Fetch the full original document for one transaction referenced in
    a daily accounting report, so the UI can show complete details
    (items, customer, address, etc.) beyond the report's flattened
    summary row."""
    # voucher_payment / voucher_receipt / voucher_<anything> all live in
    # the same vouchers collection, keyed by voucher_number.
    if type.startswith("voucher_"):
        collection_name, id_field = "vouchers", "voucher_number"
    elif type in _TRANSACTION_DETAIL_MAP:
        collection_name, id_field = _TRANSACTION_DETAIL_MAP[type]
    else:
        raise HTTPException(status_code=400, detail=f"Unknown transaction type: {type}")

    collection = db[collection_name]
    doc = await collection.find_one({id_field: id}, {"_id": 0})

    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"No {type} document found with {id_field}={id}"
        )

    return {"status": "success", "type": type, "document": doc}


@router.get("/daily-reports/{report_date}")
async def get_daily_report(report_date: str, db = Depends(get_db)):
    """Get specific daily report by date"""
    try:
        report = await db.daily_accounting_reports.find_one(
            {"report_date": report_date},
            {"_id": 0}
        )
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return {
            "status": "success",
            "report": report
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@router.get("/journal-entries")
async def get_journal_entries(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get journal entries created by AI"""
    try:
        query = {"created_by": "AI Daily Accountant"}
        
        if from_date and to_date:
            query["date"] = {"$gte": from_date, "$lte": to_date}
        
        entries = await db.journal_entries.find(
            query,
            {"_id": 0}
        ).sort("date", -1).limit(limit).to_list(None)
        
        return {
            "status": "success",
            "journal_entries": entries,
            "count": len(entries)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch journal entries: {str(e)}")

@router.get("/gst-liability")
async def get_gst_liability(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db = Depends(get_db)
):
    """Get GST liability calculated by AI"""
    try:
        query = {}
        
        if from_date and to_date:
            query["date"] = {"$gte": from_date, "$lte": to_date}
        
        liabilities = await db.gst_liability.find(
            query,
            {"_id": 0}
        ).sort("date", -1).to_list(None)
        
        # Calculate totals
        total_output = sum(l.get("output_tax", 0) for l in liabilities)
        total_input = sum(l.get("input_tax", 0) for l in liabilities)
        total_liability = total_output - total_input
        
        return {
            "status": "success",
            "daily_liabilities": liabilities,
            "summary": {
                "total_output_tax": round(total_output, 2),
                "total_input_tax": round(total_input, 2),
                "net_liability": round(total_liability, 2),
                "cgst_payable": round(total_liability / 2, 2),
                "sgst_payable": round(total_liability / 2, 2),
                "period": f"{from_date} to {to_date}" if from_date and to_date else "All time"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch GST liability: {str(e)}")

@router.get("/issues")
async def get_flagged_issues(
    severity: Optional[str] = None,
    limit: int = 50,
    db = Depends(get_db)
):
    """Get issues flagged by AI accountant"""
    try:
        # Get reports with issues
        reports = await db.daily_accounting_reports.find(
            {"issues_found": {"$ne": []}},
            {"_id": 0}
        ).sort("report_date", -1).limit(limit).to_list(None)
        
        # Extract and flatten issues
        all_issues = []
        for report in reports:
            for issue in report.get("issues_found", []):
                issue["report_date"] = report["report_date"]
                if not severity or issue.get("severity") == severity:
                    all_issues.append(issue)
        
        return {
            "status": "success",
            "issues": all_issues,
            "count": len(all_issues)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch issues: {str(e)}")

@router.get("/scheduler-status")
async def get_scheduler_status():
    """Get scheduler status and next run times"""
    try:
        from ai_accountant_scheduler import scheduler
        
        jobs = []
        for job in scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "success",
            "scheduler_running": scheduler.running,
            "jobs": jobs
        }
    
    except Exception as e:
        return {
            "status": "error",
            "message": "Scheduler not initialized",
            "detail": str(e)
        }
