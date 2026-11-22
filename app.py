import streamlit as st
import sqlite3
import hashlib
import secrets
import os
import re
from datetime import date, datetime, timedelta
from difflib import SequenceMatcher
from contextlib import closing

# =========================================================
# 1. APP CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FindIt | Campus Lost & Found",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "findit.db"
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


# =========================================================
# 2. DESIGN SYSTEM
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800&display=swap');

:root {
    --navy: #14213d;
    --blue: #315eb5;
    --blue-light: #eaf1ff;
    --ink: #18243d;
    --muted: #718096;
    --border: #e5eaf2;
    --surface: #ffffff;
    --background: #f5f7fb;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: var(--background);
    color: var(--ink);
}

.block-container {
    max-width: 1440px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    color: var(--ink);
    letter-spacing: -0.4px;
}

h1 {
    font-weight: 800 !important;
}

h2 {
    font-weight: 700 !important;
}

p, label, li {
    color: #40516c;
}

[data-testid="stSidebar"] {
    background: #101a32;
    border-right: 1px solid #263653;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.4rem;
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #bdc9dc;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    color: #edf3ff !important;
    font-size: 14px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    color: white !important;
}

[data-testid="stSidebar"] hr {
    border-color: #2a3b5c;
}

[data-testid="stSidebar"] .stButton > button {
    background: #203455;
    color: white !important;
    border: 1px solid #385078;
    border-radius: 10px;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #2b4773;
    border-color: #7aa7ef;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 0.45rem;
}

.hero {
    background: linear-gradient(115deg, #14213d 0%, #244f98 100%);
    border-radius: 22px;
    padding: 34px 38px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 12px 30px rgba(20, 40, 80, .13);
}

.hero h1 {
    color: white !important;
    font-size: clamp(27px, 3vw, 39px);
    margin: 0 0 9px 0;
}

.hero p {
    color: #dbe8ff !important;
    font-size: 15px;
    margin: 0;
}

.eyebrow {
    text-transform: uppercase;
    letter-spacing: 1.8px;
    font-size: 11px;
    font-weight: 800;
    color: #b9d0ff;
    margin-bottom: 12px;
}

.metric-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 17px;
    padding: 19px 20px;
    min-height: 132px;
    box-shadow: 0 5px 18px rgba(24, 40, 70, .035);
}

.metric-icon {
    font-size: 23px;
    margin-bottom: 8px;
}

.metric-number {
    font-family: 'Outfit', sans-serif;
    font-size: 31px;
    line-height: 1.1;
    font-weight: 800;
    color: #2858a9;
}

.metric-label {
    color: #718096;
    font-size: 13px;
    margin-top: 7px;
    font-weight: 600;
}

.section-heading {
    font-family: 'Outfit', sans-serif;
    font-size: 23px;
    font-weight: 700;
    color: #192844;
    margin: 27px 0 12px 0;
}

.info-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    min-height: 175px;
    box-shadow: 0 5px 18px rgba(24, 40, 70, .035);
}

.info-card h3 {
    font-size: 17px;
    margin: 10px 0 5px 0;
}

.info-card p {
    font-size: 13px;
    margin: 0;
    color: #718096;
}

.item-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 19px;
    margin-bottom: 13px;
    box-shadow: 0 4px 15px rgba(24, 40, 70, .03);
}

.status-lost {
    display: inline-block;
    color: #b42318;
    background: #fff0ed;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 800;
}

.status-found {
    display: inline-block;
    color: #147346;
    background: #e8f8ef;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 800;
}

.status-pending {
    display: inline-block;
    color: #956000;
    background: #fff5d9;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 11px;
    font-weight: 800;
}

.demo-banner {
    background: #fff5dc;
    border: 1px solid #f0d48b;
    color: #805600;
    border-radius: 11px;
    padding: 13px 17px;
    margin-bottom: 20px;
    font-size: 13px;
    font-weight: 700;
}

.live-banner {
    background: #e8f8ef;
    border: 1px solid #b6e6c8;
    color: #17643a;
    border-radius: 11px;
    padding: 13px 17px;
    margin-bottom: 20px;
    font-size: 13px;
    font-weight: 700;
}

.match-box {
    background: #edf8f1;
    border: 1px solid #b9e5c8;
    padding: 19px;
    border-radius: 14px;
}

.match-box h3 {
    color: #17643a !important;
    margin: 0;
}

.small-muted {
    font-size: 12px;
    color: #7b879b;
}

.stButton > button {
    border-radius: 10px;
    min-height: 42px;
    font-weight: 700;
    border: 1px solid #d9e1ed;
}

.stButton > button[kind="primary"] {
    background: #2858a9;
    border-color: #2858a9;
}

.stButton > button[kind="primary"]:hover {
    background: #1d4488;
    border-color: #1d4488;
}

.stTextInput input, .stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 9px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 14px;
}

[data-testid="stMetricValue"] {
    color: #2858a9;
    font-family: 'Outfit', sans-serif;
}

[data-testid="stExpander"] {
    border: 1px solid var(--border);
    border-radius: 12px;
    background: white;
}

div[data-testid="stProgressBar"] > div {
    border-radius: 20px;
}

footer {
    visibility: hidden;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }
    .hero {
        padding: 24px;
    }
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 3. DATABASE CONNECTION AND MIGRATION
# =========================================================

def db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(conn, table, column, definition):
    existing = [
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    ]

    if column not in existing:
        conn.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )


def initialize_database():

    with closing(db()) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fi_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                college TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fi_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER,
                report_type TEXT NOT NULL,
                item_name TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                color TEXT,
                location TEXT NOT NULL,
                item_date TEXT NOT NULL,
                image_path TEXT,
                status TEXT DEFAULT 'Active',
                created_at TEXT NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0
            )
        """)

        ensure_column(conn, "fi_reports", "owner_id", "INTEGER")
        ensure_column(conn, "fi_reports", "image_path", "TEXT")
        ensure_column(conn, "fi_reports", "status", "TEXT DEFAULT 'Active'")
        ensure_column(conn, "fi_reports", "is_demo", "INTEGER NOT NULL DEFAULT 0")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS fi_claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                found_report_id INTEGER NOT NULL,
                lost_report_id INTEGER NOT NULL,
                claimant_id INTEGER NOT NULL,
                finder_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL,
                is_demo INTEGER NOT NULL DEFAULT 0
            )
        """)

        conn.commit()


initialize_database()


# =========================================================
# 4. AUTHENTICATION
# =========================================================

def hash_password(password):
    salt = secrets.token_bytes(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, 310000
    )
    return salt.hex() + ":" + hashed.hex()


def verify_password(password, stored):
    try:
        salt_hex, hash_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)

        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt, 310000
        )

        return secrets.compare_digest(actual, expected)

    except (ValueError, TypeError):
        return False


def register_user(name, email, college, password):

    try:
        with closing(db()) as conn:
            conn.execute("""
                INSERT INTO fi_users
                (full_name, email, college, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                name.strip(),
                email.strip().lower(),
                college.strip(),
                hash_password(password),
                datetime.now().isoformat()
            ))
            conn.commit()

        return True, "Your account has been created."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."


def login_user(email, password):

    with closing(db()) as conn:
        user = conn.execute("""
            SELECT * FROM fi_users WHERE email=?
        """, (email.strip().lower(),)).fetchone()

    if user and verify_password(password, user["password_hash"]):
        return {
            "id": user["id"],
            "name": user["full_name"],
            "email": user["email"],
            "college": user["college"]
        }

    return None


# =========================================================
# 5. REPORT MANAGEMENT
# =========================================================

def save_report(
    owner_id, report_type, item_name, category,
    description, color, location, item_date,
    image_path, is_demo
):

    with closing(db()) as conn:
        conn.execute("""
            INSERT INTO fi_reports (
                owner_id, report_type, item_name, category,
                description, color, location, item_date,
                image_path, status, created_at, is_demo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active', ?, ?)
        """, (
            owner_id, report_type, item_name, category,
            description, color, location, str(item_date),
            image_path, datetime.now().isoformat(), int(is_demo)
        ))
        conn.commit()


def get_reports(is_demo, report_type=None, status=None):

    query = "SELECT * FROM fi_reports WHERE is_demo=?"
    params = [int(is_demo)]

    if report_type:
        query += " AND report_type=?"
        params.append(report_type)

    if status:
        query += " AND status=?"
        params.append(status)

    query += " ORDER BY id DESC"

    with closing(db()) as conn:
        return conn.execute(query, params).fetchall()


def get_my_reports(user_id, is_demo):

    with closing(db()) as conn:
        return conn.execute("""
            SELECT * FROM fi_reports
            WHERE owner_id=? AND is_demo=?
            ORDER BY id DESC
        """, (user_id, int(is_demo))).fetchall()


def get_report_by_id(report_id, is_demo):

    with closing(db()) as conn:
        return conn.execute("""
            SELECT * FROM fi_reports
            WHERE id=? AND is_demo=?
        """, (report_id, int(is_demo))).fetchone()


def update_report_status(report_id, user_id, is_demo, status):

    with closing(db()) as conn:
        conn.execute("""
            UPDATE fi_reports
            SET status=?
            WHERE id=? AND owner_id=? AND is_demo=?
        """, (status, report_id, user_id, int(is_demo)))
        conn.commit()


# =========================================================
# 6. DEMO DATA
# =========================================================

def demo_data_exists():

    with closing(db()) as conn:
        row = conn.execute("""
            SELECT COUNT(*) AS total
            FROM fi_reports WHERE is_demo=1
        """).fetchone()

    return row["total"] > 0


def load_demo_data():

    if demo_data_exists():
        return

    today = date.today()

    samples = [
        (
            "Lost", "Samsung Galaxy S23", "Electronics",
            "Black Samsung smartphone with a transparent back cover. "
            "A small scratch is visible near the camera.",
            "Black", "Central Library, Reading Hall",
            today - timedelta(days=1)
        ),
        (
            "Found", "Samsung Galaxy Phone", "Electronics",
            "Black Samsung mobile phone with a clear transparent case. "
            "Small scratch near the rear camera.",
            "Black", "Library Entrance",
            today - timedelta(days=1)
        ),
        (
            "Lost", "Blue Student Wallet", "Wallet / Money",
            "Dark blue leather wallet containing a student bus pass "
            "and a few cards.",
            "Blue", "College Canteen", today
        ),
        (
            "Found", "Blue Leather Wallet", "Wallet / Money",
            "Found a dark blue leather wallet near the canteen tables. "
            "It contains some cards.",
            "Blue", "Canteen", today
        ),
        (
            "Found", "Silver Keychain with 3 Keys", "Keys",
            "Three silver keys attached to a small round keychain.",
            "Silver", "Computer Science Block", today
        ),
        (
            "Lost", "White Water Bottle", "Other",
            "White insulated water bottle with a small sticker.",
            "White", "Sports Ground", today
        )
    ]

    with closing(db()) as conn:

        for item in samples:
            conn.execute("""
                INSERT INTO fi_reports (
                    owner_id, report_type, item_name, category,
                    description, color, location, item_date,
                    image_path, status, created_at, is_demo
                )
                VALUES (0, ?, ?, ?, ?, ?, ?, ?, NULL, 'Active', ?, 1)
            """, (
                item[0], item[1], item[2], item[3],
                item[4], item[5], str(item[6]),
                datetime.now().isoformat()
            ))

        conn.commit()


def reset_demo_data():

    with closing(db()) as conn:
        conn.execute("DELETE FROM fi_claims WHERE is_demo=1")
        conn.execute("DELETE FROM fi_reports WHERE is_demo=1")
        conn.commit()

    load_demo_data()


# =========================================================
# 7. SMART MATCHING
# =========================================================

def similarity(a, b):
    return SequenceMatcher(
        None,
        (a or "").lower().strip(),
        (b or "").lower().strip()
    ).ratio()


def calculate_match_details(lost, found):

    category = (
        30 if lost["category"].lower() == found["category"].lower()
        else 0
    )

    name = similarity(
        lost["item_name"], found["item_name"]
    ) * 25

    description = similarity(
        lost["description"], found["description"]
    ) * 25

    color = (
        10 if lost["color"] and found["color"]
        and lost["color"].lower() == found["color"].lower()
        else 0
    )

    location = similarity(
        lost["location"], found["location"]
    ) * 10

    details = {
        "Category": (round(category, 1), 30),
        "Item name": (round(name, 1), 25),
        "Description": (round(description, 1), 25),
        "Colour": (round(color, 1), 10),
        "Location": (round(location, 1), 10)
    }

    total = round(sum(v[0] for v in details.values()), 1)

    return total, details


def match_level(score):

    if score >= 75:
        return "Strong Match", "🟢"
    if score >= 50:
        return "Moderate Match", "🟡"
    return "Low Match", "🟠"


def find_matches(lost_report, is_demo):

    found_items = get_reports(
        is_demo, report_type="Found", status="Active"
    )

    matches = []

    for found in found_items:
        score, _ = calculate_match_details(lost_report, found)

        if score >= 35:
            matches.append((score, found))

    return sorted(matches, key=lambda x: x[0], reverse=True)


# =========================================================
# 8. CLAIM AND VERIFICATION
# =========================================================

def submit_claim(found, lost, claimant_id, message, is_demo):

    finder_id = found["owner_id"]

    if finder_id == claimant_id and not is_demo:
        return False, "You cannot claim your own found-item report."

    with closing(db()) as conn:

        existing = conn.execute("""
            SELECT id FROM fi_claims
            WHERE found_report_id=? AND lost_report_id=?
            AND claimant_id=? AND is_demo=? AND status='Pending'
        """, (
            found["id"], lost["id"], claimant_id, int(is_demo)
        )).fetchone()

        if existing:
            return False, "You already have a pending claim for this item."

        conn.execute("""
            INSERT INTO fi_claims (
                found_report_id, lost_report_id,
                claimant_id, finder_id, message,
                status, created_at, is_demo
            )
            VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?)
        """, (
            found["id"], lost["id"], claimant_id,
            finder_id, message.strip(),
            datetime.now().isoformat(), int(is_demo)
        ))

        conn.commit()

    return True, "Your claim request has been submitted."


def get_claims_for_finder(finder_id, is_demo):

    with closing(db()) as conn:
        return conn.execute("""
            SELECT * FROM fi_claims
            WHERE finder_id=? AND is_demo=?
            ORDER BY id DESC
        """, (finder_id, int(is_demo))).fetchall()


def get_my_claims(claimant_id, is_demo):

    with closing(db()) as conn:
        return conn.execute("""
            SELECT * FROM fi_claims
            WHERE claimant_id=? AND is_demo=?
            ORDER BY id DESC
        """, (claimant_id, int(is_demo))).fetchall()


def decide_claim(claim_id, finder_id, is_demo, decision):

    if decision not in ("Approved", "Rejected"):
        return False

    with closing(db()) as conn:

        claim = conn.execute("""
            SELECT * FROM fi_claims
            WHERE id=? AND finder_id=? AND is_demo=?
            AND status='Pending'
        """, (
            claim_id, finder_id, int(is_demo)
        )).fetchone()

        if not claim:
            return False

        conn.execute("""
            UPDATE fi_claims SET status=?
            WHERE id=? AND finder_id=? AND is_demo=?
        """, (
            decision, claim_id, finder_id, int(is_demo)
        ))

        if decision == "Approved":
            conn.execute("""
                UPDATE fi_reports
                SET status='Recovered'
                WHERE id IN (?, ?) AND is_demo=?
            """, (
                claim["found_report_id"],
                claim["lost_report_id"],
                int(is_demo)
            ))

        conn.commit()

    return True


# =========================================================
# 9. REUSABLE UI COMPONENTS
# =========================================================

def show_mode_banner():

    if st.session_state.mode == "demo":
        st.markdown("""
        <div class="demo-banner">
            🧪 DEMO MODE &nbsp; · &nbsp;
            Fictional sample reports are being displayed.
            Real student reports remain separate.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="live-banner">
            🟢 LIVE MODE &nbsp; · &nbsp;
            Showing genuine student reports.
            Example previews are labelled separately.
        </div>
        """, unsafe_allow_html=True)


def show_hero(eyebrow, title, subtitle):

    st.markdown(f"""
    <div class="hero">
        <div class="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def show_metric(col, icon, number, label):

    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-number">{number}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)


def save_uploaded_image(uploaded):

    if uploaded is None:
        return None

    extension = os.path.splitext(uploaded.name)[1].lower()

    filename = secrets.token_hex(12) + extension
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as file:
        file.write(uploaded.getbuffer())

    return path


def show_report_card(item, show_owner=False):

    with st.container(border=True):

        col1, col2 = st.columns([1, 3])

        with col1:
            if item["image_path"] and os.path.exists(item["image_path"]):
                st.image(item["image_path"], use_container_width=True)
            else:
                st.markdown(
                    "<div style='background:#eef3fb;border-radius:13px;"
                    "padding:25px;text-align:center;font-size:42px;'>📦</div>",
                    unsafe_allow_html=True
                )

        with col2:

            if item["report_type"] == "Lost":
                st.markdown(
                    '<span class="status-lost">LOST ITEM</span>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<span class="status-found">FOUND ITEM</span>',
                    unsafe_allow_html=True
                )

            st.markdown(f"### {item['item_name']}")

            st.write(item["description"])

            st.caption(
                f"📍 {item['location']}  ·  "
                f"📅 {item['item_date']}  ·  "
                f"{item['category']}"
            )

            if show_owner:
                st.caption(f"Report #{item['id']}")


# =========================================================
# 10. AUTHENTICATION SCREEN
# =========================================================

def authentication_screen():

    st.markdown("""
    <div style="max-width:850px;margin:35px auto 25px auto;
    background:linear-gradient(115deg,#14213d,#2858a9);
    padding:42px;border-radius:23px;color:white;">
        <div style="font-size:13px;letter-spacing:2px;
        font-weight:800;color:#bdd3ff;">SMART CAMPUS COMMUNITY</div>
        <h1 style="color:white !important;font-size:44px;
        margin:12px 0;">🔎 FindIt</h1>
        <p style="color:#e1eaff;font-size:17px;">
        Lost something? Found something?
        Let's help every misplaced item find its way home.
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, center, right = st.columns([1, 1.4, 1])

    with center:

        st.markdown("## Welcome to FindIt")

        st.write("Sign in to your campus account or create one.")

        choice = st.radio(
            "Account",
            ["Login", "Create Account"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if choice == "Login":

            with st.form("login_form"):

                email = st.text_input("College email")
                password = st.text_input("Password", type="password")

                submitted = st.form_submit_button(
                    "Login to FindIt",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:

                    user = login_user(email, password)

                    if user:
                        st.session_state.user = user
                        st.session_state.mode = "live"
                        st.rerun()
                    else:
                        st.error("Incorrect email or password.")

        else:

            with st.form("register_form"):

                name = st.text_input("Full name")
                email = st.text_input("College email")
                college = st.text_input("College / University")
                password = st.text_input(
                    "Create password", type="password"
                )
                confirm = st.text_input(
                    "Confirm password", type="password"
                )

                submitted = st.form_submit_button(
                    "Create Student Account",
                    use_container_width=True,
                    type="primary"
                )

                if submitted:

                    if not all([name, email, college, password, confirm]):
                        st.error("Please complete all fields.")

                    elif not re.match(
                        r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email
                    ):
                        st.error("Enter a valid email address.")

                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters.")

                    elif password != confirm:
                        st.error("Passwords do not match.")

                    else:
                        ok, message = register_user(
                            name, email, college, password
                        )

                        if ok:
                            st.success(message + " You can now log in.")
                        else:
                            st.error(message)

        st.divider()

        st.markdown("### Want to explore first?")

        st.write(
            "Try the interactive demo with fictional campus reports. "
            "No account is needed."
        )

        if st.button(
            "🧪 Explore FindIt Demo",
            use_container_width=True
        ):

            load_demo_data()

            st.session_state.user = {
                "id": 0,
                "name": "Demo Student",
                "email": "demo@findit.local",
                "college": "Sample University"
            }

            st.session_state.mode = "demo"
            st.rerun()

        st.caption(
            "Course prototype · Email verification is not enabled."
        )


# =========================================================
# 11. DASHBOARD
# =========================================================

def dashboard():

    user = st.session_state.user
    is_demo = st.session_state.mode == "demo"

    show_mode_banner()

    show_hero(
        "YOUR CAMPUS LOST & FOUND",
        f"Welcome back, {user['name'].split()[0]} 👋",
        "One campus. One community. Helping lost belongings find their way home."
    )

    reports = get_reports(is_demo)

    total = len(reports)
    lost = sum(1 for x in reports if x["report_type"] == "Lost")
    found = sum(1 for x in reports if x["report_type"] == "Found")
    recovered = sum(1 for x in reports if x["status"] == "Recovered")

    cols = st.columns(4)

    show_metric(cols[0], "📦", total, "TOTAL REPORTS")
    show_metric(cols[1], "🔴", lost, "ITEMS LOST")
    show_metric(cols[2], "🟢", found, "ITEMS FOUND")
    show_metric(cols[3], "💚", recovered, "RECOVERED")

    st.markdown('<div class="section-heading">Campus activity</div>',
                unsafe_allow_html=True)

    if total:
        st.progress(
            recovered / total,
            text=f"{recovered} recovered out of {total} reports"
        )
    else:
        st.info("No reports have been submitted yet.")

    st.markdown('<div class="section-heading">Recent reports</div>',
                unsafe_allow_html=True)

    if reports:

        for item in reports[:4]:
            show_report_card(item)

    elif not is_demo:

        st.write(
            "Your campus is ready to get started. "
            "Here are a few examples of what students can report."
        )

        st.caption("EXAMPLE PREVIEWS · NOT REAL STUDENT REPORTS")

        a, b, c = st.columns(3)

        examples = [
            (a, "📱", "Black Samsung Phone", "LOST", "Library · Electronics"),
            (b, "👛", "Blue Leather Wallet", "FOUND", "Canteen · Wallet"),
            (c, "🔑", "Silver Keychain", "FOUND", "Computer Block · Keys")
        ]

        for col, emoji, name, status, detail in examples:
            with col:
                st.markdown(f"""
                <div class="info-card">
                    <div style="font-size:35px">{emoji}</div>
                    <h3>{name}</h3>
                    <p><b>{status}</b></p>
                    <p>{detail}</p>
                    <p style="margin-top:10px;">Illustrative example</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="section-heading">How FindIt helps</div>',
                unsafe_allow_html=True)

    a, b, c = st.columns(3)

    cards = [
        (a, "📝", "Report an item",
         "Share the item details, location and an optional image."),
        (b, "✨", "Smart matching",
         "FindIt compares descriptions and item details to suggest matches."),
        (c, "🤝", "Claim & recover",
         "Submit a claim, verify ownership and arrange a safe handover.")
    ]

    for col, emoji, title, description in cards:
        with col:
            st.markdown(f"""
            <div class="info-card">
                <div style="font-size:30px">{emoji}</div>
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """, unsafe_allow_html=True)


# =========================================================
# 12. REPORT AN ITEM
# =========================================================

def report_item():

    is_demo = st.session_state.mode == "demo"

    show_mode_banner()

    show_hero(
        "CONTRIBUTE TO YOUR CAMPUS",
        "Report an item",
        "Every useful detail makes it easier to reunite an item with its owner."
    )

    with st.container(border=True):

        with st.form("report_form"):

            report_type = st.radio(
                "What would you like to report?",
                ["Lost", "Found"],
                horizontal=True
            )

            a, b = st.columns(2)

            with a:
                item_name = st.text_input(
                    "Item name *",
                    placeholder="e.g. Black Samsung phone"
                )

                category = st.selectbox(
                    "Category",
                    [
                        "Electronics",
                        "ID Card / Documents",
                        "Wallet / Money",
                        "Keys",
                        "Bags",
                        "Clothing",
                        "Books / Stationery",
                        "Accessories",
                        "Other"
                    ]
                )

                color = st.text_input(
                    "Colour",
                    placeholder="e.g. Black"
                )

            with b:
                location = st.text_input(
                    "Location *",
                    placeholder="e.g. Central Library"
                )

                item_date = st.date_input(
                    "Date lost / found",
                    value=date.today(),
                    max_value=date.today()
                )

                image = st.file_uploader(
                    "Upload an image (optional)",
                    type=["png", "jpg", "jpeg"]
                )

            description = st.text_area(
                "Description *",
                placeholder=(
                    "Describe the item, brand, special marks, "
                    "stickers or other identifying details."
                ),
                height=120
            )

            submitted = st.form_submit_button(
                "Submit report",
                type="primary",
                use_container_width=True
            )

            if submitted:

                if not item_name.strip() or not location.strip() or not description.strip():
                    st.error("Please complete all required fields.")

                else:

                    image_path = save_uploaded_image(image)

                    save_report(
                        st.session_state.user["id"],
                        report_type,
                        item_name.strip(),
                        category,
                        description.strip(),
                        color.strip(),
                        location.strip(),
                        item_date,
                        image_path,
                        is_demo
                    )

                    st.success("Your report has been submitted!")
                    st.balloons()


# =========================================================
# 13. BROWSE REPORTS
# =========================================================

def browse_reports():

    is_demo = st.session_state.mode == "demo"

    show_mode_banner()

    show_hero(
        "CAMPUS COMMUNITY",
        "Browse reports",
        "Explore items reported lost or found across your campus."
    )

    a, b = st.columns([1, 2])

    with a:
        selected = st.selectbox(
            "Report type",
            ["All reports", "Lost", "Found"]
        )

    with b:
        search = st.text_input(
            "Search items",
            placeholder="Search by item name, category or location..."
        )

    report_type = None if selected == "All reports" else selected

    rows = get_reports(
        is_demo,
        report_type=report_type,
        status="Active"
    )

    if search.strip():

        term = search.lower().strip()

        rows = [
            r for r in rows
            if term in r["item_name"].lower()
            or term in r["category"].lower()
            or term in r["location"].lower()
            or term in r["description"].lower()
        ]

    st.caption(f"{len(rows)} active report(s)")

    if not rows:

        st.info(
            "No reports match your search. Try another keyword "
            "or submit a new report."
        )

        if not is_demo:
            st.caption(
                "Example previews are available on the Dashboard. "
                "They are not included in actual search results."
            )

        return

    for item in rows:
        show_report_card(item, show_owner=True)


# =========================================================
# 14. POSSIBLE MATCHES
# =========================================================

def render_match_card(lost, found, score, details, allow_claim=True):

    level, icon = match_level(score)

    with st.container(border=True):

        a, b = st.columns([1, 3])

        with a:

            if found["image_path"] and os.path.exists(found["image_path"]):
                st.image(
                    found["image_path"],
                    use_container_width=True
                )
            else:
                st.markdown(
                    "<div style='background:#eef3fb;padding:25px;"
                    "border-radius:13px;text-align:center;font-size:40px;'>📦</div>",
                    unsafe_allow_html=True
                )

        with b:

            st.markdown(f"### {found['item_name']}")
            st.markdown(
                '<span class="status-found">FOUND ITEM</span>',
                unsafe_allow_html=True
            )

            st.markdown(f"**{icon} {level}**")

            st.metric("Similarity score", f"{score}%")
            st.progress(min(score / 100, 1.0))

            st.write(found["description"])

            st.caption(
                f"📍 {found['location']} · 📅 {found['item_date']}"
            )

        with st.expander("🔍 Why did FindIt suggest this match?"):

            st.write(
                "The score is calculated from five item characteristics."
            )

            for factor, (earned, maximum) in details.items():

                st.write(f"**{factor}: {earned}/{maximum} points**")

                st.progress(
                    min(earned / maximum, 1.0)
                )

            st.caption(
                "This is a heuristic similarity score, not a probability "
                "or proof of ownership."
            )

        if allow_claim:

            with st.expander("🤝 Request this item"):

                st.write(
                    "Provide identifying details that can help the finder "
                    "check whether this item belongs to you."
                )

                message = st.text_area(
                    "Verification details",
                    placeholder=(
                        "Example: My bottle has a small star sticker "
                        "near the bottom."
                    ),
                    key=f"claim_text_{found['id']}"
                )

                if st.button(
                    "Submit claim request",
                    key=f"claim_btn_{found['id']}",
                    type="primary",
                    use_container_width=True
                ):

                    if not message.strip():
                        st.error("Please provide verification details.")
                    else:
                        ok, result = submit_claim(
                            found,
                            lost,
                            st.session_state.user["id"],
                            message,
                            st.session_state.mode == "demo"
                        )

                        if ok:
                            st.success(result)
                            st.rerun()
                        else:
                            st.warning(result)


def possible_matches():

    is_demo = st.session_state.mode == "demo"

    show_mode_banner()

    show_hero(
        "FIND THE CONNECTION",
        "Smart matching",
        "FindIt compares lost and found reports to suggest possible matches."
    )

    lost_items = [
        r for r in get_my_reports(
            st.session_state.user["id"], is_demo
        )
        if r["report_type"] == "Lost" and r["status"] == "Active"
    ]

    # Demo uses fictional lost reports for demonstration.
    if is_demo:
        lost_items = [
            r for r in get_reports(True, "Lost", "Active")
        ]

    if not lost_items and not is_demo:

        st.info(
            "You have not submitted an active lost-item report yet. "
            "You can explore this working example below."
        )

        st.caption("INTERACTIVE EXAMPLE · FICTIONAL REPORTS")

        sample_lost = {
            "id": -1,
            "owner_id": -1,
            "report_type": "Lost",
            "item_name": "Samsung Galaxy S23",
            "category": "Electronics",
            "description": (
                "Black Samsung smartphone with a transparent back cover. "
                "A small scratch is visible near the camera."
            ),
            "color": "Black",
            "location": "Central Library, Reading Hall",
            "item_date": str(date.today()),
            "image_path": None,
            "status": "Active",
            "is_demo": 0
        }

        sample_found = {
            "id": -2,
            "owner_id": -2,
            "report_type": "Found",
            "item_name": "Samsung Galaxy Phone",
            "category": "Electronics",
            "description": (
                "Black Samsung mobile phone with a clear transparent case. "
                "Small scratch near the rear camera."
            ),
            "color": "Black",
            "location": "Library Entrance",
            "item_date": str(date.today()),
            "image_path": None,
            "status": "Active",
            "is_demo": 0
        }

        st.markdown("#### 1 · Lost item report")
        with st.container(border=True):
            st.markdown("### 📱 Samsung Galaxy S23")
            st.markdown(
                '<span class="status-lost">LOST ITEM</span>',
                unsafe_allow_html=True
            )
            st.write(sample_lost["description"])
            st.caption("Central Library · Electronics · Black")

        st.markdown("#### 2 · Found item report")
        with st.container(border=True):
            st.markdown("### 📱 Samsung Galaxy Phone")
            st.markdown(
                '<span class="status-found">FOUND ITEM</span>',
                unsafe_allow_html=True
            )
            st.write(sample_found["description"])
            st.caption("Library Entrance · Electronics · Black")

        score, details = calculate_match_details(
            sample_lost, sample_found
        )

        st.markdown("#### 3 · FindIt matching result")

        st.markdown(f"""
        <div class="match-box">
            <h3>🟢 Possible match identified</h3>
            <p style="color:#17643a;margin-top:7px;">
                The two reports share several matching characteristics.
            </p>
        </div>
        """, unsafe_allow_html=True)

        level, icon = match_level(score)

        st.markdown(f"### {icon} {level}")
        st.metric("Calculated similarity score", f"{score}%")
        st.progress(score / 100)

        st.markdown("### Why did FindIt suggest this match?")

        for factor, (earned, maximum) in details.items():
            st.write(f"**{factor}: {earned}/{maximum} points**")
            st.progress(earned / maximum)

        st.warning(
            "A similarity score is not proof of ownership. "
            "The item must be verified before returning it."
        )

        st.caption(
            "This example uses the same matching function as actual reports. "
            "It is not saved as a student report."
        )

        return

    if not lost_items:

        st.info("There are no active lost-item reports in this view yet.")
        return

    lost_by_id = {r["id"]: r for r in lost_items}

    selected_id = st.selectbox(
        "Select a lost item",
        options=[r["id"] for r in lost_items],
        format_func=lambda rid: (
            f"{lost_by_id[rid]['item_name']} · Report #{rid}"
        )
    )

    chosen = lost_by_id[selected_id]

    st.markdown("### Possible found-item matches")

    matches = find_matches(chosen, is_demo)

    if not matches:

        st.info(
            "No possible matches were found yet. "
            "New found-item reports will be checked against this item."
        )

        return

    st.caption(f"{len(matches)} possible match(es)")

    for old_score, found in matches:

        score, details = calculate_match_details(chosen, found)

        render_match_card(
            chosen, found, score, details
        )


# =========================================================
# 15. CLAIM REQUESTS
# =========================================================

def claim_requests():

    is_demo = st.session_state.mode == "demo"
    user_id = st.session_state.user["id"]

    show_mode_banner()

    show_hero(
        "SAFE ITEM RETURN",
        "Claim & verification centre",
        "Review requests and keep track of items you have claimed."
    )

    received_tab, sent_tab = st.tabs([
        "📥 Received requests",
        "📤 My claims"
    ])

    with received_tab:

        st.markdown("### Requests for items you found")

        received = get_claims_for_finder(user_id, is_demo)

        if not received:
            st.info(
                "No claim requests have been received yet. "
                "Requests will appear here when someone claims an item."
            )

        for claim in received:

            found = get_report_by_id(
                claim["found_report_id"], is_demo
            )

            lost = get_report_by_id(
                claim["lost_report_id"], is_demo
            )

            if not found or not lost:
                continue

            with st.container(border=True):

                st.markdown(f"### Claim request #{claim['id']}")

                st.write(f"**Found item:** {found['item_name']}")
                st.write(f"**Claimed lost item:** {lost['item_name']}")

                st.write("**Claimant's verification details:**")
                st.info(claim["message"])

                if claim["status"] == "Pending":

                    st.markdown(
                        '<span class="status-pending">PENDING REVIEW</span>',
                        unsafe_allow_html=True
                    )

                    st.warning(
                        "Check the details carefully and verify ownership "
                        "before approving."
                    )

                    a, b = st.columns(2)

                    with a:
                        if st.button(
                            "✅ Approve claim",
                            key=f"approve_{claim['id']}",
                            type="primary",
                            use_container_width=True
                        ):

                            if decide_claim(
                                claim["id"], user_id, is_demo, "Approved"
                            ):
                                st.success("Claim approved.")
                                st.rerun()

                    with b:
                        if st.button(
                            "Reject claim",
                            key=f"reject_{claim['id']}",
                            use_container_width=True
                        ):

                            if decide_claim(
                                claim["id"], user_id, is_demo, "Rejected"
                            ):
                                st.warning("Claim rejected.")
                                st.rerun()

                elif claim["status"] == "Approved":
                    st.success(
                        "Approved — both reports have been marked recovered."
                    )
                else:
                    st.error("This claim was rejected.")

    with sent_tab:

        st.markdown("### Claims you have submitted")

        sent = get_my_claims(user_id, is_demo)

        if not sent:
            st.info(
                "You have not submitted any claims. "
                "Visit Possible Matches to request an item."
            )

        for claim in sent:

            found = get_report_by_id(
                claim["found_report_id"], is_demo
            )

            with st.container(border=True):

                if found:
                    st.markdown(f"### {found['item_name']}")

                st.write(f"Your message: {claim['message']}")

                if claim["status"] == "Pending":
                    st.warning("⏳ Waiting for the finder to review.")
                elif claim["status"] == "Approved":
                    st.success("✅ Your claim was approved.")
                else:
                    st.error("❌ Your claim was rejected.")


# =========================================================
# 16. MY REPORTS
# =========================================================

def my_reports():

    is_demo = st.session_state.mode == "demo"
    user_id = st.session_state.user["id"]

    show_mode_banner()

    show_hero(
        "YOUR ACTIVITY",
        "My reports",
        "View and manage the lost and found reports submitted through your account."
    )

    rows = get_my_reports(user_id, is_demo)

    if not rows:
        st.info(
            "You haven't submitted any reports yet. "
            "Use Report an Item to create your first report."
        )
        return

    for item in rows:

        with st.container(border=True):

            a, b = st.columns([3, 1])

            with a:

                st.markdown(f"### {item['item_name']}")

                if item["report_type"] == "Lost":
                    st.markdown(
                        '<span class="status-lost">LOST ITEM</span>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<span class="status-found">FOUND ITEM</span>',
                        unsafe_allow_html=True
                    )

                st.write(item["description"])

                st.caption(
                    f"📍 {item['location']} · "
                    f"📅 {item['item_date']} · "
                    f"{item['category']}"
                )

                st.write(f"**Status:** {item['status']}")

            with b:

                if item["status"] == "Active":

                    if st.button(
                        "Mark recovered",
                        key=f"my_recover_{item['id']}"
                    ):

                        update_report_status(
                            item["id"], user_id, is_demo, "Recovered"
                        )

                        st.success("Report updated.")
                        st.rerun()

                else:
                    st.success("Recovered ✓")


# =========================================================
# 17. ABOUT FINDIT
# =========================================================

def about():

    show_mode_banner()

    show_hero(
        "ABOUT THE PROJECT",
        "FindIt",
        "A smarter way to reconnect lost belongings with their owners."
    )

    st.markdown("### The problem")

    st.write(
        "Students frequently lose personal belongings around campus. "
        "Information about lost and found items is often scattered "
        "across notice boards, class groups and informal conversations."
    )

    st.markdown("### Our solution")

    st.write(
        "FindIt provides one central platform to report lost and found "
        "items, browse campus reports, identify possible matches and "
        "manage claim requests."
    )

    st.markdown("### Core features")

    a, b = st.columns(2)

    with a:
        st.markdown("""
        - Student accounts
        - Lost and found reporting
        - Optional image uploads
        - Campus-wide report browsing
        """)

    with b:
        st.markdown("""
        - Text-based smart matching
        - Match score explanations
        - Claim and verification workflow
        - Recovered item tracking
        """)

    st.markdown("### Matching methodology")

    st.write(
        "FindIt calculates a heuristic similarity score using "
        "the following weighted characteristics:"
    )

    st.table({
        "Characteristic": [
            "Category",
            "Item name similarity",
            "Description similarity",
            "Colour",
            "Location"
        ],
        "Weight": ["30%", "25%", "25%", "10%", "10%"]
    })

    st.markdown("### Technology stack")

    st.write(
        "Python · Streamlit · SQLite · Text Similarity Matching"
    )

    st.caption(
        "The current prototype uses text and metadata similarity. "
        "It does not perform image recognition. Similarity scores "
        "are suggestions, not probabilities or proof of ownership."
    )


# =========================================================
# 18. MAIN NAVIGATION
# =========================================================

def main_app():

    user = st.session_state.user
    is_demo = st.session_state.mode == "demo"

    with st.sidebar:

        st.markdown("""
        <div style="padding:8px 0 17px 0;">
            <div style="font-size:31px;font-weight:800;
            color:white;font-family:Outfit,sans-serif;">
                🔎 FindIt
            </div>
            <div style="font-size:10px;letter-spacing:1.5px;
            color:#aabbd6;font-weight:700;">
                SMART CAMPUS LOST & FOUND
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        st.markdown(f"### Hello, {user['name'].split()[0]}!")

        st.caption(user["college"])
        st.caption(user["email"])

        st.divider()

        if is_demo:
            st.warning("🧪 DEMO MODE")
        else:
            st.success("🟢 LIVE MODE")

        st.markdown("**WORKSPACE**")

        pages = [
            "🏠 Dashboard",
            "📝 Report an Item",
            "🔎 Browse Reports",
            "✨ Possible Matches",
            "🤝 Claim Requests",
            "📁 My Reports",
            "💡 About FindIt"
        ]

        page = st.radio(
            "Navigation",
            pages,
            label_visibility="collapsed"
        )

        st.divider()

        if is_demo:

            st.markdown("**DEMO CONTROLS**")

            if st.button(
                "🔄 Reset sample data",
                use_container_width=True
            ):

                reset_demo_data()
                st.success("Demo data has been reset.")
                st.rerun()

            st.caption(
                "Only fictional sample reports are reset. "
                "Live student reports are not affected."
            )

            if st.button(
                "← Return to login",
                use_container_width=True
            ):

                st.session_state.user = None
                st.session_state.mode = "live"
                st.rerun()

        else:

            if st.button(
                "Logout",
                use_container_width=True
            ):

                st.session_state.user = None
                st.session_state.mode = "live"
                st.rerun()

        st.markdown("""
        <div style="padding-top:25px;font-size:11px;color:#8192ad;">
            FINDIT · CAMPUS COMMUNITY
            <br>Helping belongings find their way home.
        </div>
        """, unsafe_allow_html=True)

    if page == "🏠 Dashboard":
        dashboard()

    elif page == "📝 Report an Item":
        report_item()

    elif page == "🔎 Browse Reports":
        browse_reports()

    elif page == "✨ Possible Matches":
        possible_matches()

    elif page == "🤝 Claim Requests":
        claim_requests()

    elif page == "📁 My Reports":
        my_reports()

    elif page == "💡 About FindIt":
        about()


# =========================================================
# 19. APP ENTRY POINT
# =========================================================

if "user" not in st.session_state:
    st.session_state.user = None

if "mode" not in st.session_state:
    st.session_state.mode = "live"

if st.session_state.user is None:
    authentication_screen()
else:
    main_app()