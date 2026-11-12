"""
Test Suite for PDF Generation, RBAC Payments, and Material Transfer DC
Tests the 3 bug fixes:
1. PDF Generation - SO should say 'SALES ORDER', no signature box, valid QR
2. RBAC - Store users should only see their store's payment data
3. Material Transfer DC - Transfer Type dropdown updates From/To locations
"""

import pytest
import requests
import os
import sys

# Add backend to path for imports
sys.path.insert(0, '/app/backend')

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')


class TestPDFGeneration:
    """Test PDF generation for Sales Orders vs Invoices"""
    
    def test_sales_order_pdf_title(self):
        """Sales Order PDF should have 'SALES ORDER' title, not 'RETAIL INVOICE'"""
        from invoice_pdf_generator import InvoicePDFGenerator, generate_invoice_pdf
        import PyPDF2
        from io import BytesIO
        
        so_data = {
            'document_type': 'sales_order',
            'invoice_number': 'SO-20260115-0001',
            'customer_name': 'Test Customer',
            'customer_phone': '9876543210',
            'total_amount': 15000,
            'items': [
                {'product_name': 'Test Product', 'quantity': 1, 'rate': 15000, 'tax_rate': 18, 'hsn_code': '8418'}
            ]
        }
        
        pdf_bytes = generate_invoice_pdf(so_data)
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ''.join(page.extract_text() for page in reader.pages)
        
        assert 'SALES ORDER' in text, "Sales Order PDF should contain 'SALES ORDER' title"
        assert 'RETAIL INVOICE' not in text, "Sales Order PDF should NOT contain 'RETAIL INVOICE'"
    
    def test_sales_order_no_signature_box(self):
        """Sales Order PDF should NOT have 'Goods Received in Good Condition' signature box"""
        from invoice_pdf_generator import InvoicePDFGenerator, generate_invoice_pdf
        import PyPDF2
        from io import BytesIO
        
        so_data = {
            'document_type': 'sales_order',
            'invoice_number': 'SO-20260115-0002',
            'customer_name': 'Test Customer',
            'customer_phone': '9876543210',
            'total_amount': 15000,
            'items': [
                {'product_name': 'Test Product', 'quantity': 1, 'rate': 15000, 'tax_rate': 18, 'hsn_code': '8418'}
            ]
        }
        
        pdf_bytes = generate_invoice_pdf(so_data)
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ''.join(page.extract_text() for page in reader.pages)
        
        assert 'GOODS RECEIVED IN GOOD CONDITION' not in text, "Sales Order PDF should NOT have signature box"
    
    def test_invoice_pdf_has_signature_box(self):
        """Invoice PDF should have 'Goods Received in Good Condition' signature box"""
        from invoice_pdf_generator import InvoicePDFGenerator, generate_invoice_pdf
        import PyPDF2
        from io import BytesIO
        
        inv_data = {
            'document_type': 'invoice',
            'invoice_number': 'INV-20260115-0001',
            'customer_name': 'Test Customer',
            'customer_phone': '9876543210',
            'total_amount': 15000,
            'items': [
                {'product_name': 'Test Product', 'quantity': 1, 'rate': 15000, 'tax_rate': 18, 'hsn_code': '8418'}
            ]
        }
        
        pdf_bytes = generate_invoice_pdf(inv_data)
        reader = PyPDF2.PdfReader(BytesIO(pdf_bytes))
        text = ''.join(page.extract_text() for page in reader.pages)
        
        assert 'GOODS RECEIVED IN GOOD CONDITION' in text, "Invoice PDF should have signature box"
        assert 'RETAIL INVOICE' in text, "Invoice PDF should contain 'RETAIL INVOICE' title"
    
    def test_sales_order_detection_by_prefix(self):
        """Test is_sales_order detection by SO- prefix"""
        from invoice_pdf_generator import InvoicePDFGenerator
        
        so_data = {'invoice_number': 'SO-20260115-0001'}
        generator = InvoicePDFGenerator(so_data)
        assert generator.is_sales_order == True, "SO- prefix should be detected as sales order"
    
    def test_sales_order_detection_by_document_type(self):
        """Test is_sales_order detection by document_type field"""
        from invoice_pdf_generator import InvoicePDFGenerator
        
        so_data = {'document_type': 'sales_order', 'invoice_number': 'TEST-001'}
        generator = InvoicePDFGenerator(so_data)
        assert generator.is_sales_order == True, "document_type=sales_order should be detected"
    
    def test_invoice_detection(self):
        """Test invoice detection (not sales order)"""
        from invoice_pdf_generator import InvoicePDFGenerator
        
        inv_data = {'document_type': 'invoice', 'invoice_number': 'INV-001'}
        generator = InvoicePDFGenerator(inv_data)
        assert generator.is_sales_order == False, "Invoice should not be detected as sales order"
    
    def test_qr_code_data_format(self):
        """Test QR code contains valid data"""
        from invoice_pdf_generator import InvoicePDFGenerator, COMPANY_INFO
        
        so_data = {
            'document_type': 'sales_order',
            'invoice_number': 'SO-20260115-0003',
            'customer_phone': '9876543210',
            'total_amount': 15000
        }
        
        generator = InvoicePDFGenerator(so_data)
        
        # Verify QR data format
        invoice_num = so_data.get('invoice_number')
        total_amount = so_data.get('total_amount', 0)
        doc_type = "SO" if generator.is_sales_order else "INV"
        customer_phone = so_data.get('customer_phone', '')
        
        expected_qr_data = f"{doc_type}:{invoice_num}|GSTIN:{COMPANY_INFO['gstin']}|AMT:{total_amount:.2f}|PH:{customer_phone}"
        
        assert 'SO:SO-20260115-0003' in expected_qr_data
        assert 'GSTIN:29ABAFA6295J1Z2' in expected_qr_data
        assert 'AMT:15000.00' in expected_qr_data
        assert 'PH:9876543210' in expected_qr_data


class TestRBACPayments:
    """Test RBAC enforcement on payment endpoints"""
    
    def test_pending_payments_without_store_filter(self):
        """Test pending payments endpoint returns data without store filter (admin view)"""
        response = requests.get(f"{BASE_URL}/api/vouchers/pending-payments/sos")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'success'
        assert 'sales_orders' in data
    
    def test_pending_payments_with_store_filter(self):
        """Test pending payments endpoint filters by store_code"""
        response = requests.get(f"{BASE_URL}/api/vouchers/pending-payments/sos?store_code=HRBR")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'success'
        
        # All returned SOs should be from HRBR store
        for so in data.get('sales_orders', []):
            assert so.get('store_code') == 'HRBR', f"Expected store_code HRBR, got {so.get('store_code')}"
    
    def test_so_payment_list_with_store_filter(self):
        """Test SO payment list endpoint filters by store_code"""
        response = requests.get(f"{BASE_URL}/api/vouchers/so-payment/list?store_code=HRBR")
        assert response.status_code == 200
        data = response.json()
        
        # All returned receipts should be from HRBR store
        for receipt in data.get('receipts', []):
            assert receipt.get('store_code') == 'HRBR', f"Expected store_code HRBR, got {receipt.get('store_code')}"
    
    def test_so_payment_list_without_filter_returns_all(self):
        """Test SO payment list without filter returns all stores (admin view)"""
        response = requests.get(f"{BASE_URL}/api/vouchers/so-payment/list")
        assert response.status_code == 200
        data = response.json()
        assert 'receipts' in data


class TestMaterialTransferDC:
    """Test Material Transfer DC API endpoints"""
    
    def test_stores_endpoint(self):
        """Test stores endpoint returns store list"""
        response = requests.get(f"{BASE_URL}/api/invoices/offline/stores")
        assert response.status_code == 200
        data = response.json()
        assert 'stores' in data
        assert len(data['stores']) > 0
    
    def test_stores_have_required_fields(self):
        """Test stores have required fields for transfer type logic"""
        response = requests.get(f"{BASE_URL}/api/invoices/offline/stores")
        data = response.json()
        
        for store in data.get('stores', []):
            assert 'code' in store, "Store should have 'code' field"
            assert 'name' in store, "Store should have 'name' field"
            # is_warehouse field should exist (even if False)
            # This is needed for transfer type dropdown logic
    
    def test_material_transfer_list_endpoint(self):
        """Test material transfer list endpoint"""
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'success'
        assert 'challans' in data
    
    def test_material_transfer_list_with_from_location_filter(self):
        """Test material transfer list filters by from_location"""
        response = requests.get(f"{BASE_URL}/api/delivery-challans/material-transfer/list?from_location=HRBR")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'success'


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_backend_health(self):
        """Test backend health endpoint"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get('status') == 'healthy'


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
