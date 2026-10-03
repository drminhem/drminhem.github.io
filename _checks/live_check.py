"""Read-only post-deployment verification against the current checkout.

Fetches HTML and shared assets without executing JavaScript or contacting analytics.
Run only after the matching GitHub Pages deployment succeeds.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://drminhem.com"
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
urls = [n.text for n in ET.parse(ROOT / "sitemap.xml").findall("sm:url/sm:loc", NS)]
condition_guides = json.loads((ROOT / '_content/generated.json').read_text())['slugs']
patient_guides = json.loads((ROOT / '_content/patient_generated.json').read_text())['slugs']
expected_pages = 10 + 2 * (len(condition_guides) + len(patient_guides) + 1)
assert len(urls) == expected_pages and len(set(urls)) == expected_pages
paths = [url.removeprefix(BASE) for url in urls]
paths += ["/sitemap.xml", "/robots.txt", "/booking.html", "/clinic.css", "/clinic.js",
          "/site.css", "/site.js", "/language.js", "/analytics.js"]


def check(path):
    local = ROOT / (path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
    expected = sha256(local.read_bytes()).hexdigest()
    req = Request(BASE + path, headers={"User-Agent": "DrMinhemReleaseVerification/1.0", "Cache-Control": "no-cache"})
    with urlopen(req, timeout=30) as response:
        body = response.read()
        actual = sha256(body).hexdigest()
        result = {"url": BASE + path, "status": response.status, "final_url": response.url,
                  "matches_checkout": expected == actual, "sha256": actual}
    return result


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(check, paths))
    out = {"checked_at": datetime.now(timezone.utc).isoformat(),
           "checkout_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "indexable_pages": len(urls), "results": results}
    evidence = ROOT.parent / "evidence"
    evidence.mkdir(exist_ok=True)
    (evidence / "live-verification.json").write_text(json.dumps(out, indent=2) + "\n")
    failures = [r for r in results if r["status"] != 200 or not r["matches_checkout"] or r["final_url"] != r["url"]]
    assert not failures, json.dumps(failures, indent=2)
    print(f"PASS: all {len(urls)} live pages and {len(paths) - len(urls)} shared resources return HTTP 200 and exactly match the tested checkout.")
