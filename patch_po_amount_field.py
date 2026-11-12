#!/usr/bin/env python3
import shutil

# ---------- Backend: make edit + create endpoints also set total_amount ----------
TARGET_BE = "backend/stock_transfer_routes.py"
with open(TARGET_BE, "r") as f:
    be = f.read()
shutil.copy(TARGET_BE, TARGET_BE + ".bak2")

old_1 = '''            update_data["estimated_value"] = sum(
                (i.get("quantity", 0) or 0) * (i.get("cost_price", 0) or 0) for i in new_items
            )'''
new_1 = '''            new_total = sum(
                (i.get("quantity", 0) or 0) * (i.get("cost_price", 0) or 0) for i in new_items
            )
            update_data["estimated_value"] = new_total
            update_data["total_amount"] = new_total'''
assert old_1 in be, "BACKEND EDIT 1 anchor not found"
be = be.replace(old_1, new_1, 1)

old_2 = '''            "estimated_value": total_estimated_value,
            "urgency": request.urgency,'''
new_2 = '''            "estimated_value": total_estimated_value,
            "total_amount": total_estimated_value,
            "urgency": request.urgency,'''
assert old_2 in be, "BACKEND EDIT 2 anchor not found"
be = be.replace(old_2, new_2, 1)

with open(TARGET_BE, "w") as f:
    f.write(be)
print("Patched", TARGET_BE)

# ---------- Frontend: fallback unit_price -> cost_price in View Details modal ----------
TARGET_FE = "frontend/src/components/AdminPORequestsView.js"
with open(TARGET_FE, "r") as f:
    fe = f.read()
shutil.copy(TARGET_FE, TARGET_FE + ".bak2")

old_3 = '''                          <td className="px-4 py-3 text-sm text-right">
                            {formatCurrency ? formatCurrency(item.unit_price || 0) : `₹${(item.unit_price || 0).toLocaleString()}`}
                          </td>
                          <td className="px-4 py-3 text-sm text-right font-medium">
                            {formatCurrency ? formatCurrency((item.quantity || 0) * (item.unit_price || 0)) : `₹${((item.quantity || 0) * (item.unit_price || 0)).toLocaleString()}`}
                          </td>'''
new_3 = '''                          <td className="px-4 py-3 text-sm text-right">
                            {formatCurrency ? formatCurrency(item.unit_price || item.cost_price || 0) : `₹${(item.unit_price || item.cost_price || 0).toLocaleString()}`}
                          </td>
                          <td className="px-4 py-3 text-sm text-right font-medium">
                            {formatCurrency ? formatCurrency((item.quantity || 0) * (item.unit_price || item.cost_price || 0)) : `₹${((item.quantity || 0) * (item.unit_price || item.cost_price || 0)).toLocaleString()}`}
                          </td>'''
assert old_3 in fe, "FRONTEND EDIT anchor not found"
fe = fe.replace(old_3, new_3, 1)

with open(TARGET_FE, "w") as f:
    f.write(fe)
print("Patched", TARGET_FE)
