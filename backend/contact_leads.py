import time, uuid
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from lead_sweeps import add_lead
from mail_leads import get_db

router = APIRouter(prefix="/contact", tags=["contact"])
_hits = {}

class ContactIn(BaseModel):
    name: str = Field("", max_length=100)
    email: str = Field("", max_length=150)
    phone: str = Field("", max_length=20)
    subject: str = Field("", max_length=200)
    message: str = Field("", max_length=2000)
    website: str = ""  # honeypot, real users leave it empty

@router.post("/")
async def submit(body: ContactIn, request: Request):
    if body.website:
        return {"ok": True}
    fwd = request.headers.get("x-forwarded-for", "")
    ip = fwd.split(",")[0].strip() or (request.client.host if request.client else "?")
    now = time.time()
    hits = [t for t in _hits.get(ip, []) if now - t < 3600]
    if len(hits) >= 5:
        raise HTTPException(status_code=429, detail="Too many requests, please try later")
    hits.append(now)
    _hits[ip] = hits
    if not (body.email.strip() or body.phone.strip()):
        raise HTTPException(status_code=400, detail="Please enter an email or phone number")
    note = "Contact form: %s | %s" % (body.subject.strip() or "(no subject)", body.message.strip() or "(no message)")
    r = await add_lead(get_db(), "contact_" + uuid.uuid4().hex, body.name.strip(), body.email, body.phone,
                       "contact_form", note, None, 65)
    if r is None:
        raise HTTPException(status_code=400, detail="Invalid email or phone number")
    return {"ok": True}
