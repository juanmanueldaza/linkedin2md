/**
 * Shared Analytics Configuration for daza.ar ecosystem (UMD)
 * Based on the ConsentManager pattern from wallpapers/linkedin2md/github2md
 *
 * Usage: <script src="/_shared/analytics-config.umd.js"></script>
 * Access via: window.DazaAnalytics
 *
 * Sites using this config (all under GA4 property: daza.ar / properties/521233901):
 *   - wallpapers.daza.ar          G-DBDHBPP6ZS
 *   - linkedin2md.daza.ar         G-KBXL3M8D5P
 *   - github2md.daza.ar           G-757KW9Y1RM
 *   - gitlab2md.daza.ar           G-D2DMNZMZQH
 *   - cv.daza.ar                  G-GWCZ0041FP
 *   - start.daza.ar               G-549QBGBBKS
 *   - onepager.daza.ar            G-99DHPDQ9VB
 *   - mdsite.daza.ar              G-KL32NMGJL4
 *   - navbar.daza.ar              G-L3JHQSC8TV
 *   - data.daza.ar                G-KL0NEYS6Z4
 *   - laboratoriodeprogramacioncreativa.daza.ar G-00HLR6S41M
 *   - spanishlessons.daza.ar      G-N3NJX0CR82
 */

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define([], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory();
  } else {
    root.DazaAnalytics = factory();
  }
}(typeof self !== 'undefined' ? self : this, function () {

  'use strict';

  // ============================================================
  // SITE REGISTRY — one entry per property
  // Each site gets its OWN GA4 property for clean data separation
  // ============================================================
  const SITE_REGISTRY = {
    // --- All sites use property: daza.ar / properties/521233901 ---
    wallpapers: {
      measurementId: 'G-DBDHBPP6ZS',
      propertyId: 'properties/521233901',
      name: 'wallpapers.daza.ar',
      domain: 'wallpapers.daza.ar',
      description: 'Analog wallpaper gallery',
    },
    linkedin2md: {
      measurementId: 'G-KBXL3M8D5P',
      propertyId: 'properties/521233901',
      name: 'linkedin2md.daza.ar',
      domain: 'linkedin2md.daza.ar',
      description: 'LinkedIn export to Markdown converter',
    },
    github2md: {
      measurementId: 'G-757KW9Y1RM',
      propertyId: 'properties/521233901',
      name: 'github2md.daza.ar',
      domain: 'github2md.daza.ar',
      description: 'GitHub export to Markdown converter',
    },
    gitlab2md: {
      measurementId: 'G-D2DMNZMZQH',
      propertyId: 'properties/521233901',
      name: 'gitlab2md.daza.ar',
      domain: 'gitlab2md.daza.ar',
      description: 'GitLab export to Markdown converter',
    },
    cv: {
      measurementId: 'G-GWCZ0041FP',
      propertyId: 'properties/521233901',
      name: 'cv.daza.ar',
      domain: 'cv.daza.ar',
      description: 'Personal CV/portfolio',
    },
    start: {
      measurementId: 'G-549QBGBBKS',
      propertyId: 'properties/521233901',
      name: 'start.daza.ar',
      domain: 'start.daza.ar',
      description: 'Startup landing page',
    },
    onepager: {
      measurementId: 'G-99DHPDQ9VB',
      propertyId: 'properties/521233901',
      name: 'onepager.daza.ar',
      domain: 'onepager.daza.ar',
      description: 'One-pager site builder',
    },
    mdsite: {
      measurementId: 'G-KL32NMGJL4',
      propertyId: 'properties/521233901',
      name: 'mdsite.daza.ar',
      domain: 'mdsite.daza.ar',
      description: 'Markdown site renderer',
    },
    navbar: {
      measurementId: 'G-L3JHQSC8TV',
      propertyId: 'properties/521233901',
      name: 'navbar.daza.ar',
      domain: 'navbar.daza.ar',
      description: 'Reusable navbar component',
    },
    data: {
      measurementId: 'G-KL0NEYS6Z4',
      propertyId: 'properties/521233901',
      name: 'data.daza.ar',
      domain: 'data.daza.ar',
      description: 'Shared data server',
    },
    laboratoriodeprogramacioncreativa: {
      measurementId: 'G-00HLR6S41M',
      propertyId: 'properties/521233901',
      name: 'laboratoriodeprogramacioncreativa.daza.ar',
      domain: 'laboratoriodeprogramacioncreativa.daza.ar',
      description: 'Creative programming lab',
    },
    spanishlessons: {
      measurementId: 'G-N3NJX0CR82',
      propertyId: 'properties/521233901',
      name: 'spanishlessons.daza.ar',
      domain: 'spanishlessons.daza.ar',
      description: 'Spanish lessons site',
    },
  };

  // ============================================================
  // CONSENT MODE v2 — default deny, update on user choice
  // GDPR compliant — matches existing ConsentManager pattern
  // ============================================================
  function initConsentDefault() {
    window.dataLayer = window.dataLayer || [];
    function gtag() { dataLayer.push(arguments); }

    gtag('consent', 'default', {
      'ad_storage': 'denied',
      'ad_user_data': 'denied',
      'ad_personalization': 'denied',
      'analytics_storage': 'denied',
    });

    gtag('js', new Date());
    return gtag;
  }

  // Update consent when user accepts/rejects
  function updateConsent(granted) {
    if (typeof gtag === 'undefined') return;
    const state = granted ? 'granted' : 'denied';
    window.gtag('consent', 'update', {
      'ad_storage': state,
      'ad_user_data': state,
      'ad_personalization': state,
      'analytics_storage': state,
    });
  }

  // ============================================================
  // BOOTSTRAP — init GA4 for a specific site
  // ============================================================
  function bootstrap(siteKey) {
    const site = SITE_REGISTRY[siteKey];
    if (!site) {
      console.error('[DazaAnalytics] Unknown site key:', siteKey);
      return;
    }

    if (!site.measurementId) {
      console.error('[DazaAnalytics] No measurementId for', siteKey, '- skipping GA4 init');
      return;
    }

    const gtag = initConsentDefault();

    gtag('config', site.measurementId, {
      'cookie_flags': 'SameSite=None;Secure',
      'send_page_view': true,
      // 'cross_domain': ['wallpapers.daza.ar', 'data.daza.ar'], // fill per site
    });

    // Load GTM script asynchronously
    const script = document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${site.measurementId}`;
    document.head.appendChild(script);

    console.log(`[DazaAnalytics] Initialized for ${siteKey} (${site.measurementId})`);
  }

  // ============================================================
  // EVENT HELPERS — fire events from any page
  // ============================================================

  /**
   * Track a page view (automatic in GA4, but lets you add custom params)
   */
  function trackPageView(title, path) {
    if (typeof gtag === 'undefined') return;
    window.gtag('event', 'page_view', {
      page_title: title || document.title,
      page_location: path || window.location.href,
    });
  }

  /**
   * Track a custom event
   * @param {string} name - Event name (use snake_case, no G- prefix)
   * @param {object} params - Event parameters
   */
  function trackEvent(name, params) {
    if (typeof gtag === 'undefined') return;
    window.gtag('event', name, params || {});
  }

  // Convenience methods for common events
  const events = {
    // --- Content engagement ---
    download: function(fileType, fileName, fileUrl) {
      trackEvent('file_download', {
        file_type: fileType,
        file_name: fileName,
        file_url: fileUrl,
      });
    },
    externalLink: function(linkUrl, linkText) {
      trackEvent('click_external_link', {
        link_url: linkUrl,
        link_text: linkText || '',
      });
    },
    outboundClick: function(destination, destinationName) {
      trackEvent('outbound_click', {
        destination: destination,
        destination_name: destinationName || '',
      });
    },

    // --- User actions ---
    ctaClick: function(ctaId, ctaLabel, ctaDestination) {
      trackEvent('cta_click', {
        cta_id: ctaId,
        cta_label: ctaLabel,
        cta_destination: ctaDestination || '',
      });
    },
    formSubmit: function(formId, formName) {
      trackEvent('form_submit', {
        form_id: formId,
        form_name: formName || '',
      });
    },
    searchQuery: function(searchTerm, searchResults) {
      trackEvent('search', {
        search_term: searchTerm,
        number_of_results: searchResults || 0,
      });
    },
    videoPlay: function(videoId, videoTitle) {
      trackEvent('video_play', {
        video_id: videoId,
        video_title: videoTitle || '',
      });
    },
    videoComplete: function(videoId, videoTitle) {
      trackEvent('video_complete', {
        video_id: videoId,
        video_title: videoTitle || '',
      });
    },

    // --- Tool-specific events ---
    toolExport: function(toolName, exportFormat, exportSize) {
      trackEvent('tool_export', {
        tool_name: toolName,
        export_format: exportFormat,
        export_size_kb: exportSize || 0,
      });
    },
    toolConversion: function(toolName, conversionStep) {
      trackEvent('tool_conversion', {
        tool_name: toolName,
        conversion_step: conversionStep,
      });
    },

    // --- Error tracking ---
    jsError: function(errorMessage, errorFatal) {
      trackEvent('exception', {
        description: errorMessage,
        fatal: errorFatal || false,
      });
    },
    cspViolation: function(violatedDirective, blockedURI) {
      trackEvent('csp_violation', {
        violated_directive: violatedDirective,
        blocked_uri: blockedURI || '',
      });
    },
  };

  // ============================================================
  // AUTOMATIC EVENT LISTENERS — enhance without code changes
  // ============================================================
  function initAutoTrackers() {
    if (typeof document === 'undefined') return;

    // File downloads
    document.addEventListener('click', function(e) {
      const link = e.target.closest('a[href]');
      if (!link) return;

      const href = link.getAttribute('href');
      const fileExts = ['.pdf', '.zip', '.tar', '.gz', '.doc', '.docx',
                         '.xls', '.xlsx', '.ppt', '.pptx', '.md', '.txt'];
      const isFile = fileExts.some(ext => href.toLowerCase().includes(ext));
      const isExternal = link.hostname && link.hostname !== window.location.hostname;

      if (isFile) {
        const fileName = href.split('/').pop();
        const fileType = fileName.split('.').pop();
        events.download(fileType, fileName, href);
      } else if (isExternal) {
        events.externalLink(href, link.textContent.trim());
      }
    });

    // Form submissions
    document.addEventListener('submit', function(e) {
      const form = e.target;
      if (form.id) {
        events.formSubmit(form.id, form.name || form.id);
      }
    });

    // JS errors
    window.addEventListener('error', function(e) {
      events.jsError(e.error?.message || e.message, false);
    });

    // CSP violations
    document.addEventListener('securitypolicyviolation', function(e) {
      events.cspViolation(e.violatedDirective, e.blockedURI);
    });
  }

  // ============================================================
  // CONSENT MANAGER — matches existing ConsentManager pattern
  // ============================================================
  const ConsentManager = {
    STORAGE_KEY: 'cookie_consent',

    init: function() {
      const consent = this.getConsent();
      if (consent === null) {
        this.showBanner();
      } else {
        this.applyConsent(consent);
      }
      this.bindEvents();
    },

    getConsent: function() {
      const s = localStorage.getItem(this.STORAGE_KEY);
      return s === null ? null : s === 'granted';
    },

    setConsent: function(granted) {
      localStorage.setItem(this.STORAGE_KEY, granted ? 'granted' : 'denied');
      this.applyConsent(granted);
      this.hideBanner();
    },

    applyConsent: function(granted) {
      updateConsent(granted);
    },

    showBanner: function() {
      const banner = document.getElementById('cookie-banner');
      if (banner) banner.hidden = false;
    },

    hideBanner: function() {
      const banner = document.getElementById('cookie-banner');
      if (banner) banner.hidden = true;
    },

    bindEvents: function() {
      document.getElementById('cookie-accept')?.addEventListener('click', () => this.setConsent(true));
      document.getElementById('cookie-reject')?.addEventListener('click', () => this.setConsent(false));
      document.getElementById('cookie-settings')?.addEventListener('click', () => this.showBanner());
    },
  };

  // ============================================================
  // PUBLIC API
  // ============================================================
  return {
    // Bootstrap GA4 for a site (call once per page load)
    bootstrap: bootstrap,

    // Event tracking
    trackEvent: trackEvent,
    trackPageView: trackPageView,
    events: events,

    // Consent management
    ConsentManager: ConsentManager,

    // Auto-install event listeners
    initAutoTrackers: initAutoTrackers,

    // Site registry access
    getSiteConfig: function(siteKey) {
      return SITE_REGISTRY[siteKey] || null;
    },

    getAllSites: function() {
      return Object.keys(SITE_REGISTRY);
    },
  };

}));