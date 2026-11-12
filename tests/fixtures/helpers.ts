import { Page, expect } from '@playwright/test';

export async function waitForAppReady(page: Page) {
  await page.waitForLoadState('domcontentloaded');
}

export async function dismissToasts(page: Page) {
  await page.addLocatorHandler(
    page.locator('[data-sonner-toast], .Toastify__toast, [role="status"].toast, .MuiSnackbar-root'),
    async () => {
      const close = page.locator('[data-sonner-toast] [data-close], [data-sonner-toast] button[aria-label="Close"], .Toastify__close-button, .MuiSnackbar-root button');
      await close.first().click({ timeout: 2000 }).catch(() => {});
    },
    { times: 10, noWaitAfter: true }
  );
}

export async function checkForErrors(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const errorElements = Array.from(
      document.querySelectorAll('.error, [class*="error"], [id*="error"]')
    );
    return errorElements.map(el => el.textContent || '').filter(Boolean);
  });
}

export async function storeLogin(page: Page, email: string, password: string) {
  await page.goto('/#/store/login');
  await page.waitForLoadState('domcontentloaded');
  
  // Wait for and fill login form
  await expect(page.getByTestId('store-login-email')).toBeVisible();
  await page.getByTestId('store-login-email').fill(email);
  await page.getByTestId('store-login-password').fill(password);
  await page.getByTestId('store-login-submit').click();
  
  // Wait for redirect to dashboard
  await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
}

export async function storeLogout(page: Page) {
  await page.getByTestId('store-logout-btn').click();
  await page.waitForURL('**/#/store/login', { timeout: 10000 });
}

export async function navigateToStoreTab(page: Page, tabId: string) {
  await page.getByTestId(`store-tab-${tabId}`).click();
  await page.waitForLoadState('domcontentloaded');
}

export const TEST_CREDENTIALS = {
  storeUser1: {
    email: 'manager@mgroad.adityaretail.com',
    password: 'store123'
  },
  storeUser2: {
    email: 'testmanager@tst001.adityaretail.com',
    password: 'test123'
  },
  // New credentials from test request
  armStore: {
    email: 'manager@arm.adityaretail.com',
    password: 'store123',
    storeName: 'Bosch Malleswaram',
    storeCode: 'ARM'
  },
  bnsStore: {
    email: 'manager@bns.adityaretail.com',
    password: 'store123',
    storeName: 'Banaswadi Store (BNS)',
    storeCode: 'BNS'
  },
  warehouse: {
    email: 'manager@warehouse.adityaretail.com',
    password: 'store123',
    storeName: 'Warehouse',
    storeCode: 'ARP',
    isWarehouse: true
  },
  admin: {
    email: 'admin@adityaretail.com',
    password: 'admin123'
  }
};

export async function adminLogin(page: Page, email: string, password: string) {
  await page.goto('/#/admin/login');
  await page.waitForLoadState('domcontentloaded');
  
  // Fill login form
  await page.locator('input[type="email"]').fill(email);
  await page.locator('input[type="password"]').fill(password);
  await page.locator('button[type="submit"]').click();
  
  // Wait for redirect to admin dashboard
  await page.waitForURL('**/#/admin/**', { timeout: 15000 });
}
