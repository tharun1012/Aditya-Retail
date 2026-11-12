"""
Expert Consultation Routes
API endpoints for deep research consultation requests
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import os
import uuid

from deep_research_consultant import deep_research_consultant
from database import get_db

router = APIRouter(prefix="/consultation", tags=["Expert Consultation"])

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL')
db_name = os.environ.get('DB_NAME', 'startup_template')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]


class ConsultationRequest(BaseModel):
    # Customer Info
    customer_name: str
    email: EmailStr
    phone: Optional[str] = None
    
    # Kitchen Details
    kitchen_size: str = "medium"  # small, medium, large
    kitchen_dimensions: Optional[str] = None  # e.g., "10x12 feet"
    
    # Budget
    budget_min: int = 50000
    budget_max: int = 500000
    
    # Appliances Needed
    appliance_types: List[str] = []  # refrigerator, washing_machine, dishwasher, oven, cooktop, chimney
    
    # Preferences
    family_size: str = "4"  # 1-2, 3-4, 5-6, 7+
    cooking_frequency: str = "daily"  # rarely, weekly, daily, multiple_times_daily
    
    # Priority Factors (ranked list)
    priority_factors: List[str] = ["quality", "energy_efficiency", "price", "aesthetics", "features"]
    
    # Brand Preference
    brand_preference: List[str] = ["any"]  # Bosch, Siemens, any
    
    # Energy & Aesthetics
    energy_priority: str = "important"  # not_important, somewhat, important, very_important
    aesthetic_preference: str = "modern"  # traditional, modern, minimalist, premium
    
    # Special Requirements
    special_requirements: Optional[str] = None


@router.post("/request")
async def submit_consultation_request(
    request: ConsultationRequest,
    background_tasks: BackgroundTasks
):
    """
    Submit a consultation request
    The report will be generated and emailed within 10-15 minutes
    Also creates a lead in CRM for sales follow-up
    """
    
    try:
        consultation_id = str(uuid.uuid4())
        
        # Create consultation record
        consultation = {
            "id": consultation_id,
            "customer_name": request.customer_name,
            "email": request.email,
            "phone": request.phone,
            "requirements": request.dict(),
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.consultations.insert_one(consultation)
        
        # Auto-create lead in CRM for sales follow-up
        lead_id = f"LEAD-CONSULT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        lead = {
            "id": lead_id,
            "name": request.customer_name,
            "email": request.email,
            "phone": request.phone or "",
            "source": "Expert Consultation",
            "status": "new",
            "score": 85,  # High score for consultation leads (high intent)
            "tags": ["consultation", "high-intent"] + request.appliance_types[:3],
            "notes": f"Expert consultation request. Budget: ₹{request.budget_min:,} - ₹{request.budget_max:,}. Kitchen: {request.kitchen_size}. Appliances: {', '.join(request.appliance_types)}",
            "consultation_id": consultation_id,
            "budget_min": request.budget_min,
            "budget_max": request.budget_max,
            "appliance_interests": request.appliance_types,
            "brand_preference": request.brand_preference,
            "assigned_to": None,
            "follow_up_date": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.leads.insert_one(lead)

        # Notify CRM inbox (fire-and-forget; failures are logged, not raised)
        try:
            from crm_lead_notifier import notify_new_lead
            notify_new_lead(
                lead,
                source="consultation",
                extra={
                    "kitchen_size": request.kitchen_size,
                    "consultation_details": (
                        f"Kitchen Size: {request.kitchen_size}\n"
                        f"Budget: ₹{request.budget_min:,} – ₹{request.budget_max:,}\n"
                        f"Appliances: {', '.join(request.appliance_types)}\n"
                        f"Brand Preference: {request.brand_preference or '—'}\n"
                        f"Consultation ID: {consultation_id}"
                    ),
                },
            )
        except Exception as _e:
            print(f"CRM notify (consultation) failed: {_e}")

        # Process consultation in background
        background_tasks.add_task(
            deep_research_consultant.process_consultation_request,
            consultation_id,
            request.dict()
        )
        
        return {
            "status": "success",
            "message": "Your consultation request has been received! You'll receive a detailed report via email within 10-15 minutes.",
            "consultation_id": consultation_id,
            "lead_id": lead_id,
            "email": request.email
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{consultation_id}")
async def get_consultation_status(consultation_id: str):
    """
    Check the status of a consultation request
    """
    
    consultation = await db.consultations.find_one(
        {"id": consultation_id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    return {
        "status": "success",
        "consultation": {
            "id": consultation['id'],
            "status": consultation['status'],
            "created_at": consultation['created_at'],
            "completed_at": consultation.get('completed_at'),
            "email_sent": consultation.get('email_sent', False),
            "products_matched": consultation.get('products_matched', 0)
        }
    }


@router.get("/report/{consultation_id}")
async def get_consultation_report(consultation_id: str):
    """
    Get the full consultation report
    """
    
    consultation = await db.consultations.find_one(
        {"id": consultation_id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    if consultation['status'] != 'completed':
        return {
            "status": "pending",
            "message": f"Report is still being generated. Current status: {consultation['status']}"
        }
    
    return {
        "status": "success",
        "report": consultation.get('report', {}),
        "generated_at": consultation.get('completed_at')
    }


@router.get("/history")
async def get_consultation_history(
    email: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """
    Get consultation history (optionally filtered by email)
    """
    
    query = {}
    if email:
        query["email"] = email
    
    skip = (page - 1) * limit
    
    consultations = await db.consultations.find(
        query,
        {"_id": 0, "report": 0}  # Exclude large report data
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.consultations.count_documents(query)
    
    return {
        "status": "success",
        "consultations": consultations,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }


@router.post("/process-sync/{consultation_id}")
async def process_consultation_sync(consultation_id: str):
    """
    Process consultation synchronously (for testing)
    """
    
    consultation = await db.consultations.find_one(
        {"id": consultation_id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    result = await deep_research_consultant.process_consultation_request(
        consultation_id,
        consultation['requirements']
    )
    
    return result


@router.get("/options")
async def get_consultation_options():
    """
    Get available options for consultation form
    Dynamically fetches brands from the products database
    """
    
    # Dynamically fetch brands from products collection
    try:
        brands_from_db = await db.products.distinct("brand")
        # Filter out empty or None values, normalize to title case, deduplicate
        normalized_brands = set()
        for b in brands_from_db:
            if b and isinstance(b, str):
                # Normalize: strip whitespace, title case
                normalized = b.strip().title()
                # Skip very short brand names or obvious non-brands
                if len(normalized) >= 2 and normalized not in ['N/A', 'Na', 'None', 'Unknown']:
                    normalized_brands.add(normalized)
        brands_from_db = sorted(list(normalized_brands))
    except Exception as e:
        print(f"Error fetching brands: {e}")
        brands_from_db = ["Bosch", "Siemens", "Electrolux"]  # Fallback
    
    # Build brand options dynamically
    brand_options = [{"value": "any", "label": "No Preference"}]
    for brand in brands_from_db:
        brand_options.append({"value": brand.lower(), "label": brand})
    
    # FIXED: Use a predefined list of valid appliance categories
    # Don't pull from products.category as it may contain product names
    appliance_types = [
        {"value": "refrigerator", "label": "Refrigerator", "icon": "🧊"},
        {"value": "washing_machine", "label": "Washing Machine", "icon": "🧺"},
        {"value": "dishwasher", "label": "Dishwasher", "icon": "🍽️"},
        {"value": "oven", "label": "Oven", "icon": "🔥"},
        {"value": "microwave", "label": "Microwave", "icon": "🍳"},
        {"value": "cooktop", "label": "Cooktop / Hob", "icon": "🔥"},
        {"value": "chimney", "label": "Chimney / Hood", "icon": "💨"},
        {"value": "dryer", "label": "Dryer", "icon": "👕"},
        {"value": "coffee_machine", "label": "Coffee Machine", "icon": "☕"},
        {"value": "air_fryer", "label": "Air Fryer", "icon": "🍟"},
        {"value": "cooking_range", "label": "Cooking Range", "icon": "🍳"},
        {"value": "induction", "label": "Induction Cooktop", "icon": "🔥"},
        {"value": "mixer_grinder", "label": "Mixer / Grinder", "icon": "🥤"},
        {"value": "water_purifier", "label": "Water Purifier", "icon": "💧"},
        {"value": "vacuum_cleaner", "label": "Vacuum Cleaner", "icon": "🧹"},
        {"value": "air_conditioner", "label": "Air Conditioner", "icon": "❄️"},
        {"value": "geyser", "label": "Geyser / Water Heater", "icon": "🚿"},
        {"value": "other", "label": "Other Appliance", "icon": "🔌"}
    ]
    
    return {
        "kitchen_sizes": [
            {"value": "small", "label": "Small (< 80 sq ft)"},
            {"value": "medium", "label": "Medium (80-150 sq ft)"},
            {"value": "large", "label": "Large (> 150 sq ft)"}
        ],
        "appliance_types": appliance_types,
        "family_sizes": [
            {"value": "1-2", "label": "1-2 Members"},
            {"value": "3-4", "label": "3-4 Members"},
            {"value": "5-6", "label": "5-6 Members"},
            {"value": "7+", "label": "7+ Members"}
        ],
        "cooking_frequencies": [
            {"value": "rarely", "label": "Rarely (1-2 times/week)"},
            {"value": "weekly", "label": "Few times a week"},
            {"value": "daily", "label": "Daily"},
            {"value": "multiple_times_daily", "label": "Multiple times daily"}
        ],
        "priority_factors": [
            {"value": "quality", "label": "Build Quality & Durability"},
            {"value": "energy_efficiency", "label": "Energy Efficiency"},
            {"value": "price", "label": "Price / Value for Money"},
            {"value": "aesthetics", "label": "Look & Design"},
            {"value": "features", "label": "Smart Features"},
            {"value": "brand", "label": "Brand Reputation"}
        ],
        "brands": brand_options,
        "energy_priorities": [
            {"value": "not_important", "label": "Not Important"},
            {"value": "somewhat", "label": "Somewhat Important"},
            {"value": "important", "label": "Important"},
            {"value": "very_important", "label": "Very Important"}
        ],
        "aesthetic_preferences": [
            {"value": "traditional", "label": "Traditional"},
            {"value": "modern", "label": "Modern"},
            {"value": "minimalist", "label": "Minimalist"},
            {"value": "premium", "label": "Premium / Luxury"}
        ],
        "budget_ranges": [
            {"min": 25000, "max": 50000, "label": "₹25K - ₹50K"},
            {"min": 50000, "max": 100000, "label": "₹50K - ₹1L"},
            {"min": 100000, "max": 200000, "label": "₹1L - ₹2L"},
            {"min": 200000, "max": 500000, "label": "₹2L - ₹5L"},
            {"min": 500000, "max": 1000000, "label": "₹5L - ₹10L"},
            {"min": 1000000, "max": 2500000, "label": "₹10L+"}
        ]
    }



# ==================== ADMIN ENDPOINTS ====================

@router.get("/admin/list")
async def get_all_consultations_admin(
    page: int = 1,
    limit: int = 20,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    Admin endpoint to view all consultations with filters
    Used for sales team follow-up and tracking
    """
    
    query = {}
    
    if status:
        query["status"] = status
    
    if search:
        query["$or"] = [
            {"customer_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}}
        ]
    
    skip = (page - 1) * limit
    
    # Get consultations with all details
    consultations = await db.consultations.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    total = await db.consultations.count_documents(query)
    
    # Get summary stats
    total_all = await db.consultations.count_documents({})
    total_pending = await db.consultations.count_documents({"status": "pending"})
    total_completed = await db.consultations.count_documents({"status": "completed"})
    total_email_sent = await db.consultations.count_documents({"email_sent": True})
    
    return {
        "status": "success",
        "consultations": consultations,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit,
        "stats": {
            "total_consultations": total_all,
            "pending": total_pending,
            "completed": total_completed,
            "emails_sent": total_email_sent
        }
    }


@router.get("/admin/detail/{consultation_id}")
async def get_consultation_detail_admin(consultation_id: str):
    """
    Admin endpoint to get full consultation details including report
    """
    
    consultation = await db.consultations.find_one(
        {"id": consultation_id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    # Get associated lead if exists
    lead = await db.leads.find_one(
        {"consultation_id": consultation_id},
        {"_id": 0}
    )
    
    return {
        "status": "success",
        "consultation": consultation,
        "lead": lead
    }


@router.put("/admin/assign/{consultation_id}")
async def assign_consultation_to_sales(
    consultation_id: str,
    assigned_to: str,
    follow_up_date: Optional[str] = None,
    notes: Optional[str] = None
):
    """
    Assign a consultation to a sales team member for follow-up
    """
    
    # Update consultation
    update_data = {
        "assigned_to": assigned_to,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    if follow_up_date:
        update_data["follow_up_date"] = follow_up_date
    
    if notes:
        update_data["admin_notes"] = notes
    
    result = await db.consultations.update_one(
        {"id": consultation_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    # Also update associated lead
    await db.leads.update_one(
        {"consultation_id": consultation_id},
        {"$set": {
            "assigned_to": assigned_to,
            "follow_up_date": follow_up_date,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "status": "success",
        "message": f"Consultation assigned to {assigned_to}"
    }


@router.get("/admin/html-report/{consultation_id}")
async def get_html_report_admin(consultation_id: str):
    """
    Get the HTML report for a consultation (for preview/download)
    """
    
    consultation = await db.consultations.find_one(
        {"id": consultation_id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    if consultation.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Report not yet generated")
    
    report = consultation.get('report', {})
    
    # Generate HTML report
    html_report = deep_research_consultant.generate_html_report(report)
    
    return {
        "status": "success",
        "consultation_id": consultation_id,
        "customer_name": consultation.get('customer_name'),
        "email": consultation.get('email'),
        "html_report": html_report
    }


@router.post("/admin/resend-email/{consultation_id}")
async def resend_consultation_email(consultation_id: str):
    """
    Resend consultation report email
    """
    
    consultation = await db.consultations.find_one(
        {"id": consultation_id},
        {"_id": 0}
    )
    
    if not consultation:
        raise HTTPException(status_code=404, detail="Consultation not found")
    
    if consultation.get('status') != 'completed':
        raise HTTPException(status_code=400, detail="Report not yet generated")
    
    report = consultation.get('report', {})
    email = consultation.get('email')
    
    if not email:
        raise HTTPException(status_code=400, detail="No email address found")
    
    # Send email
    email_sent = await deep_research_consultant.send_consultation_report(
        consultation_id,
        email,
        report
    )
    
    if email_sent:
        await db.consultations.update_one(
            {"id": consultation_id},
            {"$set": {
                "email_sent": True,
                "email_resent_at": datetime.now(timezone.utc).isoformat()
            }}
        )
    
    return {
        "status": "success" if email_sent else "error",
        "message": "Email sent successfully" if email_sent else "Failed to send email",
        "email": email
    }
