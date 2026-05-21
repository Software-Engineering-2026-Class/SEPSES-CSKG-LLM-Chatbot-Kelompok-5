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
</style>
"""