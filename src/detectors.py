import re
from typing import List, Dict, Any, Tuple
import spacy

try:
    nlp = spacy.load("en_core_web_sm", disable=["parser", "senter", "attribute_ruler", "lemmatizer"])
except OSError:
    # If not loaded, download and load
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm", disable=["parser", "senter", "attribute_ruler", "lemmatizer"])

from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern, RecognizerResult, EntityRecognizer
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer.predefined_recognizers import CreditCardRecognizer, IpRecognizer

# Pre-compiled Regex patterns
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERN = r'(?:\+?\s*91\s*[\s-]?\s*\d{2,4}\s*[\s-]?\s*\d{6,8}|\b[6-9]\d{9}\b|\b\d{2,4}\s*[-]\s*\d{6,8}\b)'
SSN_PATTERN = r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'
DOB_PATTERN = r'\b(?:(?:0[1-9]|[12][0-9]|3[01])[-/.](?:0[1-9]|1[012])[-/.](?:19|20)\d\d|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2}, \d{4})\b'

# Context words for DOB
DOB_CONTEXT = ["dob", "date of birth", "born", "birth date", "birth"]

class CustomDOBRecognizer(EntityRecognizer):
    def __init__(self):
        super().__init__(supported_entities=["DATE_OF_BIRTH"], supported_language="en")
    
    def load(self) -> None:
        pass
    
    def analyze(self, text: str, entities: List[str], nlp_artifacts: Any) -> List[RecognizerResult]:
        results = []
        lower_text = text.lower()
        # Only detect DOB if context words are present nearby, or if it explicitly says DOB.
        # But for robustness, we'll search for date patterns and check context.
        # Alternatively, if a table cell just has a date but the header is DOB, we might miss it if we only look at the text itself.
        # So we will give a small score for dates without context, but high score with context.
        
        matches = re.finditer(DOB_PATTERN, text, re.IGNORECASE)
        for match in matches:
            start, end = match.span()
            score = 0.4 # base score for a date
            
            # check context in the text
            for context in DOB_CONTEXT:
                if context in lower_text:
                    score = 0.85
                    break
            
            if score >= 0.8:
                results.append(RecognizerResult(entity_type="DATE_OF_BIRTH", start=start, end=end, score=score))
        return results

class PIIDetector:
    def __init__(self):
        # We will use Presidio for some, and custom regex for others to ensure high precision/recall.
        
        # Setup NLP Engine for Presidio
        provider = NlpEngineProvider(nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}]
        })
        nlp_engine = provider.create_engine()
        
        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            supported_languages=["en"]
        )
        
        # Add custom recognizer for DOB
        self.analyzer.registry.add_recognizer(CustomDOBRecognizer())
        
        self.spacy_nlp = nlp
        
    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in the given text.
        Returns a list of dicts: {'entity_type': str, 'start': int, 'end': int, 'text': str}
        """
        results = []
        
        # 1. Use Presidio for generic entities
        # PERSON, EMAIL_ADDRESS, PHONE_NUMBER, US_SSN, CREDIT_CARD, IP_ADDRESS, DATE_OF_BIRTH
        presidio_entities = [
            "PERSON", 
            "EMAIL_ADDRESS", 
            "PHONE_NUMBER", 
            "US_SSN", 
            "CREDIT_CARD", 
            "IP_ADDRESS",
            "DATE_OF_BIRTH"
        ]
        
        # We disable some noisy Presidio recognizers if needed, but default is fine.
        presidio_results = self.analyzer.analyze(text=text, entities=presidio_entities, language="en", score_threshold=0.5)
        
        for res in presidio_results:
            results.append({
                'entity_type': res.entity_type,
                'start': res.start,
                'end': res.end,
                'text': text[res.start:res.end],
                'score': res.score
            })
            
        # 2. Use pure SpaCy for ORG and GPE/FAC (Company names, Addresses)
        doc = self.spacy_nlp(text)
        for ent in doc.ents:
            if ent.label_ == "ORG":
                # Filter out generic terms that aren't specific companies if needed
                results.append({
                    'entity_type': "ORGANIZATION",
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'text': ent.text,
                    'score': 0.8
                })
            elif ent.label_ in ["GPE", "LOC", "FAC"]:
                # Address might be captured as GPE/LOC
                # Let's label it as ADDRESS
                results.append({
                    'entity_type': "ADDRESS",
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'text': ent.text,
                    'score': 0.8
                })
                
        # 3. Custom Regex Fallbacks (To ensure high recall for strict patterns)
        self._add_regex_matches(text, EMAIL_PATTERN, "EMAIL_ADDRESS", results)
        self._add_regex_matches(text, PHONE_PATTERN, "PHONE_NUMBER", results)
        self._add_regex_matches(text, SSN_PATTERN, "US_SSN", results)
        
        # Resolve overlaps (keep highest score, or longest match)
        return self._resolve_overlaps(results)
        
    def _add_regex_matches(self, text: str, pattern: str, entity_type: str, results: List[Dict[str, Any]]):
        for match in re.finditer(pattern, text):
            # Check if it already exists in results
            start, end = match.span()
            exists = any(r['start'] == start and r['end'] == end for r in results)
            if not exists:
                results.append({
                    'entity_type': entity_type,
                    'start': start,
                    'end': end,
                    'text': match.group(),
                    'score': 1.0 # High confidence for regex
                })
                
    def _resolve_overlaps(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Sort by start index, then by length (descending)
        entities.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))
        
        resolved = []
        for entity in entities:
            if not resolved:
                resolved.append(entity)
                continue
                
            last_entity = resolved[-1]
            if entity['start'] < last_entity['end']:
                # Overlap detected
                # If current is longer or has higher score, we could replace, but usually keeping the first (longest) is better
                # Let's keep the one with higher score, or if equal, the longer one
                if entity['score'] > last_entity['score']:
                    resolved[-1] = entity
            else:
                resolved.append(entity)
                
        return resolved

if __name__ == "__main__":
    detector = PIIDetector()
    text = "John Doe works at Google. His email is john.doe@example.com. Call +91 9876543210. Born on 12/05/1999."
    print(detector.detect(text))
