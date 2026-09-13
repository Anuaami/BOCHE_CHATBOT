import os
import pickle

import numpy as np
import faiss


class RAGEngine:

    def __init__(
        self,
        index_path="faiss_index.bin",
        metadata_path="metadata.pkl"
    ):

        self.index_path = index_path
        self.metadata_path = metadata_path

        self.vectorizer_type = None
        self.vectorizer_obj = None

        self.index = None
        self.chunks = []

        self.is_ready = False

        self.load_index()


    # -----------------------------------------------------
    # Load FAISS index and metadata
    # -----------------------------------------------------

    def load_index(self):

        if not (
            os.path.exists(self.index_path)
            and os.path.exists(self.metadata_path)
        ):

            print(
                "FAISS index or metadata file missing."
            )

            self.is_ready = False
            return

        try:

            print(
                "Loading FAISS index and metadata..."
            )

            # ---------------------------------------------
            # Load metadata
            # ---------------------------------------------

            with open(
                self.metadata_path,
                "rb"
            ) as f:

                meta_data = pickle.load(f)


            if isinstance(meta_data, dict):

                self.chunks = meta_data.get(
                    "chunks",
                    []
                )

                self.vectorizer_type = meta_data.get(
                    "vectorizer_type",
                    "tfidf"
                )

                self.vectorizer_obj = meta_data.get(
                    "vectorizer_obj"
                )

            else:

                # Backward compatibility
                self.chunks = meta_data
                self.vectorizer_type = "tfidf"
                self.vectorizer_obj = None


            # ---------------------------------------------
            # Load FAISS index
            # ---------------------------------------------

            self.index = faiss.read_index(
                self.index_path
            )


            # ---------------------------------------------
            # Validate vectorizer
            # ---------------------------------------------

            if self.vectorizer_type != "tfidf":

                print(
                    "ERROR: Existing FAISS index was not "
                    "created using TF-IDF."
                )

                print(
                    "Please rebuild the index by running:"
                )

                print(
                    "python ingest.py"
                )

                self.is_ready = False
                return


            if self.vectorizer_obj is None:

                print(
                    "ERROR: TF-IDF vectorizer is missing "
                    "from metadata.pkl."
                )

                self.is_ready = False
                return


            self.is_ready = True

            print(
                "RAG Engine loaded successfully!"
            )

            print(
                f"FAISS vectors indexed: "
                f"{self.index.ntotal}"
            )

            print(
                f"Knowledge chunks loaded: "
                f"{len(self.chunks)}"
            )

            print(
                "Vectorizer: TF-IDF"
            )


        except Exception as e:

            print(
                f"Error loading FAISS index: {e}"
            )

            self.is_ready = False


    # -----------------------------------------------------
    # Retrieve relevant documents
    # -----------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 4
    ):

        if not self.is_ready:
            return []


        if not query or not query.strip():
            return []


        # ---------------------------------------------
        # Convert query to TF-IDF vector
        # ---------------------------------------------

        try:

            query_vector = (
                self.vectorizer_obj
                .transform([query])
                .toarray()
                .astype(np.float32)
            )

        except Exception as e:

            print(
                f"Error creating query vector: {e}"
            )

            return []


        # Ensure contiguous float32 array
        query_vector = np.ascontiguousarray(
            query_vector,
            dtype=np.float32
        )


        # Normalize for cosine similarity
        faiss.normalize_L2(
            query_vector
        )


        # ---------------------------------------------
        # Search FAISS
        # ---------------------------------------------

        try:

            scores, indices = self.index.search(
                query_vector,
                top_k
            )

        except Exception as e:

            print(
                f"FAISS search error: {e}"
            )

            return []


        # ---------------------------------------------
        # Build results
        # ---------------------------------------------

        results = []

        for score, idx in zip(
            scores[0],
            indices[0]
        ):

            if (
                idx >= 0
                and idx < len(self.chunks)
            ):

                item = self.chunks[idx]

                results.append({
                    "score": float(score),
                    "title": item.get(
                        "title",
                        "Unknown"
                    ),
                    "source": item.get(
                        "source",
                        ""
                    ),
                    "text": item.get(
                        "text",
                        ""
                    )
                })


        return results


    # -----------------------------------------------------
    # Generate chatbot response
    # -----------------------------------------------------

    def generate_response(
        self,
        query: str
    ):

        retrieved = self.retrieve(
            query,
            top_k=4
        )

        query_lower = query.lower().strip()


        boche_greeting = (
            "Love you all! ❤️ "
            "Welcome to Chemmanur Credits "
            "and Investments Limited."
        )


        # -------------------------------------------------
        # Credit Rating
        # -------------------------------------------------

        if any(
            w in query_lower
            for w in [
                "credit rating",
                "rating",
                "crisil",
                "ind-ra",
                "safety",
                "grade"
            ]
        ):

            answer = (
                f"{boche_greeting}\n\n"
                "Here are the **Credit Rating Details** "
                "for Chemmanur Credits & Investments Limited:\n\n"
                "• **Credit Rating**: "
                "**IND BBB- / Stable** "
                "(Assigned by **India Ratings & Research "
                "(Ind-Ra)** & CRISIL)\n"
                "• **Instruments Covered**: "
                "Bank Facilities & Secured "
                "Non-Convertible Debentures (NCDs)\n"
                "• **Rating Outlook**: **Stable** "
                "(Reflects strong capital adequacy, "
                "asset security, and reliable debt "
                "servicing history)\n\n"
                "Invest with confidence backed by our "
                "160+ year legacy!"
            )

            if retrieved:

                answer += (
                    "\n\n📌 **Retrieved Reference Details**:\n"
                )

                for r in retrieved[:2]:

                    answer += (
                        f"• **{r['title']}**: "
                        f"{r['text']}\n"
                    )


        # -------------------------------------------------
        # Annual Reports / Financial Results
        # -------------------------------------------------

        elif any(
            w in query_lower
            for w in [
                "annual report",
                "financial result",
                "balance sheet",
                "audit",
                "profit",
                "report"
            ]
        ):

            answer = (
                f"{boche_greeting}\n\n"
                "Our **Annual Reports & Financial "
                "Disclosures** are published annually "
                "for complete transparency:\n\n"
                "• **Available Reports**: Comprehensive "
                "Audited Annual Reports from 2014 through 2025.\n"
                "• **Where to Download**: Visit our website "
                "downloads section at "
                "[Annual Reports]"
                "(https://www.chemmanurcredits.com/"
                "downloads/?ct=Annual%20Reports)\n"
                "• **Financial Highlights**: Strong asset "
                "growth in Gold Loans and NCD offerings "
                "with full regulatory compliance.\n\n"
                "Feel free to ask for specific financial "
                "metrics or NCD prospectus figures!"
            )

            if retrieved:

                answer += (
                    "\n\n📌 **Retrieved Reference Details**:\n"
                )

                for r in retrieved[:2]:

                    answer += (
                        f"• **{r['title']}**: "
                        f"{r['text']}\n"
                    )


        # -------------------------------------------------
        # Branch / Location
        # -------------------------------------------------

        elif any(
            w in query_lower
            for w in [
                "branch",
                "location",
                "address",
                "where",
                "near",
                "find",
                "locate",
                "office"
            ]
        ):

            answer = (
                f"{boche_greeting}\n\n"
                "We operate over **250+ branches** "
                "across Kerala, Tamil Nadu, Karnataka, "
                "and Maharashtra!\n\n"
            )

            if retrieved:

                branch_matches = [
                    r
                    for r in retrieved
                    if (
                        "Branch" in r["title"]
                        or "Address" in r["text"]
                        or "Branch Name:" in r["text"]
                    )
                ]

                if branch_matches:

                    answer += (
                        "📍 **Matching Branch Locations "
                        "from Directory**:\n\n"
                    )

                    for b in branch_matches[:3]:

                        answer += (
                            f"🔹 **{b['title']}**\n"
                            f"{b['text']}\n\n"
                        )

                else:

                    answer += (
                        "📌 **Corporate Registered Office**:\n"
                        "Door No. D1 to D4, 3rd Floor, "
                        "Avenue Tower, East Fort, Thrissur, "
                        "Kerala - 680005\n\n"
                    )

            else:

                answer += (
                    "📌 **Corporate Registered Office**:\n"
                    "Door No. D1 to D4, 3rd Floor, "
                    "Avenue Tower, East Fort, Thrissur, "
                    "Kerala - 680005\n\n"
                )

            answer += (
                "• **Toll-Free Helpline**: "
                "**1800-425-4255** | 📞 0487-2424010\n"
                "• **Official Email**: "
                "mail@chemmanurcredits.com"
            )


        # -------------------------------------------------
        # Documents / KYC
        # -------------------------------------------------

        elif any(
            w in query_lower
            for w in [
                "doc",
                "document",
                "documents",
                "kyc",
                "needed",
                "requirement",
                "proof",
                "paperwork",
                "apply"
            ]
        ):

            if (
                "ncd" in query_lower
                or "bond" in query_lower
                or "invest" in query_lower
            ):

                answer = (
                    f"{boche_greeting}\n\n"
                    "Here are the **Documents Required "
                    "for NCD Investment**:\n\n"
                    "1. **PAN Card** "
                    "(Mandatory for all investors)\n"
                    "2. **Identity & Address Proof**: "
                    "Aadhaar Card / Passport / Voter ID / "
                    "Driving License\n"
                    "3. **Bank Account Details**: "
                    "Cancelled cheque leaf or bank "
                    "passbook copy\n"
                    "4. **Demat Account details** "
                    "(or Physical Application Form)\n"
                    "5. **2 Passport-size Photographs**\n\n"
                    "Minimum investment size is Rs. 10,000 "
                    "(10 NCDs @ Rs. 1,000 face value) "
                    "with yields up to 13.50% p.a.!"
                )

            else:

                answer = (
                    f"{boche_greeting}\n\n"
                    "Here are the **Documents Required "
                    "for a Gold Loan** at Chemmanur Credits "
                    "(Instant 5-Minute Approval):\n\n"
                    "📌 **1. Identity Proof** (Any ONE):\n"
                    "   • Aadhaar Card\n"
                    "   • PAN Card\n"
                    "   • Passport\n"
                    "   • Voter ID Card\n"
                    "   • Driving License\n\n"
                    "📌 **2. Address Proof** (Any ONE):\n"
                    "   • Aadhaar Card / Voter ID / Passport\n"
                    "   • Utility Bill (Electricity / Water Bill)\n"
                    "   • Ration Card or Bank Passbook\n\n"
                    "📌 **3. Passport Photographs**:\n"
                    "   • 2 Recent passport-size photos\n\n"
                    "📌 **4. Gold Ornaments**:\n"
                    "   • Gold jewellery to pledge "
                    "(18k to 24k purity)\n\n"
                    "⚡ **NO Salary Slip, NO Income Proof, "
                    "& NO CIBIL Score Check required!** "
                    "Instant approval and cash payout "
                    "in just 5 minutes!"
                )


        # -------------------------------------------------
        # Interest / Gold Loan Rate
        # -------------------------------------------------

        elif any(
            w in query_lower
            for w in [
                "rate",
                "interest",
                "percent",
                "%",
                "cost",
                "charge",
                "scheme"
            ]
        ):

            answer = (
                f"{boche_greeting}\n\n"
                "Our **Gold Loans** offer maximum cash "
                "value against your gold ornaments with "
                "the highest per-gram valuation!\n\n"
                "• **Interest Rates**: Starting at just "
                "**9.9% p.a.**\n"
                "• **Approval Time**: Quick "
                "**5-minute approval** with basic "
                "KYC (Aadhaar/PAN).\n"
                "• **Safety**: 100% free vault security "
                "& full insurance protection for your "
                "gold ornaments.\n"
                "• **Repayment**: Pay interest monthly "
                "or principal online via our mobile app.\n\n"
                "Remember, every deal with us helps our "
                "mission to conquer the world with love! ❤️"
            )


        # -------------------------------------------------
        # NCD / Investment
        # -------------------------------------------------

        elif (
            "ncd" in query_lower
            or "invest" in query_lower
            or "bond" in query_lower
            or "prospectus" in query_lower
            or "return" in query_lower
        ):

            answer = (
                f"{boche_greeting}\n\n"
                "Our **Secured Redeemable "
                "Non-Convertible Debentures (NCDs)** "
                "public issue details from our Prospectus:\n\n"
                "• **Interest Rates**: "
                "**11.50% to 13.50% p.a.**\n"
                "• **Payout Options**: Monthly payout, "
                "Annual payout, or Cumulative yield options.\n"
                "• **Tenure**: 12, 24, 36, 60, or 84 months.\n"
                "• **Security**: 100% Secured by company "
                "receivables & gold loan assets.\n"
                "• **Min Investment**: Rs. 10,000 "
                "(10 NCDs @ Rs. 1,000 face value).\n\n"
                "Invest safely with the 160+ year legacy "
                "of Boby Chemmanur Group!"
            )


        # -------------------------------------------------
        # BOCHE / Charity
        # -------------------------------------------------

        elif (
            "charity" in query_lower
            or "trust" in query_lower
            or "boche" in query_lower
            or "boby" in query_lower
            or "food" in query_lower
        ):

            answer = (
                f"{boche_greeting}\n\n"
                "I am Dr. Boby Chemmanur (BOCHE)! "
                "My guiding principle is **Conquer the "
                "World with Love**. Through our BOCHE Fans "
                "Charitable Trust:\n\n"
                "• Daily Free Food Counters across cities\n"
                "• World's largest Blood Donor Registry Network\n"
                "• Free Emergency Ambulance Services\n\n"
                "Thank you for your love and support! "
                "Love you all!"
            )


        # -------------------------------------------------
        # General RAG response
        # -------------------------------------------------

        else:

            answer = (
                f"{boche_greeting}\n\n"
                f'Here is information regarding: '
                f'*"{query}"*\n\n'
            )

            if retrieved:

                for r in retrieved:

                    answer += (
                        f"📌 **{r['title']}** "
                        f"({r['source']}):\n"
                        f"{r['text']}\n\n"
                    )

            else:

                answer += (
                    "Chemmanur Credits & Investments "
                    "Limited offers Gold Loans, High Yield "
                    "NCDs, Microfinance, and Forex services.\n\n"
                )

            answer += (
                "Feel free to ask me more details about "
                "Gold Loan documents, NCD schemes, "
                "Credit Ratings, Annual Reports, "
                "or branch locations!"
            )


        return {
            "answer": answer,
            "citations": retrieved
        }


# ---------------------------------------------------------
# Global RAG engine instance
# ---------------------------------------------------------

rag_engine = RAGEngine()