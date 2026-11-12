"""
Phase 2 Accounting Dashboard Tests
Tests for Bank Reconciliation, Landed Cost Calculator, and Payment Reminders
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')

# Test data prefixes for cleanup
TEST_PREFIX = "TEST_"


class TestBankReconciliationAccounts:
    """Bank Reconciliation - Bank Account CRUD Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.created_account_ids = []
        yield
    
    def test_create_bank_account(self):
        """Test creating a bank account for reconciliation"""
        account_data = {
            "name": f"{TEST_PREFIX}Business_Account_{uuid.uuid4().hex[:8]}",
            "account_number": f"1234{uuid.uuid4().hex[:8]}",
            "bank_name": "HDFC Bank",
            "ifsc_code": "HDFC0001234",
            "branch": "Test Branch",
            "account_type": "current",
            "opening_balance": 50000
        }
        
        response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/accounts/create", json=account_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "account_id" in data
        
        # Verify account was created by fetching it
        account_id = data["account_id"]
        self.created_account_ids.append(account_id)
        
        get_response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/accounts/{account_id}")
        assert get_response.status_code == 200
        account_data_resp = get_response.json()
        assert account_data_resp["status"] == "success"
        assert account_data_resp["account"]["bank_name"] == "HDFC Bank"
        assert account_data_resp["account"]["current_balance"] == 50000
        print(f"Created bank account: {account_id}")
    
    def test_get_bank_accounts_list(self):
        """Test getting all bank accounts"""
        response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/accounts")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "accounts" in data
        print(f"Found {len(data['accounts'])} bank accounts")
    
    def test_duplicate_bank_account_fails(self):
        """Test that duplicate bank account creation fails"""
        unique_account_number = f"DUP{uuid.uuid4().hex[:8]}"
        account_data = {
            "name": f"{TEST_PREFIX}Duplicate_Test",
            "account_number": unique_account_number,
            "bank_name": "ICICI Bank",
            "account_type": "savings",
            "opening_balance": 10000
        }
        
        # Create first account
        response1 = self.session.post(f"{BASE_URL}/api/bank-reconciliation/accounts/create", json=account_data)
        assert response1.status_code == 200
        
        # Try to create duplicate
        response2 = self.session.post(f"{BASE_URL}/api/bank-reconciliation/accounts/create", json=account_data)
        assert response2.status_code == 400
        print("Duplicate account correctly rejected")


class TestBankReconciliationTransactions:
    """Bank Reconciliation - Transaction Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and create test bank account"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Create a test bank account
        account_data = {
            "name": f"{TEST_PREFIX}TxnTest_Account_{uuid.uuid4().hex[:8]}",
            "account_number": f"TXN{uuid.uuid4().hex[:8]}",
            "bank_name": "SBI",
            "account_type": "current",
            "opening_balance": 100000
        }
        response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/accounts/create", json=account_data)
        if response.status_code == 200:
            self.bank_account_id = response.json()["account_id"]
        else:
            self.bank_account_id = None
        yield
    
    def test_create_bank_transaction_deposit(self):
        """Test creating a deposit transaction"""
        if not self.bank_account_id:
            pytest.skip("Bank account not created")
        
        txn_data = {
            "bank_account_id": self.bank_account_id,
            "transaction_date": datetime.now().strftime("%Y-%m-%d"),
            "description": f"{TEST_PREFIX}Customer payment received",
            "reference_number": f"DEP-{uuid.uuid4().hex[:8]}",
            "debit_amount": 0,
            "credit_amount": 25000,
            "transaction_type": "deposit"
        }
        
        response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/transactions/create", json=txn_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "transaction_id" in data
        assert data["new_balance"] == 125000  # 100000 + 25000
        print(f"Created deposit transaction: {data['transaction_id']}")
    
    def test_create_bank_transaction_withdrawal(self):
        """Test creating a withdrawal transaction"""
        if not self.bank_account_id:
            pytest.skip("Bank account not created")
        
        txn_data = {
            "bank_account_id": self.bank_account_id,
            "transaction_date": datetime.now().strftime("%Y-%m-%d"),
            "description": f"{TEST_PREFIX}Vendor payment",
            "reference_number": f"WDR-{uuid.uuid4().hex[:8]}",
            "debit_amount": 15000,
            "credit_amount": 0,
            "transaction_type": "withdrawal"
        }
        
        response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/transactions/create", json=txn_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Created withdrawal transaction: {data['transaction_id']}")
    
    def test_get_bank_transactions(self):
        """Test getting bank transactions for an account"""
        if not self.bank_account_id:
            pytest.skip("Bank account not created")
        
        response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/transactions/{self.bank_account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "transactions" in data
        assert "total" in data
        print(f"Found {data['total']} transactions")
    
    def test_get_unreconciled_transactions(self):
        """Test filtering unreconciled transactions"""
        if not self.bank_account_id:
            pytest.skip("Bank account not created")
        
        response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/transactions/{self.bank_account_id}?reconciled=false")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Found {data['total']} unreconciled transactions")


class TestBankReconciliationSummary:
    """Bank Reconciliation - Summary and Matching Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session and create test bank account"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        
        # Create a test bank account
        account_data = {
            "name": f"{TEST_PREFIX}Summary_Account_{uuid.uuid4().hex[:8]}",
            "account_number": f"SUM{uuid.uuid4().hex[:8]}",
            "bank_name": "Axis Bank",
            "account_type": "current",
            "opening_balance": 75000
        }
        response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/accounts/create", json=account_data)
        if response.status_code == 200:
            self.bank_account_id = response.json()["account_id"]
        else:
            self.bank_account_id = None
        yield
    
    def test_get_reconciliation_summary(self):
        """Test getting reconciliation summary for a bank account"""
        if not self.bank_account_id:
            pytest.skip("Bank account not created")
        
        response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/summary/{self.bank_account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "bank_balance" in data
        assert "ledger_balance" in data
        assert "difference" in data
        assert "unreconciled_bank" in data
        print(f"Summary - Bank: {data['bank_balance']}, Ledger: {data['ledger_balance']}, Diff: {data['difference']}")
    
    def test_get_reconciliation_suggestions(self):
        """Test getting auto-match suggestions"""
        if not self.bank_account_id:
            pytest.skip("Bank account not created")
        
        response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/suggestions/{self.bank_account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "suggestions" in data
        assert "total_unreconciled" in data
        print(f"Found {len(data['suggestions'])} suggestions, {data['total_unreconciled']} unreconciled")


class TestLandedCostTemplates:
    """Landed Cost Calculator - Template Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.created_template_ids = []
        yield
    
    def test_create_landed_cost_template(self):
        """Test creating a landed cost template"""
        template_data = {
            "name": f"{TEST_PREFIX}Import_Template_{uuid.uuid4().hex[:8]}",
            "description": "Standard import cost template",
            "components": [
                {"name": "Freight", "amount": 5000, "is_percentage": False, "allocation_method": "value"},
                {"name": "Insurance", "amount": 1, "is_percentage": True, "allocation_method": "value"},
                {"name": "Customs Duty", "amount": 10, "is_percentage": True, "allocation_method": "value"}
            ],
            "is_default": False
        }
        
        response = self.session.post(f"{BASE_URL}/api/landed-cost/templates/create", json=template_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "template_id" in data
        self.created_template_ids.append(data["template_id"])
        print(f"Created template: {data['template_id']}")
    
    def test_get_landed_cost_templates(self):
        """Test getting all landed cost templates"""
        response = self.session.get(f"{BASE_URL}/api/landed-cost/templates")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "templates" in data
        print(f"Found {len(data['templates'])} templates")
    
    def test_create_default_template(self):
        """Test creating a default template"""
        template_data = {
            "name": f"{TEST_PREFIX}Default_Template_{uuid.uuid4().hex[:8]}",
            "description": "Default cost template",
            "components": [
                {"name": "Freight", "amount": 2000, "is_percentage": False, "allocation_method": "quantity"}
            ],
            "is_default": True
        }
        
        response = self.session.post(f"{BASE_URL}/api/landed-cost/templates/create", json=template_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Created default template: {data['template_id']}")


class TestLandedCostCalculation:
    """Landed Cost Calculator - Calculation Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_landed_cost_history(self):
        """Test getting landed cost calculation history"""
        response = self.session.get(f"{BASE_URL}/api/landed-cost/history")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "records" in data
        assert "total" in data
        print(f"Found {data['total']} landed cost records")
    
    def test_get_landed_cost_stats(self):
        """Test getting landed cost statistics"""
        response = self.session.get(f"{BASE_URL}/api/landed-cost/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stats" in data
        assert "total_records" in data["stats"]
        assert "total_base_cost" in data["stats"]
        assert "total_additional" in data["stats"]
        assert "total_landed" in data["stats"]
        print(f"Stats - Records: {data['stats']['total_records']}, Base: {data['stats']['total_base_cost']}, Landed: {data['stats']['total_landed']}")
    
    def test_get_landed_cost_for_nonexistent_bill(self):
        """Test getting landed cost for non-existent bill returns 404"""
        response = self.session.get(f"{BASE_URL}/api/landed-cost/bill/nonexistent-bill-id")
        assert response.status_code == 404
        print("Non-existent bill correctly returns 404")


class TestPaymentReminderSettings:
    """Payment Reminders - Settings Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_reminder_settings(self):
        """Test getting payment reminder settings"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/settings")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "settings" in data
        settings = data["settings"]
        assert "enabled" in settings
        assert "reminder_days" in settings
        assert "min_amount" in settings
        print(f"Settings - Enabled: {settings['enabled']}, Days: {settings['reminder_days']}, Min: {settings['min_amount']}")
    
    def test_update_reminder_settings(self):
        """Test updating payment reminder settings"""
        settings_data = {
            "enabled": True,
            "reminder_days": [7, 14, 30],
            "min_amount": 500,
            "include_sms": False,
            "include_whatsapp": False,
            "escalation_enabled": True,
            "escalation_days": 45
        }
        
        response = self.session.put(f"{BASE_URL}/api/payment-reminders/settings", json=settings_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print("Settings updated successfully")
        
        # Verify settings were updated
        get_response = self.session.get(f"{BASE_URL}/api/payment-reminders/settings")
        assert get_response.status_code == 200
        updated_settings = get_response.json()["settings"]
        assert updated_settings["min_amount"] == 500
        assert updated_settings["escalation_enabled"] == True


class TestPaymentReminderPending:
    """Payment Reminders - Pending Reminders Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_pending_reminders(self):
        """Test getting pending payment reminders"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/pending")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "pending_count" in data
        assert "total_outstanding" in data
        assert "reminders" in data
        print(f"Pending - Count: {data['pending_count']}, Outstanding: {data['total_outstanding']}")
    
    def test_get_pending_reminders_with_filters(self):
        """Test getting pending reminders with filters"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/pending?min_days_overdue=7&min_amount=1000")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"Filtered pending - Count: {data['pending_count']}")
    
    def test_pending_reminders_structure(self):
        """Test that pending reminders have correct structure"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/pending")
        assert response.status_code == 200
        data = response.json()
        
        if data["reminders"]:
            reminder = data["reminders"][0]
            assert "id" in reminder
            assert "name" in reminder
            assert "outstanding_amount" in reminder
            assert "days_overdue" in reminder
            assert "suggested_reminder_type" in reminder
            print(f"First reminder: {reminder['name']} - ₹{reminder['outstanding_amount']}")


class TestPaymentReminderHistory:
    """Payment Reminders - History Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_reminder_history(self):
        """Test getting reminder history"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/history")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "history" in data
        assert "total" in data
        print(f"History - Total: {data['total']} reminders sent")
    
    def test_get_reminder_stats(self):
        """Test getting reminder statistics"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "stats" in data
        stats = data["stats"]
        assert "total_reminders_sent" in stats
        assert "unique_customers_reminded" in stats
        assert "total_outstanding_reminded" in stats
        print(f"Stats - Sent: {stats['total_reminders_sent']}, Customers: {stats['unique_customers_reminded']}")
    
    def test_get_reminder_templates(self):
        """Test getting reminder templates"""
        response = self.session.get(f"{BASE_URL}/api/payment-reminders/templates")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "templates" in data
        print(f"Found {len(data['templates'])} reminder templates")


class TestPaymentReminderSend:
    """Payment Reminders - Send Tests (MOCKED - no real emails)"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_send_reminder_empty_list(self):
        """Test sending reminder with empty list fails gracefully"""
        send_data = {
            "ledger_ids": [],
            "message_type": "email"
        }
        
        # This should still return success but with 0 queued
        response = self.session.post(f"{BASE_URL}/api/payment-reminders/send", json=send_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["queued_count"] == 0
        print("Empty list handled correctly")
    
    def test_trigger_auto_reminders(self):
        """Test triggering automatic reminders"""
        response = self.session.post(f"{BASE_URL}/api/payment-reminders/trigger-auto")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["success", "skipped"]
        print(f"Auto trigger result: {data.get('message', data.get('eligible_count', 0))}")


class TestIntegrationBankReconciliation:
    """Integration tests for Bank Reconciliation workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_full_bank_account_workflow(self):
        """Test complete bank account workflow: create -> add transactions -> get summary"""
        # 1. Create bank account
        account_data = {
            "name": f"{TEST_PREFIX}Workflow_Account_{uuid.uuid4().hex[:8]}",
            "account_number": f"WF{uuid.uuid4().hex[:8]}",
            "bank_name": "Kotak Bank",
            "account_type": "current",
            "opening_balance": 200000
        }
        
        create_response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/accounts/create", json=account_data)
        assert create_response.status_code == 200
        account_id = create_response.json()["account_id"]
        print(f"Step 1: Created account {account_id}")
        
        # 2. Add deposit transaction
        deposit_data = {
            "bank_account_id": account_id,
            "transaction_date": datetime.now().strftime("%Y-%m-%d"),
            "description": "Customer payment",
            "debit_amount": 0,
            "credit_amount": 50000,
            "transaction_type": "deposit"
        }
        
        deposit_response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/transactions/create", json=deposit_data)
        assert deposit_response.status_code == 200
        assert deposit_response.json()["new_balance"] == 250000
        print("Step 2: Added deposit, balance = 250000")
        
        # 3. Add withdrawal transaction
        withdrawal_data = {
            "bank_account_id": account_id,
            "transaction_date": datetime.now().strftime("%Y-%m-%d"),
            "description": "Vendor payment",
            "debit_amount": 30000,
            "credit_amount": 0,
            "transaction_type": "withdrawal"
        }
        
        withdrawal_response = self.session.post(f"{BASE_URL}/api/bank-reconciliation/transactions/create", json=withdrawal_data)
        assert withdrawal_response.status_code == 200
        assert withdrawal_response.json()["new_balance"] == 220000
        print("Step 3: Added withdrawal, balance = 220000")
        
        # 4. Get summary
        summary_response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/summary/{account_id}")
        assert summary_response.status_code == 200
        summary = summary_response.json()
        assert summary["bank_balance"] == 220000
        print(f"Step 4: Summary - Bank balance: {summary['bank_balance']}")
        
        # 5. Get transactions
        txn_response = self.session.get(f"{BASE_URL}/api/bank-reconciliation/transactions/{account_id}")
        assert txn_response.status_code == 200
        assert txn_response.json()["total"] >= 2
        print(f"Step 5: Found {txn_response.json()['total']} transactions")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
