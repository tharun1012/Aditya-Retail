import os
import jwt
from fastapi import Header, Query, HTTPException
from auth_routes import SECRET_KEY, ALGORITHM, db

# Stage A = "false" (log only). Stage C = set CUSTOMER_AUTH_ENFORCE=true in backend/.env
ENFORCE = os.environ.get("CUSTOMER_AUTH_ENFORCE", "false").lower() == "true"


async def _ids_from_token(payload: dict) -> set:
    ids = set()
    for k in ("sub", "user_id", "id", "uid"):
        v = payload.get(k)
        if v:
            ids.add(str(v))
    email = payload.get("email") or payload.get("sub")
    if email and "@" in str(email):
        for e in {str(email), str(email).lower()}:
            u = await db.users.find_one({"email": e}, {"_id": 0, "id": 1, "user_id": 1})
            if u:
                for k in ("id", "user_id"):
                    if u.get(k):
                        ids.add(str(u[k]))
                break
    return ids


async def verify_self(user_id: str = Query(None), authorization: str = Header(None)):
    problem = None
    if not authorization or not authorization.lower().startswith("bearer "):
        problem = "no token"
    else:
        try:
            payload = jwt.decode(authorization.split(" ", 1)[1], SECRET_KEY, algorithms=[ALGORITHM])
            ids = await _ids_from_token(payload)
            if str(user_id) not in ids:
                problem = f"mismatch (token ids={sorted(ids)})"
        except Exception as e:
            problem = f"bad token: {type(e).__name__}"
    if problem:
        print(f"AUTHGUARD {problem} user_id={user_id}", flush=True)
        if ENFORCE:
            raise HTTPException(status_code=403, detail="Not allowed")
