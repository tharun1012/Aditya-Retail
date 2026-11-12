import shutil, py_compile, os
p = "/app/backend/customer_dashboard_routes.py"
s = open(p).read()
if "def get_recommendations" in s:
    raise SystemExit("already patched")
a = '@router.post("/addresses")'
print("anchor count:", s.count(a))
if s.count(a) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
route = '''@router.get("/recommendations")
async def get_recommendations(user_id: str, database = Depends(get_db), _auth = Depends(verify_self)):
    """Products from our catalog that go with what the customer owns"""
    try:
        from customer_recommendations import build_recommendations
        groups = await build_recommendations(database, user_id)
        return {"status": "success", "groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''
new = s.replace(a, route + a, 1)
open("/tmp/cdr_test.py", "w").write(new)
py_compile.compile("/tmp/cdr_test.py", doraise=True)
os.makedirs("/app/_backup/reco", exist_ok=True)
shutil.copy(p, "/app/_backup/reco/customer_dashboard_routes.py")
open(p, "w").write(new)
print("written OK")
