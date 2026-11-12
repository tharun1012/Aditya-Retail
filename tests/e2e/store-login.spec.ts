import { test, expect } from '@playwright/test';
import { TEST_CREDENTIALS, waitForAppReady, dismissToasts } from '../fixtures/helpers';

test.describe('Store Login', () => {
  
  test.beforeEach(async ({ page }) => {
    await dismissToasts(page);
  });

  test('Store login page loads correctly', async ({ page }) => {
    await page.goto('/#/store/login');
    await waitForAppReady(page);
    
    await expect(page.getByTestId('store-login-email')).toBeVisible();
    await expect(page.getByTestId('store-login-password')).toBeVisible();
    await expect(page.getByTestId('store-login-submit')).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Store Portal' })).toBeVisible();
    await expect(page.getByText('Store Manager Login')).toBeVisible();
  });

  test('Store login with valid credentials (ARM)', async ({ page }) => {
    await page.goto('/#/store/login');
    await waitForAppReady(page);
    
    await page.getByTestId('store-login-email').fill(TEST_CREDENTIALS.armStore.email);
    await page.getByTestId('store-login-password').fill(TEST_CREDENTIALS.armStore.password);
    await page.getByTestId('store-login-submit').click();
    
    await page.waitForURL('**/#/store/dashboard', { timeout: 15000 });
    await expect(page.getByText('Malleswaram Store (ARM)')).toBeVisible({ timeout: 10000 });
  });

  test('Store login with invalid credentials shows error', async ({ page }) => {
    await page.goto('/#/store/login');
    await waitForAppReady(page);
    
    await page.getByTestId('store-login-email').fill('invalid@test.com');
    await page.getByTestId('store-login-password').fill('wrongpassword');
    await page.getByTestId('store-login-submit').click();
    
    await expect(page.getByText(/Invalid credentials|User not found|Store user not found/i)).toBeVisible({ timeout: 10000 });
    await expect(page).toHaveURL(/.*\/#\/store\/login/);
  });
});
