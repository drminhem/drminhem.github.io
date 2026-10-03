"""Keep the confirmed video-consultation option consistent across page layouts."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COPY = {
    'en': ('Outside Beirut? Video consultations are available.', 'Request a video consultation'),
    'ar': ('تتوفّر استشارات عبر الفيديو للمرضى خارج بيروت.', 'اطلب موعداً لاستشارة عبر الفيديو'),
}


def build(names):
    for lang in ['en', 'ar']:
        for name in names:
            page = ROOT / (('ar/' if lang == 'ar' else '') + (name or 'index.html'))
            text = page.read_text()
            text = re.sub(r'\n?<!-- VIDEO_OPTION_START -->.*?<!-- VIDEO_OPTION_END -->', '', text, flags=re.S)
            if not name:
                anchor = r'(<p class="heroAlternatives">.*?</p>)'
            elif name in {'sodeco.html', 'tayouneh.html'}:
                anchor = r'(<div class="actions">.*?</div>)'
            elif 'class="card patientConsultation"' in text:
                anchor = r'(<section class="card patientConsultation"[^>]*>.*?<div class="actions">.*?</div>)'
            else:
                anchor = r'(<p class="clinicLocation">.*?</p>)'
            note, label = COPY[lang]
            block = f'\n<!-- VIDEO_OPTION_START --><div class="onlineOption"><p>{note}</p><a href="/booking.html?mode=online&amp;lang={lang}" target="_blank" rel="noopener">{label}</a></div><!-- VIDEO_OPTION_END -->'
            text, count = re.subn(anchor, lambda match: match[1] + block, text, count=1, flags=re.S)
            assert count == 1, f'Missing consultation placement in {page}'
            page.write_text(text)
