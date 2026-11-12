const fs = require('fs');
const path = require('path');
const file = path.join(__dirname, '..', 'node_modules', 'react-snap', 'src', 'puppeteer_utils.js');
const content = fs.readFileSync(file, 'utf8');
const patched = content.replace(
  'await page.goto(pageUrl, { waitUntil: "networkidle0" });',
  'await page.goto(pageUrl, { waitUntil: "networkidle2", timeout: 60000 });'
);
if (patched !== content) {
  fs.writeFileSync(file, patched);
  console.log('Patched react-snap timeout/waitUntil strategy');
} else {
  console.log('react-snap already patched or pattern not found');
}
