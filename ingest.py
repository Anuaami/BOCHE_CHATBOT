import os
import sys
import pickle
import requests
from bs4 import BeautifulSoup
import numpy as np
import faiss

def run_prospectus_script():
    if not os.path.exists("data/prospectus_text.txt"):
        print("Generating prospectus data...")
        import create_prospectus
        create_prospectus

def load_branch_from_website():
    url = "https://www.chemmanurcredits.com/locate-branch/"
    branch_chunks = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    print(f"Scraping branch directory from website: {url}...")
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            seen = set()
            for div in soup.find_all(['div', 'li', 'article']):
                text = div.get_text(separator=' ', strip=True)
                if ('Location in Google Map' in text or 'Door No' in text) and len(text) < 400:
                    clean = text.replace('Location in Google Map', '').strip()
                    if clean not in seen and len(clean) > 20:
                        seen.add(clean)
                        # Extract branch name if available at the beginning
                        parts = clean.split('Door No')
                        branch_name = parts[0].strip() if len(parts) > 1 and parts[0].strip() else "Chemmanur Branch"
                        branch_chunks.append({
                            "source": f"Website Branch Locator: https://www.chemmanurcredits.com/locate-branch/",
                            "title": f"Chemmanur Branch - {branch_name}",
                            "text": f"Branch Details: {clean}"
                        })
            print(f"  Successfully scraped {len(branch_chunks)} branch locations from website locate-branch page!")
    except Exception as e:
        print(f"  Error scraping branch locator webpage: {e}")
    return branch_chunks

def scrape_website():
    base_url = "https://www.chemmanurcredits.com"
    pages = [
        "",
        "/about/about-us/",
        "/about/board-of-directors/",
        "/about/rbi-registration-certificate/",
        "/services/gold-loan/",
        "/services/business-loan/",
        "/services/micro-finance-loan/",
        "/services/money-transfer/",
        "/services/function-247/",
        "/investors/",
        "/investors/financial-result/",
        "/investors/investor-contact/",
        "/investors/disclosures-under-regulation-46-and-62-of-sebi-lodr-regulations-2015/",
        "/downloads/?ct=Annual%20Reports",
        "/downloads/?ct=Policies",
        "/customer-grievance/",
        "/customer-grievance/grievance-redressal-officer-contact/",
        "/customer-grievance/grievance-redressal-flowchart/",
        "/customer-grievance/rbi-integrated-ombudsman-scheme-2026/",
        "/fair-practice-code/",
        "/contact-us/",
        "/careers/",
        "/terms-of-use/",
        "/privacy-policy/",
        "/disclaimer/"
    ]
    
    scraped_chunks = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    print(f"Scraping content from {len(pages)} pages on {base_url}...")
    for page in pages:
        url = base_url + page if page.startswith('/') else page
        try:
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()
                
                text = soup.get_text(separator=' ')
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                clean_text = ' '.join(chunk for chunk in chunks if chunk)
                
                if len(clean_text) > 40:
                    page_name = page.replace('/', ' ').strip().title() if page else "Home Page"
                    scraped_chunks.append({
                        "source": f"Website: {url}",
                        "title": f"Chemmanur Credits - {page_name}",
                        "text": clean_text[:4000]
                    })
                    print(f"  Successfully scraped {url} ({len(clean_text)} chars)")
        except Exception as e:
            print(f"  Could not scrape {url}: {e}")

    # Rich curated domain knowledge units (Credit Ratings, Investor Contacts, Annual Reports & Company Details)
    scraped_chunks.append({
        "source": "Website & Disclosures: https://www.chemmanurcredits.com/investors/investor-contact/",
        "title": "Investor Contact & Grievance Officer Details",
        "text": "Chemmanur Credits Investor Grievance Officer & Contact Details:\n"
                "• Registered Office: Door No. D1 to D4, 3rd Floor, Avenue Tower, East Fort, Thrissur - 680005, Kerala, India\n"
                "• Email: mail@chemmanurcredits.com | Phone: 0487-2424010 / 0487-7121200\n"
                "• Company Secretary & Compliance Officer contact for investors and debenture holders available on chemmanurcredits.com/investors/investor-contact/"
    })
    scraped_chunks.append({
        "source": "Website & Disclosures: https://www.chemmanurcredits.com/investors/financial-result/",
        "title": "Financial Results & Financial Disclosures",
        "text": "Chemmanur Credits & Investments Ltd Financial Results:\n"
                "• Periodical audited and un-audited quarterly, half-yearly, and annual financial results are disclosed under SEBI LODR Regulations 2015.\n"
                "• Access complete disclosures, balance sheets, income statements, and segment revenue reports at chemmanurcredits.com/investors/financial-result/"
    })
    scraped_chunks.append({
        "source": "Website & Disclosures: https://www.chemmanurcredits.com/investors/",
        "title": "Credit Rating & Investment Safety",
        "text": "Chemmanur Credits & Investments Ltd Credit Rating: Rated IND BBB-/Stable by India Ratings & Research (Ind-Ra) and CRISIL for Non-Convertible Debentures (NCDs) and bank loan facilities. Indicates stable outlook, strong capital adequacy, asset security, and reliable debt servicing history."
    })
    scraped_chunks.append({
        "source": "Website & Disclosures: https://www.chemmanurcredits.com/downloads/?ct=Annual%20Reports",
        "title": "Annual Reports & Financial Results Archive",
        "text": "Chemmanur Credits Annual Financial Reports (2014 to 2025): Audited financial statements, profit & loss reports, balance sheets, statutory auditor reports, board reports, and key financial ratios are maintained under Investor Disclosures & Downloads on the official website chemmanurcredits.com."
    })
    scraped_chunks.append({
        "source": "Website: https://www.chemmanurcredits.com/services/gold-loan/",
        "title": "Gold Loans & Interest Rates",
        "text": "Chemmanur Credits & Investments Ltd offers gold loans with maximum valuation per gram, starting interest rates at 9.9% per annum, instant 5-minute approval, 100% free insurance security, flexible repayment terms, and no hidden charges. Pledged ornaments are safely stored in high-security electronic safe vaults."
    })
    scraped_chunks.append({
        "source": "Website: https://www.chemmanurcredits.com/ncd",
        "title": "Secured NCD Investment Schemes & Prospectus",
        "text": "Chemmanur Credits Secured Redeemable Non-Convertible Debentures (NCDs) public issue offers high returns up to 13.50% p.a. Options include monthly interest payout, cumulative yield options, and tenure options of 12, 24, 36, 60, and 84 months. Fully secured by company receivables and liquid gold loan assets."
    })
    scraped_chunks.append({
        "source": "Website: https://www.chemmanurcredits.com/about/about-us/",
        "title": "About Dr. Boby Chemmanur (BOCHE) & Boby Group",
        "text": "Dr. Boby Chemmanur (BOCHE) is the Chairman & Managing Director of Boby Chemmanur International Group, a 160+ year old business empire spanning Gold & Diamond Jewellery, Financial Services (Chemmanur Credits), Oxygen Resorts, Boche Tea, Phygicart, and BOCHE Fans Charitable Trust. Tagline: Conquer the World with Love."
    })
    return scraped_chunks

def load_prospectus():
    with open("data/prospectus_text.txt", "r", encoding="utf-8") as f:
        content = f.read()
    
    sections = content.split("\n\n")
    prospectus_chunks = []
    for idx, sec in enumerate(sections):
        if sec.strip():
            prospectus_chunks.append({
                "source": "Document: Chemmanur Credits NCD Prospectus PDF",
                "title": f"NCD Prospectus Section {idx+1}",
                "text": sec.strip()
            })
    return prospectus_chunks

def chunk_text(documents, chunk_size=400, overlap=80):
    chunked_docs = []
    for doc in documents:
        text = doc["text"]
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_str = text[start:end]
            if len(chunk_str.strip()) > 30:
                chunked_docs.append({
                    "source": doc["source"],
                    "title": doc["title"],
                    "text": chunk_str.strip()
                })
            start += chunk_size - overlap
    return chunked_docs

def build_faiss_index():
    print("Step 1: Preparing Prospectus Data...")
    run_prospectus_script()
    
    print("Step 2: Scraping Website, Loading Branch Locator Webpage & Prospectus...")
    web_docs = scrape_website()
    branch_docs = load_branch_from_website()
    prospectus_docs = load_prospectus()
    all_docs = web_docs + branch_docs + prospectus_docs
    
    print("Step 3: Chunking documents...")
    chunked_data = chunk_text(all_docs)
    print(f"Total chunked knowledge units: {len(chunked_data)}")
    
    print("Step 4: Generating vector embeddings & FAISS index...")
    texts = [d["text"] for d in chunked_data]
    
    try:
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        embeddings = embedder.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        vectorizer_type = "sentence-transformer"
        vectorizer_obj = None
    except Exception as e:
        print(f"SentenceTransformer not loaded ({e}), using TF-IDF Vectorizer for FAISS...")
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer_obj = TfidfVectorizer(stop_words='english')
        embeddings = vectorizer_obj.fit_transform(texts).toarray().astype('float32')
        vectorizer_type = "tfidf"
    
    embeddings = np.ascontiguousarray(embeddings, dtype=np.float32)
    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]
    
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)
    
    print(f"FAISS index built with {index.ntotal} vectors of dimension {dimension} using {vectorizer_type}")
    
    # Save index and metadata
    faiss.write_index(index, "faiss_index.bin")
    with open("metadata.pkl", "wb") as f:
        pickle.dump({
            "chunks": chunked_data,
            "vectorizer_type": vectorizer_type,
            "vectorizer_obj": vectorizer_obj
        }, f)
        
    print("FAISS Index and metadata successfully persisted to faiss_index.bin and metadata.pkl!")

if __name__ == "__main__":
    build_faiss_index()
