FILE = "frontend/src/components/AccountingDashboard.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

old_effect = """  useEffect(() => {
    // Get user role from localStorage (check both key formats for compatibility)
    const adminUserStr = localStorage.getItem('adminUser') || localStorage.getItem('admin_user') || '{}';
    const adminUser = JSON.parse(adminUserStr);
    setUserRole(adminUser.role || 'admin');
    
    // Super admins, admins, and accountants have access
    if (adminUser.role === 'admin' || adminUser.role === 'super_admin' || 
        adminUser.role === 'accountant' || adminUser.email === 'rohit.gadiya@gmail.com') {
      setUserPermissions(['all']);
    }
  }, []);"""

new_effect = """  useEffect(() => {
    // Get user role from localStorage (check both key formats for compatibility)
    const adminUserStr = localStorage.getItem('adminUser') || localStorage.getItem('admin_user') || '{}';
    const adminUser = JSON.parse(adminUserStr);
    setUserRole(adminUser.role || 'admin');

    // Super admins, admins, and accountants have full access
    if (adminUser.role === 'admin' || adminUser.role === 'super_admin' ||
        adminUser.role === 'accountant' || adminUser.email === 'rohit.gadiya@gmail.com') {
      setUserPermissions(['all']);
    } else {
      // Load this admin's individually assigned permissions (from Admin User Management)
      setUserPermissions(adminUser.permissions || []);
    }
  }, []);"""

if old_effect not in content:
    print("!!! Could not find useEffect block. Aborting.")
    raise SystemExit(1)
content = content.replace(old_effect, new_effect)
print("Patched useEffect to load adminUser.permissions.")

old_access = """  // Check if user has access to a module
  const hasAccess = (requiredRoles) => {
    if (!userRole) return false;
    if (userPermissions.includes('all')) return true;
    return requiredRoles.includes(userRole);
  };

  // Filter modules based on user access
  const accessibleModules = accountingModules.filter(module => 
    hasAccess(module.requiredRole)
  );"""

new_access = """  // Maps each module's internal id to the permission key used in
  // Admin User Management, so a specifically-assigned permission
  // grants access to ONLY that module, regardless of role.
  const MODULE_PERMISSION_MAP = {
    'ai-ca-chat': 'ai_ca_assistant',
    'daily-reports': 'daily_accounting_reports',
    'offline-invoices': 'offline_invoices',
    'sales-order-conversion': 'sales_order_conversion',
    'sales-invoices': 'sales_invoices',
    'hsn-codes': 'hsn_management',
    'purchases': 'purchase_orders',
    'po-requests': 'po_requests',
    'purchase-bills': 'purchase_bills',
    'stock-reconciliation': 'stock_reconciliation',
    'stock-transfer-approval': 'stock_transfer_approval',
    'draft-products': 'draft_products_review',
    'incomplete-products': 'incomplete_products',
    'party-ledger': 'party_ledger',
    'journal-vouchers': 'journal_vouchers',
    'bank-reconciliation': 'bank_reconciliation',
    'landed-cost': 'landed_cost_calculator',
    'payment-reminders': 'payment_reminders',
    'financial-reports': 'financial_reports',
    'expenses': 'expense_management',
    'vouchers': 'vouchers_notes',
    'reports': 'reports_exports',
    'delivery-challans': 'delivery_challans',
    'delivery-persons': 'delivery_personnel',
    'inventory': 'inventory',
    'compliance-audits': 'compliance',
    'store-documents': 'store_document_manager'
  };

  // Check if user has access to a module.
  // Order: (1) 'all' permission, (2) a specifically assigned permission
  // for THIS module, (3) fallback to role-based access.
  const hasAccess = (requiredRoles, moduleId) => {
    if (!userRole) return false;
    if (userPermissions.includes('all')) return true;
    const permissionKey = MODULE_PERMISSION_MAP[moduleId];
    if (permissionKey && userPermissions.includes(permissionKey)) return true;
    return requiredRoles.includes(userRole);
  };

  // Filter modules based on user access
  const accessibleModules = accountingModules.filter(module =>
    hasAccess(module.requiredRole, module.id)
  );"""

if old_access not in content:
    print("!!! Could not find hasAccess block. Aborting.")
    raise SystemExit(1)
content = content.replace(old_access, new_access)
print("Patched hasAccess() with permission-map lookup.")

old_call1 = ".filter(module => !hasAccess(module.requiredRole))"
new_call1 = ".filter(module => !hasAccess(module.requiredRole, module.id))"
c1 = content.count(old_call1)
if c1 == 0:
    print("!!! Could not find locked-modules filter call site. Aborting.")
    raise SystemExit(1)
content = content.replace(old_call1, new_call1)
print(f"Patched {c1} locked-modules filter call site(s).")

old_call2 = "if (selectedModule && hasAccess(selectedModule.requiredRole)) {"
new_call2 = "if (selectedModule && hasAccess(selectedModule.requiredRole, selectedModule.id)) {"
c2 = content.count(old_call2)
if c2 == 0:
    print("!!! Could not find selectedModule hasAccess call site. Aborting.")
    raise SystemExit(1)
content = content.replace(old_call2, new_call2)
print(f"Patched {c2} selectedModule call site(s).")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\nDone. Review with: git diff -- " + FILE)
