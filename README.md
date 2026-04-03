# ⚡ DataSnap Pro — Zenith IN
> AI-Powered Financial OS for Freelancers | v1.0.0

---

## 🚀 Local Setup

```bash
# 1. Clone / unzip the project
cd datasnap_pro

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key
# Edit .streamlit/secrets.toml → paste your key

# 4. Run
streamlit run app.py
```

Open http://localhost:8501

**Demo logins:**
| Username | Password    | Role   |
|----------|-------------|--------|
| admin    | zenith@2026 | Admin  |
| client1  | client1pass | Client |
| client2  | client2pass | Client |

---

## 🏗 Project Structure

```
datasnap_pro/
├── app.py                    ← Main Streamlit app
├── requirements.txt
└── .streamlit/
    └── secrets.toml          ← API keys (never commit)
```

---

## 🔑 Features

| Feature | Status |
|---------|--------|
| USD Mode → LUT / 0% GST | ✅ |
| INR Mode → 18% GST (CGST+SGST) | ✅ |
| TDS 194J / 194C auto-suggest | ✅ |
| Multi-user login | ✅ |
| Professional Excel CA Audit export | ✅ |
| Gemini AI assistant (chat + PDF/image) | ✅ |
| WhatsApp API placeholder (Twilio/WATI) | ✅ |
| Dark Mode Zenith UI | ✅ |

---

## 🌐 Deployment (Streamlit Cloud — FREE)

1. Push to a **private GitHub repo**
2. Go to https://share.streamlit.io → "New app"
3. Select repo + `app.py` as main file
4. In **Advanced settings → Secrets**, paste:
   ```toml
   GEMINI_API_KEY = "your_key_here"
   ```
5. Click Deploy → get a public URL in ~2 min

---

## 💡 Coming Next (Phase 2)

- [ ] Recurring invoice scheduler
- [ ] GSTR-1 / GSTR-3B auto-fill preview
- [ ] Razorpay payment link integration
- [ ] Client portal (each client sees only their invoices)
- [ ] SQLite / Supabase persistent storage
- [ ] Live WhatsApp activation (Twilio/WATI)
- [ ] Stripe payment for SaaS monetization

---

## 💰 Market Launch Plan

### Phase 1 — Soft Launch (Month 1-2)
- Deploy on Streamlit Cloud (free)
- Share in **freelancer Facebook groups**, Reddit r/IndiaFinance, LinkedIn
- Offer free for first 50 users → collect feedback

### Phase 2 — SaaS Monetization (Month 3+)
- Add Stripe/Razorpay subscription: ₹299/mo or ₹2499/yr
- Tiers: Free (5 invoices), Pro (unlimited + AI), Agency (multi-client)
- List on **Product Hunt** for global visibility

### Phase 3 — Growth
- CA / accountant partnerships (white-label)
- API for accounting software integrations
- Mobile app via Flutter or PWA wrapper

---

*Built with ❤️ by Zenith IN*
