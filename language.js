// Stable language URLs work without JavaScript. Resolve old query/hash links only.
(function () {
  const url = new URL(window.location.href);
  const arabic = url.pathname.startsWith('/ar/');
  const page = url.pathname.replace(/^\/ar\//, '/').replace(/\/index\.html$/, '/');
  const pages = ['/', '/sodeco.html', '/tayouneh.html', '/cancer-consultation.html', '/blood-cancer-consultation.html'];
  if (!pages.includes(page)) return;
  const requested = url.searchParams.get('lang');
  const legacyAnchor = page === '/' && /^#(?:top|care|contact|recognition|background|academic)-(en|ar)$/.exec(url.hash);
  const lang = requested === 'en' || requested === 'ar' ? requested : (legacyAnchor ? legacyAnchor[1] : (arabic ? 'ar' : 'en'));
  const target = (lang === 'ar' ? '/ar' : '') + page;
  if (target !== url.pathname || requested) {
    const safeAnchor = /^#(?:top|care|contact|recognition|background|academic)-(?:en|ar)$/.test(url.hash)
      ? url.hash.replace(/-(en|ar)$/, '-' + lang) : '';
    window.location.replace(target + safeAnchor);
  }
})();
