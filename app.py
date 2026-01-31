import streamlit as st
import pandas as pd
import time
import os
from engine.sentry import Sentry
from engine.controller import Controller
from engine.database import Vault
from engine.reports import Auditor  # استيراد سكرتير التقارير

# --- تهيئة المكونات الأساسية ---
if 'sentry' not in st.session_state:
    st.session_state.sentry = Sentry()
    st.session_state.controller = Controller()
    st.session_state.vault = Vault()
    st.session_state.auditor = Auditor()
    st.session_state.stress_ticks = 0
    st.session_state.last_alert_time = 0

# --- منطق القياس والوكالة البشرية ---
# السنتري الآن يسحب بيانات حقيقية من Coinbase API
risk = st.session_state.sentry.get_risk()
btc_price = st.session_state.sentry.last_price

if risk < 40:
    zone_text, zone_color = "🟢 High-Agency: Manual decisions are safe.", "green"
    st.session_state.stress_ticks = max(0, st.session_state.stress_ticks - 1)
elif risk < 75:
    zone_text, zone_color = "🟡 Low-Agency: Automation is safer.", "yellow"
else:
    zone_text, zone_color = "🔴 Panic-Prone: Action likely regretful.", "red"
    st.session_state.stress_ticks += 1
    
    # تنبيه الماك (Mac Notification)
    current_time = time.time()
    if current_time - st.session_state.last_alert_time > 60: # تنبيه واحد كل دقيقة كحد أقصى
        msg = f"BTC Price: ${btc_price:,.0f}. Risk: {risk:.1f}%. Step away!"
        os.system(f"osascript -e 'display notification \"{msg}\" with title \"🛡️ Veloma Sentry\"'")
        st.session_state.last_alert_time = current_time

decision_quality = max(0, 100 - (st.session_state.stress_ticks * 2))

# --- حفظ البيانات في الخزنة (Vault) ---
st.session_state.vault.log_event(risk, zone_text, decision_quality)

# --- إعداد واجهة المستخدم ---
st.set_page_config(page_title="Veloma Agency Engine", layout="wide")
st.markdown(f"# :{zone_color}[{zone_text}]")
st.caption(f"Live BTC Feed: **${btc_price:,.2f}** | Structural Strain: **{risk:.2f}%**")
st.divider()

# جلب البيانات التاريخية من قاعدة البيانات
history_data = st.session_state.vault.get_history(100)
if history_data:
    df = pd.DataFrame(history_data, columns=["Market Risk", "Decision Quality"])
else:
    df = pd.DataFrame(columns=["Market Risk", "Decision Quality"])

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Cognitive Audit Log")
    st.line_chart(df)

with col2:
    st.metric("Decision Quality", f"{decision_quality}%", 
              delta=f"-{100-decision_quality}%" if decision_quality < 100 else "Optimal", 
              delta_color="inverse")
    
    # زر التنفيذ "الشاعري"
    btn_label = "🚨 EMERGENCY BREACH" if risk > 75 else "🛡️ EXECUTE STRATEGIC BREACH"
    if st.button(btn_label, use_container_width=True):
        st.session_state.controller.execute_breach()
        st.session_state.sentry.risk = 10.0 # إعادة تعيين التوتر
        st.session_state.stress_ticks = 0
        st.rerun()
    
    # تفعيل زر تحميل التقرير PDF
    if not df.empty:
        try:
            pdf_bytes = st.session_state.auditor.generate_report(df)
            st.download_button(
                label="📂 Download Audit Report",
                data=pdf_bytes,
                file_name=f"Veloma_Audit_{int(time.time())}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF Error: {e}")

# التحديث التلقائي (ننتظر ثانيتين لاحترام حدود الـ API)
time.sleep(2)
st.rerun()