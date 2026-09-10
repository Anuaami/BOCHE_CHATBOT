import os
import pickle
import numpy as np
import faiss

class RAGEngine:
    def __init__(self, index_path="faiss_index.bin", metadata_path="metadata.pkl"):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.embedder = None
        self.vectorizer_type = None
        self.vectorizer_obj = None
        self.index = None
        self.chunks = []
        self.is_ready = False
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                print("Loading FAISS index and metadata...")
                with open(self.metadata_path, "rb") as f:
                    meta_data = pickle.load(f)
                    
                if isinstance(meta_data, dict):
                    self.chunks = meta_data.get("chunks", [])
                    self.vectorizer_type = meta_data.get("vectorizer_type", "tfidf")
                    self.vectorizer_obj = meta_data.get("vectorizer_obj", None)
                else:
                    self.chunks = meta_data
                    self.vectorizer_type = "sentence-transformer"

                if self.vectorizer_type == "sentence-transformer":
                    try:
                        from sentence_transformers import SentenceTransformer
                        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
                    except Exception as e:
                        print(f"Could not load SentenceTransformer: {e}")

                self.index = faiss.read_index(self.index_path)
                self.is_ready = True
                print(f"RAG Engine loaded successfully! {self.index.ntotal} FAISS vectors indexed.")
            except Exception as e:
                print(f"Error loading FAISS index: {e}")
                self.is_ready = False
        else:
            print("FAISS index or metadata file missing.")
            self.is_ready = False

    def retrieve(self, query: str, top_k: int = 4):
        if not self.is_ready:
            return []

        if self.vectorizer_type == "sentence-transformer" and self.embedder:
            query_vector = self.embedder.encode([query], convert_to_numpy=True)
        elif self.vectorizer_obj:
            query_vector = self.vectorizer_obj.transform([query]).toarray().astype('float32')
        else:
            return []

        query_vector = np.ascontiguousarray(query_vector, dtype=np.float32)
        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                item = self.chunks[idx]
                results.append({
                    "score": float(score),
                    "title": item["title"],
                    "source": item["source"],
                    "text": item["text"]
                })
        return results

    def generate_response(self, query: str):
        retrieved = self.retrieve(query, top_k=4)
        query_lower = query.lower()
        
        boche_greeting = "Love you all! ❤️ Welcome to Chemmanur Credits and Investments Limited."
        
        
        # Specific match for Credit Rating / Rating queries
        if any(w in query_lower for w in ["credit rating", "rating", "crisil", "ind-ra", "safety", "grade"]):
            answer = f"{boche_greeting}\n\nHere are the **Credit Rating Details** for Chemmanur Credits & Investments Limited:\n\n" \
                     f"• **Credit Rating**: **IND BBB- / Stable** (Assigned by **India Ratings & Research (Ind-Ra)** & CRISIL)\n" \
                     f"• **Instruments Covered**: Bank Facilities & Secured Non-Convertible Debentures (NCDs)\n" \
                     f"• **Rating Outlook**: **Stable** (Reflects strong capital adequacy, asset security, and reliable debt servicing history)\n\n" \
                     f"Invest with confidence backed by our 160+ year legacy!"
            if retrieved:
                answer += "\n\n📌 **Retrieved Reference Details**:\n"
                for r in retrieved[:2]:
                    answer += f"• **{r['title']}**: {r['text']}\n"

        # Specific match for Annual Reports / Financial Results
        elif any(w in query_lower for w in ["annual report", "financial result", "balance sheet", "audit", "profit", "report"]):
            answer = f"{boche_greeting}\n\nOur **Annual Reports & Financial Disclosures** are published annually for complete transparency:\n\n" \
                     f"• **Available Reports**: Comprehensive Audited Annual Reports from 2014 through 2025.\n" \
                     f"• **Where to Download**: Visit our website downloads section at [chemmanurcredits.com/downloads/?ct=Annual%20Reports](https://www.chemmanurcredits.com/downloads/?ct=Annual%20Reports)\n" \
                     f"• **Financial Highlights**: Strong asset growth in Gold Loans and NCD offerings with full regulatory compliance.\n\n" \
                     f"Feel free to ask for specific financial metrics or NCD prospectus figures!"
            if retrieved:
                answer += "\n\n📌 **Retrieved Reference Details**:\n"
                for r in retrieved[:2]:
                    answer += f"• **{r['title']}**: {r['text']}\n"

        # Specific match for Branch / Location search
        elif any(w in query_lower for w in ["branch", "location", "address", "where", "near", "find", "locate", "office"]):
            answer = f"{boche_greeting}\n\nWe operate over **250+ branches** across Kerala, Tamil Nadu, Karnataka, and Maharashtra!\n\n"
            if retrieved:
                branch_matches = [r for r in retrieved if "Branch" in r['title'] or "Address" in r['text'] or "Branch Name:" in r['text']]
                if branch_matches:
                    answer += "📍 **Matching Branch Locations from Directory**:\n\n"
                    for b in branch_matches[:3]:
                        answer += f"🔹 **{b['title']}**\n{b['text']}\n\n"
                else:
                    answer += "📌 **Corporate Registered Office**:\nDoor No. D1 to D4, 3rd Floor, Avenue Tower, East Fort, Thrissur, Kerala - 680005\n\n"
            answer += f"• **Toll-Free Helpline**: **1800-425-4255** | 📞 0487-2424010\n" \
                      f"• **Official Email**: mail@chemmanurcredits.com"

        # Specific match for Documents / KYC queries
        elif any(w in query_lower for w in ["doc", "document", "documents", "kyc", "needed", "requirement", "proof", "paperwork", "apply"]):
            if "ncd" in query_lower or "bond" in query_lower or "invest" in query_lower:
                answer = f"{boche_greeting}\n\nHere are the **Documents Required for NCD Investment**:\n\n" \
                         f"1. **PAN Card** (Mandatory for all investors)\n" \
                         f"2. **Identity & Address Proof**: Aadhaar Card / Passport / Voter ID / Driving License\n" \
                         f"3. **Bank Account Details**: Cancelled cheque leaf or bank passbook copy\n" \
                         f"4. **Demat Account details** (or Physical Application Form)\n" \
                         f"5. **2 Passport-size Photographs**\n\n" \
                         f"Minimum investment size is Rs. 10,000 (10 NCDs @ Rs. 1,000 face value) with yields up to 13.50% p.a.!"
            else:
                answer = f"{boche_greeting}\n\nHere are the **Documents Required for a Gold Loan** at Chemmanur Credits (Instant 5-Minute Approval):\n\n" \
                         f"📌 **1. Identity Proof** (Any ONE):\n" \
                         f"   • Aadhaar Card\n" \
                         f"   • PAN Card\n" \
                         f"   • Passport\n" \
                         f"   • Voter ID Card\n" \
                         f"   • Driving License\n\n" \
                         f"📌 **2. Address Proof** (Any ONE):\n" \
                         f"   • Aadhaar Card / Voter ID / Passport\n" \
                         f"   • Utility Bill (Electricity / Water Bill)\n" \
                         f"   • Ration Card or Bank Passbook\n\n" \
                         f"📌 **3. Passport Photographs**:\n" \
                         f"   • 2 Recent passport-size photos\n\n" \
                         f"📌 **4. Gold Ornaments**:\n" \
                         f"   • Gold jewellery to pledge (18k to 24k purity)\n\n" \
                         f"⚡ **NO Salary Slip, NO Income Proof, & NO CIBIL Score Check required!** Instant approval and cash payout in just 5 minutes!"
                         
        elif any(w in query_lower for w in ["rate", "interest", "percent", "%", "cost", "charge", "scheme"]):
            answer = f"{boche_greeting}\n\nOur **Gold Loans** offer maximum cash value against your gold ornaments with the highest per-gram valuation!\n\n" \
                     f"• **Interest Rates**: Starting at just **9.9% p.a.**\n" \
                     f"• **Approval Time**: Quick **5-minute approval** with basic KYC (Aadhaar/PAN).\n" \
                     f"• **Safety**: 100% free vault security & full insurance protection for your gold ornaments.\n" \
                     f"• **Repayment**: Pay interest monthly or principal online via our mobile app.\n\n" \
                     f"Remember, every deal with us helps our mission to conquer the world with love! ❤️"

        elif "ncd" in query_lower or "invest" in query_lower or "bond" in query_lower or "prospectus" in query_lower or "return" in query_lower:
            answer = f"{boche_greeting}\n\nOur **Secured Redeemable Non-Convertible Debentures (NCDs)** public issue details from our Prospectus:\n\n" \
                     f"• **Interest Rates**: **11.50% to 13.50% p.a.**\n" \
                     f"• **Payout Options**: Monthly payout, Annual payout, or Cumulative yield options.\n" \
                     f"• **Tenure**: 12, 24, 36, 60, or 84 months.\n" \
                     f"• **Security**: 100% Secured by company receivables & gold loan assets.\n" \
                     f"• **Min Investment**: Rs. 10,000 (10 NCDs @ Rs. 1,000 face value).\n\n" \
                     f"Invest safely with the 160+ year legacy of Boby Chemmanur Group!"

        elif "charity" in query_lower or "trust" in query_lower or "boche" in query_lower or "boby" in query_lower or "food" in query_lower:
            answer = f"{boche_greeting}\n\nI am Dr. Boby Chemmanur (BOCHE)! My guiding principle is **Conquer the World with Love**. Through our BOCHE Fans Charitable Trust:\n\n" \
                     f"• Daily Free Food Counters across cities\n" \
                     f"• World's largest Blood Donor Registry Network\n" \
                     f"• Free Emergency Ambulance Services\n\n" \
                     f"Thank you for your love and support! Love you all!"

        else:
            answer = f"{boche_greeting}\n\nHere is information regarding: *\"{query}\"*\n\n"
            if retrieved:
                for r in retrieved:
                    answer += f"📌 **{r['title']}** ({r['source']}):\n{r['text']}\n\n"
            else:
                answer += "Chemmanur Credits & Investments Limited offers Gold Loans (9.9% p.a.), High Yield NCDs (13.5% p.a.), Microfinance, and Forex services.\n\n"
            answer += "Feel free to ask me more details about Gold Loan documents, NCD schemes, Credit Ratings, Annual Reports, or branch locations!"

        return {
            "answer": answer,
            "citations": retrieved
        }

rag_engine = RAGEngine()
