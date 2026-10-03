// Certificate links retain a direct-image fallback when dialogs are unavailable.
    const certificateDialog = document.getElementById('certificate-dialog');
    if (typeof certificateDialog?.showModal === 'function') {
      let certificateOpener;
      let previousBodyOverflow;
      document.querySelectorAll('[data-certificate]').forEach(link => {
        link.setAttribute('aria-haspopup', 'dialog');
        link.setAttribute('aria-controls', 'certificate-dialog');
        link.addEventListener('click', event => {
          if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          const isAr = link.dataset.certificate === 'ar';
          certificateDialog.lang = isAr ? 'ar' : 'en';
          certificateDialog.dir = isAr ? 'rtl' : 'ltr';
          document.getElementById('certificate-dialog-title').textContent = isAr ? 'شهادة تقدير للإنجاز المتميّز' : 'Certificate of Distinguished Achievement';
          document.getElementById('certificate-close-label').textContent = isAr ? 'إغلاق' : 'Close';
          certificateDialog.querySelector('.certificateFull').textContent = isAr ? 'فتح الصورة بالحجم الكامل' : 'Open full-size image';
          certificateDialog.querySelector('img').alt = document.querySelector('#balamand-award-' + link.dataset.certificate + ' img').alt;
          certificateOpener = link;
          previousBodyOverflow = document.body.style.overflow;
          document.body.style.overflow = 'hidden';
          certificateDialog.showModal();
        });
      });
      certificateDialog.addEventListener('close', () => {
        document.body.style.overflow = previousBodyOverflow;
        certificateOpener?.focus({ preventScroll:true });
      });
      certificateDialog.addEventListener('click', event => {
        if (event.target !== certificateDialog) return;
        const bounds = certificateDialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) certificateDialog.close();
      });
    }

    // Year
    const year = new Date().getFullYear();
    const y = document.getElementById('y');
    const yAr = document.getElementById('yAr');
    if (y) y.textContent = year;
    if (yAr) yAr.textContent = year;

    // Put patient decisions first while keeping the complete credentials and research sections.
    function prioritizePatientSections(lang){
      const main = document.querySelector('#' + lang + ' main');
      const recognition = document.getElementById('recognition-' + lang);
      const care = document.getElementById('care-' + lang);
      const contact = document.getElementById('contact-' + lang);
      if (!main || !recognition || !care || !contact) return;
      main.insertBefore(care, recognition);
      main.insertBefore(contact, recognition);
    }
    prioritizePatientSections('en');
    prioritizePatientSections('ar');

    function syncRtlArrows(){
      const isAr = document.body.getAttribute('data-lang') === 'ar';
      const uses = document.querySelectorAll('use[href="#i-arrow"], use[xlink\\:href="#i-arrow"]');
      uses.forEach(u => {
        const svg = u.closest('svg');
        if (!svg) return;
        svg.style.transform = isAr ? 'scaleX(-1)' : '';
        svg.style.transformOrigin = 'center';
        svg.style.display = 'inline-block';
      });
    }
    // Keep direct links accurate after the patient-first section reordering.
    let initialTargetId = '';
    try { initialTargetId = decodeURIComponent(window.location.hash.slice(1)); } catch (_) {}
    if (initialTargetId) {
      const scrollToInitialTarget = () => window.setTimeout(() => requestAnimationFrame(() => {
        document.getElementById(initialTargetId)?.scrollIntoView({ block: 'start' });
      }), 0);
      const settleInitialTarget = () => (document.fonts?.ready || Promise.resolve()).then(scrollToInitialTarget);
      if (document.readyState === 'complete') settleInitialTarget();
      else window.addEventListener('load', settleInitialTarget, { once: true });
    }


    // On phones, show one booking action at a time: the in-page action first,
    // then the sticky shortcut only after that action has scrolled away.
    function updateMobileBookingBars(){
      const isMobile = window.matchMedia('(max-width: 720px)').matches;
      const topbarBottom = document.querySelector('.topbar')?.getBoundingClientRect().bottom || 0;
      document.querySelectorAll('#en, #ar').forEach(pane => {
        const bar = pane.querySelector('.mobileBookingBar');
        const heroActions = pane.querySelector('.hero .ctaRow');
        if (!bar || !heroActions || !isMobile || getComputedStyle(pane).display === 'none') {
          bar?.classList.remove('is-visible');
          return;
        }

        const heroActionsRect = heroActions.getBoundingClientRect();
        const passedHeroAction = heroActionsRect.bottom < topbarBottom + 8;
        const conflictVisible = [...pane.querySelectorAll('.clinicGrid, .closingContact')].some(section => {
          const rect = section.getBoundingClientRect();
          return rect.top < window.innerHeight - 68 && rect.bottom > topbarBottom;
        });
        bar.classList.toggle('is-visible', passedHeroAction && !conflictVisible);
      });
    }

    let mobileBookingFrame = 0;
    function scheduleMobileBookingUpdate(){
      if (mobileBookingFrame) return;
      mobileBookingFrame = requestAnimationFrame(() => {
        mobileBookingFrame = 0;
        updateMobileBookingBars();
      });
    }
    window.addEventListener('scroll', scheduleMobileBookingUpdate, { passive:true });
    window.addEventListener('resize', scheduleMobileBookingUpdate);
    window.addEventListener('load', scheduleMobileBookingUpdate, { once:true });

    // Contact-click intent only; booking.html measures opening WhatsApp, not a completed consultation.
    document.querySelectorAll('[data-track]').forEach(link => {
      link.addEventListener('click', () => {
        if (typeof gtag !== 'function') return;
        gtag('event', link.dataset.track, {
          clinic_location: link.dataset.clinic || 'general',
          contact_channel: link.dataset.track.replace('contact_', ''),
          site_language: document.body.getAttribute('data-lang') || 'en'
        });
      });
    });

    // Mobile menus
    const menuBtn = document.getElementById('menuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    const menuBtnAr = document.getElementById('menuBtnAr');
    const mobileMenuAr = document.getElementById('mobileMenuAr');

    menuBtn?.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = mobileMenu.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', String(open));
    });
    mobileMenu?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      mobileMenu.classList.remove('open');
      menuBtn?.setAttribute('aria-expanded','false');
    }));
    menuBtnAr?.addEventListener('click', (e) => {
      e.stopPropagation();
      const open = mobileMenuAr.classList.toggle('open');
      menuBtnAr.setAttribute('aria-expanded', String(open));
    });
    mobileMenuAr?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      mobileMenuAr.classList.remove('open');
      menuBtnAr?.setAttribute('aria-expanded','false');
    }));

    document.addEventListener('click', (e) => {
      const withinEn = mobileMenu?.contains(e.target) || menuBtn?.contains(e.target);
      const withinAr = mobileMenuAr?.contains(e.target) || menuBtnAr?.contains(e.target);
      if (mobileMenu?.classList.contains('open') && !withinEn){ mobileMenu.classList.remove('open'); menuBtn?.setAttribute('aria-expanded','false'); }
      if (mobileMenuAr?.classList.contains('open') && !withinAr){ mobileMenuAr.classList.remove('open'); menuBtnAr?.setAttribute('aria-expanded','false'); }
    });

    syncRtlArrows();

    // Scroll reveal
    (function(){
      const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const els = document.querySelectorAll('.reveal');
      if (reduce || !('IntersectionObserver' in window)){
        els.forEach(el => el.classList.add('in'));
        return;
      }
      const io = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting){ entry.target.classList.add('in'); io.unobserve(entry.target); }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });
      els.forEach(el => io.observe(el));
    })();

    document.addEventListener('keydown', event => {
      if (event.key !== 'Escape') return;
      [[menuBtn,mobileMenu],[menuBtnAr,mobileMenuAr]].forEach(([button,menu]) => {
        if (!menu?.classList.contains('open')) return;
        menu.classList.remove('open'); button?.setAttribute('aria-expanded','false'); button?.focus();
      });
    });
