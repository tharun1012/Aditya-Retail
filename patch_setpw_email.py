import os, re, shutil
B, BK = "/app/backend", "/app/_backup/setpw"
os.makedirs(BK, exist_ok=True)

# ---- 1) email_notification_service.py ----
p = f"{B}/email_notification_service.py"
src = open(p).read()
if "set_password_link" in src:
    print("email service: already patched")
else:
    shutil.copy(p, f"{BK}/email_notification_service.py")
    start = src.find("async def send_customer_account_created(")
    if start < 0: raise SystemExit("ABORT: function not found")
    head_end = src.find('"""Send welcome email when a customer account is auto-created', start)
    sig_old = "        store_name: str\n    ) -> Dict[str, Any]:"
    sig_pos = src.find(sig_old, start)
    if sig_pos < 0 or sig_pos > head_end:
        raise SystemExit("ABORT: signature anchor not found")
    src = src[:sig_pos] + "        store_name: str,\n        set_password_link: Optional[str] = None\n    ) -> Dict[str, Any]:" + src[sig_pos+len(sig_old):]

    # replace the Temporary Password row inside this function only
    fn_end = src.find("    async def ", start + 10)
    fn_end = fn_end if fn_end > 0 else len(src)
    body = src[start:fn_end]
    m = re.search(r'^[ \t]*<tr><td[^\n]*Temporary Password:</td>[^\n]*</tr>[ \t]*\n', body, re.M)
    if not m: raise SystemExit("ABORT: Temporary Password row not found")
    body = body[:m.start()] + "                        {pw_row}\n" + body[m.end():]

    doc_end = body.find('"""', body.find('"""') + 3) + 3
    pw_block = '''
        if set_password_link:
            pw_row = (
                '<tr><td style="padding: 8px 0; color: #666;">Password:</td><td>'
                f'<a href="{set_password_link}" style="background:#1a1a2e;color:#fff;padding:10px 20px;'
                'border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;">Set your password</a>'
                '<div style="color:#999;font-size:12px;margin-top:6px;">Link works once and expires in 72 hours.</div></td></tr>'
            )
        else:
            pw_row = (
                '<tr><td style="padding: 8px 0; color: #666;">Temporary Password:</td>'
                f'<td style="font-weight: bold; color: #d32f2f; font-family: monospace; font-size: 16px;">{temp_password}</td></tr>'
            )
'''
    body = body[:doc_end] + pw_block + body[doc_end:]
    src = src[:start] + body + src[fn_end:]
    open(p, "w").write(src)
    print("email service: patched")

# ---- 2) offline_invoice_routes.py: create token, pass link ----
p = f"{B}/offline_invoice_routes.py"
src = open(p).read()
if "set_link" in src:
    print("offline_invoice_routes: already patched")
else:
    a = "    # Send welcome email with credentials\n    try:\n"
    b = "            temp_password=plain_password,\n"
    print("anchors:", src.count(a), src.count(b))
    if src.count(a) != 1 or src.count(b) != 1:
        raise SystemExit("ABORT: anchors not unique, nothing written")
    shutil.copy(p, f"{BK}/offline_invoice_routes.py")
    gen = '''    # Set-password link (72h, single use) instead of emailing a plain-text password
    set_link = None
    try:
        from customer_password_routes import create_reset_token, STORE_URL as _STORE_URL
        _raw = await create_reset_token(user_id, hours=72)
        set_link = f"{_STORE_URL}/reset-password?token={_raw}"
    except Exception as _tok_err:
        print(f"Warning: could not create set-password link: {_tok_err}")

'''
    src = src.replace(a, gen + a)
    src = src.replace(b, b + "            set_password_link=set_link,\n")
    open(p, "w").write(src)
    print("offline_invoice_routes: patched")
