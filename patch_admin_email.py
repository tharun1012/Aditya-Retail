import shutil, py_compile, os
p = "/app/backend/orders_routes.py"
s = open(p).read()
if "admin delivered email" in s:
    raise SystemExit("already patched")
a = '''            except Exception as lifecycle_error:
                print(f"Lifecycle hook error (non-blocking): {lifecycle_error}")
'''
print("anchor count:", s.count(a))
if s.count(a) != 1:
    raise SystemExit("ABORT: anchor not unique, nothing written")
add = '''
            # admin delivered email (once only, shares the flag with the Shiprocket path)
            try:
                _notified = order.get("shipping_notifications") or {}
                _email = (order.get("customer_details") or {}).get("email")
                if _email and not _notified.get("delivered"):
                    from sendgrid_email_service import sendgrid_email_service
                    from shiprocket_tracking_service import _stage_email
                    _subj, _body = _stage_email("delivered", order, order.get("sr_awb_code"), order.get("sr_courier"))
                    _res = sendgrid_email_service.send_email(
                        to_email=_email, subject=_subj, body=_body, from_agent="delivery", html=True)
                    if _res and _res.get("status") in ("sent", "success"):
                        await db.orders.update_one(
                            {"id": order_id},
                            {"$set": {"shipping_notifications.delivered": datetime.now().isoformat()}})
            except Exception as _email_err:
                print(f"Delivered email error (non-blocking): {_email_err}")
'''
new = s.replace(a, a + add, 1)
open("/tmp/or_test.py", "w").write(new)
py_compile.compile("/tmp/or_test.py", doraise=True)
os.makedirs("/app/_backup/adminemail", exist_ok=True)
shutil.copy(p, "/app/_backup/adminemail/orders_routes.py")
open(p, "w").write(new)
print("written OK")
