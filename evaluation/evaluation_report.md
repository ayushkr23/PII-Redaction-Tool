# Evaluation Report

## Overall Metrics (Entity Level)
- **Precision:** 0.3774
- **Recall:** 0.7692
- **F1-Score:** 0.5063
- **TP:** 20, **FP:** 33, **FN:** 6

## Character-Level Accuracy
- **Accuracy:** 0.8805
- **Total Chars:** 5505

## Per-Category Results
### PERSON
- Precision: 0.5000 | Recall: 0.6667 | F1: 0.5714
- TP: 6 | FP: 6 | FN: 3

### EMAIL_ADDRESS
- Precision: 1.0000 | Recall: 1.0000 | F1: 1.0000
- TP: 1 | FP: 0 | FN: 0

### PHONE_NUMBER
- Precision: 1.0000 | Recall: 1.0000 | F1: 1.0000
- TP: 1 | FP: 0 | FN: 0

### ORGANIZATION
- Precision: 0.1935 | Recall: 0.8571 | F1: 0.3158
- TP: 6 | FP: 25 | FN: 1

### ADDRESS
- Precision: 0.5000 | Recall: 0.5000 | F1: 0.5000
- TP: 2 | FP: 2 | FN: 2

### US_SSN
- Precision: 1.0000 | Recall: 1.0000 | F1: 1.0000
- TP: 1 | FP: 0 | FN: 0

### CREDIT_CARD
- Precision: 1.0000 | Recall: 1.0000 | F1: 1.0000
- TP: 1 | FP: 0 | FN: 0

### DATE_OF_BIRTH
- Precision: 1.0000 | Recall: 1.0000 | F1: 1.0000
- TP: 1 | FP: 0 | FN: 0

### IP_ADDRESS
- Precision: 1.0000 | Recall: 1.0000 | F1: 1.0000
- TP: 1 | FP: 0 | FN: 0

## False Positives (Sample)
- `E-MAIL` classified as `ORGANIZATION` in context: *E-MAIL AND TELEPHONE*
- `Village Birdewadi` classified as `ORGANIZATION` in context: *11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune – 410 501
Maharashtra, India*
- `Taluka - Khed Pune` classified as `PERSON` in context: *11/3, 11/4 and 11/5 Village Birdewadi Chakan Taluka - Khed Pune – 410 501
Maharashtra, India*
- `Tower 2` classified as `ORGANIZATION` in context: *201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner Pune – 411 045
Maharashtra, India*
- `Montreal Business Centre` classified as `ORGANIZATION` in context: *201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner Pune – 411 045
Maharashtra, India*
- `Baner Pune` classified as `PERSON` in context: *201, Tower 2, Montreal Business Centre, Off Pallod Farms, Baner Pune – 411 045
Maharashtra, India*
- `OFFER` classified as `ORGANIZATION` in context: *DETAILS OF THE OFFER TO PUBLIC*
- `SIZE` classified as `ORGANIZATION` in context: *SIZE OF THE FRESH ISSUE*
- `SIZE` classified as `ORGANIZATION` in context: *SIZE	OF	THE OFFER FOR SALE*
- `ELIGIBILITY` classified as `ORGANIZATION` in context: *ELIGIBILITY	AND	SHARE
RESERVATION AMONG QIBs, NIIs AND RIIs*

## False Negatives (Sample)
- Missed `RAKHI GIRIJA SHETTY` of type `PERSON` in context: *OUR PROMOTERS: KUSHAL SUBBAYYA HEGDE, PUSHPA KUSHAL HEGDE, RAJESH KUSHAL HEGDE, ROHIT KUSHAL HEGDE, RAKHI GIRIJA SHETTY, DHAULAGIRI FAMILY TRUST, EVEREST FAMILY TRUST, MAKALU FAMILY TRUST, BROAD FAMILY TRUST, ANNAPURNA FAMILY TRUST, KANCHENJUNGA FAMILY TRUST AND
WATERLOO INDUSTRIAL PARK VI PRIVATE LIMITED*
- Missed `WATERLOO INDUSTRIAL PARK VI PRIVATE LIMITED` of type `ORGANIZATION` in context: *OUR PROMOTERS: KUSHAL SUBBAYYA HEGDE, PUSHPA KUSHAL HEGDE, RAJESH KUSHAL HEGDE, ROHIT KUSHAL HEGDE, RAKHI GIRIJA SHETTY, DHAULAGIRI FAMILY TRUST, EVEREST FAMILY TRUST, MAKALU FAMILY TRUST, BROAD FAMILY TRUST, ANNAPURNA FAMILY TRUST, KANCHENJUNGA FAMILY TRUST AND
WATERLOO INDUSTRIAL PARK VI PRIVATE LIMITED*
- Missed `801-804, Wing A, Building No. 3 Inspire BKC G Block, Bandra Kurla Complex` of type `ADDRESS` in context: *801-804, Wing A, Building No. 3 Inspire BKC G Block, Bandra Kurla Complex*
- Missed `Lokesh Shah` of type `PERSON` in context: *Contact person: Lokesh Shah/ Soumavo Sarkar*
- Missed `Soumavo Sarkar` of type `PERSON` in context: *Contact person: Lokesh Shah/ Soumavo Sarkar*
- Missed `5th Floor, Marathon IT Park Bund Garden Road` of type `ADDRESS` in context: *5th Floor, Marathon IT Park Bund Garden Road*
