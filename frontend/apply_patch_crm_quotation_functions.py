path = "/app/frontend/src/components/CustomerCRM.js"
with open(path, "r") as f:
    content = f.read()

old = """    } catch (error) {
      console.error('Error fetching customer data:', error);
      setLoading(false);
      setQuotationsLoading(false);
    }
  };"""

new = old + """

  const handleViewQuotation = async (quotationId) => {
    try {
      const response = await utils.fetchAPI(`/api/quotations/${quotationId}`);
      if (response.ok) {
        const data = await response.json();
        setSelectedQuotation(data.quotation);
        setShowViewModal(true);
      }
    } catch (error) {
      console.error('Failed to load quotation details:', error);
    }
  };

  const handleDownloadPDF = async (quotationId) => {
    try {
      window.open(`${BACKEND_URL}/api/quotations/${quotationId}/pdf`, '_blank');
    } catch (error) {
      console.error('Failed to download PDF:', error);
    }
  };

  const handleWhatsApp = async (quotationId) => {
    try {
      const response = await utils.fetchAPI(`/api/quotations/${quotationId}/whatsapp`);
      if (response.ok) {
        const data = await response.json();
        window.open(data.whatsapp_link, '_blank');
      }
    } catch (error) {
      console.error('Failed to generate WhatsApp link:', error);
    }
  };"""

assert content.count(old) == 1, "outer catch block not found or not unique"
content = content.replace(old, new)

with open(path, "w") as f:
    f.write(content)

print("Handler functions added successfully.")
