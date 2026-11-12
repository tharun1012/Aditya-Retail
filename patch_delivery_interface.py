import re
import shutil
import sys

FILE = "frontend/src/components/DeliveryPersonInterface.js"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

shutil.copy(FILE, FILE + ".bak")
print(f"Backup saved to {FILE}.bak")

old_fetch = '''  const fetchAssignedDeliveries = async (deliveryPersonId) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/delivery-challans/delivery-person/assigned?delivery_person_id=${deliveryPersonId}`
      );
      const data = await response.json();
      
      if (response.ok) {
        setChallans(data.challans || []);
      }
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    } finally {
      setLoading(false);
    }
  };'''

new_fetch = '''  const fetchAssignedDeliveries = async (deliveryPersonId) => {
    try {
      const challanRes = await fetch(
        `${BACKEND_URL}/api/delivery-challans/delivery-person/assigned?delivery_person_id=${deliveryPersonId}`
      );
      const challanData = await challanRes.json();
      const challanList = (challanRes.ok ? (challanData.challans || []) : []).map(c => ({
        ...c,
        source: 'challan'
      }));

      const invoiceRes = await fetch(
        `${BACKEND_URL}/api/invoices/out-for-delivery?delivery_person_id=${deliveryPersonId}`
      );
      const invoiceData = await invoiceRes.json();
      const invoiceList = (invoiceRes.ok ? (invoiceData.invoices || []) : []).map(inv => ({
        id: inv.id,
        challan_number: inv.invoice_number,
        invoice_number: inv.invoice_number,
        total_amount: inv.total_amount || 0,
        items: inv.items || [],
        customer: {
          name: inv.customer?.name || inv.customer_name || 'Customer',
          phone: inv.customer?.phone || inv.customer_phone || '',
          address: inv.customer?.address || inv.customer_address || '',
          city: inv.customer?.city || '',
          pincode: inv.customer?.pincode || ''
        },
        is_cod: (inv.payment_status !== 'paid'),
        is_pod: false,
        payment_collected: inv.payment_status === 'paid',
        delivery_photos: [],
        delivered_at: inv.delivered_at || null,
        payment_details: null,
        google_maps_link: null,
        source: 'invoice'
      }));

      setChallans([...challanList, ...invoiceList]);
    } catch (error) {
      console.error('Error fetching deliveries:', error);
    } finally {
      setLoading(false);
    }
  };'''

if old_fetch not in content:
    print("!!! Could not find fetchAssignedDeliveries block. Aborting.")
    sys.exit(1)
content = content.replace(old_fetch, new_fetch)
print("Patched fetchAssignedDeliveries().")

old_mark = '''  const handleMarkDelivered = async (challanId) => {
    try {
      const response = await fetch(
        `${BACKEND_URL}/api/delivery-challans/${challanId}/status`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            status: 'delivered',
            delivered_by: deliveryUser.full_name
          })
        }
      );

      const data = await response.json();

      if (response.ok) {
        alert('Delivery marked as completed!');
        fetchAssignedDeliveries(deliveryUser.id);
      } else {
        alert(data.detail || 'Failed to update delivery status');
      }
    } catch (error) {
      console.error('Error updating delivery status:', error);'''

new_mark = '''  const handleMarkDelivered = async (item) => {
    try {
      const isInvoice = item.source === 'invoice';
      const url = isInvoice
        ? `${BACKEND_URL}/api/invoices/mark-delivered`
        : `${BACKEND_URL}/api/delivery-challans/${item.id}/status`;

      const body = isInvoice
        ? JSON.stringify({
            invoice_id: item.id,
            delivered_by: deliveryUser.id,
            payment_collected: item.payment_collected || false
          })
        : JSON.stringify({
            status: 'delivered',
            delivered_by: deliveryUser.full_name
          });

      const response = await fetch(url, {
        method: isInvoice ? 'POST' : 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body
      });

      const data = await response.json();

      if (response.ok) {
        alert('Delivery marked as completed!');
        fetchAssignedDeliveries(deliveryUser.id);
      } else {
        alert(data.detail || 'Failed to update delivery status');
      }
    } catch (error) {
      console.error('Error updating delivery status:', error);'''

if old_mark not in content:
    print("!!! Could not find handleMarkDelivered block. Aborting.")
    sys.exit(1)
content = content.replace(old_mark, new_mark)
print("Patched handleMarkDelivered().")

old_call = "onClick={() => handleMarkDelivered(challan.id)}"
new_call = "onClick={() => handleMarkDelivered(challan)}"
count = content.count(old_call)
if count == 0:
    print("!!! Could not find call site. Aborting.")
    sys.exit(1)
content = content.replace(old_call, new_call)
print(f"Patched {count} call site(s).")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("Done. Review with: git diff -- " + FILE)
