import random
from typing import Dict
from faker import Faker

class PIIReplacer:
    def __init__(self, seed=42):
        self.faker = Faker('en_IN') # Using Indian locale as prospectus is Indian
        self.faker.seed_instance(seed)
        random.seed(seed)
        
        # Mapping dictionaries to ensure consistency
        # e.g., self.mappings["PERSON"]["Sarthak Malvadkar"] = "John Smith"
        self.mappings: Dict[str, Dict[str, str]] = {
            "PERSON": {},
            "EMAIL_ADDRESS": {},
            "PHONE_NUMBER": {},
            "ORGANIZATION": {},
            "ADDRESS": {},
            "US_SSN": {},
            "CREDIT_CARD": {},
            "DATE_OF_BIRTH": {},
            "IP_ADDRESS": {}
        }

    def get_replacement(self, entity_type: str, original_value: str) -> str:
        """
        Get or generate a consistent fake replacement for the given original value.
        """
        # Normalize original value for better consistency (e.g., lowercase email)
        normalized_value = original_value.strip()
        if entity_type == "EMAIL_ADDRESS":
            normalized_value = normalized_value.lower()
            
        if entity_type not in self.mappings:
            return original_value # Fallback if unknown type
            
        # If already mapped, return it
        if normalized_value in self.mappings[entity_type]:
            return self.mappings[entity_type][normalized_value]
            
        # Otherwise, generate a new one
        replacement = self._generate_fake(entity_type)
        self.mappings[entity_type][normalized_value] = replacement
        return replacement

    def _generate_fake(self, entity_type: str) -> str:
        if entity_type == "PERSON":
            return self.faker.name()
        elif entity_type == "EMAIL_ADDRESS":
            return self.faker.email()
        elif entity_type == "PHONE_NUMBER":
            return "+91 " + "".join([str(random.randint(0, 9)) for _ in range(10)])
        elif entity_type == "ORGANIZATION":
            return self.faker.company()
        elif entity_type == "ADDRESS":
            # Just return a simple address to fit in most contexts
            return f"{self.faker.building_number()}, {self.faker.street_name()}, {self.faker.city()} - {self.faker.postcode()}"
        elif entity_type == "US_SSN":
            return self.faker.ssn()
        elif entity_type == "CREDIT_CARD":
            return self.faker.credit_card_number(card_type='visa')
        elif entity_type == "DATE_OF_BIRTH":
            return self.faker.date_of_birth(minimum_age=18, maximum_age=65).strftime("%B %d, %Y")
        elif entity_type == "IP_ADDRESS":
            return self.faker.ipv4()
        else:
            return "[REDACTED]"
