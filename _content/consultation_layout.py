"""Shared, compact appointment panel for clinic and consultation introductions."""
from html import escape
from pathlib import Path
import re


def appointment_panel(lang, clinic='sodeco', details=None):
    ar = lang == 'ar'
    base = '/ar/' if ar else '/'
    doctor = 'الدكتور محمد منعم' if ar else 'Dr. Mohamad Minhem'
    specialty = 'أمراض الدم والأورام' if ar else 'Hematology & oncology'
    name = ('عيادة سوديكو' if clinic == 'sodeco' else 'عيادة الطيونة') if ar else ('Sodeco Clinic' if clinic == 'sodeco' else 'Tayouneh Clinic')
    booking = ('اطلب استشارة في ' + name) if ar else ('Request a consultation at ' + name)
    location = 'بيروت · بموعد مسبق' if ar else 'Beirut · By appointment'
    call = 'اتصل' if ar else 'Call'
    details_label = 'العنوان والمواعيد' if ar else 'Clinic details & appointments'
    label = 'طلب موعد للاستشارة' if ar else 'Arrange a consultation'
    details = details or base + clinic + '.html'
    return f'''<aside class="appointmentPanel" aria-label="{label}">
      <div class="doctorIdentity"><picture><source type="image/webp" srcset="/portrait-480.webp"><img src="/portrait.jpg" alt="{doctor}" width="1195" height="1316" decoding="async"></picture><div><p class="doctorName">{doctor}</p><p class="doctorSpecialty">{specialty}</p></div></div>
      <div class="actions"><a class="button whatsapp" href="/booking.html?clinic={clinic}&amp;lang={lang}" target="_blank" rel="noopener">{booking}</a></div>
      <p class="clinicLocation">{location}</p>
      <!-- VIDEO_OPTION_ANCHOR -->
      <div class="appointmentUtility"><a href="tel:+96181902903" data-track="contact_phone">{call} <span class="phoneLtr">+961 81 902 903</span></a><a href="{escape(details, quote=True)}">{details_label}</a></div>
    </aside>'''


def refresh_static_pages():
    """Retain each authored introduction while keeping its appointment panel in sync."""
    root = Path(__file__).resolve().parents[1]
    for lang in ['en', 'ar']:
        base = 'ar/' if lang == 'ar' else ''
        for name in ['cancer-consultation', 'blood-cancer-consultation', 'sodeco', 'tayouneh']:
            page = root / (base + name + '.html')
            text = page.read_text()
            match = re.search(r'<header class="hero consultationHero">.*?</header>', text, re.S)
            assert match, f'Missing consultation header in {page}'
            title = re.search(r'<h1>(.*?)</h1>', match[0], re.S)[1]
            lead = re.search(r'<p class="lead">(.*?)</p>', match[0], re.S)[1]
            is_clinic = name in {'sodeco', 'tayouneh'}
            clinic = name if is_clinic else 'sodeco'
            label = 'الرئيسية والعيادات' if lang == 'ar' else 'Home & clinics'
            panel = appointment_panel(lang, clinic, '#main' if is_clinic else '#locations')
            header = f'<header class="hero consultationHero"><div class="wrap heroGrid"><div class="heroCopy"><a class="backLink" href="/{base}#contact-{lang}">{label}</a><h1>{title}</h1><p class="lead">{lead}</p></div>{panel}</div></header>'
            page.write_text(text[:match.start()] + header + text[match.end():])
