"""PDF Generation Service for Invoices and Documents"""
from datetime import datetime
from typing import Dict, Any
from store_config import get_store, COMPANY
import os

def generate_invoice_html(invoice_data: Dict[str, Any]) -> str:
    """
    Generate professional invoice HTML
    """
    store = invoice_data.get('store_details', {})
    customer = invoice_data.get('customer', {})
    items = invoice_data.get('items', [])
    
    # Determine document type
    doc_type = "SALES ORDER" if invoice_data.get('document_type') == 'sales_order' else "TAX INVOICE"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 0.5cm; }}
            body {{
                font-family: 'Arial', sans-serif;
                margin: 0;
                padding: 20px;
                color: #333;
            }}
            .invoice-container {{
                max-width: 800px;
                margin: 0 auto;
                border: 2px solid #0066cc;
            }}
            .header {{
                background: linear-gradient(135deg, #0066cc 0%, #004999 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }}
            .company-name {{
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            .company-tagline {{
                font-size: 14px;
                font-style: italic;
            }}
            .doc-type {{
                background: #ff6600;
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 2px;
            }}
            .info-section {{
                display: flex;
                padding: 20px;
                border-bottom: 2px solid #eee;
            }}
            .info-box {{
                flex: 1;
                padding: 10px;
            }}
            .info-box h3 {{
                color: #0066cc;
                font-size: 14px;
                margin: 0 0 10px 0;
                border-bottom: 2px solid #0066cc;
                padding-bottom: 5px;
            }}
            .info-box p {{
                margin: 5px 0;
                font-size: 12px;
            }}
            .invoice-details {{
                background: #f8f9fa;
                padding: 15px 20px;
                display: flex;
                justify-content: space-between;
                border-bottom: 2px solid #ddd;
            }}
            .invoice-details div {{
                font-size: 13px;
            }}
            .invoice-details strong {{
                color: #0066cc;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            thead {{
                background: #0066cc;
                color: white;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border: 1px solid #ddd;
                font-size: 12px;
            }}
            th {{
                font-weight: bold;
                text-align: center;
            }}
            td.amount {{
                text-align: right;
            }}
            tbody tr:nth-child(even) {{
                background: #f8f9fa;
            }}
            .totals-section {{
                padding: 20px;
                display: flex;
                justify-content: flex-end;
            }}
            .totals-table {{
                width: 350px;
            }}
            .totals-table tr {{
                border-bottom: 1px solid #ddd;
            }}
            .totals-table td {{
                padding: 8px 15px;
                border: none;
            }}
            .totals-table .label {{
                text-align: right;
                font-weight: 500;
            }}
            .totals-table .value {{
                text-align: right;
                font-weight: bold;
            }}
            .grand-total {{
                background: #0066cc;
                color: white;
                font-size: 16px;
            }}
            .footer {{
                padding: 20px;
                background: #f8f9fa;
                text-align: center;
                border-top: 2px solid #0066cc;
            }}
            .footer p {{
                margin: 5px 0;
                font-size: 11px;
                color: #666;
            }}
            .terms {{
                padding: 15px 20px;
                font-size: 11px;
                color: #666;
                border-top: 1px dashed #ddd;
            }}
            .terms h4 {{
                color: #0066cc;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="invoice-container">
            <!-- Header -->
            <div class="header">
                <div class="company-name">{COMPANY['name']}</div>
                <div class="company-tagline">{COMPANY['tagline']}</div>
            </div>
            
            <!-- Document Type -->
            <div class="doc-type">{doc_type}</div>
            
            <!-- Invoice Details Bar -->
            <div class="invoice-details">
                <div><strong>Invoice No:</strong> {invoice_data.get('invoice_number', 'N/A')}</div>
                <div><strong>Date:</strong> {_format_doc_date(invoice_data.get('created_at'))}</div>
                <div><strong>Payment:</strong> {invoice_data.get('payment_mode', 'Cash').upper()}</div>
            </div>
            
            <!-- Store and Customer Info -->
            <div class="info-section">
                <div class="info-box">
                    <h3>FROM (Store Details)</h3>
                    <p><strong>{store.get('name', 'N/A')}</strong></p>
                    <p>{store.get('type', '')}</p>
                    <p>{store.get('address', '')}</p>
                    <p>{store.get('city', '')} - {store.get('pincode', '')}</p>
                    <p>📞 {store.get('phone', '')}</p>
                    <p>✉️ {store.get('email', '')}</p>
                    <p>WhatsApp: {store.get('whatsapp', '')}</p>
                </div>
                <div class="info-box">
                    <h3>TO (Bill To)</h3>
                    <p><strong>{customer.get('name', 'N/A')}</strong></p>
                    <p>📞 {customer.get('phone', '')}</p>
                    <p>✉️ {customer.get('email', 'N/A')}</p>
                    <p>{customer.get('address', '')}</p>
                    <p>{customer.get('city', '')}, {customer.get('state', '')}</p>
                    <p>PIN: {customer.get('pincode', '')}</p>
                    {f'<p>GST: {customer.get("gst_number", "")}</p>' if customer.get('gst_number') else ''}
                </div>
            </div>
            
            <!-- Items Table -->
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 35%">Product / Service</th>
                        <th style="width: 12%">HSN</th>
                        <th style="width: 8%">Qty</th>
                        <th style="width: 12%">Rate</th>
                        <th style="width: 10%">Disc%</th>
                        <th style="width: 10%">Tax%</th>
                        <th style="width: 15%">Amount</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for idx, item in enumerate(items, 1):
        taxable_amount = item.get('taxable_amount', 0)
        tax_amount = item.get('tax_amount', 0)
        total = item.get('total', 0)
        
        html += f"""
                    <tr>
                        <td style="text-align: center">{idx}</td>
                        <td>{item.get('product_name', '')}</td>
                        <td style="text-align: center">{item.get('hsn_code', '')}</td>
                        <td style="text-align: center">{item.get('quantity', 0)}</td>
                        <td class="amount">₹{item.get('rate', 0):.2f}</td>
                        <td style="text-align: center">{item.get('discount', 0):.1f}%</td>
                        <td style="text-align: center">{item.get('tax_rate', 0):.1f}%</td>
                        <td class="amount">₹{total:.2f}</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            
            <!-- Totals Section -->
            <div class="totals-section">
                <table class="totals-table">
                    <tr>
                        <td class="label">Subtotal:</td>
                        <td class="value">₹{invoice_data.get('subtotal', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Discount ({invoice_data.get('discount_percentage', 0)}%):</td>
                        <td class="value">- ₹{invoice_data.get('discount_amount', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Tax (GST):</td>
                        <td class="value">+ ₹{invoice_data.get('tax_total', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Delivery Charges:</td>
                        <td class="value">+ ₹{invoice_data.get('delivery_charges', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Round Off:</td>
                        <td class="value">₹{invoice_data.get('round_off', 0):.2f}</td>
                    </tr>
                    <tr class="grand-total">
                        <td class="label">GRAND TOTAL:</td>
                        <td class="value">₹{invoice_data.get('total_amount', 0):.2f}</td>
                    </tr>
                </table>
            </div>
            
            <!-- Terms and Conditions -->
            <div class="terms">
                <h4>Terms & Conditions:</h4>
                <p>1. Goods once sold will not be taken back or exchanged.</p>
                <p>2. All disputes are subject to Bangalore jurisdiction only.</p>
                <p>3. Warranty as per manufacturer's terms.</p>
                {f'<p style="margin-top:10px"><strong>Notes:</strong> {invoice_data.get("notes", "")}</p>' if invoice_data.get('notes') else ''}
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <p><strong>{COMPANY['name']}</strong></p>
                <p>Website: {COMPANY['website']} | Email: {COMPANY['primary_email']}</p>
                <p>Thank you for your business!</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


def _format_doc_date(value):
    """Safely format a date that may be a datetime object, an ISO string, or missing."""
    if isinstance(value, datetime):
        return value.strftime('%d-%b-%Y')
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value).strftime('%d-%b-%Y')
        except ValueError:
            return value
    return datetime.now().strftime('%d-%b-%Y')


def generate_purchase_order_html(po_data: Dict[str, Any]) -> str:
    """
    Generate professional purchase order HTML
    """
    vendor = po_data.get('vendor', {})
    items = po_data.get('items', [])
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 0.5cm; }}
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 8px; color: #333; }}
            .po-container {{ max-width: 800px; margin: 0 auto; border: 2px solid #7c3aed; }}
            .header {{ background: #5b21b6; color: white; padding: 10px; text-align: center; }}
            .company-name {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }}
            .doc-type {{ background: #f59e0b; color: white; padding: 6px; text-align: center; font-size: 16px; font-weight: bold; letter-spacing: 1px; }}
            .po-details-table {{ width: 100%; border-collapse: collapse; background: #f8f9fa; border-bottom: 2px solid #ddd; margin: 0; }}
            .po-details-table td {{ padding: 6px 15px; border: none; font-size: 11px; width: 33%; }}
            .info-section-table {{ width: 100%; border-collapse: collapse; border-bottom: 2px solid #eee; margin: 0; }}
            .info-section-table td.info-box {{ vertical-align: top; width: 50%; padding: 8px 15px; border: none; }}
            .info-box h3 {{ color: #7c3aed; font-size: 14px; margin: 0 0 10px 0; border-bottom: 2px solid #7c3aed; padding-bottom: 5px; }}
            .info-box p {{ margin: 2px 0; font-size: 11px; }}
            table.items-table {{ width: 100%; border-collapse: collapse; margin: 8px 0; }}
            thead {{ background: #7c3aed; color: white; }}
            .items-table th, .items-table td {{ padding: 6px; text-align: left; border: 1px solid #ddd; font-size: 11px; }}
            th {{ text-align: center; }}
            td.amount {{ text-align: right; }}
            tbody tr:nth-child(even) {{ background: #f8f9fa; }}
            .totals-section {{ padding: 8px; }}
            .totals-table {{ width: 350px; margin-left: auto; border-collapse: collapse; }}
            .totals-table tr {{ border-bottom: 1px solid #ddd; }}
            .totals-table td {{ padding: 4px 15px; border: none; }}
            .totals-table .label {{ text-align: right; font-weight: 500; }}
            .totals-table .value {{ text-align: right; font-weight: bold; }}
            .grand-total {{ background: #7c3aed; color: white; font-size: 16px; }}
            .footer {{ padding: 8px; background: #f8f9fa; text-align: center; border-top: 2px solid #7c3aed; }}
            .terms {{ padding: 6px 15px; font-size: 10px; color: #666; border-top: 1px dashed #ddd; }}
        </style>
    </head>
    <body>
        <div class="po-container">
            <div class="header">
                <div class="company-name">{COMPANY['name']}</div>
                <div style="font-size: 14px; font-style: italic;">{COMPANY['tagline']}</div>
            </div>
            
            <div class="doc-type">PURCHASE ORDER</div>
            
            <table class="po-details-table">
                <tr>
                    <td><strong>PO No:</strong> {po_data.get('po_number', 'N/A')}</td>
                    <td><strong>Date:</strong> {_format_doc_date(po_data.get('created_at'))}</td>
                    <td><strong>Status:</strong> {po_data.get('status', 'Pending').upper()}</td>
                </tr>
            </table>
            
            <table class="info-section-table">
                <tr>
                    <td class="info-box">
                        <h3>TO (Vendor Details)</h3>
                        <p><strong>{vendor.get('name', 'N/A')}</strong></p>
                        <p>Phone: {vendor.get('phone', 'N/A')}</p>
                        <p>Email: {vendor.get('email', 'N/A')}</p>
                        <p>{vendor.get('address', '')}</p>
                        <p>{vendor.get('city', '')}, {vendor.get('state', '')}</p>
                        <p>PIN: {vendor.get('pincode', '')}</p>
                        {f'<p>GST: {vendor.get("gst_number", "")}</p>' if vendor.get('gst_number') else ''}
                    </td>
                    <td class="info-box">
                        <h3>FROM (Our Details)</h3>
                        <p><strong>{COMPANY['name']}</strong></p>
                        <p>Phone: {COMPANY['support_phone']}</p>
                        <p>Email: {COMPANY['primary_email']}</p>
                        <p>Web: {COMPANY['website']}</p>
                    </td>
                </tr>
            </table>
            
            <table class="items-table">
                <thead>
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 35%">Product / Service</th>
                        <th style="width: 12%">HSN</th>
                        <th style="width: 8%">Qty</th>
                        <th style="width: 12%">Rate</th>
                        <th style="width: 10%">Disc%</th>
                        <th style="width: 10%">Tax%</th>
                        <th style="width: 15%">Amount</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for idx, item in enumerate(items, 1):
        total = item.get('total', 0)
        html += f"""
                    <tr>
                        <td style="text-align: center">{idx}</td>
                        <td>{item.get('product_name', '')}</td>
                        <td style="text-align: center">{item.get('hsn_code', '')}</td>
                        <td style="text-align: center">{item.get('quantity', 0)}</td>
                        <td class="amount">₹{item.get('rate', 0):.2f}</td>
                        <td style="text-align: center">{item.get('discount', 0):.1f}%</td>
                        <td style="text-align: center">{item.get('tax_rate', 0):.1f}%</td>
                        <td class="amount">₹{total:.2f}</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            
            <div class="totals-section">
                <table class="totals-table">
                    <tr>
                        <td class="label">Subtotal:</td>
                        <td class="value">₹{po_data.get('subtotal', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Tax (GST):</td>
                        <td class="value">+ ₹{po_data.get('total_tax', po_data.get('tax_amount', 0)):.2f}</td>
                    </tr>
                    <tr>
                        <td class="label">Shipping Charges:</td>
                        <td class="value">+ ₹{po_data.get('shipping_charges', 0):.2f}</td>
                    </tr>
                    <tr class="grand-total">
                        <td class="label">GRAND TOTAL:</td>
                        <td class="value">₹{po_data.get('grand_total', po_data.get('total_amount', 0)):.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div class="terms">
                <h4 style="color: #7c3aed;">Terms & Conditions:</h4>
                <p>1. Please deliver the goods as per specifications mentioned above.</p>
                <p>2. Payment terms as agreed separately.</p>
                <p>3. All disputes are subject to Bangalore jurisdiction only.</p>
                {f'<p style="margin-top:10px"><strong>Notes:</strong> {po_data.get("notes", "")}</p>' if po_data.get('notes') else ''}
            </div>
            
            <div class="footer">
                <p><strong>{COMPANY['name']}</strong></p>
                <p>Website: {COMPANY['website']} | Email: {COMPANY['primary_email']}</p>
                <p style="font-size: 11px; margin-top: 10px;">This is a computer-generated document.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_grn_html(grn_data: Dict[str, Any]) -> str:
    """
    Generate professional Goods Receipt Note (GRN) HTML
    """
    items = grn_data.get('items', [])
    discrepancies = grn_data.get('discrepancies', [])

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 0.5cm; }}
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
            .grn-container {{ max-width: 800px; margin: 0 auto; border: 2px solid #16a34a; }}
            .header {{ background: linear-gradient(135deg, #16a34a 0%, #15803d 100%); color: white; padding: 20px; text-align: center; }}
            .company-name {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }}
            .doc-type {{ background: #f59e0b; color: white; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; letter-spacing: 2px; }}
            .grn-details {{ background: #f8f9fa; padding: 15px 20px; display: flex; justify-content: space-between; flex-wrap: wrap; gap: 10px; border-bottom: 2px solid #ddd; }}
            .info-section {{ padding: 20px; border-bottom: 2px solid #eee; overflow: hidden; }}
            .info-box {{ float: left; width: 48%; padding: 10px; }}
            .info-box h3 {{ color: #16a34a; font-size: 14px; margin: 0 0 10px 0; border-bottom: 2px solid #16a34a; padding-bottom: 5px; }}
            .info-box p {{ margin: 5px 0; font-size: 12px; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            thead {{ background: #16a34a; color: white; }}
            th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; font-size: 12px; }}
            th {{ text-align: center; }}
            td.amount {{ text-align: right; }}
            td.center {{ text-align: center; }}
            tbody tr:nth-child(even) {{ background: #f8f9fa; }}
            .row-mismatch {{ background: #fef3c7 !important; }}
            .totals-section {{ padding: 20px; overflow: hidden; }} .totals-section .totals-table {{ float: right; }}
            .totals-table {{ width: 350px; }}
            .totals-table tr {{ border-bottom: 1px solid #ddd; }}
            .totals-table td {{ padding: 8px 15px; border: none; }}
            .totals-table .label {{ text-align: right; font-weight: 500; }}
            .totals-table .value {{ text-align: right; font-weight: bold; }}
            .grand-total {{ background: #16a34a; color: white; font-size: 16px; }}
            .discrepancy-box {{ margin: 0 20px 20px 20px; padding: 12px 15px; background: #fef3c7; border: 1px solid #f59e0b; border-radius: 6px; font-size: 12px; }}
            .discrepancy-box h4 {{ color: #92400e; margin: 0 0 8px 0; }}
            .footer {{ padding: 20px; background: #f8f9fa; text-align: center; border-top: 2px solid #16a34a; }}
            .terms {{ padding: 15px 20px; font-size: 11px; color: #666; border-top: 1px dashed #ddd; }}
        </style>
    </head>
    <body>
        <div class="grn-container">
            <div class="header">
                <div class="company-name">{COMPANY['name']}</div>
                <div style="font-size: 14px; font-style: italic;">{COMPANY['tagline']}</div>
            </div>

            <div class="doc-type">GOODS RECEIPT NOTE</div>

            <div class="grn-details">
                <div><strong>GRN #:</strong> {grn_data.get('grn_number', 'N/A')}</div>
                <div><strong>PO #:</strong> {grn_data.get('po_number') or '-'}</div>
                <div><strong>Date:</strong> {_format_doc_date(grn_data.get('created_at'))}</div>
                <div><strong>Status:</strong> {'DISCREPANCY' if grn_data.get('has_discrepancies') else 'COMPLETE'}</div>
            </div>

            <div class="info-section">
                <div class="info-box">
                    <h3>Vendor Details</h3>
                    <p><strong>{grn_data.get('vendor_name', 'N/A')}</strong></p>
                    <p>Vendor Invoice #: {grn_data.get('vendor_invoice_number') or '-'}</p>
                    <p>Invoice Date: {grn_data.get('vendor_invoice_date') or '-'}</p>
                </div>
                <div class="info-box">
                    <h3>Received By</h3>
                    <p><strong>{grn_data.get('received_by', 'N/A')}</strong></p>
                    <p>Warehouse/Store: {grn_data.get('store_code') or grn_data.get('warehouse_id') or '-'}</p>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 35%">Product</th>
                        <th style="width: 15%">Model #</th>
                        <th style="width: 12%">Ordered Qty</th>
                        <th style="width: 12%">Received Qty</th>
                        <th style="width: 21%">Unit Price</th>
                    </tr>
                </thead>
                <tbody>
    """

    for idx, item in enumerate(items, 1):
        mismatch = item.get('ordered_quantity', 0) != item.get('received_quantity', 0)
        row_class = ' class="row-mismatch"' if mismatch else ''
        html += f"""
                    <tr{row_class}>
                        <td class="center">{idx}</td>
                        <td>{item.get('product_name', '')}</td>
                        <td class="center">{item.get('model_number', '') or '-'}</td>
                        <td class="center">{item.get('ordered_quantity', 0)}</td>
                        <td class="center">{item.get('received_quantity', 0)}</td>
                        <td class="amount">₹{item.get('unit_price', 0):.2f}</td>
                    </tr>
        """

    html += f"""
                </tbody>
            </table>
    """

    if discrepancies:
        html += """
            <div class="discrepancy-box">
                <h4>⚠ Quantity Discrepancies</h4>
        """
        for d in discrepancies:
            html += f"""
                <p>{d.get('product_name', '')}: Ordered {d.get('ordered', 0)}, Received {d.get('received', 0)} (Diff: {d.get('difference', 0):+d})</p>
            """
        html += """
            </div>
        """

    html += f"""
            <div class="totals-section">
                <table class="totals-table">
                    <tr>
                        <td class="label">Total Items:</td>
                        <td class="value">{grn_data.get('total_items', 0)}</td>
                    </tr>
                    <tr>
                        <td class="label">Total Received Qty:</td>
                        <td class="value">{grn_data.get('total_received_quantity', 0)}</td>
                    </tr>
                    <tr class="grand-total">
                        <td class="label">TOTAL VALUE:</td>
                        <td class="value">₹{grn_data.get('total_value', 0):.2f}</td>
                    </tr>
                </table>
            </div>

            <div class="terms">
                {f'<p><strong>Notes:</strong> {grn_data.get("notes", "")}</p>' if grn_data.get('notes') else ''}
            </div>

            <div class="footer">
                <p><strong>{COMPANY['name']}</strong></p>
                <p>Website: {COMPANY['website']} | Email: {COMPANY['primary_email']}</p>
                <p style="font-size: 11px; margin-top: 10px;">This is a computer-generated document.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


def generate_voucher_html(voucher_data: Dict[str, Any]) -> str:
    """
    Generate professional payment/receipt voucher HTML
    """
    voucher_type = voucher_data.get('voucher_type', 'payment')
    doc_title = "PAYMENT VOUCHER" if voucher_type == 'payment' else "RECEIPT VOUCHER"
    color = "#dc2626" if voucher_type == 'payment' else "#16a34a"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 0.5cm; }}
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
            .voucher-container {{ max-width: 700px; margin: 0 auto; border: 2px solid {color}; }}
            .header {{ background: {color}; color: white; padding: 20px; text-align: center; }}
            .company-name {{ font-size: 24px; font-weight: bold; }}
            .doc-type {{ font-size: 20px; margin-top: 10px; letter-spacing: 2px; }}
            .voucher-details {{ padding: 20px; background: #f8f9fa; border-bottom: 2px solid #ddd; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; padding: 20px; }}
            .info-item {{ padding: 10px; }}
            .info-label {{ font-size: 12px; color: #666; margin-bottom: 5px; }}
            .info-value {{ font-size: 16px; font-weight: bold; }}
            .amount-box {{ background: {color}; color: white; padding: 20px; text-align: center; margin: 20px; }}
            .amount-box .label {{ font-size: 14px; }}
            .amount-box .value {{ font-size: 32px; font-weight: bold; margin-top: 10px; }}
            .description {{ padding: 20px; border-top: 2px solid #ddd; }}
            .footer {{ padding: 20px; background: #f8f9fa; text-align: center; border-top: 2px solid {color}; }}
        </style>
    </head>
    <body>
        <div class="voucher-container">
            <div class="header">
                <div class="company-name">{COMPANY['name']}</div>
                <div class="doc-type">{doc_title}</div>
            </div>
            
            <div class="voucher-details">
                <strong>Voucher No:</strong> {voucher_data.get('voucher_number', 'N/A')} | 
                <strong>Date:</strong> {_format_doc_date(voucher_data.get('voucher_date'))}
            </div>
            
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Party Name</div>
                    <div class="info-value">{voucher_data.get('party_name', 'N/A')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Payment Mode</div>
                    <div class="info-value">{voucher_data.get('payment_mode', 'Cash').upper()}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Reference Number</div>
                    <div class="info-value">{voucher_data.get('reference_number', 'N/A') or 'N/A'}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Created By</div>
                    <div class="info-value">{voucher_data.get('created_by', 'Admin')}</div>
                </div>
            </div>
            
            <div class="amount-box">
                <div class="label">Amount {'Paid' if voucher_type == 'payment' else 'Received'}</div>
                <div class="value">₹{voucher_data.get('amount', 0):.2f}</div>
            </div>
            
            <div class="description">
                <p><strong>Description:</strong></p>
                <p style="margin-top: 10px; font-size: 14px;">{voucher_data.get('description', 'N/A')}</p>
            </div>
            
            <div class="footer">
                <p><strong>{COMPANY['name']}</strong></p>
                <p style="font-size: 12px;">Website: {COMPANY['website']}</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html




def generate_credit_debit_note_html(note_data: Dict[str, Any]) -> str:
    """Generate credit/debit note HTML - Simple version"""
    note_type = note_data.get('note_type', 'credit_note')
    is_credit = note_type == 'credit_note'
    doc_title = "CREDIT NOTE" if is_credit else "DEBIT NOTE"
    
    return f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h1>{doc_title}</h1>
        <p><strong>Note No:</strong> {note_data.get('note_number', 'N/A')}</p>
        <p><strong>Party:</strong> {note_data.get('party_name', 'N/A')}</p>
        <p><strong>Amount:</strong> ₹{note_data.get('amount', 0):.2f}</p>
        <p><strong>Reason:</strong> {note_data.get('reason', 'N/A')}</p>
    </body>
    </html>
    """

def generate_expense_receipt_html(expense_data: Dict[str, Any]) -> str:
    """Generate expense receipt HTML - Simple version"""
    return f"""
    <html>
    <body style="font-family: Arial; padding: 20px;">
        <h1>EXPENSE RECEIPT</h1>
        <p><strong>Expense No:</strong> {expense_data.get('expense_number', 'N/A')}</p>
        <p><strong>Category:</strong> {expense_data.get('category', 'N/A')}</p>
        <p><strong>Amount:</strong> ₹{expense_data.get('amount', 0):.2f}</p>
        <p><strong>Description:</strong> {expense_data.get('description', 'N/A')}</p>
    </body>
    </html>
    """

def generate_delivery_challan_html(challan_data: Dict[str, Any]) -> str:
    """
    Generate professional delivery challan HTML
    """
    store = challan_data.get('store_details', {})
    customer = challan_data.get('customer', {})
    items = challan_data.get('items', [])
    
    # Build items table rows
    items_html = ""
    for idx, item in enumerate(items, 1):
        items_html += f"""
                    <tr>
                        <td style="text-align: center">{idx}</td>
                        <td>{item.get('product_name', '')}</td>
                        <td style="text-align: center">{item.get('hsn_code', '')}</td>
                        <td style="text-align: center">{item.get('quantity', 0)}</td>
                        <td></td>
                    </tr>
        """
    
    maps_link_html = ""
    if challan_data.get('google_maps_link'):
        maps_link_html = f'<a href="{challan_data.get("google_maps_link", "")}" class="maps-link" target="_blank">📍 Open in Google Maps</a>'
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ margin: 0.5cm; }}
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; color: #333; }}
            .challan-container {{ max-width: 800px; margin: 0 auto; border: 2px solid #10b981; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 20px; text-align: center; }}
            .company-name {{ font-size: 28px; font-weight: bold; margin-bottom: 5px; }}
            .doc-type {{ background: #f59e0b; color: white; padding: 10px; text-align: center; font-size: 20px; font-weight: bold; letter-spacing: 2px; }}
            .info-section {{ padding: 20px; border-bottom: 2px solid #eee; overflow: hidden; }}
            .info-box {{ float: left; width: 48%; padding: 10px; }}
            .info-box h3 {{ color: #10b981; font-size: 14px; margin: 0 0 10px 0; border-bottom: 2px solid #10b981; padding-bottom: 5px; }}
            .info-box p {{ margin: 5px 0; font-size: 12px; }}
            .challan-details {{ background: #f8f9fa; padding: 15px 20px; display: flex; justify-content: space-between; border-bottom: 2px solid #ddd; }}
            .delivery-info {{ background: #dbeafe; padding: 15px 20px; border-left: 4px solid #3b82f6; margin: 20px; }}
            .delivery-info h3 {{ color: #1e40af; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            thead {{ background: #10b981; color: white; }}
            th, td {{ padding: 12px; text-align: left; border: 1px solid #ddd; font-size: 12px; }}
            th {{ text-align: center; }}
            tbody tr:nth-child(even) {{ background: #f8f9fa; }}
            .maps-link {{ display: inline-block; background: #3b82f6; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 10px 0; }}
            .footer {{ padding: 20px; background: #f8f9fa; text-align: center; border-top: 2px solid #10b981; }}
            .signature-box {{ display: flex; justify-content: space-between; padding: 20px; }}
            .signature {{ text-align: center; padding: 20px; border-top: 2px solid #333; }}
        </style>
    </head>
    <body>
        <div class="challan-container">
            <div class="header">
                <div class="company-name">{COMPANY['name']}</div>
                <div style="font-size: 14px; font-style: italic;">{COMPANY['tagline']}</div>
            </div>
            
            <div class="doc-type">DELIVERY CHALLAN</div>
            
            <div class="challan-details">
                <div><strong>Challan No:</strong> {challan_data.get('challan_number', 'N/A')}</div>
                <div><strong>Date:</strong> {_format_doc_date(challan_data.get('created_at'))}</div>
                <div><strong>Invoice:</strong> {challan_data.get('invoice_number', 'N/A')}</div>
            </div>
            
            <div class="info-section">
                <div class="info-box">
                    <h3>FROM (Store)</h3>
                    <p><strong>{store.get('name', 'N/A')}</strong></p>
                    <p>{store.get('type', '')}</p>
                    <p>{store.get('address', '')}</p>
                    <p>{store.get('city', '')} - {store.get('pincode', '')}</p>
                    <p>📞 {store.get('phone', '')}</p>
                </div>
                <div class="info-box">
                    <h3>TO (Delivery Address)</h3>
                    <p><strong>{customer.get('name', 'N/A')}</strong></p>
                    <p>📞 {customer.get('phone', '')}</p>
                    <p>{customer.get('address', '')}</p>
                    <p>{customer.get('city', '')}, {customer.get('state', '')}</p>
                    <p>PIN: {customer.get('pincode', '')}</p>
                </div>
            </div>
            
            <div class="delivery-info">
                <h3>🚚 Delivery Information</h3>
                <p><strong>Delivery Person:</strong> {challan_data.get('delivery_person_name', 'N/A')}</p>
                <p><strong>Contact:</strong> {challan_data.get('delivery_person_phone', 'N/A')}</p>
                <p><strong>Vehicle No:</strong> {challan_data.get('vehicle_number', 'N/A') or 'N/A'}</p>
                <p><strong>Expected Delivery:</strong> {challan_data.get('expected_delivery_date', 'N/A')}</p>
                <p><strong>Status:</strong> <span style="background: #fef3c7; padding: 5px 10px; border-radius: 5px; text-transform: uppercase;">{challan_data.get('status', 'Pending')}</span></p>
                {maps_link_html}
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%">#</th>
                        <th style="width: 45%">Product Description</th>
                        <th style="width: 15%">HSN Code</th>
                        <th style="width: 15%">Quantity</th>
                        <th style="width: 20%">Remarks</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div style="padding: 20px; border-top: 2px dashed #ddd;">
                <p><strong>Notes:</strong></p>
                <p style="font-size: 12px;">{challan_data.get('notes', 'Please check items before accepting delivery.')}</p>
            </div>
            
            <div class="signature-box">
                <div style="width: 45%;">
                    <p style="font-size: 12px; margin-bottom: 60px;"><strong>Delivered By:</strong></p>
                    <div class="signature">
                        <p style="margin: 0; font-size: 11px;">Signature & Date</p>
                    </div>
                </div>
                <div style="width: 45%;">
                    <p style="font-size: 12px; margin-bottom: 60px;"><strong>Received By (Customer):</strong></p>
                    <div class="signature">
                        <p style="margin: 0; font-size: 11px;">Signature & Date</p>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>{COMPANY['name']}</strong></p>
                <p style="font-size: 12px;">Website: {COMPANY['website']} | Email: {COMPANY['primary_email']}</p>
                <p style="font-size: 11px; margin-top: 10px; color: #666;">This is a computer-generated delivery challan.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html
    

 


def html_to_pdf_bytes(html_content: str) -> bytes:
    """Convert an HTML string (from the generate_*_html functions) into PDF bytes."""
    from xhtml2pdf import pisa
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO

    # Register a Unicode-capable font so ₹ and other special characters render
    # instead of showing as missing-glyph boxes. Both registerFont (for ReportLab)
    # AND the @font-face CSS rule (for xhtml2pdf's own font resolution) are required.
    _base_dir = os.path.dirname(os.path.abspath(__file__))
    _font_path = os.path.join(_base_dir, "assets", "fonts", "DejaVuSans.ttf")
    if "DejaVuSans" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("DejaVuSans", _font_path))

    font_css = """
    <style>
        @font-face {{
            font-family: "DejaVuSans";
            src: url("{font_path}");
        }}
        * {{ font-family: "DejaVuSans", Arial, sans-serif !important; }}
    </style>
    """.format(font_path=_font_path)
    if "<head>" in html_content:
        html_content = html_content.replace("<head>", "<head>" + font_css, 1)
    else:
        html_content = font_css + html_content

    buffer = BytesIO()
    result = pisa.CreatePDF(src=html_content, dest=buffer, raise_exception=True)
    if result.err:
        raise RuntimeError("Failed to convert HTML to PDF")
    return buffer.getvalue()
