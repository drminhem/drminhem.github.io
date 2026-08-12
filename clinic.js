(function(){
  const body = document.body;
  const params = new URLSearchParams(window.location.search);
  const requested = params.get('lang');
  const saved = localStorage.getItem('site_lang');

  function setLanguage(lang){
    const language = lang === 'ar' ? 'ar' : 'en';
    body.dataset.lang = language;
    document.documentElement.lang = language;
    document.documentElement.dir = language === 'ar' ? 'rtl' : 'ltr';
    document.querySelectorAll('[data-language-label]').forEach(el => {
      el.textContent = language === 'ar' ? 'English' : 'العربية';
    });
    localStorage.setItem('site_lang',language);
  }

  setLanguage(requested === 'ar' || requested === 'en' ? requested : (saved || 'en'));

  document.querySelectorAll('[data-language-toggle]').forEach(button => {
    button.addEventListener('click',() => setLanguage(body.dataset.lang === 'ar' ? 'en' : 'ar'));
  });

  document.querySelectorAll('[data-track]').forEach(link => {
    link.addEventListener('click',() => {
      if (typeof gtag !== 'function') return;
      gtag('event',link.dataset.track,{
        clinic_location:body.dataset.clinic || 'general',
        contact_channel:link.dataset.track.replace('contact_',''),
        site_language:body.dataset.lang || 'en'
      });
    });
  });
})();
