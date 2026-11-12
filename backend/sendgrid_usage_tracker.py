"""Records every SendGrid send (who called it, recipients, result) into db.sendgrid_usage."""
import os, sys, threading
from datetime import datetime, timezone

_PATCHED = False


def _caller_chain():
    try:
        names, f = [], sys._getframe(1)
        while f and len(names) < 3:
            fn = f.f_code.co_filename
            if fn.startswith("/app/backend") and not fn.endswith("sendgrid_usage_tracker.py"):
                names.append(f"{os.path.basename(fn)}:{f.f_code.co_name}")
            f = f.f_back
        return " < ".join(names) or "unknown"
    except Exception:
        return "unknown"


def _log(doc):
    try:
        from dotenv import load_dotenv
        from pymongo import MongoClient
        load_dotenv("/app/backend/.env")
        c = MongoClient(os.environ["MONGO_URL"], serverSelectionTimeoutMS=3000)
        c[os.environ.get("DB_NAME", "startup_template")].sendgrid_usage.insert_one(doc)
        c.close()
    except Exception as e:
        print(f"usage tracker log failed: {e}")


def install():
    global _PATCHED
    if _PATCHED:
        return
    import sendgrid.sendgrid as sg
    orig = sg.SendGridAPIClient.send

    def send(self, message):
        try:
            caller = _caller_chain()
        except Exception:
            caller = "unknown"
        info = {"subject": "", "recipients": 1}
        try:
            d = message.get()
            info["subject"] = (d.get("subject") or "")[:90]
            info["recipients"] = sum(len(p.get("to", [])) + len(p.get("cc", [])) + len(p.get("bcc", [])) for p in d.get("personalizations", [])) or 1
        except Exception:
            pass
        status = None
        try:
            resp = orig(self, message)
            status = resp.status_code
            return resp
        except Exception as e:
            status = f"ERR {getattr(e, 'status_code', '')} {str(e)[:60]}"
            raise
        finally:
            try:
                doc = {"at": datetime.now(timezone.utc).isoformat(), "caller": caller, "status": str(status), **info}
                threading.Thread(target=_log, args=(doc,), daemon=True).start()
            except Exception:
                pass

    sg.SendGridAPIClient.send = send
    _PATCHED = True
    print("SendGrid usage tracker installed")


install()
