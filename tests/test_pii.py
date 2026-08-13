import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from detectors import PIIDetector

class TestPIIDetector(unittest.TestCase):
    def setUp(self):
        self.detector = PIIDetector()

    def test_email(self):
        text = "Contact us at john.smith@example.com."
        results = self.detector.detect(text)
        emails = [r for r in results if r['entity_type'] == 'EMAIL_ADDRESS']
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['text'], "john.smith@example.com")

    def test_phone(self):
        text = "My phone is +91 9876543210."
        results = self.detector.detect(text)
        phones = [r for r in results if r['entity_type'] == 'PHONE_NUMBER']
        self.assertEqual(len(phones), 1)
        self.assertEqual(phones[0]['text'], "+91 9876543210")

    def test_ssn(self):
        text = "The SSN is 123-45-6789."
        results = self.detector.detect(text)
        ssns = [r for r in results if r['entity_type'] == 'US_SSN']
        self.assertEqual(len(ssns), 1)
        self.assertEqual(ssns[0]['text'], "123-45-6789")

    def test_credit_card(self):
        text = "Card number 4111 1111 1111 1111."
        results = self.detector.detect(text)
        ccs = [r for r in results if r['entity_type'] == 'CREDIT_CARD']
        self.assertEqual(len(ccs), 1)
        self.assertEqual(ccs[0]['text'], "4111 1111 1111 1111")

    def test_ip_address(self):
        text = "Server IP is 192.168.1.10."
        results = self.detector.detect(text)
        ips = [r for r in results if r['entity_type'] == 'IP_ADDRESS']
        self.assertEqual(len(ips), 1)
        self.assertEqual(ips[0]['text'], "192.168.1.10")

    def test_dob(self):
        text = "Date of Birth: 12/05/1999."
        results = self.detector.detect(text)
        dobs = [r for r in results if r['entity_type'] == 'DATE_OF_BIRTH']
        self.assertEqual(len(dobs), 1)
        self.assertEqual(dobs[0]['text'], "12/05/1999")
        
    def test_person(self):
        text = "Sarthak Malvadkar is the compliance officer."
        results = self.detector.detect(text)
        persons = [r for r in results if r['entity_type'] == 'PERSON']
        self.assertTrue(len(persons) >= 1)
        
    def test_organization(self):
        text = "KSH International Limited is growing."
        results = self.detector.detect(text)
        orgs = [r for r in results if r['entity_type'] == 'ORGANIZATION']
        self.assertTrue(len(orgs) >= 1)

if __name__ == '__main__':
    unittest.main()
