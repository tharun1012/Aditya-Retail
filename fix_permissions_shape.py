FILE = "frontend/src/components/AccountingDashboard.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

old = """  // Check if user has access to a module.
  // Order: (1) 'all' permission, (2) a specifically assigned permission
  // for THIS module, (3) fallback to role-based access.
  const hasAccess = (requiredRoles, moduleId) => {
    if (!userRole) return false;
    if (userPermissions.includes('all')) return true;
    const permissionKey = MODULE_PERMISSION_MAP[moduleId];
    if (permissionKey && userPermissions.includes(permissionKey)) return true;
    return requiredRoles.includes(userRole);
  };"""

new = """  // Check if user has access to a module.
  // Order: (1) 'all' permission, (2) a specifically assigned permission
  // for THIS module, (3) fallback to role-based access.
  // userPermissions may be either:
  //   - a legacy array of strings: ['orders', 'vouchers_notes', ...]
  //   - a newer dict: { orders: ['view'], vouchers_notes: ['view'], ... }
  const hasAccess = (requiredRoles, moduleId) => {
    if (!userRole) return false;

    const perms = userPermissions;
    const permissionKey = MODULE_PERMISSION_MAP[moduleId];

    if (Array.isArray(perms)) {
      if (perms.includes('all')) return true;
      if (permissionKey && perms.includes(permissionKey)) return true;
    } else if (perms && typeof perms === 'object') {
      if (Array.isArray(perms.all)) return true;
      if (permissionKey) {
        const modulePerms = perms[permissionKey];
        if (Array.isArray(modulePerms) && modulePerms.includes('view')) return true;
      }
    }

    return requiredRoles.includes(userRole);
  };"""

if old not in content:
    print("!!! Could not find hasAccess block to replace. Aborting.")
    raise SystemExit(1)
content = content.replace(old, new)

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched hasAccess() to safely handle both array and object permission shapes.")
