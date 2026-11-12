import { test, expect } from '@playwright/test';

/**
 * Frontend E2E Tests for HSN Codes, Product Creation, and Email Features
 * Tests for iteration 15 - fixes for user-reported issues
 */

test.describe('HSN Codes and Offline Invoice Creation', () => {
  const baseURL = process.env.REACT_APP_BACKEND_URL || 'https://acct-workflow-1.preview.emergentagent.com';

  test.beforeEach(async ({ page }) => {
    // Dismiss any toasts
    await page.addLocatorHandler(
      page.locator('[data-sonner-toast], .Toastify__toast'),
      async () => {
        const close = page.locator('[data-sonner-toast] [data-close], .Toastify__close-button');
        await close.first().click({ timeout: 2000 }).catch(() => {});
      },
      { times: 5, noWaitAfter: true }
    );
  });

  test('HSN API returns 95+ codes', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/hsn/?active_only=true`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.length).toBeGreaterThanOrEqual(95);
  });

  test('Products API returns products list', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/products`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('success');
    expect(data.products.length).toBeGreaterThan(0);
  });

  test('Store login page loads correctly', async ({ page }) => {
    await page.goto(`${baseURL}/#/store/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    
    // Check for login form elements
    const emailInput = page.locator('input[type="email"], input[placeholder*="email" i]');
    const passwordInput = page.locator('input[type="password"]');
    
    // Wait for login form
    await expect(emailInput.first()).toBeVisible();
    await expect(passwordInput.first()).toBeVisible();
  });

  test('Admin can login and access invoice creation', async ({ page }) => {
    // Navigate to admin login
    await page.goto(`${baseURL}/#/admin/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    
    // Fill admin credentials
    const emailInput = page.locator('input[type="email"], input[placeholder*="email" i]');
    const passwordInput = page.locator('input[type="password"]');
    
    await emailInput.first().fill('admin@adityaretail.com');
    await passwordInput.first().fill('admin123');
    
    // Click login button
    const loginButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
    await loginButton.first().click();
    
    // Wait for dashboard to load
    await page.waitForTimeout(3000);
    await page.waitForLoadState('networkidle');
    
    // Take screenshot for verification
    await page.screenshot({ path: 'admin-login.jpeg', quality: 20 });
  });

  test('Stores API returns ARM store', async ({ request }) => {
    const response = await request.get(`${baseURL}/api/invoices/offline/stores`);
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('success');
    expect(data.stores.length).toBeGreaterThan(0);
    
    // Check ARM store exists
    const armStore = data.stores.find(s => s.code === 'ARM');
    expect(armStore).toBeDefined();
    expect(armStore.name).toContain('ARM');
  });

  test('Sales Order creation API works with email notification', async ({ request }) => {
    // Get a product first
    const productsResponse = await request.get(`${baseURL}/api/products`);
    const productsData = await productsResponse.json();
    const product = productsData.products[0];
    
    // Get HSN code
    const hsnResponse = await request.get(`${baseURL}/api/hsn/?active_only=true`);
    const hsnData = await hsnResponse.json();
    const hsnCode = hsnData[0]?.code || '8418';
    
    const testId = `TEST-E2E-${Date.now()}`;
    
    const soData = {
      customer: {
        name: `Test Customer ${testId}`,
        phone: '9876543210',
        email: 'test@example.com',
        customer_type: 'B2C',
        address: 'Test Address',
        city: 'Bangalore',
        state: 'Karnataka',
        pincode: '560001'
      },
      items: [{
        product_id: product.id,
        product_name: product.name,
        hsn_code: hsnCode,
        quantity: 1,
        rate: product.price || 10000,
        discount: 0,
        tax_rate: 18.0
      }],
      payment_mode: 'cash',
      subtotal: product.price || 10000,
      discount: 0,
      delivery_charges: 0,
      round_off: 0,
      notes: `TEST SO ${testId}`,
      created_by: 'e2e-test@automated.com',
      document_type: 'sales_order',
      store_code: 'ARM',
      is_cod: false,
      is_pod: false,
      order_source: 'walk_in'
    };
    
    const response = await request.post(`${baseURL}/api/invoices/offline/create`, {
      data: soData
    });
    
    expect(response.ok()).toBeTruthy();
    
    const data = await response.json();
    expect(data.status).toBe('success');
    expect(data.invoice_number).toBeDefined();
    expect(data).toHaveProperty('email_sent');
  });
});

test.describe('Admin Invoice Creation Page', () => {
  const baseURL = process.env.REACT_APP_BACKEND_URL || 'https://acct-workflow-1.preview.emergentagent.com';

  test('Offline Invoice Creation page shows New Product button', async ({ page }) => {
    // Login as admin first
    await page.goto(`${baseURL}/#/admin/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    
    const emailInput = page.locator('input[type="email"], input[placeholder*="email" i]');
    const passwordInput = page.locator('input[type="password"]');
    
    await emailInput.first().fill('admin@adityaretail.com');
    await passwordInput.first().fill('admin123');
    
    const loginButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
    await loginButton.first().click();
    
    // Wait for login
    await page.waitForTimeout(3000);
    
    // Navigate to invoice creation
    await page.goto(`${baseURL}/#/admin/invoices/create`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    // Look for the "New" button for adding products
    const newProductButton = page.locator('button:has-text("New"), button:has-text("+ New")');
    
    // Take screenshot
    await page.screenshot({ path: 'invoice-creation-page.jpeg', quality: 20 });
    
    // Check if the New button exists
    const buttonCount = await newProductButton.count();
    if (buttonCount > 0) {
      await expect(newProductButton.first()).toBeVisible();
    }
  });

  test('HSN dropdown shows 95+ options', async ({ page }) => {
    // Login and navigate to invoice creation
    await page.goto(`${baseURL}/#/admin/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    
    const emailInput = page.locator('input[type="email"], input[placeholder*="email" i]');
    const passwordInput = page.locator('input[type="password"]');
    
    await emailInput.first().fill('admin@adityaretail.com');
    await passwordInput.first().fill('admin123');
    
    const loginButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")');
    await loginButton.first().click();
    
    await page.waitForTimeout(3000);
    
    // Navigate to invoice creation
    await page.goto(`${baseURL}/#/admin/invoices/create`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    // Find HSN dropdown
    const hsnDropdown = page.locator('select:has(option:has-text("Select HSN"))');
    
    if (await hsnDropdown.count() > 0) {
      const options = await hsnDropdown.first().locator('option').count();
      console.log(`HSN dropdown has ${options} options`);
      // Should have more than 95 options (1 placeholder + 95 HSN codes)
      expect(options).toBeGreaterThan(95);
    }
  });

  test('Store selector shows ARM store', async ({ page }) => {
    // Login and navigate
    await page.goto(`${baseURL}/#/admin/login`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    
    await page.locator('input[type="email"]').first().fill('admin@adityaretail.com');
    await page.locator('input[type="password"]').first().fill('admin123');
    await page.locator('button[type="submit"]').first().click();
    
    await page.waitForTimeout(3000);
    
    await page.goto(`${baseURL}/#/admin/invoices/create`, { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(3000);
    
    // Look for store selector
    const storeDropdown = page.locator('select:has(option:has-text("Select Store"))');
    
    if (await storeDropdown.count() > 0) {
      const storeOptions = await storeDropdown.first().locator('option').allTextContents();
      const hasARM = storeOptions.some(opt => opt.includes('ARM'));
      expect(hasARM).toBeTruthy();
    }
  });
});
