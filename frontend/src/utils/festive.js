// Seasonal/sale themes keep the default brand colours; only festivals get the festive layer
const NON_FESTIVE = /^(summer|monsoon|winter|spring|autumn|month|season)/i;

// Master switch: false = normal site theme everywhere; set true to bring festival themes back
export const FESTIVE_ENABLED = false;

export const isFestive = (theme) =>
  FESTIVE_ENABLED && !!(theme && theme.name && !NON_FESTIVE.test(theme.name));

export const greeting = (theme) =>
  theme.subtitle ? `${theme.title} · ${theme.subtitle}` : theme.title;

const DECOR = {
  new_year: ['🎊', '✨'], pongal: ['🌾', '🌻'], republic_day: ['🇮🇳'], valentines: ['💝'],
  holi: ['🎨', '🌈'], ugadi: ['🌸'], akshaya_tritiya: ['✨', '🪙'], mothers_day: ['💐'],
  fathers_day: ['👔'], independence_day: ['🇮🇳'], raksha_bandhan: ['🎁'],
  ganesh_chaturthi: ['🙏', '🌺'], onam: ['🌼'], navratri: ['🔱', '🪔'], dussehra: ['🏹', '🪔'],
  diwali: ['🪔', '✨'], black_friday: ['🖤'], christmas: ['🎄', '⭐'], year_end: ['🎉']
};

export const decorFor = (theme) => {
  if (DECOR[theme.name]) return DECOR[theme.name];
  // Admin-created festival: reuse the emoji in its title
  return (theme.title || '').match(/\p{Extended_Pictographic}/gu) || [];
};
