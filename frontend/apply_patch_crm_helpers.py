path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

old_helper = """  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {"""

new_helper = """  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return new Date(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
    } catch {
      return dateStr;
    }
  };

  const quotationStatusBadge = (status) => {
    const s = (status || 'draft').toLowerCase();
    const styles = {
      draft: 'bg-gray-100 text-gray-700',
      sent: 'bg-blue-100 text-blue-800',
      accepted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      expired: 'bg-orange-100 text-orange-800',
      converted: 'bg-purple-100 text-purple-800',
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${styles[s] || 'bg-gray-100 text-gray-700'}`}>
        {s.charAt(0).toUpperCase() + s.slice(1)}
      </span>
    );
  };

  if (loading) {"""

assert old_helper in content, "helper block not found"
content = content.replace(old_helper, new_helper)

with open(path, "w") as f:
    f.write(content)

print("Helpers patched successfully.")
