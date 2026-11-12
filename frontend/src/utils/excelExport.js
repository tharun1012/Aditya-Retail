import * as XLSX from 'xlsx';

/**
 * Export data to Excel file
 * @param {Array} data - Array of objects to export
 * @param {String} filename - Name of the file (without extension)
 * @param {String} sheetName - Name of the worksheet
 */
export const exportToExcel = (data, filename = 'export', sheetName = 'Sheet1') => {
  try {
    // Create a new workbook
    const wb = XLSX.utils.book_new();
    
    // Convert data to worksheet
    const ws = XLSX.utils.json_to_sheet(data);
    
    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, sheetName);
    
    // Generate filename with date
    const date = new Date().toISOString().split('T')[0];
    const fullFilename = `${filename}_${date}.xlsx`;
    
    // Write file
    XLSX.writeFile(wb, fullFilename);
    
    return { success: true, filename: fullFilename };
  } catch (error) {
    console.error('Export to Excel failed:', error);
    return { success: false, error: error.message };
  }
};

/**
 * Export invoices to Excel
 */
export const exportInvoicesToExcel = (invoices) => {
  const data = invoices.map(invoice => ({
    'Invoice Number': invoice.invoice_number,
    'Date': new Date(invoice.created_at).toLocaleDateString('en-IN'),
    'Customer Name': invoice.customer?.name || 'N/A',
    'Customer Phone': invoice.customer?.phone || 'N/A',
    'Document Type': invoice.document_type === 'sales_order' ? 'Sales Order' : 'Invoice',
    'Payment Mode': invoice.payment_mode?.toUpperCase() || 'N/A',
    'Subtotal': `₹${invoice.subtotal?.toLocaleString()}`,
    'Discount': `₹${invoice.discount_amount?.toLocaleString()}`,
    'Tax': `₹${invoice.tax_total?.toLocaleString()}`,
    'Total Amount': `₹${invoice.total_amount?.toLocaleString()}`,
    'Payment Status': invoice.payment_status || 'N/A',
    'Status': invoice.status || 'N/A',
    'Store': invoice.store_code || 'N/A'
  }));
  
  return exportToExcel(data, 'invoices', 'Invoices');
};

/**
 * Export purchases to Excel
 */
export const exportPurchasesToExcel = (purchases) => {
  const data = purchases.map(purchase => ({
    'PO Number': purchase.po_number,
    'Date': new Date(purchase.po_date).toLocaleDateString('en-IN'),
    'Vendor Name': purchase.vendor_name,
    'Vendor Phone': purchase.vendor_phone || 'N/A',
    'Total Items': purchase.items?.length || 0,
    'Subtotal': `₹${purchase.subtotal?.toLocaleString()}`,
    'Tax': `₹${purchase.tax_total?.toLocaleString()}`,
    'Total Amount': `₹${purchase.total_amount?.toLocaleString()}`,
    'Status': purchase.status,
    'Payment Terms': purchase.payment_terms || 'N/A',
    'Expected Delivery': purchase.expected_delivery_date || 'N/A'
  }));
  
  return exportToExcel(data, 'purchase_orders', 'Purchase Orders');
};

/**
 * Export expenses to Excel
 */
export const exportExpensesToExcel = (expenses) => {
  const data = expenses.map(expense => ({
    'Expense ID': expense.expense_number || expense.id,
    'Date': new Date(expense.expense_date).toLocaleDateString('en-IN'),
    'Category': expense.category,
    'Description': expense.description,
    'Vendor': expense.vendor_name || 'N/A',
    'Amount': `₹${expense.amount?.toLocaleString()}`,
    'Payment Mode': expense.payment_mode?.toUpperCase() || 'N/A',
    'Payment Status': expense.payment_status || 'N/A',
    'Approved By': expense.approved_by || 'Pending'
  }));
  
  return exportToExcel(data, 'expenses', 'Expenses');
};

/**
 * Export vouchers to Excel
 */
export const exportVouchersToExcel = (vouchers) => {
  const data = vouchers.map(voucher => ({
    'Voucher Number': voucher.voucher_number,
    'Date': new Date(voucher.voucher_date).toLocaleDateString('en-IN'),
    'Type': voucher.voucher_type,
    'Party Name': voucher.party_name,
    'Amount': `₹${voucher.amount?.toLocaleString()}`,
    'Payment Mode': voucher.payment_mode?.toUpperCase() || 'N/A',
    'Reference': voucher.reference_number || 'N/A',
    'Status': voucher.status || 'N/A',
    'Notes': voucher.notes || ''
  }));
  
  return exportToExcel(data, 'vouchers', 'Vouchers');
};

/**
 * Export inventory to Excel
 */
export const exportInventoryToExcel = (products) => {
  const data = products.map(product => ({
    'Product Name': product.name,
    'Brand': product.brand || 'N/A',
    'Category': product.category || 'N/A',
    'HSN Code': product.hsn_code || 'N/A',
    'Current Stock': product.current_stock || 0,
    'Reorder Level': product.reorder_level || 0,
    'Price': `₹${product.price?.toLocaleString()}`,
    'Stock Value': `₹${((product.current_stock || 0) * (product.price || 0)).toLocaleString()}`,
    'Status': (product.current_stock || 0) <= 0 ? 'OUT OF STOCK' : 
              (product.current_stock || 0) <= (product.reorder_level || 5) ? 'LOW STOCK' : 'IN STOCK'
  }));
  
  return exportToExcel(data, 'inventory', 'Inventory');
};

/**
 * Export sales report to Excel
 */
export const exportSalesReportToExcel = (report) => {
  const data = report.map(item => ({
    'Date': item.date,
    'Total Sales': `₹${item.total_sales?.toLocaleString()}`,
    'Total Orders': item.order_count,
    'Cash Sales': `₹${item.cash_sales?.toLocaleString()}`,
    'Card Sales': `₹${item.card_sales?.toLocaleString()}`,
    'UPI Sales': `₹${item.upi_sales?.toLocaleString()}`,
    'Average Order Value': `₹${item.avg_order_value?.toLocaleString()}`
  }));
  
  return exportToExcel(data, 'sales_report', 'Sales Report');
};

/**
 * Export generic data with custom mapping
 */
export const exportGenericData = (data, columnMapping, filename, sheetName) => {
  const mappedData = data.map(item => {
    const row = {};
    Object.keys(columnMapping).forEach(key => {
      const value = columnMapping[key](item);
      row[key] = value;
    });
    return row;
  });
  
  return exportToExcel(mappedData, filename, sheetName);
};
