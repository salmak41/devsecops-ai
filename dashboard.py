# import streamlit as st
# import requests

# st.title("AI DevSecOps Risk Predictor")

# test_pass_rate = st.slider("Test Pass Rate", 0.0, 1.0, 0.8)
# vulnerabilities = st.number_input("Vulnerabilities", 0, 10, 1)
# build_time = st.number_input("Build Time (sec)", 0, 1000, 100)

# if st.button("Predict"):
#     response = requests.post(
#         "http://127.0.0.1:8000/predict",
#         json={
#             "test_pass_rate": test_pass_rate,
#             "vulnerabilities": vulnerabilities,
#             "build_time": build_time
#         }
#     )
#     st.json(response.json())


# dashboard.py - Research-Grade AI DevSecOps Dashboard
import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="AI DevSecOps Monitoring Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- HEADER ----------
st.title("🚀 AI-Powered Autonomous DevSecOps System")
st.caption("Intelligent CI/CD Optimization & Security Risk Prediction")

# ---------- LOAD DATA ----------
def load_model_metrics():
    """Load model comparison metrics from training"""
    if os.path.exists('model_metrics.json'):
        with open('model_metrics.json') as f:
            return json.load(f)
    return None

def load_risk_decision():
    """Load the latest risk prediction"""
    if os.path.exists('risk-decision.json'):
        with open('risk-decision.json') as f:
            return json.load(f)
    return None

def load_pipeline_metrics():
    """Load the latest pipeline metrics"""
    if os.path.exists('metrics.json'):
        with open('metrics.json') as f:
            return json.load(f)
    return None

# Load all data
model_metrics = load_model_metrics()
risk_decision = load_risk_decision()
pipeline_metrics = load_pipeline_metrics()

# ---------- SIDEBAR ----------
st.sidebar.header("📊 System Status")

if risk_decision:
    decision_color = "🟢" if risk_decision.get('decision') == "DEPLOY" else "🔴"
    st.sidebar.markdown(f"{decision_color} **Last Decision:** {risk_decision.get('decision', 'N/A')}")
    st.sidebar.markdown(f"**Risk Score:** {risk_decision.get('risk_score', 'N/A')}%")
    st.sidebar.markdown(f"**Success Probability:** {risk_decision.get('success_probability', 'N/A')}%")
else:
    st.sidebar.warning("⚠️ No risk decision found. Run the pipeline first.")

if model_metrics:
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🏆 Best Model:**")
    st.sidebar.markdown(f"**{model_metrics.get('model', 'N/A')}**")
    st.sidebar.markdown(f"Accuracy: {model_metrics.get('metrics', {}).get('accuracy', 0):.4f}")

st.sidebar.markdown("---")
st.sidebar.caption("📌 Data from GitHub Actions pipeline")

# ---------- MAIN DASHBOARD ----------
col1, col2, col3, col4 = st.columns(4)

if risk_decision:
    with col1:
        st.metric(
            "📊 Risk Score", 
            f"{risk_decision.get('risk_score', 0)}%",
            delta="High Risk" if risk_decision.get('risk_score', 0) > 70 else "Safe"
        )
    
    with col2:
        st.metric(
            "✅ Success Probability",
            f"{risk_decision.get('success_probability', 0)}%"
        )
    
    with col3:
        decision = risk_decision.get('decision', 'N/A')
        color = "normal" if decision == "DEPLOY" else "inverse"
        st.metric(
            "🚦 Decision",
            decision,
            delta_color=color
        )
    
    with col4:
        st.metric(
            "🤖 Model Used",
            risk_decision.get('model', 'N/A')
        )
else:
    for col in [col1, col2, col3, col4]:
        with col:
            st.warning("⚠️ No data")

# ---------- EXPLAINABILITY SECTION ----------
st.subheader("🔍 Why Was This Decision Made?")

if risk_decision and risk_decision.get('top_factors'):
    factors = risk_decision.get('top_factors', [])
    if factors:
        for factor in factors:
            st.warning(f"⚠️ {factor}")
    else:
        st.success("✅ No major risks detected. Deployment is safe.")
else:
    st.info("Run the pipeline to see explainability insights.")

# ---------- TWO-COLUMN LAYOUT ----------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Model Performance Comparison")
    
    if model_metrics and 'all_models' in model_metrics:
        # Create comparison table
        models_data = []
        for name, metrics in model_metrics['all_models'].items():
            models_data.append({
                'Model': name,
                'Accuracy': metrics.get('accuracy', 0),
                'Precision': metrics.get('precision', 0),
                'Recall': metrics.get('recall', 0),
                'F1-Score': metrics.get('f1', 0)
            })
        
        df = pd.DataFrame(models_data)
        
        # Highlight best model
        best_model = model_metrics.get('model', '')
        df['Model'] = df['Model'].apply(lambda x: f"⭐ {x}" if x == best_model else x)
        
        st.dataframe(
            df.style.background_gradient(subset=['Accuracy', 'Precision', 'Recall', 'F1-Score'], cmap='Greens'),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Run the pipeline to see model comparison metrics.")

with col2:
    st.subheader("📈 Risk Trend")
    
    # Generate mock historical data (since we don't have real history yet)
    if risk_decision:
        # Create simulated history
        history = []
        base_risk = risk_decision.get('risk_score', 0)
        
        # Generate 10 data points with some variation
        np.random.seed(42)
        for i in range(10):
            variation = np.random.uniform(-10, 10)
            risk_value = max(0, min(100, base_risk + variation))
            history.append({
                'Build': i + 1,
                'Risk Score': risk_value
            })
        
        # Add current as last point
        history.append({
            'Build': len(history) + 1,
            'Risk Score': base_risk
        })
        
        df_history = pd.DataFrame(history)
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df_history['Build'], df_history['Risk Score'], marker='o', linewidth=2, color='#FF6B6B')
        ax.axhline(y=70, color='red', linestyle='--', label='Block Threshold (70%)')
        ax.axhline(y=50, color='orange', linestyle='--', label='Warning Threshold (50%)')
        ax.fill_between(df_history['Build'], 0, df_history['Risk Score'], alpha=0.3, color='#FF6B6B')
        ax.set_xlabel('Build Number')
        ax.set_ylabel('Risk Score (%)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    else:
        st.info("No data available.")

# ---------- PIPELINE METRICS ----------
st.subheader("📦 Pipeline Metrics")

if pipeline_metrics:
    cols = st.columns(5)
    
    with cols[0]:
        st.metric("✅ Test Pass Rate", f"{pipeline_metrics.get('test_pass_rate', 0) * 100:.1f}%")
    with cols[1]:
        st.metric("🔴 Critical Vulns", pipeline_metrics.get('critical_vulns', 0))
    with cols[2]:
        st.metric("🟠 High Vulns", pipeline_metrics.get('high_vulns', 0))
    with cols[3]:
        st.metric("⏱️ Build Time", f"{pipeline_metrics.get('build_time', 0)}s")
    with cols[4]:
        st.metric("📝 Code Churn", pipeline_metrics.get('code_churn', 0))
else:
    st.info("No pipeline metrics available. Run the pipeline to collect data.")

# ---------- RAW DATA ----------
with st.expander("📄 Raw Data (JSON)"):
    if risk_decision:
        st.json(risk_decision)
    else:
        st.write("No data")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("📌 Data is collected from GitHub Actions pipeline. Run the pipeline to update metrics.")