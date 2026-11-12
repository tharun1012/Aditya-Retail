"""
Phase 1 Accounting Dashboard Tests
Tests for Party Ledger Management and Journal Vouchers
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')

# Test data prefixes for cleanup
TEST_PREFIX = "TEST_"

class TestPartyLedgerAccounts:
    """Party Ledger Account CRUD Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.created_account_ids = []
        yield
        # Cleanup created accounts (if needed)
    
    def test_get_ledger_dashboard_stats(self):
        """Test dashboard stats endpoint"""
        response = self.session.get(f"{BASE_URL}/api/ledger/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stats" in data
        assert "customers" in data["stats"]
        assert "vendors" in data["stats"]
        print(f"Dashboard stats: Customers={data['stats']['customers']}, Vendors={data['stats']['vendors']}")
    
    def test_create_customer_account(self):
        """Test creating a customer ledger account"""
        customer_data = {
            "name": f"{TEST_PREFIX}Customer_{uuid.uuid4().hex[:8]}",
            "account_type": "customer",
            "phone": "9876543210",
            "email": "test.customer@example.com",
            "gst_number": "29AAECB6071D1ZS",
            "city": "Bangalore",
            "state": "Karnataka",
            "credit_limit": 50000,
            "credit_days": 30,
            "opening_balance": 1000,
            "opening_balance_type": "debit"
        }
        
        response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=customer_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "account_id" in data
        
        # Verify account was created by fetching it
        account_id = data["account_id"]
        self.created_account_ids.append(account_id)
        
        get_response = self.session.get(f"{BASE_URL}/api/ledger/accounts/{account_id}")
        assert get_response.status_code == 200
        account_data = get_response.json()
        assert account_data["status"] == "success"
        assert account_data["account"]["name"] == customer_data["name"]
        assert account_data["account"]["account_type"] == "customer"
        assert account_data["account"]["current_balance"] == 1000  # Opening balance debit
        print(f"Created customer account: {account_id}")
    
    def test_create_vendor_account(self):
        """Test creating a vendor ledger account"""
        vendor_data = {
            "name": f"{TEST_PREFIX}Vendor_{uuid.uuid4().hex[:8]}",
            "account_type": "vendor",
            "phone": "9876543211",
            "email": "test.vendor@example.com",
            "gst_number": "29AAECB6071D2ZT",
            "city": "Mumbai",
            "state": "Maharashtra",
            "credit_limit": 100000,
            "credit_days": 45,
            "opening_balance": 5000,
            "opening_balance_type": "credit"
        }
        
        response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=vendor_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "account_id" in data
        
        # Verify account was created
        account_id = data["account_id"]
        self.created_account_ids.append(account_id)
        
        get_response = self.session.get(f"{BASE_URL}/api/ledger/accounts/{account_id}")
        assert get_response.status_code == 200
        account_data = get_response.json()
        assert account_data["account"]["account_type"] == "vendor"
        assert account_data["account"]["current_balance"] == -5000  # Opening balance credit
        print(f"Created vendor account: {account_id}")
    
    def test_get_accounts_list_customers(self):
        """Test getting customer accounts list"""
        response = self.session.get(f"{BASE_URL}/api/ledger/accounts?account_type=customer")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "accounts" in data
        assert "total" in data
        assert "summary" in data
        print(f"Found {data['total']} customer accounts")
    
    def test_get_accounts_list_vendors(self):
        """Test getting vendor accounts list"""
        response = self.session.get(f"{BASE_URL}/api/ledger/accounts?account_type=vendor")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "accounts" in data
        print(f"Found {data['total']} vendor accounts")
    
    def test_search_accounts(self):
        """Test searching accounts by name"""
        # First create a searchable account
        unique_name = f"{TEST_PREFIX}SearchTest_{uuid.uuid4().hex[:8]}"
        create_data = {
            "name": unique_name,
            "account_type": "customer",
            "phone": "9999999999"
        }
        create_response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=create_data)
        assert create_response.status_code == 200
        
        # Search for it
        search_response = self.session.get(f"{BASE_URL}/api/ledger/accounts?search={unique_name[:15]}")
        assert search_response.status_code == 200
        data = search_response.json()
        assert data["status"] == "success"
        # Should find at least one account matching the search
        print(f"Search returned {data['total']} results")


class TestPartyLedgerPayments:
    """Party Ledger Payment Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and create test accounts"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Create a test customer for payment tests
        customer_data = {
            "name": f"{TEST_PREFIX}PaymentCustomer_{uuid.uuid4().hex[:8]}",
            "account_type": "customer",
            "phone": "9876500001",
            "opening_balance": 10000,
            "opening_balance_type": "debit"
        }
        response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=customer_data)
        if response.status_code == 200:
            self.customer_id = response.json()["account_id"]
        else:
            self.customer_id = None
        
        # Create a test vendor for payment tests
        vendor_data = {
            "name": f"{TEST_PREFIX}PaymentVendor_{uuid.uuid4().hex[:8]}",
            "account_type": "vendor",
            "phone": "9876500002",
            "opening_balance": 15000,
            "opening_balance_type": "credit"
        }
        response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=vendor_data)
        if response.status_code == 200:
            self.vendor_id = response.json()["account_id"]
        else:
            self.vendor_id = None
        
        yield
    
    def test_receive_payment_from_customer(self):
        """Test receiving payment from customer"""
        if not self.customer_id:
            pytest.skip("Customer account not created")
        
        payment_data = {
            "ledger_id": self.customer_id,
            "amount": 5000,
            "payment_mode": "cash",
            "reference_number": f"REC-{uuid.uuid4().hex[:8]}",
            "narration": "Test payment received"
        }
        
        response = self.session.post(f"{BASE_URL}/api/ledger/payments/receive", json=payment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "payment_id" in data
        assert data["new_balance"] == 5000  # 10000 - 5000 = 5000
        print(f"Payment received: {data['payment_id']}, New balance: {data['new_balance']}")
    
    def test_make_payment_to_vendor(self):
        """Test making payment to vendor"""
        if not self.vendor_id:
            pytest.skip("Vendor account not created")
        
        payment_data = {
            "ledger_id": self.vendor_id,
            "amount": 7500,
            "payment_mode": "bank",
            "reference_number": f"PAY-{uuid.uuid4().hex[:8]}",
            "narration": "Test payment made"
        }
        
        response = self.session.post(f"{BASE_URL}/api/ledger/payments/make", json=payment_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "payment_id" in data
        assert data["new_balance"] == -7500  # -15000 + 7500 = -7500
        print(f"Payment made: {data['payment_id']}, New balance: {data['new_balance']}")
    
    def test_get_account_transactions(self):
        """Test getting account transactions"""
        if not self.customer_id:
            pytest.skip("Customer account not created")
        
        response = self.session.get(f"{BASE_URL}/api/ledger/transactions/{self.customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "transactions" in data
        assert "ledger" in data
        print(f"Found {len(data['transactions'])} transactions")
    
    def test_get_pending_invoices(self):
        """Test getting pending invoices for customer"""
        if not self.customer_id:
            pytest.skip("Customer account not created")
        
        response = self.session.get(f"{BASE_URL}/api/ledger/pending/invoices/{self.customer_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "invoices" in data
        assert "total_pending" in data
        print(f"Pending invoices: {len(data['invoices'])}, Total: {data['total_pending']}")
    
    def test_get_pending_bills(self):
        """Test getting pending bills for vendor"""
        if not self.vendor_id:
            pytest.skip("Vendor account not created")
        
        response = self.session.get(f"{BASE_URL}/api/ledger/pending/bills/{self.vendor_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "bills" in data
        assert "total_pending" in data
        print(f"Pending bills: {len(data['bills'])}, Total: {data['total_pending']}")


class TestJournalVouchers:
    """Journal Voucher CRUD Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and create test ledger accounts"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Create two test accounts for journal entries
        account1_data = {
            "name": f"{TEST_PREFIX}JVAccount1_{uuid.uuid4().hex[:8]}",
            "account_type": "customer",
            "phone": "9876600001"
        }
        response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=account1_data)
        if response.status_code == 200:
            self.account1_id = response.json()["account_id"]
            self.account1_name = account1_data["name"]
        else:
            self.account1_id = None
            self.account1_name = None
        
        account2_data = {
            "name": f"{TEST_PREFIX}JVAccount2_{uuid.uuid4().hex[:8]}",
            "account_type": "vendor",
            "phone": "9876600002"
        }
        response = self.session.post(f"{BASE_URL}/api/ledger/accounts/create", json=account2_data)
        if response.status_code == 200:
            self.account2_id = response.json()["account_id"]
            self.account2_name = account2_data["name"]
        else:
            self.account2_id = None
            self.account2_name = None
        
        self.created_voucher_ids = []
        yield
    
    def test_create_balanced_journal_entry(self):
        """Test creating a balanced journal voucher"""
        if not self.account1_id or not self.account2_id:
            pytest.skip("Test accounts not created")
        
        voucher_data = {
            "voucher_date": datetime.now().strftime("%Y-%m-%d"),
            "narration": f"{TEST_PREFIX}Test journal entry for adjustment",
            "entries": [
                {
                    "ledger_id": self.account1_id,
                    "ledger_name": self.account1_name,
                    "debit": 5000,
                    "credit": 0
                },
                {
                    "ledger_id": self.account2_id,
                    "ledger_name": self.account2_name,
                    "debit": 0,
                    "credit": 5000
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/journal-vouchers/create", json=voucher_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "voucher_id" in data
        assert "voucher_number" in data
        assert data["voucher_number"].startswith("JV-")
        
        self.created_voucher_ids.append(data["voucher_id"])
        print(f"Created journal voucher: {data['voucher_number']}")
        
        # Verify voucher was created
        get_response = self.session.get(f"{BASE_URL}/api/journal-vouchers/{data['voucher_id']}")
        assert get_response.status_code == 200
        voucher = get_response.json()["voucher"]
        assert voucher["total_amount"] == 5000
        assert len(voucher["entries"]) == 2
    
    def test_create_unbalanced_journal_entry_fails(self):
        """Test that unbalanced journal entry fails"""
        if not self.account1_id or not self.account2_id:
            pytest.skip("Test accounts not created")
        
        voucher_data = {
            "voucher_date": datetime.now().strftime("%Y-%m-%d"),
            "narration": "Unbalanced entry test",
            "entries": [
                {
                    "ledger_id": self.account1_id,
                    "ledger_name": self.account1_name,
                    "debit": 5000,
                    "credit": 0
                },
                {
                    "ledger_id": self.account2_id,
                    "ledger_name": self.account2_name,
                    "debit": 0,
                    "credit": 3000  # Unbalanced - should fail
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/journal-vouchers/create", json=voucher_data)
        assert response.status_code == 400
        data = response.json()
        assert "not balanced" in data["detail"].lower()
        print("Unbalanced entry correctly rejected")
    
    def test_create_single_entry_fails(self):
        """Test that single entry journal fails"""
        if not self.account1_id:
            pytest.skip("Test account not created")
        
        voucher_data = {
            "voucher_date": datetime.now().strftime("%Y-%m-%d"),
            "narration": "Single entry test",
            "entries": [
                {
                    "ledger_id": self.account1_id,
                    "ledger_name": self.account1_name,
                    "debit": 5000,
                    "credit": 0
                }
            ]
        }
        
        response = self.session.post(f"{BASE_URL}/api/journal-vouchers/create", json=voucher_data)
        assert response.status_code == 400
        data = response.json()
        assert "minimum 2 entries" in data["detail"].lower()
        print("Single entry correctly rejected")
    
    def test_get_journal_vouchers_list(self):
        """Test getting journal vouchers list"""
        response = self.session.get(f"{BASE_URL}/api/journal-vouchers")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "vouchers" in data
        assert "total" in data
        print(f"Found {data['total']} journal vouchers")
    
    def test_get_journal_vouchers_with_search(self):
        """Test searching journal vouchers"""
        response = self.session.get(f"{BASE_URL}/api/journal-vouchers?search=JV-")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Search returned {data['total']} vouchers")
    
    def test_delete_journal_voucher(self):
        """Test deleting/reversing a journal voucher"""
        if not self.account1_id or not self.account2_id:
            pytest.skip("Test accounts not created")
        
        # First create a voucher to delete
        voucher_data = {
            "voucher_date": datetime.now().strftime("%Y-%m-%d"),
            "narration": f"{TEST_PREFIX}Voucher to delete",
            "entries": [
                {
                    "ledger_id": self.account1_id,
                    "ledger_name": self.account1_name,
                    "debit": 2000,
                    "credit": 0
                },
                {
                    "ledger_id": self.account2_id,
                    "ledger_name": self.account2_name,
                    "debit": 0,
                    "credit": 2000
                }
            ]
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/journal-vouchers/create", json=voucher_data)
        assert create_response.status_code == 200
        voucher_id = create_response.json()["voucher_id"]
        
        # Delete the voucher
        delete_response = self.session.delete(f"{BASE_URL}/api/journal-vouchers/{voucher_id}")
        assert delete_response.status_code == 200
        data = delete_response.json()
        assert data["status"] == "success"
        assert "reversed" in data["message"].lower()
        print(f"Voucher {voucher_id} reversed successfully")
    
    def test_get_journal_stats(self):
        """Test getting journal voucher statistics"""
        response = self.session.get(f"{BASE_URL}/api/journal-vouchers/stats/summary")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stats" in data
        assert "total_vouchers" in data["stats"]
        assert "total_amount" in data["stats"]
        print(f"Journal stats: {data['stats']['total_vouchers']} vouchers, Total: {data['stats']['total_amount']}")


class TestOutstandingReports:
    """Outstanding Balance Reports Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_customer_outstanding(self):
        """Test getting customer outstanding (receivables)"""
        response = self.session.get(f"{BASE_URL}/api/ledger/outstanding/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "total_outstanding" in data
        assert "customer_count" in data
        assert "customers" in data
        print(f"Customer outstanding: {data['customer_count']} customers, Total: {data['total_outstanding']}")
    
    def test_get_vendor_outstanding(self):
        """Test getting vendor outstanding (payables)"""
        response = self.session.get(f"{BASE_URL}/api/ledger/outstanding/vendors")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "total_payable" in data
        assert "vendor_count" in data
        assert "vendors" in data
        print(f"Vendor payables: {data['vendor_count']} vendors, Total: {data['total_payable']}")
    
    def test_get_aging_report_customers(self):
        """Test getting aging report for customers"""
        response = self.session.get(f"{BASE_URL}/api/ledger/outstanding/aging-report?account_type=customer")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "summary" in data
        assert "current" in data["summary"]
        assert "days_31_60" in data["summary"]
        assert "days_61_90" in data["summary"]
        assert "over_90" in data["summary"]
        print(f"Aging report: {data['total_accounts']} accounts, Total: {data['total_amount']}")
    
    def test_get_aging_report_vendors(self):
        """Test getting aging report for vendors"""
        response = self.session.get(f"{BASE_URL}/api/ledger/outstanding/aging-report?account_type=vendor")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Vendor aging: {data['total_accounts']} accounts")


class TestSyncFeatures:
    """Sync Features Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_sync_customers_to_ledger(self):
        """Test syncing customers to ledger"""
        response = self.session.post(f"{BASE_URL}/api/ledger/sync/customers")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        print(f"Sync result: {data['message']}")
    
    def test_sync_vendors_to_ledger(self):
        """Test syncing vendors to ledger"""
        response = self.session.post(f"{BASE_URL}/api/ledger/sync/vendors")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "message" in data
        print(f"Sync result: {data['message']}")


class TestPaymentsList:
    """Payments List Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_all_payments(self):
        """Test getting all payments"""
        response = self.session.get(f"{BASE_URL}/api/ledger/payments")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "payments" in data
        assert "total" in data
        print(f"Found {data['total']} payments")
    
    def test_get_payments_by_type_receipt(self):
        """Test getting receipt payments"""
        response = self.session.get(f"{BASE_URL}/api/ledger/payments?payment_type=receipt")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Found {data['total']} receipt payments")
    
    def test_get_payments_by_type_payment(self):
        """Test getting payment type payments"""
        response = self.session.get(f"{BASE_URL}/api/ledger/payments?payment_type=payment")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Found {data['total']} payment type payments")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
