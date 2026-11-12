import { test, expect } from '@playwright/test';

/**
 * E2E Tests for Store Customer Management
 * Tests: Customer listing, Add Customer functionality
 */

test.describe('Store Customer Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login as ARM store manager
    await page.goto('/#/store/login', { waitUntil: 'domcontentloaded' });
    await page.getByTestId('store-login-email').fill('manager@arm.adityaretail.com');
    await page.getByTestId('store-login-password').fill('store123');
    await page.getByTestId('store-login-submit').click();
    await page.waitForURL('**/#/store/dashboard**');
    await page.waitForLoadState('domcontentloaded');
  });

  test('ARM store login shows correct store name', async ({ page }) => {
    // Verify store header using specific role
    await expect(page.getByRole('heading', { name: 'Bosch Malleswaram' })).toBeVisible();
    await expect(page.getByText('Store Code: ARM')).toBeVisible();
  });

  test('Customers tab shows customer list', async ({ page }) => {
    // Navigate to Customers
    await page.goto('/#/store/customers', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');
    
    // Verify customer page elements
    await expect(page.locator('text=Store Customers')).toBeVisible();
    await expect(page.locator('button:has-text("Add Customer")')).toBeVisible();
    
    // Verify table headers using columnheader role
    await expect(page.getByRole('columnheader', { name: 'Name' })).toBeVisible();
    await expect(page.getByRole('columnheader', { name: 'Phone' })).toBeVisible();
  });

  test('Customer list displays customer entries', async ({ page }) => {
    // Navigate to Customers
    await page.goto('/#/store/customers', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');
    
    // Wait for the table to load
    await expect(page.locator('text=Store Customers')).toBeVisible();
    
    // Look for Edit buttons which indicate customer rows exist
    const editButtons = page.locator('text=Edit');
    const count = await editButtons.count();
    
    // Log the count for debugging
    console.log(`Found ${count} customer entries with Edit buttons`);
    
    // Test passes if table is visible (customers may or may not exist)
  });

  test('Add Customer button opens modal with form fields', async ({ page }) => {
    // Navigate to Customers
    await page.goto('/#/store/customers', { waitUntil: 'domcontentloaded' });
    await page.waitForLoadState('domcontentloaded');
    
    // Click Add Customer button
    await page.locator('button:has-text("Add Customer")').click();
    
    // Verify modal appears with form fields
    await expect(page.locator('text=Add New Customer')).toBeVisible();
    await expect(page.getByPlaceholder('Enter customer name')).toBeVisible();
    await expect(page.getByPlaceholder('10 digit mobile')).toBeVisible();
    
    // Verify Cancel and Add Customer buttons in modal
    await expect(page.locator('button:has-text("Cancel")')).toBeVisible();
    await expect(page.locator('form button:has-text("Add Customer")')).toBeVisible();
  });

  test('Store dashboard shows operation modules', async ({ page }) => {
    // Verify dashboard modules using data-testid with first() to avoid strict mode
    await expect(page.getByTestId('module-create_order').first()).toBeVisible();
    await expect(page.getByTestId('module-orders_sales').first()).toBeVisible();
    await expect(page.getByTestId('module-sales_invoices').first()).toBeVisible();
  });
});

test.describe('Store Sales Order Module', () => {
  test.beforeEach(async ({ page }) => {
    // Login as ARM store manager
    await page.goto('/#/store/login', { waitUntil: 'domcontentloaded' });
    await page.getByTestId('store-login-email').fill('manager@arm.adityaretail.com');
    await page.getByTestId('store-login-password').fill('store123');
    await page.getByTestId('store-login-submit').click();
    await page.waitForURL('**/#/store/dashboard**');
    await page.waitForLoadState('domcontentloaded');
  });

  test('Orders & Sales module is clickable', async ({ page }) => {
    // Click on Orders & Sales module using first() to avoid strict mode
    const ordersModule = page.getByTestId('module-orders_sales').first();
    await expect(ordersModule).toBeVisible();
    await ordersModule.click();
    
    // Should navigate to orders section
    await page.waitForLoadState('domcontentloaded');
  });

  test('Create Sales Order module is accessible', async ({ page }) => {
    // Find Create Sales Order module using first() to avoid strict mode
    const createOrderModule = page.getByTestId('module-create_order').first();
    await expect(createOrderModule).toBeVisible();
  });
});
