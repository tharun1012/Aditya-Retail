// Large appliance categories that qualify for:
//   • Brand-provided installation badge
//   • Extended delivery options
//   • Bangalore-priority COD (legacy)
export const LARGE_APPLIANCE_CATEGORIES = [
  'hob',
  'chimney',
  'oven',
  'microwave',
  'dishwasher',
  'refrigerator',
  'refrigerators',
  'dryer',
  'washing machine',
  'washing machines',
  'robotic vacuum cleaner',
  'robotic vacuum cleaners',
  'led tv',
  "led tv's",
  'tv',
  'air conditioner',
  'air conditioners',
  "ac",
  "ac's",
  'induction',
  'coffee machine',
  'coffee machines',
];

export const isLargeAppliance = (product) => {
  if (!product) return false;
  if (product.is_large_appliance === true) return true;
  if (product.is_large_appliance === false) return false; // explicit admin override
  const cat = (product.category || '').toLowerCase().trim();
  const subcat = (product.subcategory || '').toLowerCase().trim();
  return LARGE_APPLIANCE_CATEGORIES.includes(cat) || LARGE_APPLIANCE_CATEGORIES.includes(subcat);
};
