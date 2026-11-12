import { test, expect, Page } from '@playwright/test';
import { TEST_CREDENTIALS, dismissToasts } from '../fixtures/helpers';

// Helper function for ARM store login
async function loginArmStore(page: Page) {
  await page.goto('/#/store/login');
  await page.getByTestId('store-login-email').fill(TEST_CREDENTIALS.armStore.email);
  await page.getByTestId('store-login-password').fill(TEST_CREDENTIALS.armStore.password);
  await page.getByTestId('store-login-submit').click();
  await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
}

test.describe('Store Dashboard Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
    await loginArmStore(page);
  });

  test('Store dashboard loads with modules', async ({ page }) => {
    // Dashboard should show modules/cards
    await expect(page.getByText('Operations')).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('heading', { name: 'Sales Invoices' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Orders & Sales' })).toBeVisible();
  });

  test('Sales Invoices module is present in store dashboard', async ({ page }) => {
    // This is a key requirement - Sales Invoices must be visible
    await expect(page.getByRole('heading', { name: 'Sales Invoices' })).toBeVisible({ timeout: 10000 });
  });

  test('Orders & Sales navigates to /store/orders (not /admin)', async ({ page }) => {
    // Click on Orders & Sales card
    await page.click('text=Orders & Sales');
    await page.waitForURL('**/#/store/orders', { timeout: 10000 });
    
    // Verify we're NOT on admin
    expect(page.url()).toContain('/store/orders');
    expect(page.url()).not.toContain('/admin');
    
    // Verify StoreRouter content loads
    await expect(page.getByText('Recent Sales Orders')).toBeVisible({ timeout: 10000 });
  });

  test('All store tabs visible in StoreRouter', async ({ page }) => {
    // First navigate to orders to get StoreRouter
    await page.click('text=Orders & Sales');
    await page.waitForURL('**/#/store/orders', { timeout: 10000 });
    
    // Verify all tabs are visible
    const expectedTabs = [
      { id: 'overview', label: 'Overview' },
      { id: 'orders', label: 'Sales Orders' },
      { id: 'invoices', label: 'Sales Invoices' },
      { id: 'inventory', label: 'Inventory' },
      { id: 'transfers', label: 'Stock Transfers' },
      { id: 'po-requests', label: 'PO Requests' },
      { id: 'reports', label: 'Reports' },
      { id: 'customers', label: 'Customers' }
    ];

    for (const tab of expectedTabs) {
      await expect(page.getByTestId(`store-tab-${tab.id}`)).toBeVisible();
    }
  });
});

test.describe('Store Tab Navigation', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
    await loginArmStore(page);
    // Navigate to orders first to get StoreRouter
    await page.click('text=Orders & Sales');
    await page.waitForURL('**/#/store/orders', { timeout: 10000 });
    await page.waitForLoadState('domcontentloaded');
  });

  test('Sales Invoices tab navigates correctly', async ({ page }) => {
    await page.getByTestId('store-tab-invoices').click();
    await page.waitForURL('**/#/store/invoices', { timeout: 10000 });
    
    expect(page.url()).toContain('/store/invoices');
    expect(page.url()).not.toContain('/admin');
    await expect(page.getByText('Sales Invoices').first()).toBeVisible();
  });

  test('Inventory tab navigates correctly', async ({ page }) => {
    await page.getByTestId('store-tab-inventory').click();
    await page.waitForURL('**/#/store/inventory', { timeout: 10000 });
    
    expect(page.url()).toContain('/store/inventory');
    expect(page.url()).not.toContain('/admin');
    await expect(page.getByText('Store Inventory')).toBeVisible();
  });

  test('Stock Transfers tab navigates correctly', async ({ page }) => {
    await page.getByTestId('store-tab-transfers').click();
    await page.waitForURL('**/#/store/transfers', { timeout: 10000 });
    
    expect(page.url()).toContain('/store/transfers');
    expect(page.url()).not.toContain('/admin');
    await expect(page.getByText('Stock Transfer Requests')).toBeVisible();
  });

  test('Reports tab navigates correctly', async ({ page }) => {
    await page.getByTestId('store-tab-reports').click();
    await page.waitForURL('**/#/store/reports', { timeout: 10000 });
    
    expect(page.url()).toContain('/store/reports');
    expect(page.url()).not.toContain('/admin');
    await expect(page.getByText('Daily Report')).toBeVisible();
  });

  test('Customers tab navigates correctly', async ({ page }) => {
    await page.getByTestId('store-tab-customers').click();
    await page.waitForURL('**/#/store/customers', { timeout: 10000 });
    
    expect(page.url()).toContain('/store/customers');
    expect(page.url()).not.toContain('/admin');
    await expect(page.getByText('Store Customers')).toBeVisible();
  });
});
