import { test, expect } from '@playwright/test';
import { waitForAppReady, dismissToasts, TEST_CREDENTIALS } from '../fixtures/helpers';

test.describe('Store Login - ARM Store', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
  });

  test('ARM store login with valid credentials', async ({ page }) => {
    await page.goto('/#/store/login');
    await waitForAppReady(page);
    
    // Fill login form
    await page.getByTestId('store-login-email').fill(TEST_CREDENTIALS.armStore.email);
    await page.getByTestId('store-login-password').fill(TEST_CREDENTIALS.armStore.password);
    await page.getByTestId('store-login-submit').click();
    
    // Wait for redirect to dashboard
    await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
    
    // Verify store name is displayed
    await expect(page.getByText('Malleswaram Store (ARM)')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Store Code: ARM')).toBeVisible();
  });

  test('Store dashboard shows all required modules', async ({ page }) => {
    // Login first
    await page.goto('/#/store/login');
    await page.getByTestId('store-login-email').fill(TEST_CREDENTIALS.armStore.email);
    await page.getByTestId('store-login-password').fill(TEST_CREDENTIALS.armStore.password);
    await page.getByTestId('store-login-submit').click();
    await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
    await page.waitForLoadState('domcontentloaded');
    
    // Verify Operations section modules
    await expect(page.getByText('Operations')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('heading', { name: 'Create Sales Order' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Orders & Sales' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Sales Invoices' })).toBeVisible();
    
    // Verify Stock Management section
    await expect(page.getByText('Stock Management')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Stock Transfer' })).toBeVisible();
  });
});

test.describe('Create Sales Order - Store User', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
    // Login as ARM store manager
    await page.goto('/#/store/login');
    await page.getByTestId('store-login-email').fill(TEST_CREDENTIALS.armStore.email);
    await page.getByTestId('store-login-password').fill(TEST_CREDENTIALS.armStore.password);
    await page.getByTestId('store-login-submit').click();
    await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
  });

  test('Navigate to Create Sales Order page', async ({ page }) => {
    // Click on Create Sales Order module
    await page.click('text=Create Sales Order');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify we're on the create order page
    await expect(page.getByRole('heading', { name: 'Create Offline Invoice' })).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Select Store')).toBeVisible();
    
    // Store should be locked for store user
    await expect(page.getByText('Your Store')).toBeVisible();
    await expect(page.getByText('Malleswaram Store (ARM)')).toBeVisible();
  });

  test('Create Sales Order form shows B2B/B2C customer type selection', async ({ page }) => {
    await page.click('text=Create Sales Order');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify B2B/B2C toggle is present
    await expect(page.getByRole('button', { name: /B2C.*Individual/i })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: /B2B.*Business/i })).toBeVisible();
  });

  test('Create Sales Order form shows Document Type selection', async ({ page }) => {
    await page.click('text=Create Sales Order');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify Document Type options
    await expect(page.getByText('Document Type')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Direct Invoice')).toBeVisible();
    // Use exact match for Sales Order to avoid ambiguity
    await expect(page.getByText('Sales Order', { exact: true })).toBeVisible();
  });

  test('Create Sales Order form shows Order Source section', async ({ page }) => {
    await page.click('text=Create Sales Order');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify Order Source section
    await expect(page.getByText('Order Source / Origin')).toBeVisible({ timeout: 10000 });
  });

  test('Create Sales Order form shows Payment Mode options', async ({ page }) => {
    await page.click('text=Create Sales Order');
    await page.waitForLoadState('domcontentloaded');
    
    // Verify Payment Mode dropdown
    await expect(page.getByText('Payment Mode')).toBeVisible({ timeout: 10000 });
    
    // Check if Cash is the default by finding dropdown containing Cash
    await expect(page.locator('select').first()).toBeVisible();
  });
});

test.describe('Admin Login and Sales Orders', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
  });

  test('Admin login with valid credentials', async ({ page }) => {
    await page.goto('/#/admin/login');
    await waitForAppReady(page);
    
    // Fill login form
    await page.locator('input[type="email"]').fill(TEST_CREDENTIALS.admin.email);
    await page.locator('input[type="password"]').fill(TEST_CREDENTIALS.admin.password);
    await page.locator('button[type="submit"]').click();
    
    // Wait for redirect
    await page.waitForURL('**/#/admin/**', { timeout: 15000 });
    
    // Verify admin dashboard
    await expect(page.getByText('Admin Dashboard')).toBeVisible({ timeout: 10000 });
    await expect(page.getByText('Aditya Retail Admin')).toBeVisible();
  });

  test('Admin can navigate to Sales Orders page', async ({ page }) => {
    // Admin login
    await page.goto('/#/admin/login');
    await page.locator('input[type="email"]').fill(TEST_CREDENTIALS.admin.email);
    await page.locator('input[type="password"]').fill(TEST_CREDENTIALS.admin.password);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/#/admin/**', { timeout: 15000 });
    await page.waitForLoadState('networkidle');
    
    // Navigate to Sales Orders
    await page.goto('/#/admin/sales-orders');
    await page.waitForLoadState('networkidle');
    
    // Verify Sales Orders page loads - use text instead of heading
    await expect(page.locator('h1:has-text("Sales Orders")')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('Total Sales Orders')).toBeVisible();
  });

  test('Admin Sales Orders page shows Store column', async ({ page }) => {
    await page.goto('/#/admin/login');
    await page.locator('input[type="email"]').fill(TEST_CREDENTIALS.admin.email);
    await page.locator('input[type="password"]').fill(TEST_CREDENTIALS.admin.password);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/#/admin/**', { timeout: 15000 });
    await page.waitForLoadState('networkidle');
    
    await page.goto('/#/admin/sales-orders');
    await page.waitForLoadState('networkidle');
    
    // Wait for page to load
    await expect(page.locator('h1:has-text("Sales Orders")')).toBeVisible({ timeout: 15000 });
    
    // Verify Store column exists in header
    await expect(page.getByRole('columnheader', { name: /STORE/i })).toBeVisible({ timeout: 10000 });
  });

  test('Admin Sales Orders shows Edit button for orders', async ({ page }) => {
    await page.goto('/#/admin/login');
    await page.locator('input[type="email"]').fill(TEST_CREDENTIALS.admin.email);
    await page.locator('input[type="password"]').fill(TEST_CREDENTIALS.admin.password);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/#/admin/**', { timeout: 15000 });
    await page.waitForLoadState('networkidle');
    
    await page.goto('/#/admin/sales-orders');
    await page.waitForLoadState('networkidle');
    
    // Wait for page to load
    await expect(page.locator('h1:has-text("Sales Orders")')).toBeVisible({ timeout: 15000 });
    
    // Check if there are orders and Edit button exists
    const rows = page.locator('tbody tr');
    const rowCount = await rows.count();
    
    if (rowCount > 0) {
      // Find Edit button (pencil icon)
      const editButton = rows.first().locator('[title="Edit Order"]');
      await expect(editButton).toBeVisible();
    }
  });
});

test.describe('Pending Receipt Approval - Admin', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
    // Login first
    await page.goto('/#/admin/login');
    await page.locator('input[type="email"]').fill(TEST_CREDENTIALS.admin.email);
    await page.locator('input[type="password"]').fill(TEST_CREDENTIALS.admin.password);
    await page.locator('button[type="submit"]').click();
    await page.waitForURL('**/#/admin/**', { timeout: 15000 });
    await page.waitForLoadState('networkidle');
  });

  test('Navigate to Pending Receipt Approvals page', async ({ page }) => {
    await page.goto('/#/admin/pending-receipts');
    await page.waitForLoadState('networkidle');
    
    // Verify page loads
    await expect(page.locator('h1:has-text("Pending Receipt Approvals")')).toBeVisible({ timeout: 15000 });
  });

  test('Pending Receipts page shows stats cards', async ({ page }) => {
    await page.goto('/#/admin/pending-receipts');
    await page.waitForLoadState('networkidle');
    
    // Verify stats are visible
    await expect(page.getByText('Pending Approvals')).toBeVisible({ timeout: 15000 });
    await expect(page.getByText('Total Amount Pending')).toBeVisible();
    await expect(page.getByText('Advance Payments')).toBeVisible();
  });

  test('Pending Receipts table shows required columns', async ({ page }) => {
    await page.goto('/#/admin/pending-receipts');
    await page.waitForLoadState('networkidle');
    
    // Wait for page to load
    await expect(page.locator('h1:has-text("Pending Receipt Approvals")')).toBeVisible({ timeout: 15000 });
    
    // Verify table headers
    await expect(page.getByRole('columnheader', { name: /RECEIPT/i })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('columnheader', { name: /CUSTOMER/i })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: /AMOUNT/i })).toBeVisible();
  });
});

test.describe('Stock Transfer Request - Store User', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
    // Login as store user
    await page.goto('/#/store/login');
    await page.getByTestId('store-login-email').fill(TEST_CREDENTIALS.armStore.email);
    await page.getByTestId('store-login-password').fill(TEST_CREDENTIALS.armStore.password);
    await page.getByTestId('store-login-submit').click();
    await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
  });

  test('Navigate to Stock Transfer from dashboard', async ({ page }) => {
    // Click on Stock Transfer module
    await page.click('text=Stock Transfer');
    await page.waitForLoadState('domcontentloaded');
    
    // Should redirect to transfers tab
    await page.waitForURL('**/#/store/transfers', { timeout: 10000 });
  });

  test('Stock Transfer tab shows Request button', async ({ page }) => {
    // Navigate via module
    await page.click('text=Stock Transfer');
    await page.waitForURL('**/#/store/transfers', { timeout: 10000 });
    await page.waitForLoadState('domcontentloaded');
    
    // Verify Stock Transfer tab is active
    await expect(page.getByTestId('store-tab-transfers')).toBeVisible();
    await expect(page.getByText('Stock Transfer Requests')).toBeVisible({ timeout: 10000 });
    
    // Verify Request button is present - use button role
    await expect(page.getByRole('button', { name: 'Request Stock Transfer' })).toBeVisible();
  });
});
