import re, shutil, os
p = "/app/frontend/src/components/CustomerDashboard.js"
s = open(p).read()
if "handleSaveAddress" in s:
    raise SystemExit("already patched")

state_a = "  const [addressForm, setAddressForm] = useState(emptyAddress);"
fn_a    = "  const handleAddAddress = async () => {"
save_a  = "onClick={handleAddAddress}"
edit_re = re.compile(r'<button className="p-2 text-gray-400 hover:text-blue-600">(\s*)<Edit2 className="w-4 h-4" />')
del_re  = re.compile(r'<button className="p-2 text-gray-400 hover:text-red-600">(\s*)<Trash2 className="w-4 h-4" />')
title_a = '<h3 className="text-xl font-bold text-gray-900">Add Address</h3>'

counts = {
  "state": s.count(state_a), "fn": s.count(fn_a), "save": s.count(save_a),
  "edit_btn": len(edit_re.findall(s)), "del_btn": len(del_re.findall(s)),
}
print("anchors:", counts)
if any(v != 1 for v in counts.values()):
    raise SystemExit("ABORT: anchors not unique, nothing written")

state_new = state_a + """
  const [editingAddressId, setEditingAddressId] = useState(null);
  useEffect(() => {
    if (!showAddAddress) { setEditingAddressId(null); setAddressForm(emptyAddress); }
    // eslint-disable-next-line
  }, [showAddAddress]);"""

fns = """  const startEditAddress = (addr) => {
    if (!addr.id) { alert('This address cannot be edited.'); return; }
    setEditingAddressId(addr.id);
    setAddressForm({
      label: addr.label || 'Home',
      address: addr.address || '',
      city: addr.city || '',
      state: addr.state || 'Karnataka',
      pincode: String(addr.pincode || ''),
      phone: String(addr.phone || ''),
      is_default: !!addr.is_default
    });
    setShowAddAddress(true);
  };

  const deleteAddress = async (addr) => {
    if (!addr.id) { alert('This address cannot be deleted.'); return; }
    if (!window.confirm('Delete this address?')) return;
    try {
      const response = await authFetch(`${BACKEND_URL}/api/customer/addresses/${addr.id}?user_id=${user.id}`, { method: 'DELETE' });
      const data = await response.json().catch(() => ({}));
      if (response.ok && data.status === 'success') {
        fetchProfile(user.id);
      } else {
        alert(data.detail || 'Failed to delete address');
      }
    } catch (error) {
      console.error('Error deleting address:', error);
      alert('Failed to delete address. Please try again.');
    }
  };

  const handleSaveAddress = async () => {
    if (!editingAddressId) { return handleAddAddress(); }
    try {
      const response = await authFetch(`${BACKEND_URL}/api/customer/addresses/${editingAddressId}?user_id=${user.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(addressForm)
      });
      const data = await response.json().catch(() => ({}));
      if (response.ok && data.status === 'success') {
        setShowAddAddress(false);
        fetchProfile(user.id);
      } else {
        alert(data.detail || 'Failed to update address');
      }
    } catch (error) {
      console.error('Error updating address:', error);
      alert('Failed to update address. Please try again.');
    }
  };

"""

s = s.replace(state_a, state_new, 1)
s = s.replace(fn_a, fns + fn_a, 1)
s = s.replace(save_a, "onClick={handleSaveAddress}", 1)
s = edit_re.sub(lambda m: '<button onClick={() => startEditAddress(addr)} className="p-2 text-gray-400 hover:text-blue-600">' + m.group(1) + '<Edit2 className="w-4 h-4" />', s, count=1)
s = del_re.sub(lambda m: '<button onClick={() => deleteAddress(addr)} className="p-2 text-gray-400 hover:text-red-600">' + m.group(1) + '<Trash2 className="w-4 h-4" />', s, count=1)
if s.count(title_a) == 1:
    s = s.replace(title_a, '<h3 className="text-xl font-bold text-gray-900">{editingAddressId ? "Edit Address" : "Add Address"}</h3>', 1)
else:
    print("note: modal title not changed (anchor count", s.count(title_a), ")")

os.makedirs("/app/_backup/addrfe", exist_ok=True)
shutil.copy(p, "/app/_backup/addrfe/CustomerDashboard.js")
open(p, "w").write(s)
print("written OK")
