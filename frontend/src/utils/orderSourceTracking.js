/**
 * Order Source Tracking Utility
 * Captures UTM parameters, referrer, and other source information
 */

// Source types
export const ORDER_SOURCES = {
  ORGANIC_GOOGLE: 'Organic Google',
  ORGANIC_BING: 'Organic Bing',
  DIRECT: 'Direct',
  GOOGLE_ADS: 'Google Ads',
  FACEBOOK_ADS: 'Facebook Ads',
  INSTAGRAM_ADS: 'Instagram Ads',
  CHATGPT: 'ChatGPT',
  WHATSAPP: 'WhatsApp',
  PHONE_CALL: 'Phone Call',
  WALK_IN: 'Walk-in',
  OFFLINE_STORE: 'Offline Store',
  REFERRAL: 'Referral',
  EMAIL: 'Email Campaign',
  SMS: 'SMS Campaign',
  OTHER: 'Other'
};

// Parse UTM parameters from URL
export const getUTMParams = () => {
  const urlParams = new URLSearchParams(window.location.search);
  return {
    utm_source: urlParams.get('utm_source') || '',
    utm_medium: urlParams.get('utm_medium') || '',
    utm_campaign: urlParams.get('utm_campaign') || '',
    utm_term: urlParams.get('utm_term') || '',
    utm_content: urlParams.get('utm_content') || '',
    gclid: urlParams.get('gclid') || '',  // Google Click ID
    fbclid: urlParams.get('fbclid') || ''  // Facebook Click ID
  };
};

// Get referrer information
export const getReferrer = () => {
  const referrer = document.referrer;
  if (!referrer) return { referrer: '', referrer_domain: '' };
  
  try {
    const url = new URL(referrer);
    return {
      referrer: referrer,
      referrer_domain: url.hostname
    };
  } catch {
    return { referrer: referrer, referrer_domain: '' };
  }
};

// Determine order source from UTM and referrer
export const determineOrderSource = () => {
  const utmParams = getUTMParams();
  const { referrer, referrer_domain } = getReferrer();
  
  // Check for paid ads first (UTM or click IDs)
  if (utmParams.gclid) {
    return {
      source: ORDER_SOURCES.GOOGLE_ADS,
      source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
      ...utmParams,
      referrer,
      referrer_domain
    };
  }
  
  if (utmParams.fbclid) {
    return {
      source: ORDER_SOURCES.FACEBOOK_ADS,
      source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
      ...utmParams,
      referrer,
      referrer_domain
    };
  }
  
  if (utmParams.utm_source) {
    // Check UTM source
    const source = utmParams.utm_source.toLowerCase();
    const medium = utmParams.utm_medium?.toLowerCase() || '';
    
    if (source.includes('google') && medium === 'cpc') {
      return {
        source: ORDER_SOURCES.GOOGLE_ADS,
        source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (source.includes('facebook') || source.includes('fb')) {
      return {
        source: medium === 'cpc' || medium === 'paid' ? ORDER_SOURCES.FACEBOOK_ADS : ORDER_SOURCES.REFERRAL,
        source_detail: `Referral: ${utmParams.utm_source}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (source.includes('instagram')) {
      return {
        source: ORDER_SOURCES.INSTAGRAM_ADS,
        source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (source.includes('email') || medium === 'email') {
      return {
        source: ORDER_SOURCES.EMAIL,
        source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (source.includes('sms') || medium === 'sms') {
      return {
        source: ORDER_SOURCES.SMS,
        source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (source.includes('whatsapp')) {
      return {
        source: ORDER_SOURCES.WHATSAPP,
        source_detail: `Campaign: ${utmParams.utm_campaign || 'Unknown'}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    return {
      source: ORDER_SOURCES.REFERRAL,
      source_detail: `Source: ${utmParams.utm_source}`,
      ...utmParams,
      referrer,
      referrer_domain
    };
  }
  
  // No UTM, check referrer
  if (referrer_domain) {
    if (referrer_domain.includes('google')) {
      return {
        source: ORDER_SOURCES.ORGANIC_GOOGLE,
        source_detail: `Referral: ${referrer_domain}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (referrer_domain.includes('bing')) {
      return {
        source: ORDER_SOURCES.ORGANIC_BING,
        source_detail: `Referral: ${referrer_domain}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (referrer_domain.includes('chatgpt') || referrer_domain.includes('openai')) {
      return {
        source: ORDER_SOURCES.CHATGPT,
        source_detail: `Source: ${referrer_domain}`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (referrer_domain.includes('facebook') || referrer_domain.includes('fb.com')) {
      return {
        source: ORDER_SOURCES.REFERRAL,
        source_detail: `Referral: Facebook`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (referrer_domain.includes('instagram')) {
      return {
        source: ORDER_SOURCES.REFERRAL,
        source_detail: `Referral: Instagram`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    if (referrer_domain.includes('whatsapp')) {
      return {
        source: ORDER_SOURCES.WHATSAPP,
        source_detail: `Referral: WhatsApp`,
        ...utmParams,
        referrer,
        referrer_domain
      };
    }
    
    // Other referral
    return {
      source: ORDER_SOURCES.REFERRAL,
      source_detail: `Referral: ${referrer_domain}`,
      ...utmParams,
      referrer,
      referrer_domain
    };
  }
  
  // No referrer - Direct traffic
  return {
    source: ORDER_SOURCES.DIRECT,
    source_detail: 'Direct visit',
    ...utmParams,
    referrer: '',
    referrer_domain: ''
  };
};

// Store tracking data in sessionStorage (persists during session)
export const storeTrackingData = () => {
  // Only store if not already stored (keep the first touch)
  if (!sessionStorage.getItem('order_source_data')) {
    const sourceData = determineOrderSource();
    sourceData.first_visit_time = new Date().toISOString();
    sourceData.landing_page = window.location.href;
    sessionStorage.setItem('order_source_data', JSON.stringify(sourceData));
  }
};

// Get stored tracking data
export const getStoredTrackingData = () => {
  const data = sessionStorage.getItem('order_source_data');
  if (data) {
    return JSON.parse(data);
  }
  // If not stored, determine now
  return determineOrderSource();
};

// For offline/manual orders
export const getManualSourceData = (source, sourceDetail = '') => {
  return {
    source: source,
    source_detail: sourceDetail || source,
    utm_source: '',
    utm_medium: '',
    utm_campaign: '',
    utm_term: '',
    utm_content: '',
    gclid: '',
    fbclid: '',
    referrer: '',
    referrer_domain: '',
    is_manual: true
  };
};

export default {
  ORDER_SOURCES,
  getUTMParams,
  getReferrer,
  determineOrderSource,
  storeTrackingData,
  getStoredTrackingData,
  getManualSourceData
};
