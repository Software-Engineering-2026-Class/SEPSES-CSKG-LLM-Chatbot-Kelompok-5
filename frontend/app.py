import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env")

st.set_page_config(
    page_title="SEPSES CSKG Chatbot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "SEPSES CSKG LLM Chatbot — Cybersecurity Analysis via Knowledge Graph + LLM",
    }
)

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg-primary:    #0a0e1a;
    --bg-secondary:  #0f1629;
    --bg-card:       #131d35;
    --bg-card-hover: #1a2545;
    --accent-green:  #00ff88;
    --accent-blue:   #00b4ff;
    --accent-red:    #ff4d6d;
    --accent-yellow: #ffd60a;
    --text-primary:  #e8eaf0;
    --text-muted:    #6b7a99;
    --border-color:  #1e2d4a;
    --border-accent: #00ff8840;
    --gradient-main: linear-gradient(135deg, #0a0e1a 0%, #0f1629 50%, #0a1628 100%);
}

.stApp {
    background: var(--gradient-main);
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080c18 0%, #0c1526 100%);
    border-right: 1px solid var(--border-color);
}
[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

.sidebar-logo {
    padding: 1.5rem 1rem 1rem;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 1rem;
}
.sidebar-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--accent-green) !important;
    letter-spacing: 0.05em;
    text-shadow: 0 0 20px rgba(0,255,136,0.4);
}
.sidebar-subtitle {
    font-size: 0.72rem;
    color: var(--text-muted) !important;
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
/* ── Nav Button  ────────────────────────────── */
[data-testid="stSidebar"] .stRadio label {
    cursor: pointer;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    margin: 2px 0;
    transition: all 0.2s ease;
    display: block;
    font-size: 0.9rem;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(0,255,136,0.08) !important;
    color: var(--accent-green) !important;
}
/* ── Cards ────────────────────────────────────────────────── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
}
.metric-card:hover {
    border-color: var(--border-accent);
    box-shadow: 0 0 25px rgba(0,255,136,0.1);
    transform: translateY(-2px);
}
.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--accent-green);
    font-family: 'JetBrains Mono', monospace;
}
.metric-sub {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}
/* ── Chat Bubbles ─────────────────────────────────────────── */
.chat-bubble-user {
    background: linear-gradient(135deg, #1a3a5c, #1e4a7a);
    border: 1px solid #2a5a8a;
    border-radius: 18px 18px 4px 18px;
    padding: 0.9rem 1.2rem;
    margin: 0.5rem 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 0.92rem;
    box-shadow: 0 2px 12px rgba(0,180,255,0.15);
}
.chat-bubble-assistant {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 18px 18px 18px 4px;
    padding: 0.9rem 1.2rem;
    margin: 0.5rem 0;
    max-width: 85%;
    font-size: 0.92rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    position: relative;
}
.chat-bubble-assistant::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px;
    height: 100%;
    background: linear-gradient(180deg, var(--accent-green), var(--accent-blue));
    border-radius: 4px 0 0 4px;
}
/* ── Source Citation Box ──────────────────────────────────── */
.source-box {
    background: rgba(0,255,136,0.05);
    border: 1px solid rgba(0,255,136,0.2);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-top: 0.5rem;
    font-size: 0.78rem;
    font-family: 'JetBrains Mono', monospace;
    color: var(--accent-green);
}

/* ── Status Badges ────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.badge-critical { background: rgba(255,77,109,0.2); color: #ff4d6d; border: 1px solid #ff4d6d40; }
.badge-high     { background: rgba(255,140,0,0.2);  color: #ff8c00; border: 1px solid #ff8c0040; }
.badge-medium   { background: rgba(255,214,10,0.2); color: #ffd60a; border: 1px solid #ffd60a40; }
.badge-low      { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff8840; }
.badge-info     { background: rgba(0,180,255,0.15); color: #00b4ff; border: 1px solid #00b4ff40; }

/* ── Section Headers ──────────────────────────────────────── */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.5rem;
    margin-bottom: 1.5rem;
    position: relative;
}
.section-header::after {
    content: '';
    position: absolute;
    bottom: -2px; left: 0;
    width: 60px;
    height: 2px;
    background: linear-gradient(90deg, var(--accent-green), var(--accent-blue));
}
/* ── Input Fields ─────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent-green) !important;
    box-shadow: 0 0 0 2px rgba(0,255,136,0.15) !important;
}

/* ── Buttons ──────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #00ff88, #00b4ff) !important;
    color: #0a0e1a !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.3s ease !important;
    letter-spacing: 0.03em !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 20px rgba(0,255,136,0.4) !important;
}
</style>
"""