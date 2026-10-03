// Stable language URLs work without JavaScript. Resolve old query/hash links only.
(function () {
  const url = new URL(window.location.href);
  const arabic = url.pathname.startsWith('/ar/');
  const page = url.pathname.replace(/^\/ar\//, '/').replace(/\/index\.html$/, '/');
  const pages = ["/", "/sodeco.html", "/tayouneh.html", "/cancer-consultation.html", "/blood-cancer-consultation.html", "/breast-cancer.html", "/lung-cancer.html", "/colorectal-cancer.html", "/prostate-cancer.html", "/bladder-cancer.html", "/stomach-cancer.html", "/lymphoma.html", "/leukemia.html", "/multiple-myeloma.html", "/pancreatic-cancer.html", "/biopsy-cancer-spread.html", "/chemotherapy-benefits-risks.html", "/immunotherapy-candidacy.html", "/oral-cancer-treatment.html", "/targeted-therapy.html", "/cancer-genetic-testing.html", "/nutrition-during-cancer-treatment.html", "/diet-cancer-prevention.html", "/cancer-symptoms.html", "/cancer-screening.html", "/non-cancer-blood-conditions.html", "/easy-bruising.html", "/patient-guides.html"];
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
