#!/usr/bin/env python3
"""
Basic smoke test untuk jpteunm.com
Menguji fungsionalitas dasar (ISO 25010: Functional Suitability)
"""

import requests
from urllib.parse import urljoin

BASE_URL = 'https://jpteunm.com'
PATHS_TO_CHECK = [
    '/',
    '/profil',
    '/akademik',
    '/penelitian',
    '/kontak'
]

def test_url(url):
    """Test a single URL"""
    try:
        response = requests.get(url, timeout=10)
        success = response.status_code == 200
        print(f"{'✅' if success else '❌'} {url} - {response.status_code}")
        return success
    except requests.RequestException as e:
        print(f"❌ {url} - ERROR: {e}")
        return False

def main():
    print("🚀 Running Smoke Test for jpteunm.com...")
    results = []
    
    for path in PATHS_TO_CHECK:
        test_url = urljoin(BASE_URL, path)
        results.append(test_url(test_url))
    
    # Hitung score functional suitability (persentase halaman yang bisa diakses)
    functional_score = (sum(results) / len(results)) * 100
    
    # Simpan score untuk dibaca quality gate
    with open('tests/results/functional-score.json', 'w') as f:
        json.dump({'score': functional_score}, f)
    
    print(f"\n📊 Functional Suitability Score: {functional_score:.2f}%")
    
    # Exit code 0 jika semua test pass, 1 jika ada yang gagal
    sys.exit(0 if all(results) else 1)

if __name__ == "__main__":
    main()
