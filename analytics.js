// Keep the existing GA4 property. These events measure contact intent, never consultations.
// Do not forward arbitrary query strings, fragments, referrer paths, or message content.
window.dataLayer = window.dataLayer || [];
window.gtag = function () { window.dataLayer.push(arguments); };
(function () {
  const production = ['drminhem.com', 'www.drminhem.com'].includes(window.location.hostname);
  const preview = new URLSearchParams(window.location.search).get('preview') === '1';
  if (!production || preview) return;
  const tag = document.createElement('script');
  tag.async = true;
  tag.src = 'https://www.googletagmanager.com/gtag/js?id=G-B46GF8Q2KX';
  document.head.appendChild(tag);
  let referrer = '';
  try { if (document.referrer) referrer = new URL(document.referrer).origin + '/'; } catch (_) {}
  gtag('js', new Date());
  gtag('config', 'G-B46GF8Q2KX', {
    page_location: window.location.origin + window.location.pathname,
    page_referrer: referrer,
    page_title: document.title
  });
})();
