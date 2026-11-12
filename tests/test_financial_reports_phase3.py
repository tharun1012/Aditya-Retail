"""
Phase 3 Financial Reports Tests
Tests for P&L Statement, Balance Sheet, Cash Flow Statement, GST Reports, Audit Trail, and Export
"""

import pytest
import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://acct-workflow-1.preview.emergentagent.com')

# Test data prefixes for cleanup
TEST_PREFIX = "TEST_"


class TestFinancialDashboard:
    """Financial Dashboard Summary Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_financial_dashboard(self):
        """Test getting financial dashboard summary"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "dashboard" in data
        
        # Verify dashboard structure
        dashboard = data["dashboard"]
        assert "this_month" in dashboard
        assert "receivables" in dashboard
        assert "payables" in dashboard
        assert "cash_position" in dashboard
        
        # Verify this_month structure
        this_month = dashboard["this_month"]
        assert "revenue" in this_month
        assert "expenses" in this_month
        assert "profit" in this_month
        assert "margin" in this_month
        
        # Verify receivables structure
        assert "total" in dashboard["receivables"]
        assert "count" in dashboard["receivables"]
        
        # Verify payables structure
        assert "total" in dashboard["payables"]
        assert "count" in dashboard["payables"]
        
        # Verify cash_position structure
        assert "bank_balance" in dashboard["cash_position"]
        assert "bank_accounts" in dashboard["cash_position"]
        
        print(f"Dashboard - Revenue: {this_month['revenue']}, Profit: {this_month['profit']}, Bank: {dashboard['cash_position']['bank_balance']}")


class TestProfitLossStatement:
    """Profit & Loss Statement Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_pl_this_month(self):
        """Test P&L for this month"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?period=this_month")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["report_type"] == "profit_loss"
        
        # Verify period
        assert "period" in data
        assert data["period"]["label"] == "this_month"
        
        # Verify revenue structure
        assert "revenue" in data
        revenue = data["revenue"]
        assert "online_sales" in revenue
        assert "offline_sales" in revenue
        assert "gross_revenue" in revenue
        assert "less_gst" in revenue
        assert "net_revenue" in revenue
        assert "order_count" in revenue
        
        # Verify COGS structure
        assert "cost_of_goods_sold" in data
        assert "purchases" in data["cost_of_goods_sold"]
        assert "purchase_count" in data["cost_of_goods_sold"]
        
        # Verify profit calculations
        assert "gross_profit" in data
        assert "gross_margin_percent" in data
        assert "operating_expenses" in data
        assert "operating_profit" in data
        assert "operating_margin_percent" in data
        assert "tax_provision" in data
        assert "net_profit" in data
        assert "net_margin_percent" in data
        
        print(f"P&L This Month - Revenue: {revenue['net_revenue']}, Net Profit: {data['net_profit']}")
    
    def test_get_pl_last_month(self):
        """Test P&L for last month"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?period=last_month")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["period"]["label"] == "last_month"
        
        print(f"P&L Last Month - Revenue: {data['revenue']['net_revenue']}, Net Profit: {data['net_profit']}")
    
    def test_get_pl_custom_date_range(self):
        """Test P&L with custom date range"""
        from_date = "2025-01-01"
        to_date = "2025-12-31"
        
        response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?from_date={from_date}&to_date={to_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # Verify custom dates are used
        assert data["period"]["from"] == from_date
        assert data["period"]["to"] == to_date
        
        print(f"P&L Custom Range - Revenue: {data['revenue']['net_revenue']}, Net Profit: {data['net_profit']}")
    
    def test_get_pl_this_quarter(self):
        """Test P&L for this quarter"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?period=this_quarter")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["period"]["label"] == "this_quarter"
        
        print(f"P&L This Quarter - Revenue: {data['revenue']['net_revenue']}")
    
    def test_get_pl_this_year(self):
        """Test P&L for this year"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?period=this_year")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["period"]["label"] == "this_year"
        
        print(f"P&L This Year - Revenue: {data['revenue']['net_revenue']}")
    
    def test_pl_expense_breakdown(self):
        """Test P&L expense breakdown structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?period=this_year")
        assert response.status_code == 200
        data = response.json()
        
        # Verify operating expenses structure
        assert "operating_expenses" in data
        assert "total" in data["operating_expenses"]
        assert "breakdown" in data["operating_expenses"]
        
        # Breakdown should be a dict
        assert isinstance(data["operating_expenses"]["breakdown"], dict)
        
        print(f"Operating Expenses: {data['operating_expenses']['total']}, Breakdown: {data['operating_expenses']['breakdown']}")


class TestBalanceSheet:
    """Balance Sheet Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_balance_sheet_current(self):
        """Test Balance Sheet as of current date"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["report_type"] == "balance_sheet"
        
        # Verify as_of_date is present
        assert "as_of_date" in data
        
        # Verify assets structure
        assert "assets" in data
        assets = data["assets"]
        assert "current_assets" in assets
        assert "fixed_assets" in assets
        assert "total_assets" in assets
        
        # Verify current assets breakdown
        current_assets = assets["current_assets"]
        assert "cash_and_bank" in current_assets
        assert "accounts_receivable" in current_assets
        assert "inventory" in current_assets
        assert "total_current_assets" in current_assets
        
        # Verify cash_and_bank has accounts list
        assert "total" in current_assets["cash_and_bank"]
        assert "accounts" in current_assets["cash_and_bank"]
        
        print(f"Balance Sheet - Total Assets: {assets['total_assets']}")
    
    def test_balance_sheet_liabilities_structure(self):
        """Test Balance Sheet liabilities structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        
        # Verify liabilities structure
        assert "liabilities" in data
        liabilities = data["liabilities"]
        assert "current_liabilities" in liabilities
        assert "long_term_liabilities" in liabilities
        assert "total_liabilities" in liabilities
        
        # Verify current liabilities breakdown
        current_liabilities = liabilities["current_liabilities"]
        assert "accounts_payable" in current_liabilities
        assert "gst_payable" in current_liabilities
        assert "other_liabilities" in current_liabilities
        assert "total_current_liabilities" in current_liabilities
        
        print(f"Balance Sheet - Total Liabilities: {liabilities['total_liabilities']}")
    
    def test_balance_sheet_equity_structure(self):
        """Test Balance Sheet equity structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        
        # Verify equity structure
        assert "equity" in data
        equity = data["equity"]
        assert "retained_earnings" in equity
        assert "total_equity" in equity
        
        print(f"Balance Sheet - Total Equity: {equity['total_equity']}")
    
    def test_balance_sheet_is_balanced(self):
        """Test that Balance Sheet is balanced (Assets = Liabilities + Equity)"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/balance-sheet")
        assert response.status_code == 200
        data = response.json()
        
        # Verify is_balanced flag
        assert "is_balanced" in data
        assert "total_liabilities_and_equity" in data
        
        # Verify the balance equation
        total_assets = data["assets"]["total_assets"]
        total_liab_equity = data["total_liabilities_and_equity"]
        
        # Should be balanced (within small tolerance for floating point)
        assert abs(total_assets - total_liab_equity) < 0.01, f"Balance sheet not balanced: Assets={total_assets}, Liab+Equity={total_liab_equity}"
        assert data["is_balanced"] == True
        
        print(f"Balance Sheet Balanced: Assets={total_assets}, Liab+Equity={total_liab_equity}")
    
    def test_balance_sheet_with_custom_date(self):
        """Test Balance Sheet with custom as_of_date"""
        as_of_date = "2025-12-31T23:59:59"
        response = self.session.get(f"{BASE_URL}/api/financial-reports/balance-sheet?as_of_date={as_of_date}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        print(f"Balance Sheet as of {as_of_date} - Total Assets: {data['assets']['total_assets']}")


class TestCashFlowStatement:
    """Cash Flow Statement Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_cash_flow_this_month(self):
        """Test Cash Flow Statement for this month"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/cash-flow?period=this_month")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["report_type"] == "cash_flow"
        
        # Verify period
        assert "period" in data
        assert data["period"]["label"] == "this_month"
        
        # Verify operating activities structure
        assert "operating_activities" in data
        operating = data["operating_activities"]
        assert "cash_from_customers" in operating
        assert "cash_from_online_sales" in operating
        assert "total_inflows" in operating
        assert "cash_to_suppliers" in operating
        assert "cash_for_expenses" in operating
        assert "total_outflows" in operating
        assert "net_operating_cash_flow" in operating
        
        print(f"Cash Flow - Net Operating: {operating['net_operating_cash_flow']}")
    
    def test_cash_flow_investing_activities(self):
        """Test Cash Flow investing activities structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/cash-flow?period=this_month")
        assert response.status_code == 200
        data = response.json()
        
        # Verify investing activities structure
        assert "investing_activities" in data
        investing = data["investing_activities"]
        assert "asset_purchases" in investing
        assert "asset_sales" in investing
        assert "net_investing_cash_flow" in investing
        
        print(f"Cash Flow - Net Investing: {investing['net_investing_cash_flow']}")
    
    def test_cash_flow_financing_activities(self):
        """Test Cash Flow financing activities structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/cash-flow?period=this_month")
        assert response.status_code == 200
        data = response.json()
        
        # Verify financing activities structure
        assert "financing_activities" in data
        financing = data["financing_activities"]
        assert "loan_receipts" in financing
        assert "loan_payments" in financing
        assert "net_financing_cash_flow" in financing
        
        print(f"Cash Flow - Net Financing: {financing['net_financing_cash_flow']}")
    
    def test_cash_flow_summary(self):
        """Test Cash Flow summary section"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/cash-flow?period=this_month")
        assert response.status_code == 200
        data = response.json()
        
        # Verify summary structure
        assert "summary" in data
        summary = data["summary"]
        assert "net_change_in_cash" in summary
        assert "opening_cash_balance" in summary
        assert "closing_cash_balance" in summary
        
        print(f"Cash Flow Summary - Opening: {summary['opening_cash_balance']}, Closing: {summary['closing_cash_balance']}, Change: {summary['net_change_in_cash']}")
    
    def test_cash_flow_different_periods(self):
        """Test Cash Flow with different periods"""
        periods = ["this_week", "last_month", "this_quarter", "this_year"]
        
        for period in periods:
            response = self.session.get(f"{BASE_URL}/api/financial-reports/cash-flow?period={period}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["period"]["label"] == period
            print(f"Cash Flow {period} - Net Operating: {data['operating_activities']['net_operating_cash_flow']}")


class TestGSTSummary:
    """GST Summary Report Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_gst_summary_this_month(self):
        """Test GST Summary for this month"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/summary?period=this_month")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["report_type"] == "gst_summary"
        
        # Verify period
        assert "period" in data
        assert data["period"]["label"] == "this_month"
        
        # Verify output GST structure
        assert "output_gst" in data
        output = data["output_gst"]
        assert "taxable_value" in output
        assert "cgst" in output
        assert "sgst" in output
        assert "igst" in output
        assert "total" in output
        assert "invoice_count" in output
        
        print(f"GST Summary - Output GST: {output['total']}")
    
    def test_gst_summary_input_gst(self):
        """Test GST Summary input GST structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/summary?period=this_month")
        assert response.status_code == 200
        data = response.json()
        
        # Verify input GST structure
        assert "input_gst" in data
        input_gst = data["input_gst"]
        assert "taxable_value" in input_gst
        assert "cgst" in input_gst
        assert "sgst" in input_gst
        assert "igst" in input_gst
        assert "total" in input_gst
        assert "bill_count" in input_gst
        
        print(f"GST Summary - Input GST: {input_gst['total']}")
    
    def test_gst_summary_net_liability(self):
        """Test GST Summary net liability calculation"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/summary?period=this_month")
        assert response.status_code == 200
        data = response.json()
        
        # Verify net liability structure
        assert "net_liability" in data
        net_liability = data["net_liability"]
        assert "amount" in net_liability
        assert "status" in net_liability
        
        # Status should be one of: payable, refundable, nil
        assert net_liability["status"] in ["payable", "refundable", "nil"]
        
        # Verify calculation: net = output - input
        expected_net = data["output_gst"]["total"] - data["input_gst"]["total"]
        assert abs(net_liability["amount"] - expected_net) < 0.01
        
        print(f"GST Net Liability: {net_liability['amount']} ({net_liability['status']})")
    
    def test_gst_summary_different_periods(self):
        """Test GST Summary with different periods"""
        periods = ["this_month", "last_month", "this_quarter", "this_year"]
        
        for period in periods:
            response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/summary?period={period}")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            print(f"GST {period} - Output: {data['output_gst']['total']}, Input: {data['input_gst']['total']}")


class TestHSNWiseReport:
    """HSN-wise GST Report Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_hsn_wise_report(self):
        """Test HSN-wise GST report"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/hsn-wise?period=this_month")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["report_type"] == "hsn_wise_summary"
        
        # Verify period
        assert "period" in data
        
        # Verify hsn_data is a list
        assert "hsn_data" in data
        assert isinstance(data["hsn_data"], list)
        
        # Verify totals structure
        assert "totals" in data
        totals = data["totals"]
        assert "taxable_value" in totals
        assert "cgst" in totals
        assert "sgst" in totals
        assert "total_gst" in totals
        
        print(f"HSN Report - {len(data['hsn_data'])} HSN codes, Total GST: {totals['total_gst']}")
    
    def test_hsn_wise_data_structure(self):
        """Test HSN-wise data item structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/hsn-wise?period=this_year")
        assert response.status_code == 200
        data = response.json()
        
        # If there's HSN data, verify structure
        if data["hsn_data"]:
            hsn_item = data["hsn_data"][0]
            assert "hsn_code" in hsn_item
            assert "description" in hsn_item
            assert "quantity" in hsn_item
            assert "taxable_value" in hsn_item
            assert "gst_rate" in hsn_item
            assert "cgst" in hsn_item
            assert "sgst" in hsn_item
            assert "total_gst" in hsn_item
            assert "invoice_count" in hsn_item
            
            print(f"First HSN: {hsn_item['hsn_code']} - {hsn_item['description']}, GST: {hsn_item['total_gst']}")
        else:
            print("No HSN data available for this period")


class TestAuditTrail:
    """Audit Trail Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_get_audit_trail_all(self):
        """Test getting all audit trail entries"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["report_type"] == "audit_trail"
        
        # Verify structure
        assert "period" in data
        assert "entries" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        
        print(f"Audit Trail - Total: {data['total']} entries")
    
    def test_audit_trail_entry_structure(self):
        """Test audit trail entry structure"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?limit=10")
        assert response.status_code == 200
        data = response.json()
        
        # If there are entries, verify structure
        if data["entries"]:
            entry = data["entries"][0]
            assert "timestamp" in entry
            assert "type" in entry
            assert "reference" in entry
            assert "description" in entry
            assert "amount" in entry
            assert "direction" in entry
            assert "entity_id" in entry
            
            # Type should be one of: order, payment, expense, journal
            assert entry["type"] in ["order", "payment", "expense", "journal"]
            
            # Direction should be one of: credit, debit, journal
            assert entry["direction"] in ["credit", "debit", "journal"]
            
            print(f"First entry: {entry['type']} - {entry['reference']} - {entry['amount']}")
    
    def test_audit_trail_filter_by_entity_type_orders(self):
        """Test filtering audit trail by orders"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?entity_type=orders")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # All entries should be orders
        for entry in data["entries"]:
            assert entry["type"] == "order"
        
        print(f"Audit Trail Orders - Total: {data['total']}")
    
    def test_audit_trail_filter_by_entity_type_payments(self):
        """Test filtering audit trail by payments"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?entity_type=payments")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # All entries should be payments
        for entry in data["entries"]:
            assert entry["type"] == "payment"
        
        print(f"Audit Trail Payments - Total: {data['total']}")
    
    def test_audit_trail_filter_by_entity_type_expenses(self):
        """Test filtering audit trail by expenses"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?entity_type=expenses")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # All entries should be expenses
        for entry in data["entries"]:
            assert entry["type"] == "expense"
        
        print(f"Audit Trail Expenses - Total: {data['total']}")
    
    def test_audit_trail_filter_by_entity_type_journal(self):
        """Test filtering audit trail by journal vouchers"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?entity_type=journal")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        
        # All entries should be journal
        for entry in data["entries"]:
            assert entry["type"] == "journal"
        
        print(f"Audit Trail Journal - Total: {data['total']}")
    
    def test_audit_trail_pagination(self):
        """Test audit trail pagination"""
        # Get first page
        response1 = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?page=1&limit=5")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Get second page
        response2 = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?page=2&limit=5")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Verify pagination
        assert data1["page"] == 1
        assert data2["page"] == 2
        
        # If there are enough entries, pages should be different
        if data1["total"] > 5:
            # First entries should be different
            if data1["entries"] and data2["entries"]:
                assert data1["entries"][0]["entity_id"] != data2["entries"][0]["entity_id"]
        
        print(f"Pagination - Page 1: {len(data1['entries'])} entries, Page 2: {len(data2['entries'])} entries")


class TestReportExport:
    """Report Export Tests"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        yield
    
    def test_export_pl_to_csv(self):
        """Test exporting P&L to CSV"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/export/profit-loss?period=this_month&format=csv")
        assert response.status_code == 200
        
        # Verify content type is CSV
        assert "text/csv" in response.headers.get("Content-Type", "")
        
        # Verify content disposition header
        content_disposition = response.headers.get("Content-Disposition", "")
        assert "attachment" in content_disposition
        assert "profit-loss" in content_disposition
        
        # Verify CSV content
        content = response.text
        assert "Profit & Loss Statement" in content
        assert "REVENUE" in content
        assert "Online Sales" in content
        assert "Net Revenue" in content
        assert "COST OF GOODS SOLD" in content
        assert "Gross Profit" in content
        assert "Net Profit" in content
        
        print(f"P&L CSV Export - {len(content)} bytes")
    
    def test_export_gst_to_csv(self):
        """Test exporting GST Summary to CSV"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/export/gst-summary?period=this_month&format=csv")
        assert response.status_code == 200
        
        # Verify content type is CSV
        assert "text/csv" in response.headers.get("Content-Type", "")
        
        # Verify CSV content
        content = response.text
        assert "GST Summary Report" in content
        assert "OUTPUT GST" in content
        assert "INPUT GST" in content
        assert "CGST" in content
        assert "SGST" in content
        assert "Net GST Liability" in content
        
        print(f"GST CSV Export - {len(content)} bytes")
    
    def test_export_unsupported_report_type(self):
        """Test exporting unsupported report type"""
        response = self.session.get(f"{BASE_URL}/api/financial-reports/export/unsupported-type?period=this_month&format=csv")
        assert response.status_code == 200
        
        # Should return a message about unsupported type
        content = response.text
        assert "not supported" in content.lower()
        
        print("Unsupported export type handled correctly")
    
    def test_export_pl_different_periods(self):
        """Test exporting P&L with different periods"""
        periods = ["this_month", "last_month", "this_quarter", "this_year"]
        
        for period in periods:
            response = self.session.get(f"{BASE_URL}/api/financial-reports/export/profit-loss?period={period}&format=csv")
            assert response.status_code == 200
            assert "text/csv" in response.headers.get("Content-Type", "")
            print(f"P&L Export {period} - OK")


class TestIntegrationFinancialReports:
    """Integration tests for Financial Reports workflow"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test session"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        yield
    
    def test_full_financial_reports_workflow(self):
        """Test complete financial reports workflow"""
        # 1. Get Dashboard
        dashboard_response = self.session.get(f"{BASE_URL}/api/financial-reports/dashboard")
        assert dashboard_response.status_code == 200
        dashboard = dashboard_response.json()
        print(f"Step 1: Dashboard - Revenue: {dashboard['dashboard']['this_month']['revenue']}")
        
        # 2. Get P&L
        pl_response = self.session.get(f"{BASE_URL}/api/financial-reports/profit-loss?period=this_month")
        assert pl_response.status_code == 200
        pl = pl_response.json()
        print(f"Step 2: P&L - Net Profit: {pl['net_profit']}")
        
        # 3. Get Balance Sheet
        bs_response = self.session.get(f"{BASE_URL}/api/financial-reports/balance-sheet")
        assert bs_response.status_code == 200
        bs = bs_response.json()
        assert bs["is_balanced"] == True
        print(f"Step 3: Balance Sheet - Total Assets: {bs['assets']['total_assets']}")
        
        # 4. Get Cash Flow
        cf_response = self.session.get(f"{BASE_URL}/api/financial-reports/cash-flow?period=this_month")
        assert cf_response.status_code == 200
        cf = cf_response.json()
        print(f"Step 4: Cash Flow - Closing Balance: {cf['summary']['closing_cash_balance']}")
        
        # 5. Get GST Summary
        gst_response = self.session.get(f"{BASE_URL}/api/financial-reports/gst/summary?period=this_month")
        assert gst_response.status_code == 200
        gst = gst_response.json()
        print(f"Step 5: GST Summary - Net Liability: {gst['net_liability']['amount']}")
        
        # 6. Get Audit Trail
        audit_response = self.session.get(f"{BASE_URL}/api/financial-reports/audit-trail?limit=10")
        assert audit_response.status_code == 200
        audit = audit_response.json()
        print(f"Step 6: Audit Trail - {audit['total']} entries")
        
        # 7. Export P&L
        export_response = self.session.get(f"{BASE_URL}/api/financial-reports/export/profit-loss?period=this_month&format=csv")
        assert export_response.status_code == 200
        print(f"Step 7: Export P&L - {len(export_response.text)} bytes")
        
        print("Full workflow completed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
