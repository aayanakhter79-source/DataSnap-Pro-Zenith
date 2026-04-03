"""
DataSnap Pro - AI-Powered Financial OS for Freelancers
Built by Zenith IN | Version 1.0.0
"""

import streamlit as st
import pandas as pd
import json
import io
import hashlib
from datetime import datetime, date
import google.generativeai as genai
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side, GradientFill
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

# ─────────────────────────────────────────
#  PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────
st.set_page_config(
    page_title="DataSnap Pro | Zenith IN",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("🚀 Zenith Control Panel")
usd_to_inr = st.sidebar.number_input("Current USD to INR Rate", value=92.63, step=0.01)

st.title("🤖 DataSnap Pro")
# ─────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────
USD_TO_INR = 93.08  # April 2026 rate
GST_RATE = 0.18
CGST_RATE = 0.09
SGST_RATE = 0.09

TDS_RATES = {
    "194J – Professional / Technical Services (10%)": 0.10,
    "194J – Royalty / FTS (2%)": 0.02,
    "194C – Contractor (Individual/HUF 1%)": 0.01,
    "194C – Contractor (Company 2%)": 0.02,
    "No TDS": 0.00,
}

# ─────────────────────────────────────────
#  USER DATABASE  (extend to DB as needed)
# ─────────────────────────────────────────
USERS = {
    "admin": {
        "password": hashlib.sha256(b"zenith@2026").hexdigest(),
        "role": "Admin",
        "name": "Admin User",
    },
    "client1": {
        "password": hashlib.sha256(b"client1pass").hexdigest(),
        "role": "Client",
        "name": "Rahul Sharma",
    },
    "client2": {
        "password": hashlib.sha256(b"client2pass").hexdigest(),
        "role": "Client",
        "name": "Priya Mehta",
    },
}


# ─────────────────────────────────────────
#  SMART GEMINI SETUP (Zenith Optimized)
# ─────────────────────────────────────────
@st.cache_resource
def get_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)

        # Bhai ye tera wala smart logic hai jo best model choose karega
        all_m = [
            m.name
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]

        # Agar 1.5-flash milta hai toh thik, nahi toh jo pehla available hai wo le lo
        model_name = (
            "models/gemini-1.5-flash"
            if "models/gemini-1.5-flash" in all_m
            else all_m[0]
        )

        return genai.GenerativeModel(model_name)
    except Exception as e:
        st.error(f"AI Connection Error: {e}")
        return None


# ─────────────────────────────────────────
#  CUSTOM CSS  — Zenith Dark Theme
# ─────────────────────────────────────────
def inject_css():
    st.markdown(
        """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

    :root {
        --black:   #080c10;
        --surface: #0d1117;
        --card:    #111820;
        --border:  #1e2d3d;
        --blue:    #00a3ff;
        --blue2:   #0066cc;
        --white:   #f0f6fc;
        --muted:   #8b98a5;
        --green:   #00e676;
        --red:     #ff5252;
        --gold:    #ffd700;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--black) !important;
        color: var(--white) !important;
        font-family: 'DM Mono', monospace !important;
    }

    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * { color: var(--white) !important; }

    h1,h2,h3 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; }

    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-top: 3px solid var(--blue);
        border-radius: 8px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }
    .metric-label  { font-size: 0.72rem; letter-spacing: 0.12em; color: var(--muted); text-transform: uppercase; }
    .metric-value  { font-size: 1.9rem; font-weight: 700; font-family: 'Syne', sans-serif; color: var(--white); line-height: 1.2; }
    .metric-sub    { font-size: 0.75rem; color: var(--blue); margin-top: 0.2rem; }

    .badge-export  { background: #00332a; color: var(--green);  padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid var(--green); }
    .badge-inr     { background: #2a1a00; color: var(--gold);   padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid var(--gold); }
    .badge-admin   { background: #001833; color: var(--blue);   padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; border: 1px solid var(--blue); }

    .section-header {
        border-left: 3px solid var(--blue);
        padding-left: 0.8rem;
        margin: 1.5rem 0 1rem;
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--white);
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--blue2), var(--blue)) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em !important;
        padding: 0.55rem 1.4rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select,
    .stTextArea textarea {
        background: var(--card) !important;
        color: var(--white) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-family: 'DM Mono', monospace !important;
    }

    [data-testid="stDataFrame"] { background: var(--card) !important; }

    .zenith-logo {
        font-family: 'Syne', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        color: var(--blue);
    }
    .zenith-sub { font-size: 0.68rem; color: var(--muted); letter-spacing: 0.15em; text-transform: uppercase; }

    .whatsapp-preview {
        background: #0a1a0f;
        border: 1px solid #1a4a1a;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-size: 0.82rem;
        color: #cce8cc;
        white-space: pre-wrap;
        font-family: 'DM Mono', monospace;
    }

    .ai-response {
        background: var(--card);
        border: 1px solid var(--border);
        border-left: 3px solid var(--blue);
        border-radius: 8px;
        padding: 1rem 1.2rem;
        font-size: 0.85rem;
        line-height: 1.6;
        color: var(--white);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--muted) !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 0 !important;
        border-bottom: 2px solid transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--blue) !important;
        border-bottom: 2px solid var(--blue) !important;
        background: transparent !important;
    }

    div[data-testid="stAlert"] { border-radius: 6px !important; }
    footer { display: none !important; }
    </style>
    """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def fmt_inr(amount: float) -> str:
    return f"₹{amount:,.2f}"


def fmt_usd(amount: float) -> str:
    return f"${amount:,.2f}"


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


def login_block():
    """Render login UI. Returns True if authenticated."""
    st.markdown(
        """
    <div style='text-align:center; padding: 3rem 0 1.5rem'>
        <div class='zenith-logo'>⚡ ZENITH IN</div>
        <div class='zenith-sub'>DataSnap Pro · Financial OS</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col = st.columns([1, 1.2, 1])[1]
    with col:
        st.markdown("#### Sign In")
        username = st.text_input("Username", key="li_user")
        password = st.text_input("Password", type="password", key="li_pw")
        if st.button("LOGIN  →", use_container_width=True):
            user = USERS.get(username)
            if user and user["password"] == hash_pw(password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["role"] = user["role"]
                st.session_state["display_name"] = user["name"]
                st.rerun()
            else:
                st.error("Invalid credentials.")
        st.markdown(
            """
        <div style='font-size:0.72rem; color:#8b98a5; margin-top:1rem;'>
        Demo → admin / zenith@2026<br>
        Demo → client1 / client1pass
        </div>""",
            unsafe_allow_html=True,
        )
    return False


# ─────────────────────────────────────────
#  INVOICE CALCULATOR CORE
# ─────────────────────────────────────────
def calculate_invoice(mode, base_amount, tds_label, description=""):
    result = {}
    tds_rate = TDS_RATES[tds_label]

    if mode == "USD (Export)":
        inr_amount = base_amount * USD_TO_INR
        result = {
            "mode": "USD – Export of Service",
            "usd_amount": base_amount,
            "inr_amount": inr_amount,
            "gst_type": "LUT / Export – 0% GST",
            "cgst": 0.0,
            "sgst": 0.0,
            "total_gst": 0.0,
            "taxable_value": inr_amount,
            "tds_rate": tds_rate,
            "tds_amount": inr_amount * tds_rate,
            "net_receivable": inr_amount - (inr_amount * tds_rate),
            "exchange_rate": USD_TO_INR,
        }
    else:
        cgst = base_amount * CGST_RATE
        sgst = base_amount * SGST_RATE
        total_gst = cgst + sgst
        invoice_total = base_amount + total_gst
        tds_amount = base_amount * tds_rate
        result = {
            "mode": "INR – Domestic",
            "usd_amount": None,
            "inr_amount": base_amount,
            "gst_type": "18% GST (CGST 9% + SGST 9%)",
            "cgst": cgst,
            "sgst": sgst,
            "total_gst": total_gst,
            "taxable_value": base_amount,
            "invoice_total": invoice_total,
            "tds_rate": tds_rate,
            "tds_amount": tds_amount,
            "net_receivable": invoice_total - tds_amount,
            "exchange_rate": None,
        }
    result["description"] = description
    result["date"] = datetime.now().strftime("%d %b %Y")
    return result


# ─────────────────────────────────────────
#  WHATSAPP MOCK
# ─────────────────────────────────────────
def whatsapp_message(inv: dict, client_name: str, phone: str) -> str:
    lines = [
        f"👋 Hello {client_name}!",
        f"",
        f"📋 *Invoice Summary — DataSnap Pro*",
        f"🗓  Date: {inv['date']}",
        f"📝 Desc: {inv.get('description','—')}",
        f"",
        f"💰 Mode: {inv['mode']}",
    ]
    if inv.get("usd_amount"):
        lines.append(
            f"   USD: {fmt_usd(inv['usd_amount'])} → {fmt_inr(inv['inr_amount'])}"
        )
    else:
        lines.append(f"   Taxable: {fmt_inr(inv['inr_amount'])}")
        lines.append(f"   GST (18%): {fmt_inr(inv['total_gst'])}")
        lines.append(
            f"   Invoice Total: {fmt_inr(inv.get('invoice_total', inv['inr_amount']))}"
        )

    if inv["tds_amount"] > 0:
        lines.append(
            f"   TDS: {fmt_inr(inv['tds_amount'])} ({inv['tds_rate']*100:.0f}%)"
        )
    lines += [
        f"",
        f"✅ *Net Receivable: {fmt_inr(inv['net_receivable'])}*",
        f"",
        f"Powered by ⚡ Zenith IN / DataSnap Pro",
    ]
    return "\n".join(lines)


def send_whatsapp_placeholder(phone: str, message: str):
    """
    PLACEHOLDER — replace with real Twilio/WATI call.

    Twilio example:
        from twilio.rest import Client
        client = Client(st.secrets["TWILIO_SID"], st.secrets["TWILIO_TOKEN"])
        client.messages.create(
            from_='whatsapp:+14155238886',
            to=f'whatsapp:{phone}',
            body=message
        )

    WATI example:
        requests.post(
            f"https://api.wati.io/api/v1/sendSessionMessage/{phone}",
            headers={"Authorization": f"Bearer {st.secrets['WATI_TOKEN']}"},
            json={"messageText": message}
        )
    """
    return {"status": "mock_sent", "to": phone, "chars": len(message)}


# ─────────────────────────────────────────
#  EXCEL EXPORT
# ─────────────────────────────────────────
def build_excel(invoices: list[dict], owner_name: str) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "CA Audit Report"

    # Colours
    BG_DARK = "0D1117"
    BG_HEADER = "0A2540"
    BLUE = "00A3FF"
    WHITE = "F0F6FC"
    MUTED = "8B98A5"
    GREEN = "00E676"
    GOLD = "FFD700"
    RED = "FF5252"

    def cell_style(
        ws,
        row,
        col,
        value,
        bold=False,
        fg=WHITE,
        bg=BG_DARK,
        align="left",
        num_fmt=None,
        size=10,
    ):
        c = ws.cell(row=row, column=col, value=value)
        c.font = Font(name="Calibri", bold=bold, color=fg, size=size)
        c.fill = PatternFill("solid", fgColor=bg)
        c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)
        thin = Side(style="thin", color="1E2D3D")
        c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        if num_fmt:
            c.number_format = num_fmt
        return c

    # ── Title block ──────────────────────────────────────────────────────────
    ws.merge_cells("A1:L1")
    cell_style(
        ws,
        1,
        1,
        "⚡  DataSnap Pro  |  CA Audit Report  |  Zenith IN",
        bold=True,
        fg=BLUE,
        bg="080C10",
        align="center",
        size=14,
    )
    ws.row_dimensions[1].height = 30

    ws.merge_cells("A2:L2")
    cell_style(
        ws,
        2,
        1,
        f"Prepared for: {owner_name}   |   Generated: {datetime.now().strftime('%d %b %Y %H:%M')}   |   Exchange Rate: ₹{USD_TO_INR} / USD",
        fg=MUTED,
        bg="080C10",
        align="center",
        size=9,
    )
    ws.row_dimensions[2].height = 18

    # ── Column headers ───────────────────────────────────────────────────────
    headers = [
        "#",
        "Date",
        "Description",
        "Mode",
        "USD Amount",
        "INR (Taxable)",
        "CGST (9%)",
        "SGST (9%)",
        "GST Total",
        "Invoice Total",
        "TDS Amount",
        "Net Receivable",
    ]
    col_widths = [5, 14, 32, 20, 14, 16, 12, 12, 12, 14, 12, 16]

    for i, (h, w) in enumerate(zip(headers, col_widths), 1):
        cell_style(
            ws, 3, i, h, bold=True, fg=BLUE, bg=BG_HEADER, align="center", size=10
        )
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[3].height = 22

    # ── Data rows ────────────────────────────────────────────────────────────
    totals = dict(usd=0, inr=0, cgst=0, sgst=0, gst=0, inv_total=0, tds=0, net=0)

    for idx, inv in enumerate(invoices, 1):
        r = idx + 3
        bg = BG_DARK if idx % 2 == 0 else "0F161F"
        is_usd = inv.get("usd_amount") is not None
        inv_total = inv.get("invoice_total", inv["inr_amount"])

        vals = [
            idx,
            inv["date"],
            inv.get("description", "—"),
            inv["mode"],
            inv["usd_amount"] if is_usd else "—",
            inv["inr_amount"],
            inv["cgst"],
            inv["sgst"],
            inv["total_gst"],
            inv_total,
            inv["tds_amount"],
            inv["net_receivable"],
        ]
        fmts = [
            None,
            None,
            None,
            None,
            "[$$-en-US]#,##0.00",
            "₹#,##0.00",
            "₹#,##0.00",
            "₹#,##0.00",
            "₹#,##0.00",
            "₹#,##0.00",
            "₹#,##0.00",
            "₹#,##0.00",
        ]
        fgs = [
            MUTED,
            MUTED,
            WHITE,
            (GOLD if is_usd else GREEN),
            WHITE,
            WHITE,
            WHITE,
            WHITE,
            WHITE,
            WHITE,
            RED,
            GREEN,
        ]

        for ci, (v, fmt, fg) in enumerate(zip(vals, fmts, fgs), 1):
            cell_style(
                ws,
                r,
                ci,
                v,
                fg=fg,
                bg=bg,
                num_fmt=fmt,
                align="right" if ci > 4 else "left",
            )

        # accumulate totals
        totals["usd"] += inv["usd_amount"] or 0
        totals["inr"] += inv["inr_amount"]
        totals["cgst"] += inv["cgst"]
        totals["sgst"] += inv["sgst"]
        totals["gst"] += inv["total_gst"]
        totals["inv_total"] += inv_total
        totals["tds"] += inv["tds_amount"]
        totals["net"] += inv["net_receivable"]

    # ── Totals row ────────────────────────────────────────────────────────────
    tr = len(invoices) + 4
    ws.row_dimensions[tr].height = 22
    total_vals = [
        "",
        "TOTALS",
        "",
        "",
        totals["usd"],
        totals["inr"],
        totals["cgst"],
        totals["sgst"],
        totals["gst"],
        totals["inv_total"],
        totals["tds"],
        totals["net"],
    ]
    total_fmts = [
        None,
        None,
        None,
        None,
        "[$$-en-US]#,##0.00",
        "₹#,##0.00",
        "₹#,##0.00",
        "₹#,##0.00",
        "₹#,##0.00",
        "₹#,##0.00",
        "₹#,##0.00",
        "₹#,##0.00",
    ]
    for ci, (v, fmt) in enumerate(zip(total_vals, total_fmts), 1):
        cell_style(
            ws,
            tr,
            ci,
            v,
            bold=True,
            fg=BLUE,
            bg=BG_HEADER,
            num_fmt=fmt,
            align="right" if ci > 4 else "left",
            size=11,
        )

    # ── Summary sheet ─────────────────────────────────────────────────────────
    ws2 = wb.create_sheet("Summary")
    ws2.sheet_view.showGridLines = False

    summary_data = [
        ("METRIC", "AMOUNT", "NOTES"),
        ("Total Invoices", len(invoices), "Count"),
        ("Total Revenue (INR)", totals["inr"], "Taxable value"),
        ("Total GST Liability", totals["gst"], "CGST + SGST"),
        ("  ↳ CGST (9%)", totals["cgst"], "Central GST"),
        ("  ↳ SGST (9%)", totals["sgst"], "State GST"),
        ("TDS Receivable", totals["tds"], "To be claimed in ITR"),
        ("Net Receivable", totals["net"], "After TDS deduction"),
        ("USD Revenue", totals["usd"], "Export of Service (LUT)"),
    ]
    for ri, row in enumerate(summary_data, 1):
        for ci, val in enumerate(row, 1):
            is_hdr = ri == 1
            bg = BG_HEADER if is_hdr else (BG_DARK if ri % 2 == 0 else "0F161F")
            fg = BLUE if is_hdr else (GREEN if ci == 2 and ri > 1 else WHITE)
            fmt = (
                "₹#,##0.00"
                if (ci == 2 and ri not in [1, 2, 9])
                else ("[$$-en-US]#,##0.00" if (ci == 2 and ri == 9) else None)
            )
            c = cell_style(
                ws2,
                ri,
                ci,
                val,
                bold=is_hdr,
                fg=fg,
                bg=bg,
                num_fmt=fmt,
                align="right" if ci == 2 else "left",
            )
        ws2.row_dimensions[ri].height = 20
    for ci, w in [(1, 30), (2, 20), (3, 30)]:
        ws2.column_dimensions[get_column_letter(ci)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
        <div style='padding:1rem 0 0.5rem'>
            <div class='zenith-logo'>⚡ ZENITH IN</div>
            <div class='zenith-sub'>DataSnap Pro v1.0</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.divider()

        name = st.session_state.get("display_name", "User")
        role = st.session_state.get("role", "Client")
        badge = "badge-admin" if role == "Admin" else "badge-inr"
        st.markdown(
            f"""
        <div style='margin-bottom:1rem'>
            <div style='font-size:0.8rem; color:#8b98a5'>Logged in as</div>
            <div style='font-size:1rem; font-weight:700'>{name}</div>
            <span class='{badge}'>{role}</span>
        </div>
        """,
            unsafe_allow_html=True,
        )

        pages = [
            "📊 Dashboard",
            "🧾 New Invoice",
            "📁 Invoice History",
            "🤖 AI Assistant",
            "📤 Export & WhatsApp",
        ]
        if role == "Admin":
            pages.append("👥 Admin Panel")

        page = st.radio("Navigation", pages, label_visibility="collapsed")

        st.divider()
        st.markdown(
            f"""
        <div style='font-size:0.72rem; color:#8b98a5'>
            💱 Rate: ₹{USD_TO_INR} / USD<br>
            📅 {date.today().strftime('%d %b %Y')}<br>
            🔒 Session active
        </div>
        """,
            unsafe_allow_html=True,
        )

        if st.button("Logout", use_container_width=True):
            for key in ["authenticated", "username", "role", "display_name"]:
                st.session_state.pop(key, None)
            st.rerun()

    return page


# ─────────────────────────────────────────
#  PAGE: DASHBOARD
# ─────────────────────────────────────────
def page_dashboard():
    st.markdown("<h2>📊 Financial Dashboard</h2>", unsafe_allow_html=True)

    invoices = st.session_state.get("invoices", [])

    total_rev = sum(i["inr_amount"] for i in invoices)
    total_gst = sum(i["total_gst"] for i in invoices)
    total_tds = sum(i["tds_amount"] for i in invoices)
    total_net = sum(i["net_receivable"] for i in invoices)
    usd_invoices = [i for i in invoices if i.get("usd_amount")]

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, sub in [
        (c1, "TOTAL REVENUE", fmt_inr(total_rev), f"{len(invoices)} invoices"),
        (c2, "GST LIABILITY", fmt_inr(total_gst), "CGST + SGST (18%)"),
        (c3, "TDS RECEIVABLE", fmt_inr(total_tds), "Claim in ITR"),
        (c4, "NET RECEIVABLE", fmt_inr(total_net), "After TDS deduction"),
    ]:
        with col:
            st.markdown(
                f"""
            <div class='metric-card'>
                <div class='metric-label'>{label}</div>
                <div class='metric-value'>{value}</div>
                <div class='metric-sub'>{sub}</div>
            </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            "<div class='section-header'>Revenue Breakdown</div>",
            unsafe_allow_html=True,
        )
        if invoices:
            df_chart = pd.DataFrame(
                {
                    "Invoice": [f"#{i+1}" for i in range(len(invoices))],
                    "Taxable (₹)": [inv["inr_amount"] for inv in invoices],
                    "GST (₹)": [inv["total_gst"] for inv in invoices],
                    "TDS (₹)": [inv["tds_amount"] for inv in invoices],
                }
            ).set_index("Invoice")
            st.bar_chart(df_chart, height=220)
        else:
            st.info("No invoices yet. Create your first invoice →")

    with col_b:
        st.markdown(
            "<div class='section-header'>Export vs Domestic</div>",
            unsafe_allow_html=True,
        )
        export_rev = sum(i["inr_amount"] for i in invoices if i.get("usd_amount"))
        domestic_rev = sum(i["inr_amount"] for i in invoices if not i.get("usd_amount"))
        df_pie = pd.DataFrame(
            {
                "Category": ["Export (USD→INR)", "Domestic (INR)"],
                "Amount": [export_rev, domestic_rev],
            }
        )
        if export_rev + domestic_rev > 0:
            st.bar_chart(df_pie.set_index("Category"), height=220)
        else:
            st.info("Invoice data will appear here.")

    if usd_invoices:
        st.markdown(
            "<div class='section-header'>🌐 Export of Service Summary (LUT)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """<span class='badge-export'>0% GST — LUT Filed</span>
        <span style='font-size:0.78rem; color:#8b98a5; margin-left:8px'>
        All USD invoices qualify as Export of Service under IGST Act Section 16(1)(a)</span>""",
            unsafe_allow_html=True,
        )
        usd_df = pd.DataFrame(
            [
                {
                    "Date": i["date"],
                    "USD": fmt_usd(i["usd_amount"]),
                    "INR Equivalent": fmt_inr(i["inr_amount"]),
                    "Description": i.get("description", "—"),
                }
                for i in usd_invoices
            ]
        )
        st.dataframe(usd_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────
#  PAGE: NEW INVOICE
# ─────────────────────────────────────────
def page_new_invoice():
    st.markdown("<h2>🧾 Create Invoice</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown(
            "<div class='section-header'>Invoice Details</div>", unsafe_allow_html=True
        )
        mode = st.selectbox("Currency Mode", ["USD (Export)", "INR (Domestic)"])
        description = st.text_input(
            "Description / Client Name", placeholder="e.g. Web Dev – Acme Corp Q1"
        )
        amount = st.number_input(
            f"Amount ({'USD' if 'USD' in mode else 'INR'})",
            min_value=0.0,
            value=1000.0,
            step=100.0,
            format="%.2f",
        )
        tds_label = st.selectbox("TDS Section", list(TDS_RATES.keys()))

        if st.button("⚡  Calculate Invoice", use_container_width=True):
            inv = calculate_invoice(mode, amount, tds_label, description)
            st.session_state["current_invoice"] = inv

            invoices = st.session_state.get("invoices", [])
            invoices.append(inv)
            st.session_state["invoices"] = invoices
            st.success("Invoice calculated and saved!")

    with col2:
        st.markdown(
            "<div class='section-header'>Live Preview</div>", unsafe_allow_html=True
        )
        inv = st.session_state.get("current_invoice")
        if inv:
            is_usd = inv.get("usd_amount") is not None
            badge_html = (
                "<span class='badge-export'>EXPORT / LUT</span>"
                if is_usd
                else "<span class='badge-inr'>DOMESTIC / GST</span>"
            )
            st.markdown(badge_html, unsafe_allow_html=True)

            rows = []
            if is_usd:
                rows = [
                    ("USD Amount", fmt_usd(inv["usd_amount"])),
                    ("Exchange Rate", f"₹{USD_TO_INR}"),
                    ("INR Equivalent", fmt_inr(inv["inr_amount"])),
                    ("GST", inv["gst_type"]),
                    ("TDS", fmt_inr(inv["tds_amount"])),
                    ("✅ Net Receivable", fmt_inr(inv["net_receivable"])),
                ]
            else:
                rows = [
                    ("Taxable Value", fmt_inr(inv["inr_amount"])),
                    ("CGST (9%)", fmt_inr(inv["cgst"])),
                    ("SGST (9%)", fmt_inr(inv["sgst"])),
                    ("Total GST", fmt_inr(inv["total_gst"])),
                    ("Invoice Total", fmt_inr(inv.get("invoice_total", 0))),
                    ("TDS Deduction", fmt_inr(inv["tds_amount"])),
                    ("✅ Net Receivable", fmt_inr(inv["net_receivable"])),
                ]

            df = pd.DataFrame(rows, columns=["Field", "Value"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Fill the form and calculate to see preview.")


# ─────────────────────────────────────────
#  PAGE: INVOICE HISTORY
# ─────────────────────────────────────────
def page_history():
    st.markdown("<h2>📁 Invoice History</h2>", unsafe_allow_html=True)
    invoices = st.session_state.get("invoices", [])
    if not invoices:
        st.info("No invoices yet. Head to 'New Invoice' to create one.")
        return

    rows = []
    for i, inv in enumerate(invoices, 1):
        rows.append(
            {
                "#": i,
                "Date": inv["date"],
                "Description": inv.get("description", "—"),
                "Mode": inv["mode"],
                "Taxable (₹)": inv["inr_amount"],
                "GST (₹)": inv["total_gst"],
                "TDS (₹)": inv["tds_amount"],
                "Net (₹)": inv["net_receivable"],
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if st.button("🗑  Clear All Invoices"):
        st.session_state["invoices"] = []
        st.rerun()


# ─────────────────────────────────────────
#  PAGE: AI ASSISTANT
# ─────────────────────────────────────────
def page_ai():
    st.markdown("<h2>🤖 AI Financial Assistant</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div style='color:#8b98a5; font-size:0.82rem'>Powered by Gemini 1.5 Flash · Multi-modal (PDF/Image support)</div>",
        unsafe_allow_html=True,
    )

    model = get_gemini()
    if not model:
        st.warning(
            "⚠️ GEMINI_API_KEY not found in Streamlit Secrets. Add it via Settings → Secrets → `GEMINI_API_KEY = 'your_key'`"
        )
        return

    tabs = st.tabs(["💬 Chat Query", "📄 Upload Document"])

    with tabs[0]:
        query = st.text_area(
            "Ask anything about GST, TDS, invoicing, ITR...",
            placeholder="e.g. Should I file GSTR-1 monthly or quarterly? What is Section 44ADA?",
            height=100,
        )
        invoices = st.session_state.get("invoices", [])
        context = ""
        if invoices:
            total_rev = sum(i["inr_amount"] for i in invoices)
            total_gst = sum(i["total_gst"] for i in invoices)
            context = f"\n\nUser context: {len(invoices)} invoices, Total Revenue ₹{total_rev:,.2f}, GST Liability ₹{total_gst:,.2f}."

        if st.button("Ask Gemini ⚡"):
            if query.strip():
                with st.spinner("Consulting AI..."):
                    system = (
                        "You are DataSnap Pro's AI financial advisor for Indian freelancers. "
                        "Provide concise, accurate advice on GST, TDS, ITR, invoicing. "
                        "Always mention relevant sections/rules. Be friendly but professional."
                        + context
                    )
                    resp = model.generate_content(system + "\n\nUser: " + query)
                    st.markdown(
                        f"<div class='ai-response'>{resp.text}</div>",
                        unsafe_allow_html=True,
                    )

    with tabs[1]:
        uploaded = st.file_uploader(
            "Upload Invoice PDF or Image", type=["pdf", "png", "jpg", "jpeg"]
        )
        if uploaded:
            file_bytes = uploaded.read()
            mime = uploaded.type
            st.success(f"File received: {uploaded.name} ({len(file_bytes)//1024} KB)")

            if st.button("🔍 Analyse with Gemini"):
                with st.spinner("Processing document..."):
                    import base64

                    b64 = base64.standard_b64encode(file_bytes).decode()
                    parts = [
                        {"inline_data": {"mime_type": mime, "data": b64}},
                        {
                            "text": "Extract all financial data from this document: invoice number, date, amounts, GST, TDS, client details. Present in a clean structured format."
                        },
                    ]
                    resp = model.generate_content(parts)
                    st.markdown(
                        f"<div class='ai-response'>{resp.text}</div>",
                        unsafe_allow_html=True,
                    )


# ─────────────────────────────────────────
#  PAGE: EXPORT & WHATSAPP
# ─────────────────────────────────────────
def page_export():
    st.markdown("<h2>📤 Export & Notifications</h2>", unsafe_allow_html=True)
    invoices = st.session_state.get("invoices", [])

    tabs = st.tabs(["📊 Excel Report", "💬 WhatsApp Notification"])

    with tabs[0]:
        st.markdown(
            "<div class='section-header'>CA Audit Excel Report</div>",
            unsafe_allow_html=True,
        )
        if not invoices:
            st.info("Create some invoices first.")
        else:
            owner = st.text_input(
                "Owner / Freelancer Name",
                value=st.session_state.get("display_name", ""),
            )
            if st.button("Generate Excel Report ⬇"):
                xls_bytes = build_excel(invoices, owner)
                st.download_button(
                    label="📥 Download Excel",
                    data=xls_bytes,
                    file_name=f"DataSnap_Pro_Audit_{date.today().isoformat()}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
                st.success("Report ready! Formatted for CA audit submission.")

    with tabs[1]:
        st.markdown(
            "<div class='section-header'>WhatsApp Summary (API Placeholder)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """
        <div style='background:#0a1833; border:1px solid #1e2d3d; border-radius:8px; padding:0.9rem 1.1rem; margin-bottom:1rem; font-size:0.78rem; color:#8b98a5'>
        ℹ️  This feature is pre-wired for <b style='color:#00a3ff'>Twilio</b> or <b style='color:#00a3ff'>WATI</b> WhatsApp API.
        To activate: add <code>TWILIO_SID</code>, <code>TWILIO_TOKEN</code>, or <code>WATI_TOKEN</code> in Streamlit Secrets
        and uncomment the live code in <code>send_whatsapp_placeholder()</code>.
        </div>
        """,
            unsafe_allow_html=True,
        )

        phone = st.text_input("Client WhatsApp Number", placeholder="+91XXXXXXXXXX")
        c_name = st.text_input("Client Name", value="Client")
        inv_sel = st.session_state.get("current_invoice")

        if not inv_sel and invoices:
            inv_sel = invoices[-1]

        if inv_sel:
            msg = whatsapp_message(inv_sel, c_name, phone)
            st.markdown("**Message Preview:**")
            st.markdown(
                f"<div class='whatsapp-preview'>{msg}</div>", unsafe_allow_html=True
            )

            if st.button("📲 Send WhatsApp (Mock)"):
                result = send_whatsapp_placeholder(phone, msg)
                st.success(
                    f"✅ Mock sent to {result['to']}  |  {result['chars']} chars  |  Status: {result['status']}"
                )
                st.info(
                    "To go live: uncomment Twilio/WATI code in send_whatsapp_placeholder()."
                )
        else:
            st.info("Create an invoice first to generate a WhatsApp summary.")


# ─────────────────────────────────────────
#  PAGE: ADMIN PANEL
# ─────────────────────────────────────────
def page_admin():
    st.markdown("<h2>👥 Admin Panel</h2>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header'>Registered Users</div>", unsafe_allow_html=True
    )
    df = pd.DataFrame(
        [
            {"Username": u, "Name": d["name"], "Role": d["role"]}
            for u, d in USERS.items()
        ]
    )
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.info(
        "To add users, edit the USERS dict in app.py or wire to a database (SQLite / Supabase)."
    )

    st.markdown(
        "<div class='section-header'>System Config</div>", unsafe_allow_html=True
    )
    st.json(
        {
            "USD_TO_INR": USD_TO_INR,
            "GST_RATE": f"{int(GST_RATE*100)}%",
            "CGST": f"{int(CGST_RATE*100)}%",
            "SGST": f"{int(SGST_RATE*100)}%",
            "Gemini_Model": "gemini-1.5-flash",
        }
    )


# ─────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────
def main():
    inject_css()

    if "invoices" not in st.session_state:
        st.session_state["invoices"] = []

    if not st.session_state.get("authenticated"):
        login_block()
        return

    page = render_sidebar()

    if "Dashboard" in page:
        page_dashboard()
    elif "Invoice" in page:
        page_new_invoice()
    elif "History" in page:
        page_history()
    elif "AI" in page:
        page_ai()
    elif "Export" in page:
        page_export()
    elif "Admin" in page:
        page_admin()


if __name__ == "__main__":
    main()
