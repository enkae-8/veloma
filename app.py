import streamlit as st
import pandas as pd
import time
import os
from engine.sentry import Sentry
from engine.controller import Controller
from engine.database import Vault
from engine.reports import Auditor

# --- Initialize Core Components ---
if 'sentry' not in st.session_state:
    st.session_state.sentry = Sentry()
    st.session_state.controller = Controller()
    st.session_state.vault = Vault()
    st.session_state.auditor = Auditor()
    st.session_state.stress_ticks = 0
    st.session_state.last_alert_time = 0
    # Task Performance Tracking
    st.session_state.last_interaction = time.time()
    st.session_state.click_count = 0

# --- Telemetry: Market & Cognitive ---
risk = st.session_state.sentry.get_risk()
btc_price = st.session_state.sentry.last_price

# Update Interaction Latency (Reaction Time)
interaction_latency = time.time() - st.session_state.last_interaction

# Zone Logic
if risk < 40:
    zone_text, zone_color = "🟢 High-Agency: Manual decisions are safe.", "green"
    st.session_state.stress_ticks = max(0, st.session_state.stress_ticks - 1)
elif risk < 75:
    zone_text, zone_color = "🟡 Low-Agency: Automation is safer.", "yellow"
else:
    zone_text, zone_color = "🔴 Panic-Prone: Action likely regretful.", "red"
    st.session_state.stress_ticks += 1
    
    # Watchdog: Notify OS on critical risk
    current_time = time.time()
    if current_time - st.session_state.last_alert_time > 60:
        msg = f"BTC Stress: {risk:.1f}%. Trading gated for safety."
        os.system(f"osascript -e 'display notification \"{msg}\" with title \"🛡️ Veloma Watchdog\"'")
        st.session_state.last_alert_time = current_time

# Task Performance Multiplier: Penalize score if clicking too fast (frantic behavior)
# or if the user has been idle/lagging too long during high risk
performance_penalty = 0
if st.session_state.click_count > 5: # Frantic clicking detected
    performance_penalty = 10

decision_quality = max(0, 100 - (st.session_state.stress_ticks * 2) - performance_penalty)

# Log to Vault
st.session_state.vault.log_event(risk, zone_text, decision_quality)

# --- UI Setup ---
st.set_page_config(page_title="Veloma Agency Engine", layout="wide")

# --- Sidebar: Paper Wallet & Performance ---
with st.sidebar:
    st.header("💰 Paper Wallet")
    st.session_state.vault.initialize_wallet()
    balance, btc_held = st.session_state.vault.get_wallet()
    total_val = balance + (btc_held * btc_price)
    
    st.metric("Total Assets", f"${total_val:,.2f}", delta=f"{total_val-10000:,.2f}")
    
    # Execution Gating: Only allow if Agency > 85%
    can_trade = decision_quality > 85
    
    st.divider()
    if st.button("🛒 BUY $500 BTC", use_container_width=True, disabled=not can_trade):
        st.session_state.vault.execute_trade("BUY", 500, btc_price)
        st.session_state.click_count += 1
        st.rerun()
        
    if st.button("📉 SELL ALL BTC", use_container_width=True, disabled=not can_trade):
        st.session_state.vault.execute_trade("SELL", 0, btc_price)
        st.session_state.click_count += 1
        st.rerun()

    if not can_trade:
        st.warning("Decision Agency too low to execute trades.")

    st.divider()
    st.caption(f"Task Latency: {interaction_latency:.2f}s")
    if st.button("Clear Performance Noise"):
        st.session_state.click_count = 0

# --- Main Dashboard ---
st.markdown(f"# :{zone_color}[{zone_text}]")
st.caption(f"Live BTC Feed: **${btc_price:,.2f}** | Structural Strain: **{risk:.2f}%**")
st.divider()

history_data = st.session_state.vault.get_history(100)
df = pd.DataFrame(history_data, columns=["Market Risk", "Decision Quality"])

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Cognitive Audit Log")
    st.line_chart(df)

with col2:
    st.metric("Decision Quality", f"{decision_quality}%", 
              delta=f"{'OPTIMAL' if decision_quality > 90 else 'DEGRADED'}")
    
    if st.button("🚨 BREACH", use_container_width=True):
        st.session_state.controller.execute_breach()
        st.session_state.sentry.risk = 10.0
        st.session_state.stress_ticks = 0
        st.rerun()
    
    if not df.empty:
        pdf_bytes = st.session_state.auditor.generate_report(df)
        st.download_button("📂 Export Audit", data=pdf_bytes, file_name="audit.pdf")

# Reset interaction clock
st.session_state.last_interaction = time.time()

# Watchdog heartbeat
time.sleep(2)
st.rerun()