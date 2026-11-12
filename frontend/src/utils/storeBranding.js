export const HEADER_TITLE = 'Aditya Retail';

export const STORE_HEADER_SUBTITLES = {
  DAS: 'Dasarahalli Bosch Brand Store',
  ARM: 'Malleswaram Bosch Brand Store',
  BNS: 'Banaswadi Siemens And Bosch Brand Store',
  ARH: 'Malleswaram Haier Experience Center',
  ART: 'RT Nagar Bosch Brand Store',
  HRBR: 'HRBR Electrolux Exclusive Store',
};

export function getStoreHeaderSubtitle(storeCode, docNumber = '') {
  let code = (storeCode || '').toUpperCase();
  if (!STORE_HEADER_SUBTITLES[code]) {
    code =
      Object.keys(STORE_HEADER_SUBTITLES)
        .sort((a, b) => b.length - a.length)
        .find((c) => (docNumber || '').toUpperCase().startsWith(c)) || '';
  }
  return STORE_HEADER_SUBTITLES[code] || '';
}
