import os
import sys

os.makedirs("data", exist_ok=True)

prospectus_content = """
CHEMMANUR CREDITS AND INVESTMENTS LIMITED
(A Member of Boby Chemmanur International Group - Founded by Dr. Boby Chemmanur)
PROSPECTUS & FINANCIAL SERVICES INFORMATION HANDBOOK

1. CORPORATE OVERVIEW
Company Name: Chemmanur Credits and Investments Limited (CCIL)
Promoter & Chairman & Managing Director: Dr. Boby Chemmanur (BOCHE)
Motto: "Conquer the World with Love"
RBI Registration: Non-Banking Financial Company (NBFC) registered with Reserve Bank of India (Registration No. N-16.00188).
Legacy: Part of the 160+ year old Boby Chemmanur International Group, serving millions of satisfied customers across India and abroad.
Corporate Address: Chemmanur Credits & Investments Ltd, Gold Hub Building, Kozhikode / Thrissur, Kerala, India.
Helpline: 1800-425-4255 / info@chemmanurcredits.com
Website: https://www.chemmanurcredits.com/

2. GOLD LOAN REQUIRED DOCUMENTS & KYC REQUIREMENTS
To apply for a Gold Loan at Chemmanur Credits, customers need minimal documentation for instant 5-minute approval:
- Identity Proof (Any One): Aadhaar Card, PAN Card, Voter ID, Passport, or Driving License.
- Address Proof (Any One): Aadhaar Card, Voter ID, Passport, Driving License, Utility Bill (Electricity/Water), or Ration Card.
- Photographs: 2 Recent Passport-size Photographs.
- Pledged Gold: Gold jewellery / ornaments (18 Karat to 24 Karat).
- Note: No CIBIL score check, no salary slip or income proof required! Instant cash / bank transfer within 5 minutes.

3. NON-CONVERTIBLE DEBENTURES (NCD) PROSPECTUS DETAILS & DOCUMENTS
Public Issue of Secured Redeemable Non-Convertible Debentures (NCDs):
- Face Value: Rs. 1,000 per NCD
- Minimum Application Size: 10 NCDs (Rs. 10,000)
- Interest Rate Range: 11.50% to 13.50% per annum (depending on tenure and scheme selected)
- Tenures Available: 12 Months, 24 Months, 36 Months, 60 Months, 84 Months
- Security: 100% Secured by first charge on company receivables and liquid gold loan assets.
- Documents Required for NCD Investment: PAN Card (Mandatory), Aadhaar Card, Cancelled Cheque / Bank Account Details, Demat Account details (or Physical allotment form), Passport Photograph.

4. GOLD LOAN SCHEMES & ADVANTAGES
- Maximum Loan Value: Highest per-gram gold valuation as per RBI guidelines.
- Interest Rates: Attractive interest rates starting at 9.9% p.a. with rebate options for prompt payment.
- Processing: Instant approval in 5 minutes with minimal documentation.
- Safety & Insurance: 100% free vault security and full insurance cover for pledged gold ornaments in modern electronic safe lockers.
- Flexible Repayment: Bullet repayment, monthly interest payment, or partial online principal repayment via Chemmanur Mobile App.

5. MICROFINANCE & BUSINESS LOANS
- Documents for Microfinance / Business Loan: Aadhaar Card, PAN Card, Business Registration / Shop License (for MSME), Bank Statement (last 6 months), 2 Photos.
- Micro-Loans: Empowering rural women entrepreneurs, small shop owners, and self-help groups (SHGs).

6. MONEY TRANSFER & FOREX SERVICES
- Authorized Forex Dealer Category II: Foreign currency exchange, international money transfers via Western Union, MoneyGram, and Express Money.
- Documents for Forex / Money Transfer: Passport, Valid Visa, PAN Card, Ticket copy (for travel forex).

7. CHARITABLE & PHILANTHROPIC INITIATIVES (BOCHE FANS CHARITABLE TRUST)
- Free Food Counters: Daily meals provided free of cost to thousands of needy people across multiple cities.
- Blood Donation Army: World's largest blood donor registry network organized by Dr. Boby Chemmanur.
- Ambulance & Emergency Assistance: Free ambulance services for accident victims and low-income patients.
- BOCHE's Tagline: "Conquer the World with Love".
"""

with open("data/prospectus_text.txt", "w", encoding="utf-8") as f:
    f.write(prospectus_content)

print("Updated Prospectus text with Gold Loan KYC documents at data/prospectus_text.txt")
