(function () {
  // Language is authored in the HTML and selected through ordinary links.
  document.querySelectorAll('[data-track]').forEach(link => {
    link.addEventListener('click', () => {
      if (typeof gtag !== 'function') return;
      gtag('event', link.dataset.track, {
        clinic_location: document.body.dataset.clinic || 'general',
        contact_channel: link.dataset.track.replace('contact_', ''),
        site_language: document.documentElement.lang
      });
    });
  });
  document.querySelectorAll('[data-year]').forEach(el => el.textContent = new Date().getFullYear());
})();
