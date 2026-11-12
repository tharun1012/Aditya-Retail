"""Customer password management: change, forgot, reset."""
import os, re, asyncio, secrets, hashlib, logging
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

from auth_routes import db, SECRET_KEY, ALGORITHM, hash_password, verify_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Customer Password"])
bearer = HTTPBearer()
STORE_URL = os.environ.get("STORE_URL", "https://adityaretail.com").rstrip("/")
GENERIC_MSG = "If an account exists for that email, a reset link has been sent."


class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    new_password: str


def check_strength(pw: str):
    if len(pw) < 8 or not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        raise HTTPException(400, "Password must be at least 8 characters and include a letter and a number.")


async def current_customer(cred: HTTPAuthorizationCredentials = Depends(bearer)):
    try:
        payload = jwt.decode(cred.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(401, "Invalid or expired session. Please log in again.")
    if payload.get("role") != "customer" or not payload.get("user_id"):
        raise HTTPException(403, "Customer accounts only")
    user = await db.users.find_one({"id": payload["user_id"]})
    if not user:
        raise HTTPException(401, "Account not found")
    return user


def _send(to_email, subject, html):
    try:
        from sendgrid_email_service import sendgrid_email_service
        return sendgrid_email_service.send_email(to_email=to_email, subject=subject, body=html,
                                                 from_agent="sales", html=True)
    except Exception as e:
        logger.warning(f"password email failed for {to_email}: {e}")


def _wrap(title, body):
    return (f'<div style="font-family:Arial,sans-serif;max-width:560px;margin:auto;padding:20px;">'
            f'<h2 style="color:#1e3a5f;">{title}</h2>{body}'
            f'<p style="color:#999;font-size:12px;margin-top:24px;">Aditya Retail</p></div>')


async def create_reset_token(user_id: str, hours: int = 1) -> str:
    """Also reusable for 'set your password' links in the new-account email."""
    raw = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    await db.password_resets.insert_one({
        "user_id": user_id, "token_hash": hashlib.sha256(raw.encode()).hexdigest(),
        "created_at": now, "expires_at": now + timedelta(hours=hours), "used": False})
    return raw


@router.post("/customer/change-password")
async def change_password(body: ChangePassword, user=Depends(current_customer)):
    if not user.get("password") or not verify_password(body.current_password, user["password"]):
        raise HTTPException(400, "Current password is incorrect")
    check_strength(body.new_password)
    if body.new_password == body.current_password:
        raise HTTPException(400, "New password must be different from the current one")
    now = datetime.now(timezone.utc).isoformat()
    await db.users.update_one({"id": user["id"]}, {"$set": {
        "password": hash_password(body.new_password), "password_changed_at": now,
        "must_change_password": False, "updated_at": now}})
    if user.get("email"):
        await asyncio.to_thread(_send, user["email"], "Your password was changed",
            _wrap("Password changed", "<p>Your Aditya Retail password was just changed. "
                  "If this wasn't you, reset it immediately using 'Forgot password' on the login page.</p>"))
    return {"status": "success", "message": "Password changed successfully"}


@router.post("/customer/forgot-password")
async def forgot_password(body: ForgotPassword):
    email = (body.email or "").strip().lower()
    if email:
        user = await db.users.find_one({"email": {"$regex": f"^{re.escape(email)}$", "$options": "i"}, "role": "customer"})
        if user:
            since = datetime.now(timezone.utc) - timedelta(hours=1)
            recent = await db.password_resets.count_documents({"user_id": user["id"], "created_at": {"$gt": since}})
            if recent < 3:
                raw = await create_reset_token(user["id"])
                link = f"{STORE_URL}/reset-password?token={raw}"
                html = _wrap("Reset your password",
                    f'<p>Hi {user.get("first_name") or "there"}, click the button to choose a new password. '
                    f'This link works once and expires in 1 hour.</p>'
                    f'<p><a href="{link}" style="background:#1e3a5f;color:#fff;padding:12px 22px;border-radius:6px;'
                    f'text-decoration:none;font-weight:bold;">Reset password</a></p>'
                    f'<p style="color:#777;">If you didn\'t request this, you can ignore this email.</p>')
                await asyncio.to_thread(_send, user["email"], "Reset your Aditya Retail password", html)
    return {"status": "success", "message": GENERIC_MSG}


@router.post("/customer/reset-password")
async def reset_password(body: ResetPassword):
    check_strength(body.new_password)
    th = hashlib.sha256(body.token.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    rec = await db.password_resets.find_one({"token_hash": th, "used": False, "expires_at": {"$gt": now}})
    if not rec:
        raise HTTPException(400, "This reset link is invalid or has expired. Please request a new one.")
    user = await db.users.find_one({"id": rec["user_id"]})
    if not user:
        raise HTTPException(400, "Account not found")
    await db.users.update_one({"id": user["id"]}, {"$set": {
        "password": hash_password(body.new_password), "password_changed_at": now.isoformat(),
        "must_change_password": False, "updated_at": now.isoformat()}})
    await db.password_resets.update_many({"user_id": user["id"], "used": False}, {"$set": {"used": True}})
    if user.get("email"):
        await asyncio.to_thread(_send, user["email"], "Your password was changed",
            _wrap("Password changed", "<p>Your password was reset successfully. You can now log in.</p>"))
    return {"status": "success", "message": "Password updated. You can now log in."}
