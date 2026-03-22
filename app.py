import streamlit as st
import anthropic
import requests
import base64
import re
import json
from io import BytesIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeForge",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0a0a0f 0%, #0d1117 50%, #0a0f1a 100%);
    color: #e8e4dc;
}

/* Header */
.forge-header {
    text-align: center;
    padding: 2rem 0 1rem;
}
.forge-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f0ece4, #93c5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
}
.forge-subtitle {
    color: #9ca3af;
    font-size: 0.95rem;
}

/* Mode cards */
.mode-card {
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 1.2rem;
    background: rgba(255,255,255,0.02);
    cursor: pointer;
    transition: all 0.2s;
    height: 100%;
}
.mode-card:hover { border-color: rgba(255,255,255,0.2); }
.mode-card.selected-blue { border-color: rgba(59,130,246,0.5); background: rgba(59,130,246,0.06); }
.mode-card.selected-purple { border-color: rgba(139,92,246,0.5); background: rgba(139,92,246,0.06); }

/* Step badge */
.step-badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.badge-blue { background: rgba(59,130,246,0.12); color: #93c5fd; border: 1px solid rgba(59,130,246,0.25); }
.badge-purple { background: rgba(139,92,246,0.12); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.25); }
.badge-amber { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
.badge-green { background: rgba(134,239,172,0.1); color: #86efac; border: 1px solid rgba(134,239,172,0.2); }

/* Info boxes */
.info-box {
    border-radius: 10px;
    padding: 0.85rem 1rem;
    font-size: 0.82rem;
    line-height: 1.6;
    margin: 0.5rem 0;
}
.info-purple { background: rgba(139,92,246,0.06); border: 1px solid rgba(139,92,246,0.18); color: #c4b5fd; }
.info-amber { background: rgba(245,158,11,0.06); border: 1px solid rgba(245,158,11,0.18); color: #fbbf24; }
.info-green { background: rgba(78,205,196,0.05); border: 1px solid rgba(78,205,196,0.15); color: #6ee7b7; }
.info-red { background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2); color: #f87171; }

/* LaTeX preview box */
.latex-box {
    background: #0d1117;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 1rem;
    font-family: 'Courier New', monospace;
    font-size: 0.75rem;
    color: #86efac;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-all;
}

/* Recruiter card */
.recruiter-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
}
.recruiter-name { font-size: 1rem; font-weight: 600; color: #f0ece4; }
.recruiter-title { font-size: 0.82rem; color: #fbbf24; margin-bottom: 0.5rem; }
.recruiter-detail { font-size: 0.78rem; color: #9ca3af; }
.recruiter-detail a { color: #86efac; text-decoration: none; }

/* Credit badge */
.credit-badge {
    display: inline-block;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 4px;
    padding: 1px 8px;
    font-size: 0.7rem;
    color: #6b7280;
    margin-left: 8px;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1.5rem 0;
}

/* Override streamlit elements */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background-color: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e8e4dc !important;
    border-radius: 8px !important;
}
.stButton > button {
    border-radius: 9px !important;
    font-weight: 500 !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e40af, #2563eb) !important;
    border: none !important;
    color: white !important;
}

/* File uploader */
.stFileUploader {
    border: 2px dashed rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    background: rgba(255,255,255,0.02) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.02);
    border-radius: 10px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: #9ca3af;
}
.stTabs [aria-selected="true"] {
    background: rgba(59,130,246,0.15) !important;
    color: #93c5fd !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
LATEX_SYSTEM_PROMPT = """You are an expert resume writer and LaTeX typesetter. Given a job description and resume, output ONLY a complete compilable LaTeX resume. No explanation, no markdown fences.

CRITICAL RULES FOR SPECIAL CHARACTERS:
- NEVER use the ₹ symbol — write Rs. or INR instead, e.g. "Rs. 40 Lakhs"
- NEVER use € £ ¥ symbols — write EUR, GBP, JPY instead
- Use --- for em dash, -- for en dash
- Stick to plain ASCII text in content

Use exactly this preamble:
\\documentclass[10pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{enumitem}
\\usepackage{titlesec}
\\usepackage[hidelinks]{hyperref}
\\usepackage{parskip}
\\usepackage{xcolor}
\\usepackage{textcomp}
\\definecolor{accent}{RGB}{30,64,175}
\\titleformat{\\section}{\\large\\bfseries\\color{accent}}{}{0em}{}[\\titlerule]
\\titlespacing{\\section}{0pt}{8pt}{4pt}
\\setlist[itemize]{noitemsep,topsep=2pt,leftmargin=*}
\\begin{document}\\pagestyle{empty}
...
\\end{document}

Rules: mirror job description language, strong action verbs, quantified results, 1 page, ATS-friendly. Output ONLY raw LaTeX starting with \\documentclass"""

SCRATCH_SYSTEM_PROMPT = """You are an expert resume writer and LaTeX typesetter. Generate a complete professional resume FROM SCRATCH using a job description and optional personal details. Invent plausible realistic details for anything missing. 2-3 relevant past jobs, strong bullet points, education, skills. Output ONLY compilable LaTeX.

CRITICAL RULES FOR SPECIAL CHARACTERS:
- NEVER use ₹ — write Rs. or INR instead
- NEVER use € £ ¥ — write EUR, GBP, JPY instead
- Use --- for em dash, -- for en dash

Use exactly this preamble:
\\documentclass[10pt,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[margin=0.75in]{geometry}
\\usepackage{enumitem}
\\usepackage{titlesec}
\\usepackage[hidelinks]{hyperref}
\\usepackage{parskip}
\\usepackage{xcolor}
\\usepackage{textcomp}
\\definecolor{accent}{RGB}{109,40,217}
\\titleformat{\\section}{\\large\\bfseries\\color{accent}}{}{0em}{}[\\titlerule]
\\titlespacing{\\section}{0pt}{8pt}{4pt}
\\setlist[itemize]{noitemsep,topsep=2pt,leftmargin=*}
\\begin{document}\\pagestyle{empty}
...
\\end{document}

1 page, ATS-friendly. Output ONLY raw LaTeX starting with \\documentclass"""


# ── Helper functions ──────────────────────────────────────────────────────────
def sanitize_latex(tex: str) -> str:
    """Replace Unicode characters that break pdflatex."""
    replacements = {
        '₹': 'Rs.',
        '€': 'EUR ',
        '£': 'GBP ',
        '¥': 'JPY ',
        '°': r'\textdegree{}',
        '©': r'\textcopyright{}',
        '®': r'\textregistered{}',
        '™': r'\texttrademark{}',
        '–': '--',
        '—': '---',
        '\u2018': '`',
        '\u2019': "'",
        '\u201c': '``',
        '\u201d': "''",
        '…': '...',
        '×': 'x',
        '→': '->',
        '•': r'\textbullet{}',
    }
    for char, replacement in replacements.items():
        tex = tex.replace(char, replacement)
    # Strip remaining non-ASCII that inputenc can't handle
    result = []
    for char in tex:
        code = ord(char)
        if code <= 0x7F or (0xC0 <= code <= 0x024F):
            result.append(char)
        # else: drop it
    return ''.join(result)


def call_claude(system: str, user: str, api_key: str) -> str:
    """Call Claude API and return text response."""
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    text = message.content[0].text if message.content else ""
    # Strip any accidental markdown fences
    text = re.sub(r'```latex\n?', '', text)
    text = re.sub(r'```\n?', '', text)
    return text.strip()


def extract_text_from_pdf(pdf_bytes: bytes, api_key: str = None) -> str:
    """Extract text from PDF using pypdf (local, no API cost)."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(BytesIO(pdf_bytes))
        pages = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
        extracted = "\n\n".join(pages)
        if extracted.strip():
            return extracted
        return ""
    except Exception as e:
        raise Exception(f"Could not read PDF: {str(e)}. Please paste your resume text manually instead.")


def search_apollo(api_key: str, company: str, location: str = "") -> list:
    """Search Apollo.io for recruiters at a company. Returns list of contacts."""
    search_body = {
        "api_key": api_key,
        "q_organization_name": company,
        "person_titles": [
            "HR", "Recruiter", "Talent Acquisition", "Human Resources",
            "Hiring Manager", "People Operations", "HR Manager",
            "Technical Recruiter", "Campus Recruiter", "Recruiting Manager"
        ],
        "page": 1,
        "per_page": 3,  # Cap at 3 to save free tier credits
    }
    if location:
        search_body["person_locations"] = [location]

    try:
        resp = requests.post(
            "https://api.apollo.io/v1/mixed_people/search",
            json=search_body,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        resp.raise_for_status()
        return resp.json().get("people", [])
    except Exception as e:
        raise Exception(f"Apollo search failed: {str(e)}")


def enrich_person(apollo_key: str, person_id: str) -> dict:
    """Enrich a person record to get email/phone."""
    try:
        resp = requests.post(
            "https://api.apollo.io/v1/people/match",
            json={"api_key": apollo_key, "id": person_id, "reveal_personal_emails": False},
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        if resp.ok:
            return resp.json().get("person", {})
    except:
        pass
    return {}


def generate_outreach_email(api_key: str, recruiter: dict, job_role: str, company: str,
                             job_description: str, your_name: str, your_email: str) -> str:
    """Generate a personalised cold outreach email."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""Write a professional, warm, concise cold outreach email from a job applicant to a recruiter.

Candidate name: {your_name or 'the candidate'}
Candidate email: {your_email or 'not provided'}
Applying for: {job_role or 'a relevant role'}
Company: {company}
Recruiter name: {recruiter.get('name', 'there')}
Recruiter title: {recruiter.get('title', 'HR')}

Job description summary (first 600 chars): {job_description[:600]}

Write a compelling 3-paragraph email:
1. Engaging opening — reference the role and company specifically
2. 2-3 sentences about why the candidate is a strong fit (reference the job description)
3. Clear CTA — ask to connect or discuss the opportunity

Tone: professional yet human, not robotic. No excessive flattery. Under 180 words.
Include a subject line at the very top prefixed with "Subject: "
Return ONLY the subject line + email body. No extra commentary."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip() if message.content else ""


def latex_to_overleaf_url(latex: str) -> str:
    """Encode latex as base64 and return Overleaf snip URL."""
    encoded = base64.b64encode(latex.encode('utf-8')).decode('utf-8')
    return f"https://www.overleaf.com/docs?snip_uri=data:application/x-tex;base64,{encoded}"


# ── Session state init ────────────────────────────────────────────────────────
defaults = {
    "step": "api_key",          # api_key → mode → upload → job → result → outreach
    "mode": None,               # "existing" or "scratch"
    "resume_text": "",
    "job_role": "",
    "company": "",
    "location": "",
    "job_description": "",
    "latex": "",
    "recruiters": [],
    "selected_recruiter": None,
    "outreach_email": "",
    "your_name": "",
    "your_email": "",
    "anthropic_key": "",
    "apollo_key": "",
    # scratch fields
    "s_name": "", "s_email": "", "s_phone": "", "s_location": "",
    "s_linkedin": "", "s_years": "", "s_education": "", "s_skills": "", "s_extra": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="forge-header">
  <div class="forge-title">✦ ResumeForge</div>
  <div class="forge-subtitle">AI × LaTeX Resume Tailoring × Recruiter Outreach</div>
</div>
""", unsafe_allow_html=True)

# ── Step progress ─────────────────────────────────────────────────────────────
step_order = ["api_key", "mode", "upload", "job", "result", "outreach"]
step_labels = ["API Key", "Mode", "Resume", "Job", "Download", "Outreach"]
current_idx = step_order.index(st.session_state.step) if st.session_state.step in step_order else 0

cols = st.columns(len(step_labels))
for i, (col, label) in enumerate(zip(cols, step_labels)):
    with col:
        if i < current_idx:
            st.markdown(f"<div style='text-align:center;font-size:0.7rem;color:#1e40af;'>✓ {label}</div>", unsafe_allow_html=True)
        elif i == current_idx:
            st.markdown(f"<div style='text-align:center;font-size:0.7rem;color:#93c5fd;font-weight:600;'>● {label}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:center;font-size:0.7rem;color:#4b5563;'>○ {label}</div>", unsafe_allow_html=True)

st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# STEP 0 — API KEY
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.step == "api_key":
    st.markdown("### 🔑 Enter Your API Keys")
    st.markdown("<div class='info-box info-amber'>Your keys are stored only in your browser session — never saved anywhere.</div>", unsafe_allow_html=True)

    anthropic_key = st.text_input(
        "Anthropic API Key *",
        type="password",
        placeholder="sk-ant-...",
        help="Get yours at console.anthropic.com"
    )
    st.markdown("<div style='font-size:0.75rem;color:#6b7280;margin-top:-8px;margin-bottom:12px;'>Get your key at <a href='https://console.anthropic.com' target='_blank' style='color:#93c5fd;'>console.anthropic.com</a></div>", unsafe_allow_html=True)

    apollo_key = st.text_input(
        "Apollo.io API Key (optional — for recruiter search)",
        type="password",
        placeholder="Paste Apollo API key...",
        help="Get yours at apollo.io → Settings → API. Free tier = 50 credits/month."
    )
    st.markdown("<div style='font-size:0.75rem;color:#6b7280;margin-top:-8px;margin-bottom:16px;'>Get your key at <a href='https://app.apollo.io/#/settings/integrations/api' target='_blank' style='color:#93c5fd;'>apollo.io → Settings → API</a>. Free tier: 50 credits/month, app uses max ~6 per search.</div>", unsafe_allow_html=True)

    if st.button("Continue →", type="primary", use_container_width=True):
        if not anthropic_key.strip():
            st.error("Anthropic API key is required.")
        else:
            st.session_state.anthropic_key = anthropic_key.strip()
            st.session_state.apollo_key = apollo_key.strip()
            st.session_state.step = "mode"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — MODE SELECT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == "mode":
    st.markdown("### How would you like to proceed?")

    col1, col2 = st.columns(2)
    with col1:
        selected_existing = st.session_state.mode == "existing"
        card_class = "mode-card selected-blue" if selected_existing else "mode-card"
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='font-size:2rem;margin-bottom:0.5rem;'>📄</div>
            <div style='font-size:0.95rem;font-weight:600;color:#f0ece4;margin-bottom:0.4rem;'>I have a resume</div>
            <div style='font-size:0.78rem;color:#9ca3af;line-height:1.5;'>Upload or paste your existing resume — Claude tailors it to the job description</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select →", key="btn_existing", use_container_width=True):
            st.session_state.mode = "existing"
            st.session_state.step = "upload"
            st.rerun()

    with col2:
        selected_scratch = st.session_state.mode == "scratch"
        card_class = "mode-card selected-purple" if selected_scratch else "mode-card"
        st.markdown(f"""
        <div class='{card_class}'>
            <div style='font-size:2rem;margin-bottom:0.5rem;'>✨</div>
            <div style='font-size:0.95rem;font-weight:600;color:#f0ece4;margin-bottom:0.4rem;'>Generate from scratch</div>
            <div style='font-size:0.78rem;color:#9ca3af;line-height:1.5;'>No resume? Fill a few optional details and Claude builds one from the job description</div>
        </div>""", unsafe_allow_html=True)
        if st.button("Select →", key="btn_scratch", use_container_width=True):
            st.session_state.mode = "scratch"
            st.session_state.step = "upload"
            st.rerun()

    st.markdown("")
    if st.button("← Change API Keys", use_container_width=False):
        st.session_state.step = "api_key"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — UPLOAD / PERSONAL DETAILS
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == "upload":
    is_scratch = st.session_state.mode == "scratch"
    badge = "<span class='step-badge badge-purple'>✨ From Scratch</span>" if is_scratch else "<span class='step-badge badge-blue'>📄 Tailoring Existing</span>"

    st.markdown(f"### Resume Details &nbsp; {badge}", unsafe_allow_html=True)

    if is_scratch:
        st.markdown("<div class='info-box info-purple'>💡 All fields optional — Claude fills gaps intelligently from the job description.</div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.session_state.s_name = st.text_input("Full Name", value=st.session_state.s_name, placeholder="e.g. Jane Doe")
            st.session_state.s_phone = st.text_input("Phone", value=st.session_state.s_phone, placeholder="e.g. +91 99999 99999")
            st.session_state.s_linkedin = st.text_input("LinkedIn / Portfolio", value=st.session_state.s_linkedin, placeholder="linkedin.com/in/janedoe")
            st.session_state.s_education = st.text_input("Education", value=st.session_state.s_education, placeholder="e.g. B.Tech CS, IIT Delhi, 2019")
        with c2:
            st.session_state.s_email = st.text_input("Email", value=st.session_state.s_email, placeholder="e.g. jane@email.com")
            st.session_state.s_location = st.text_input("Location", value=st.session_state.s_location, placeholder="e.g. Pune, India")
            st.session_state.s_years = st.text_input("Years of Experience", value=st.session_state.s_years, placeholder="e.g. 3 years in software")
            st.session_state.s_skills = st.text_input("Skills / Technologies", value=st.session_state.s_skills, placeholder="Python, React, AWS, SQL...")

        st.session_state.s_extra = st.text_area("Anything else to include (optional)", value=st.session_state.s_extra,
            placeholder="e.g. Led a team of 6, published NLP paper, worked in fintech...", height=80)

    else:
        uploaded_file = st.file_uploader("Upload Resume (PDF or TXT)", type=["pdf", "txt"])
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                st.session_state.resume_text = uploaded_file.read().decode("utf-8")
                st.success(f"✅ {uploaded_file.name} loaded")
            elif uploaded_file.type == "application/pdf":
                with st.spinner("Reading your PDF resume..."):
                    pdf_bytes = uploaded_file.read()
                    st.session_state.resume_text = extract_text_from_pdf(pdf_bytes, st.session_state.anthropic_key)
                st.success(f"✅ {uploaded_file.name} extracted")

        st.session_state.resume_text = st.text_area(
            "Or paste your resume text",
            value=st.session_state.resume_text,
            placeholder="John Smith\njohn@email.com\n\nEXPERIENCE\nSenior Engineer at Acme...",
            height=200
        )

    st.markdown("")
    col_back, col_next = st.columns([1, 3])
    with col_back:
        if st.button("← Back"):
            st.session_state.step = "mode"
            st.rerun()
    with col_next:
        label = "Continue to Job Description →" if is_scratch else "Continue →"
        if st.button(label, type="primary", use_container_width=True):
            if not is_scratch and not st.session_state.resume_text.strip():
                st.error("Please upload or paste your resume first.")
            else:
                st.session_state.step = "job"
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — JOB DESCRIPTION
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == "job":
    is_scratch = st.session_state.mode == "scratch"
    badge = "<span class='step-badge badge-purple'>✨ From Scratch</span>" if is_scratch else "<span class='step-badge badge-blue'>📄 Tailoring</span>"
    st.markdown(f"### Job Details &nbsp; {badge}", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.8rem;color:#9ca3af;margin-bottom:1rem;'>These details are also used to find the right recruiter on Apollo.io</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.job_role = st.text_input("Role / Position *", value=st.session_state.job_role, placeholder="e.g. Senior SWE")
    with c2:
        st.session_state.company = st.text_input("Company *", value=st.session_state.company, placeholder="e.g. Google")
    with c3:
        st.session_state.location = st.text_input("Location (optional)", value=st.session_state.location, placeholder="e.g. Bangalore")

    st.session_state.job_description = st.text_area(
        "Job Description *",
        value=st.session_state.job_description,
        placeholder="Paste the full job description here...\n\nResponsibilities:\n- ...\n\nRequirements:\n- ...",
        height=280
    )

    col_back, col_gen = st.columns([1, 3])
    with col_back:
        if st.button("← Back"):
            st.session_state.step = "upload"
            st.rerun()
    with col_gen:
        btn_label = "✨ Generate Resume from Scratch" if is_scratch else "✦ Generate Tailored Resume"
        if st.button(btn_label, type="primary", use_container_width=True):
            if not st.session_state.job_description.strip():
                st.error("Please provide the job description.")
            else:
                # Build prompt
                if is_scratch:
                    details = "\n".join(filter(None, [
                        st.session_state.s_name and f"Full Name: {st.session_state.s_name}",
                        st.session_state.s_email and f"Email: {st.session_state.s_email}",
                        st.session_state.s_phone and f"Phone: {st.session_state.s_phone}",
                        st.session_state.s_location and f"Location: {st.session_state.s_location}",
                        st.session_state.s_linkedin and f"LinkedIn/Portfolio: {st.session_state.s_linkedin}",
                        st.session_state.s_years and f"Years of Experience: {st.session_state.s_years}",
                        st.session_state.s_education and f"Education: {st.session_state.s_education}",
                        st.session_state.s_skills and f"Known Skills: {st.session_state.s_skills}",
                        st.session_state.s_extra and f"Additional Notes: {st.session_state.s_extra}",
                    ]))
                    prompt = f"JOB ROLE: {st.session_state.job_role or 'Not specified'}\nCOMPANY: {st.session_state.company or 'Not specified'}\n\nJOB DESCRIPTION:\n{st.session_state.job_description}\n\n---\n\nPERSONAL DETAILS:\n{details or 'None — invent realistic details.'}\n\n---\n\nGenerate complete LaTeX resume from scratch. Output ONLY the LaTeX code."
                    system = SCRATCH_SYSTEM_PROMPT
                else:
                    prompt = f"JOB ROLE: {st.session_state.job_role or 'Not specified'}\nCOMPANY: {st.session_state.company or 'Not specified'}\n\nJOB DESCRIPTION:\n{st.session_state.job_description}\n\n---\n\nCANDIDATE'S RESUME:\n{st.session_state.resume_text}\n\n---\n\nGenerate a tailored LaTeX resume. Output ONLY the LaTeX code."
                    system = LATEX_SYSTEM_PROMPT

                with st.spinner("🤖 Generating your resume with Claude AI..."):
                    try:
                        raw_latex = call_claude(system, prompt, st.session_state.anthropic_key)
                        st.session_state.latex = sanitize_latex(raw_latex)
                        st.session_state.step = "result"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Generation failed: {str(e)}")


# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — RESULT / DOWNLOAD
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == "result":
    is_scratch = st.session_state.mode == "scratch"
    st.markdown("### 🎉 Your Resume is Ready!")

    badge = "Built from scratch" if is_scratch else "Tailored"
    role_str = st.session_state.job_role or "the role"
    company_str = st.session_state.company
    st.markdown(f"<div style='color:#9ca3af;font-size:0.85rem;margin-bottom:1.2rem;'>{badge} for <strong style='color:#93c5fd;'>{role_str}</strong>{(' at <strong style=\"color:#93c5fd;\">' + company_str + '</strong>') if company_str else ''}</div>", unsafe_allow_html=True)

    # Download buttons
    col1, col2 = st.columns(2)
    with col1:
        latex_bytes = st.session_state.latex.encode("utf-8")
        filename = f"resume_{(st.session_state.company or 'tailored').replace(' ', '_')}.tex"
        st.download_button(
            label="⬇ Download LaTeX (.tex)",
            data=latex_bytes,
            file_name=filename,
            mime="text/plain",
            use_container_width=True
        )

    with col2:
        overleaf_url = latex_to_overleaf_url(st.session_state.latex)
        st.link_button("🍃 Open in Overleaf → PDF", overleaf_url, use_container_width=True)

    st.markdown("<div class='info-box info-green'>💡 Click <strong>Open in Overleaf</strong> to compile your LaTeX into a polished PDF — free, no account required for basic use.</div>", unsafe_allow_html=True)

    # LaTeX preview
    with st.expander("📄 View LaTeX Source", expanded=False):
        line_count = len(st.session_state.latex.splitlines())
        st.markdown(f"<div style='font-size:0.75rem;color:#6b7280;margin-bottom:6px;'>resume.tex — {line_count} lines</div>", unsafe_allow_html=True)
        st.code(st.session_state.latex, language="latex")

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)

    # CTA to recruiter outreach
    st.markdown("""
    <div class='info-box info-amber' style='padding:1rem 1.2rem;'>
        <div style='font-size:0.9rem;font-weight:600;color:#fbbf24;margin-bottom:0.4rem;'>🎯 Find the right recruiter</div>
        <div style='font-size:0.8rem;'>Search Apollo.io for HR & Talent Acquisition contacts — get their email, phone, LinkedIn, and a custom outreach email.</div>
    </div>
    """, unsafe_allow_html=True)

    col_back, col_outreach = st.columns([1, 2])
    with col_back:
        if st.button("← Back to Job"):
            st.session_state.step = "job"
            st.rerun()
    with col_outreach:
        if st.button("Find Recruiter on Apollo.io →", type="primary", use_container_width=True):
            st.session_state.step = "outreach"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — RECRUITER OUTREACH
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == "outreach":
    st.markdown("### 🎯 Recruiter Outreach")
    st.markdown(f"<div style='color:#9ca3af;font-size:0.82rem;margin-bottom:1rem;'>Find HR & Talent Acquisition contacts at <strong style='color:#e8e4dc;'>{st.session_state.company or 'the company'}</strong></div>", unsafe_allow_html=True)

    # Your details for email
    with st.expander("👤 Your Contact Details (for the outreach email)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.your_name = st.text_input("Your Name", value=st.session_state.your_name or st.session_state.s_name, placeholder="e.g. Jane Doe")
        with c2:
            st.session_state.your_email = st.text_input("Your Email", value=st.session_state.your_email or st.session_state.s_email, placeholder="e.g. jane@email.com")

    # Apollo key check
    if not st.session_state.apollo_key:
        st.markdown("<div class='info-box info-amber'>🔑 Apollo.io API key not set. Please enter it below.</div>", unsafe_allow_html=True)
        apollo_key_input = st.text_input("Apollo.io API Key", type="password", placeholder="Paste your Apollo API key...")
        if st.button("Save Key & Search", type="primary"):
            if apollo_key_input.strip():
                st.session_state.apollo_key = apollo_key_input.strip()
                st.rerun()
            else:
                st.error("Please enter your Apollo.io API key.")
    else:
        st.markdown("<div class='info-box info-green' style='margin-bottom:0.8rem;'>✓ Apollo.io API key saved &nbsp; <span class='credit-badge'>~6 credits per search · 50 free/month</span></div>", unsafe_allow_html=True)

        col_search, col_change = st.columns([3, 1])
        with col_search:
            if st.button(f"🔍 Search Recruiters at {st.session_state.company or 'Company'}", type="primary", use_container_width=True):
                if not st.session_state.company.strip():
                    st.error("Company name is required. Please go back and fill it in.")
                else:
                    with st.spinner("Connecting to Apollo.io and fetching contacts..."):
                        try:
                            people = search_apollo(
                                st.session_state.apollo_key,
                                st.session_state.company,
                                st.session_state.location
                            )
                            if not people:
                                st.error(f'No recruiters found at "{st.session_state.company}". Try a slightly different company name.')
                            else:
                                enriched = []
                                for person in people[:3]:
                                    ep = enrich_person(st.session_state.apollo_key, person.get("id", ""))
                                    enriched.append({
                                        "id": person.get("id"),
                                        "name": person.get("name", "Unknown"),
                                        "title": person.get("title", "HR / Recruiter"),
                                        "email": ep.get("email") or person.get("email"),
                                        "phone": ep.get("sanitized_phone") or (ep.get("phone_numbers", [{}])[0].get("sanitized_number") if ep.get("phone_numbers") else None),
                                        "linkedin": person.get("linkedin_url"),
                                        "location": f"{person.get('city', '')}{', ' + person.get('state', '') if person.get('state') else ''}".strip(', ') or st.session_state.location,
                                        "company": (person.get("organization") or {}).get("name", st.session_state.company),
                                    })
                                st.session_state.recruiters = enriched
                                st.session_state.outreach_email = ""
                                st.session_state.selected_recruiter = None
                                st.rerun()
                        except Exception as e:
                            st.error(f"Search failed: {str(e)}")

        with col_change:
            if st.button("Change Key"):
                st.session_state.apollo_key = ""
                st.session_state.recruiters = []
                st.rerun()

    # Show recruiter results
    if st.session_state.recruiters:
        st.markdown(f"<div style='font-size:0.8rem;color:#9ca3af;text-transform:uppercase;letter-spacing:0.06em;margin:1rem 0 0.5rem;'>{len(st.session_state.recruiters)} Recruiters Found at {st.session_state.company} <span class='credit-badge'>~{len(st.session_state.recruiters) * 2} credits used</span></div>", unsafe_allow_html=True)

        for i, r in enumerate(st.session_state.recruiters):
            with st.container():
                st.markdown(f"""
                <div class='recruiter-card'>
                    <div class='recruiter-name'>👤 {r['name']}</div>
                    <div class='recruiter-title'>{r['title']} · {r['company']}</div>
                    <div class='recruiter-detail'>
                        {'📧 <a href="mailto:' + r['email'] + '">' + r['email'] + '</a>' if r.get('email') else '📧 Email not available'}
                        {' &nbsp;|&nbsp; 📞 ' + r['phone'] if r.get('phone') else ''}
                        {' &nbsp;|&nbsp; <a href="' + (r['linkedin'] if r['linkedin'].startswith('http') else 'https://' + r['linkedin']) + '" target="_blank">🔗 LinkedIn</a>' if r.get('linkedin') else ''}
                        {' &nbsp;|&nbsp; 📍 ' + r['location'] if r.get('location') else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"✍️ Write Outreach Email for {r['name']}", key=f"email_btn_{i}"):
                    st.session_state.selected_recruiter = r
                    with st.spinner(f"Crafting personalised email for {r['name']}..."):
                        try:
                            st.session_state.outreach_email = generate_outreach_email(
                                st.session_state.anthropic_key,
                                r,
                                st.session_state.job_role,
                                st.session_state.company,
                                st.session_state.job_description,
                                st.session_state.your_name,
                                st.session_state.your_email,
                            )
                            st.rerun()
                        except Exception as e:
                            st.error(f"Email generation failed: {str(e)}")

    # Show generated email
    if st.session_state.outreach_email and st.session_state.selected_recruiter:
        r = st.session_state.selected_recruiter
        st.markdown(f"<hr class='section-divider'><div style='font-size:0.9rem;font-weight:600;color:#f0ece4;margin-bottom:0.5rem;'>✉️ Outreach Email → <span style='color:#fbbf24;'>{r['name']}</span></div>", unsafe_allow_html=True)

        # Editable email
        st.session_state.outreach_email = st.text_area(
            "Edit if needed, then copy or send:",
            value=st.session_state.outreach_email,
            height=260
        )

        # Extract subject and body for Gmail
        lines = st.session_state.outreach_email.split("\n")
        subject_line = next((l for l in lines if l.lower().startswith("subject:")), "")
        subject = subject_line.replace("Subject:", "").replace("subject:", "").strip()
        body = st.session_state.outreach_email.replace(subject_line, "").strip()
        to_addr = r.get("email", "")

        gmail_url = f"https://mail.google.com/mail/?view=cm&to={requests.utils.quote(to_addr)}&su={requests.utils.quote(subject)}&body={requests.utils.quote(body)}"

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "📋 Download Email (.txt)",
                data=st.session_state.outreach_email.encode(),
                file_name=f"outreach_{r['name'].replace(' ','_')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            st.link_button("📨 Open in Gmail", gmail_url, use_container_width=True)

    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    col_back, col_restart = st.columns([1, 1])
    with col_back:
        if st.button("← Back to Resume"):
            st.session_state.step = "result"
            st.rerun()
    with col_restart:
        if st.button("🔄 Start Over", use_container_width=True):
            for k, v in defaults.items():
                st.session_state[k] = v
            st.rerun()
