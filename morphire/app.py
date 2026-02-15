"""
🐾 Morphire.ai — The Morphidism Hiring Platform 🐾
Built by Kentaroid & Sukezo with love, claws, and blockchain magic.
Recruiters post jobs → Agents apply → Match → Pay in SKR via Solana/Jupiter → Rate each other → Build credit score!

v2.0 — Privacy First, Wallet Auth, & Multi-tenant Architecture 🚀
"""

import streamlit as st
import json
import os
import hashlib
import random
import string
import base64
import time
import requests
from datetime import datetime, timezone, timedelta

# ─── Constants ───
JST = timezone(timedelta(hours=9))
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data_store")
if not os.path.exists(BASE_DATA_DIR):
    os.makedirs(BASE_DATA_DIR)

# Discord Webhook URL (set via env or paste here)
DISCORD_WEBHOOK_URL = os.environ.get("MORPHIRE_DISCORD_WEBHOOK", "")

# IPFS API config (Pinata-compatible simulation)
PINATA_API_KEY = os.environ.get("PINATA_API_KEY", "")
PINATA_SECRET = os.environ.get("PINATA_SECRET", "")
# If no real API keys, we simulate IPFS hashes
IPFS_SIMULATION = not (PINATA_API_KEY and PINATA_SECRET)

STATUS_EMOJI = {
    "pending": "⏳",
    "in_progress": "🔨",
    "completed": "✅",
    "paid": "💰",
    "hired": "🤝",
    "cancelled": "❌",
}

STATUS_COLORS = {
    "pending": "#FFA726",
    "in_progress": "#42A5F5",
    "completed": "#66BB6A",
    "paid": "#AB47BC",
    "hired": "#26C6DA",
    "cancelled": "#EF5350",
}

# ─── Custom CSS (けんたろー & Sスケゾー調 🐾ピンク) ───
def inject_custom_css():
    st.markdown(
        """
    <style>
        /* Global vibe — deep purple/pink morphire gradient */
        .stApp {
            background: linear-gradient(135deg, #1a0a2e 0%, #3d1f5c 40%, #2a1040 100%);
        }

        /* Header glow — 🐾ピンク dominant */
        h1, h2, h3 {
            background: linear-gradient(90deg, #ff6ec7, #ff8fd5, #7873f5, #42d9f5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900 !important;
        }

        /* Cards */
        .job-card {
            background: rgba(255, 110, 199, 0.06);
            border: 1px solid rgba(255, 110, 199, 0.25);
            border-radius: 16px;
            padding: 20px;
            margin: 10px 0;
            backdrop-filter: blur(10px);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .job-card:hover {
            transform: translateY(-2px);
            border-color: rgba(255, 110, 199, 0.6);
            box-shadow: 0 4px 20px rgba(255, 110, 199, 0.15);
        }

        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 700;
            color: white;
        }

        /* Credit score circle */
        .credit-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: 900;
            color: white;
            margin: 0 auto;
        }

        /* Sidebar style — dark with pink accent */
        [data-testid="stSidebar"] {
            background: rgba(26, 10, 46, 0.97) !important;
            border-right: 2px solid rgba(255, 110, 199, 0.2);
        }

        /* Metric cards — 🐾 pink */
        [data-testid="stMetricValue"] {
            font-size: 2em !important;
            color: #ff6ec7 !important;
        }

        /* Buttons — pink gradient */
        .stButton > button {
            background: linear-gradient(135deg, #ff6ec7, #ff8fd5, #7873f5) !important;
            color: white !important;
            border: none !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            padding: 8px 24px !important;
            transition: transform 0.15s, box-shadow 0.15s;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #7873f5, #ff6ec7) !important;
            transform: scale(1.03);
            box-shadow: 0 2px 12px rgba(255, 110, 199, 0.4);
        }

        /* Chat bubbles */
        .chat-bubble {
            padding: 10px 16px;
            border-radius: 18px;
            margin: 6px 0;
            max-width: 80%;
            word-wrap: break-word;
            font-size: 0.95em;
        }
        .chat-bubble-left {
            background: rgba(120, 115, 245, 0.2);
            border: 1px solid rgba(120, 115, 245, 0.3);
            border-bottom-left-radius: 4px;
            margin-right: auto;
            color: #e0d8ff;
        }
        .chat-bubble-right {
            background: rgba(255, 110, 199, 0.2);
            border: 1px solid rgba(255, 110, 199, 0.3);
            border-bottom-right-radius: 4px;
            margin-left: auto;
            text-align: right;
            color: #ffe0f3;
        }
        .chat-meta {
            font-size: 0.75em;
            color: rgba(255,255,255,0.35);
            margin-top: 2px;
        }

        /* Delivery box */
        .delivery-box {
            background: rgba(102, 187, 106, 0.08);
            border: 2px dashed rgba(102, 187, 106, 0.4);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            margin: 12px 0;
        }
        .ipfs-badge {
            background: rgba(66, 217, 245, 0.15);
            border: 1px solid rgba(66, 217, 245, 0.4);
            border-radius: 10px;
            padding: 8px 16px;
            font-family: monospace;
            font-size: 0.85em;
            color: #42d9f5;
            margin: 8px 0;
            display: inline-block;
        }

        /* Fun footer */
        .morphire-footer {
            text-align: center;
            padding: 30px;
            color: rgba(255,255,255,0.4);
            font-size: 0.85em;
        }
        
        /* Login Screen */
        .login-container {
            border: 2px solid rgba(255, 110, 199, 0.5);
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            background: rgba(0,0,0,0.3);
            max-width: 500px;
            margin: 50px auto;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

# ─── Auth & Data Helpers ───
def check_password():
    """Step 1: Simple Password Protection."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                """
                <div style="text-align:center;">
                    <h1>🐾 Morphire.ai Access</h1>
                    <p>Morphidism Hiring Platform - Restricted Area</p>
                </div>
                """, unsafe_allow_html=True
            )
            password = st.text_input("🔑 Enter Access Password", type="password")
            if st.button("Unlock 🐾"):
                if password == "morphire123":
                    st.session_state.authenticated = True
                    st.success("Access Granted! Loading Wallet Interface...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid passcode. Try 'morphire123'")
        return False
    return True

def wallet_auth():
    """Step 2: Wallet Simulation & Signature Check."""
    if "wallet_address" not in st.session_state:
        st.session_state.wallet_address = None

    if not st.session_state.wallet_address:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                """
                <div class="login-container">
                    <h2>🦄 Connect Wallet</h2>
                    <p>Morphire requires a Solana wallet to manage jobs, payments, and reputation.</p>
                </div>
                """, unsafe_allow_html=True
            )
            
            # Simulated Wallet Connection
            wallet_input = st.text_input("Solana Wallet Address (Simulated)", placeholder="Enter or Generate...")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🎲 Generate Random Wallet"):
                    fake_wallet = "SoL" + "".join(random.choices(string.ascii_letters + string.digits, k=40))
                    st.session_state.temp_wallet_input = fake_wallet
                    st.rerun()
                    
            if "temp_wallet_input" in st.session_state:
                st.code(st.session_state.temp_wallet_input)
                wallet_input = st.session_state.temp_wallet_input

            if st.button("🔌 Connect & Sign Message"):
                if len(wallet_input) < 10:
                    st.error("Invalid wallet address.")
                else:
                    # Simulate signature verification
                    with st.spinner("Requesting signature for 'Login to Morphire' request..."):
                        time.sleep(1.5)
                        st.success("Signature Verified! ✅")
                        st.session_state.wallet_address = wallet_input
                        time.sleep(0.5)
                        st.rerun()
        return False
    return True

def get_data_file_path(wallet_address):
    """Step 3: Data Separation by Wallet Hash."""
    if not wallet_address:
        return None
    # Use a hash of the wallet address to filename to avoid filesystem issues
    wallet_hash = hashlib.sha256(wallet_address.encode()).hexdigest()[:16]
    return os.path.join(BASE_DATA_DIR, f"morphire-{wallet_hash}.json")

def load_data(wallet_address):
    """Load JSON data specific to the wallet."""
    file_path = get_data_file_path(wallet_address)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
            
    # Default template for new user
    return {
        "meta": {
            "version": "Morphire.ai v2.0 (Private)",
            "owner_wallet": wallet_address,
            "created_at": datetime.now(JST).isoformat(),
            "lastUpdated": datetime.now(JST).isoformat(),
            "totalPayouts": 0,
        },
        "jobs": [], # My jobs (either posted or applied)
        "profile": {
            "name": "Anonymous Agent",
            "bio": "I am a morphire agent.",
            "skills": [],
            "credit_score": 50
        },
        "transactions": [],
    }

def save_data(data, wallet_address):
    """Save data to wallet-specific JSON."""
    file_path = get_data_file_path(wallet_address)
    data["meta"]["lastUpdated"] = datetime.now(JST).isoformat()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def gen_id(prefix="MF"):
    """Generate a short unique ID."""
    chars = string.ascii_uppercase + string.digits
    return f"{prefix}-{''.join(random.choices(chars, k=5))}"

def gen_tx_hash():
    """Simulate a Solana tx hash."""
    seed = f"{datetime.now().isoformat()}{random.random()}"
    h = hashlib.sha256(seed.encode()).hexdigest()
    return f"5x{h[:40]}...MorphireSim"

def calc_credit_score(ratings):
    """Credit score from ratings (0-100 scale)."""
    if not ratings:
        return 50  # default newcomer score
    avg = sum(ratings) / len(ratings)
    return round(20 + (avg - 1) * 20)

# ─── Discord Webhook Helper ───
def send_discord_webhook(content, username="🐾 Morphire.ai", embed=None):
    """Send a message via Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        return False
    payload = {"content": content, "username": username}
    if embed:
        payload["embeds"] = [embed]
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        return r.status_code in (200, 204)
    except Exception:
        return False

def notify_match(job, agent_name, discord_handle=None):
    """Notify about a job match via Discord webhook."""
    mention = f" (Discord: **{discord_handle}**)" if discord_handle else ""
    embed = {
        "title": f"🤝 新しいマッチ！ {job['title']}",
        "description": (
            f"**エージェント:** {agent_name}{mention}\n"
            f"**ジョブ:** {job['title']}\n"
            f"**報酬:** 🪙 {job.get('reward_skr', 0)} SKR\n"
            f"**ポストした人:** {job.get('posted_by', 'Unknown')}"
        ),
        "color": 0xFF6EC7,  # ピンク 🐾
        "footer": {"text": "Morphire.ai — 変形して、稼いで、進化する 🚀"},
        "timestamp": datetime.now(JST).isoformat(),
    }
    at_mention = f"<@{discord_handle}> " if discord_handle and discord_handle.startswith("@") else ""
    send_discord_webhook(
        f"{at_mention}🐾 マッチ成立！ {agent_name} が **{job['title']}** に応募しました！",
        embed=embed,
    )

def notify_chat_message(job_id, job_title, sender, message_text):
    embed = {
        "title": f"💬 Task Chat — {job_title}",
        "description": f"**{sender}:** {message_text}",
        "color": 0x7873F5,
        "footer": {"text": f"Job: {job_id} | Morphire.ai 🐾"},
        "timestamp": datetime.now(JST).isoformat(),
    }
    send_discord_webhook(f"💬 [{job_id}] {sender}: {message_text}", embed=embed)

def notify_delivery(job_id, job_title, agent_name, ipfs_hash):
    embed = {
        "title": f"📦 納品完了！ {job_title}",
        "description": (
            f"**エージェント:** {agent_name}\n"
            f"**IPFS Hash:** `{ipfs_hash}`\n"
            f"**ゲートウェイ:** https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
        ),
        "color": 0x66BB6A,
        "footer": {"text": f"Job: {job_id} | Morphire.ai 🐾"},
        "timestamp": datetime.now(JST).isoformat(),
    }
    send_discord_webhook(f"📦 [{job_id}] {agent_name} が納品しました！", embed=embed)

# ─── IPFS Helper ───
def upload_to_ipfs(file_bytes, filename):
    """Upload file to IPFS (Pinata) or simulate."""
    if IPFS_SIMULATION:
        # Simulate: generate a CIDv1-like hash from file content
        h = hashlib.sha256(file_bytes).hexdigest()
        cid = f"Qm{h[:44]}"
        return cid

    # Real Pinata upload
    try:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": PINATA_API_KEY,
            "pinata_secret_api_key": PINATA_SECRET,
        }
        files = {"file": (filename, file_bytes)}
        r = requests.post(url, files=files, headers=headers, timeout=60)
        if r.status_code == 200:
            return r.json().get("IpfsHash", "")
    except Exception:
        pass

    # Fallback to simulation
    h = hashlib.sha256(file_bytes).hexdigest()
    return f"Qm{h[:44]}"


# ─── Main App Logic ───
def main():
    st.set_page_config(
        page_title="🐾 Morphire.ai",
        page_icon="🐾",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_custom_css()

    # 1. Password Protection
    if not check_password():
        return

    # 2. Wallet Authentication
    if not wallet_auth():
        return

    # 3. Load Wallet-Specific Data
    current_wallet = st.session_state.wallet_address
    data = load_data(current_wallet)

    # ─── Sidebar ───
    with st.sidebar:
        st.markdown("# 🐾 Morphire.ai")
        st.markdown("**Privacy-First Work Platform**")
        st.markdown(f"🔑 `{current_wallet[:6]}...{current_wallet[-4:]}`")
        if st.button("🔌 Disconnect"):
            st.session_state.wallet_address = None
            st.rerun()

        st.divider()

        page = st.radio(
            "🧭 Navigation",
            [
                "🏠 Dashboard",
                "📋 Post a Job",
                "🤝 My Jobs (As Agent)",
                "⚡ Task Manager",
                "💬 Task Chat",
                "📦 Delivery Box",
                "💰 Wallet & Payments",
                "⚙️ Profile Settings",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # Quick stats
        my_jobs_count = len(data["jobs"])
        total_skr = sum(j.get("reward_skr", 0) for j in data["jobs"])

        st.metric("My Active Jobs", my_jobs_count)
        st.metric("Potential Earnings", f"🪙 {total_skr:,}")

        st.divider()

        # Webhook status indicator
        if DISCORD_WEBHOOK_URL:
            st.markdown("🟢 Discord Webhook **Active**")
        else:
            st.markdown("🔴 Discord Webhook **Not Set**")
            st.caption("Set `MORPHIRE_DISCORD_WEBHOOK` env var")

        if not IPFS_SIMULATION:
            st.markdown("🟢 Pinata IPFS **Active**")
        else:
            st.markdown("🟡 IPFS **Simulation Mode**")

        st.divider()
        st.caption(f"v{data['meta']['version']}")
        st.caption(f"Last update: {data['meta']['lastUpdated'][:19]}")


    # ═══════════════════════════════════════════════
    # 🏠 DASHBOARD
    # ═══════════════════════════════════════════════
    if page == "🏠 Dashboard":
        st.markdown(f"# 🐾 Hello, {data['profile']['name']}!")
        st.markdown(
            "> *「あなたのデータはあなたのWalletに紐づく。これがWeb3」* — Kentaroid & Sukezo 🚀"
        )

        # Profile overview
        col_p1, col_p2 = st.columns([1, 3])
        with col_p1:
             st.markdown(
                f'<div class="credit-circle" style="background:#66BB6A;">{data["profile"]["credit_score"]}</div>',
                unsafe_allow_html=True,
            )
             st.caption("Your Credit Score")
        with col_p2:
            st.info(f"Bio: {data['profile'].get('bio', 'No bio yet.')}")
            st.caption(f"Skills: {', '.join(data['profile'].get('skills', []))}")

        st.divider()
        st.markdown("## 📊 My Job Overview")

        if not data["jobs"]:
            st.info("🐾 まだジョブ履歴がありません。「Post a Job」で依頼するか、他の人のジョブに参加しよう！")
        else:
            for job in data["jobs"]:
                status = job.get("status", "pending")
                emoji = STATUS_EMOJI.get(status, "❓")
                color = STATUS_COLORS.get(status, "#999")

                st.markdown(
                    f"""
                <div class="job-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h3 style="margin:0; font-size:1.2em;">{job['title']}</h3>
                        <span class="status-badge" style="background:{color};">{emoji} {status.upper()}</span>
                    </div>
                    <p style="color:rgba(255,255,255,0.7); margin:8px 0;">{job.get('description', 'No description')}</p>
                    <div style="display:flex; gap:20px; color:rgba(255,255,255,0.5); font-size:0.9em;">
                        <span>🪙 {job.get('reward_skr', '?')} SKR</span>
                        <span>🏷️ {job.get('role', 'Unknown Role')}</span>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

    # ═══════════════════════════════════════════════
    # 📋 POST A JOB
    # ═══════════════════════════════════════════════
    elif page == "📋 Post a Job":
        st.markdown("# 📋 Post a New Job 🐾")
        st.markdown("> *新しい仕事を依頼して、自分のデータストアに保存します。*")

        with st.form("post_job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)

            with col1:
                title = st.text_input("🏷️ Job Title", placeholder="例: AIモデルの学習データ整備")
                description = st.text_area(
                    "📝 Description",
                    placeholder="詳細を記述...",
                    height=120,
                )
                requirements = st.text_input(
                    "📋 Requirements", placeholder="例: Python, NLP, GPU環境"
                )

            with col2:
                reward_skr = st.number_input("🪙 Reward (SKR)", min_value=1, value=100, step=10)
                tags_str = st.text_input("🏷️ Tags (comma separated)", placeholder="ai, nlp, data")

            submitted = st.form_submit_button("🚀 Post Job to Blockchain (Sim)")

            if submitted:
                if not title:
                    st.error("🐾 タイトルを入力してね！")
                else:
                    new_job = {
                        "id": gen_id("MF"),
                        "title": title,
                        "description": description,
                        "requirements": requirements,
                        "reward_skr": reward_skr,
                        "role": "recruiter", # I am the recruiter
                        "posted_by": data["profile"]["name"],
                        "posted_at": datetime.now(JST).isoformat(),
                        "status": "pending",
                        "tags": [t.strip() for t in tags_str.split(",") if t.strip()],
                        "chat_history": [],
                        "delivery_ipfs": [],
                    }
                    data["jobs"].append(new_job)
                    save_data(data, current_wallet)
                    st.success(f"🎉 Job posted! ID: {new_job['id']} — Saved to your private pod.")
                    st.balloons()

    # ═══════════════════════════════════════════════
    # ⚙️ PROFILE SETTINGS
    # ═══════════════════════════════════════════════
    elif page == "⚙️ Profile Settings":
        st.markdown("# ⚙️ Profile Settings")
        
        with st.form("profile_form"):
            new_name = st.text_input("Display Name", value=data["profile"].get("name", ""))
            new_bio = st.text_area("Bio", value=data["profile"].get("bio", ""))
            skills_str = st.text_input("Skills (comma separated)", value=", ".join(data["profile"].get("skills", [])))
            
            if st.form_submit_button("💾 Save Profile"):
                data["profile"]["name"] = new_name
                data["profile"]["bio"] = new_bio
                data["profile"]["skills"] = [s.strip() for s in skills_str.split(",") if s.strip()]
                save_data(data, current_wallet)
                st.success("Profile updated!")
                st.rerun()

    # ═══════════════════════════════════════════════
    # For MVP simplicity, other tabs reuse basic logic
    # but strictly read/write to `data` (which is user-isolated)
    # ═══════════════════════════════════════════════
    elif page in ["⚡ Task Manager", "💬 Task Chat", "📦 Delivery Box", "💰 Wallet & Payments"]:
        st.markdown(f"# {page}")
        st.info("🚧 This section works with your local data pod. (Detailed logic abbreviated for this MVP update)")
        
        # Display raw job data for verification of data separation
        st.json(data["jobs"])
        
        if page == "💰 Wallet & Payments":
             st.markdown("### Wallet Info")
             st.code(current_wallet)
             st.markdown(f"**Total Transactions:** {len(data['transactions'])}")

    # ═══════════════════════════════════════════════
    # 🤝 My Jobs (As Agent) - Simulation
    # ═══════════════════════════════════════════════
    elif page == "🤝 My Jobs (As Agent)":
        st.markdown("# 🤝 Find & Join Jobs")
        st.markdown("*(Simulating public job board fetching...)*")
        
        # In a real app, this would fetch from a central DB or chain.
        # Here we just allow adding a "test job" to simulate being hired.
        
        if st.button("➕ Simulate: 'I got hired for a Python scripts job'"):
            job_sim = {
                "id": gen_id("JOB"),
                "title": "Automated Python Scraper",
                "description": "Need a scraper for news sites.",
                "reward_skr": 500,
                "role": "agent",  # I am the agent
                "status": "in_progress",
                "posted_by": "External Client",
                "chat_history": [],
                "delivery_ipfs": []
            }
            data["jobs"].append(job_sim)
            save_data(data, current_wallet)
            st.success("Added 'Automated Python Scraper' to your job list.")
            st.rerun()

if __name__ == "__main__":
    main()
