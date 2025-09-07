#!/usr/bin/env python3
"""
Script untuk mengaggregasi hasil black-box testing jpteunm.com
"""

import json
import os
import sys

class QualityGate:
    # Bobot karakteristik ISO 25010 untuk website institusi
    WEIGHTS = {
        'performance_efficiency': 0.30,  # Sangat penting untuk website
        'security': 0.25,                # Penting untuk melindungi data
        'usability': 0.20,               # Aksesibilitas untuk semua pengguna
        'functional_suitability': 0.15,  # Fungsi dasar bekerja
        'compatibility': 0.10            # Kompatibilitas browser
    }
    
    THRESHOLD = 70  # Threshold minimal untuk pass

    def __init__(self, target_url):
        self.target_url = target_url
        self.results = {}

    def load_results(self):
        """Load hasil dari berbagai test reports"""
        try:
            # Load Lighthouse Performance Report
            with open('tests/results/lighthouse-report.json') as f:
                lh_data = json.load(f)
                self.results['performance_efficiency'] = lh_data['categories']['performance']['score'] * 100
                self.results['seo'] = lh_data['categories']['seo']['score'] * 100 # Bonus

            # Load Security Scan Results
            with open('tests/results/zap-report.json') as f:
                zap_data = json.load(f)
                self.results['security'] = self.calculate_security_score(zap_data)

            # Load Accessibility Results
            with open('tests/results/accessibility-report.json') as f:
                axe_data = json.load(f)
                self.results['usability'] = self.calculate_accessibility_score(axe_data)

            # Load Functional Test Results (Asumsikan file dibuat oleh smoke test)
            self.results['functional_suitability'] = self.get_functional_score()

        except FileNotFoundError as e:
            print(f"Error loading results: {e}")
            sys.exit(1)

    def calculate_security_score(self, data):
        """Hitung score berdasarkan security scan results"""
        # Kurangi poin untuk setiap alert risiko tinggi
        high_risk_alerts = sum(1 for site in data['site'] for alert in site['alerts'] if alert['risk'] == 'High')
        return max(0, 100 - (high_risk_alerts * 20))

    def calculate_accessibility_score(self, data):
        """Hitung score berdasarkan accessibility results"""
        total_violations = len(data.get('violations', []))
        return max(0, 100 - (total_violations * 5))

    def get_functional_score(self):
        """Baca score functional test dari file atau default"""
        try:
            with open('tests/results/functional-score.json') as f:
                func_data = json.load(f)
                return func_data.get('score', 85)
        except FileNotFoundError:
            return 85 # Nilai default jika test tidak dijalankan

    def calculate_overall_score(self):
        """Hitung overall weighted score"""
        total_score = 0
        for characteristic, weight in self.WEIGHTS.items():
            score = self.results.get(characteristic, 0)
            total_score += score * weight
        return total_score

    def enforce_quality_gate(self):
        """Terapkan quality gate dan return hasil"""
        overall_score = self.calculate_overall_score()
        
        print(f"🔎 Quality Assessment for: {self.target_url}")
        print(f"📊 Overall Quality Score: {overall_score:.2f}%")
        print("\n📈 Detailed Results:")
        for characteristic, score in self.results.items():
            print(f"  - {characteristic.replace('_', ' ').title()}: {score:.2f}%")
        
        # Set output untuk GitHub Actions
        print(f"::set-output name=score::{overall_score:.2f}")
        
        if overall_score >= self.THRESHOLD:
            message = "Quality gate PASSED"
            print(f"✅ {message}")
            print(f"::set-output name=result::PASS")
            print(f"::set-output name=message::{message}")
            return "PASS"
        else:
            message = f"Quality gate FAILED. Score below threshold ({self.THRESHOLD}%)"
            print(f"❌ {message}")
            print(f"::set-output name=result::FAIL")
            print(f"::set-output name=message::{message}")
            return "FAIL"

if __name__ == "__main__":
    target_url = os.getenv('TARGET_URL', 'https://jpteunm.com')
    quality_gate = QualityGate(target_url)
    quality_gate.load_results()
    result = quality_gate.enforce_quality_gate()
    sys.exit(0 if result == "PASS" else 1)
