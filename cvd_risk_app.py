import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go

# ----- Page Configuration & Branding -----
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")

# ----- Logo -----
col1, col2, col3 = st.columns([1, 6, 1])
with col3:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=300)
    else:
        st.warning("⚠️ Logo not found — please upload 'logo.png' into the app directory.")

# ----- Sidebar: Patient Profile -----
st.sidebar.title("🩺 Patient Profile")
age = st.sidebar.slider("Age (years)", 30, 90, 60)
sex = st.sidebar.radio("Sex", ["Male", "Female"])
weight = st.sidebar.number_input("Weight (kg)", 40.0, 200.0, 75.0)
height = st.sidebar.number_input("Height (cm)", 140.0, 210.0, 170.0)
bmi = weight / ((height / 100) ** 2)
st.sidebar.markdown(f"**BMI:** {bmi:.1f} kg/m²")
smoker = st.sidebar.checkbox("Current smoker", help="Tobacco use increases CVD risk")
diabetes = st.sidebar.checkbox("Diabetes", help="Diabetes doubles CVD risk")
egfr = st.sidebar.slider("eGFR (mL/min/1.73m²)", 15, 120, 90)

st.sidebar.markdown("**Vascular Disease (tick all that apply)**")
vasc1 = st.sidebar.checkbox("Coronary artery disease")
vasc2 = st.sidebar.checkbox("Cerebrovascular disease")
vasc3 = st.sidebar.checkbox("Peripheral artery disease")

# ----- Main Page -----
st.title("SMART CVD Risk Reduction Calculator")

# Step 1: Lab Results
with st.expander("🔬 Step 1: Lab Results", expanded=True):
    total_chol = st.number_input("Total Cholesterol (mmol/L)", 2.0, 10.0, 5.2, 0.1)
    hdl = st.number_input("HDL‑C (mmol/L)", 0.5, 3.0, 1.3, 0.1)
    baseline_ldl = st.number_input("Baseline LDL‑C (mmol/L)", 0.5, 6.0, 3.0, 0.1)
    crp = st.number_input("hs‑CRP (mg/L) — Baseline", 0.1, 20.0, 2.5, 0.1)
    hba1c = st.number_input("Latest HbA₁c (%)", 4.5, 15.0, 7.0, 0.1)
    tg = st.number_input("Fasting Triglycerides (mmol/L)", 0.5, 5.0, 1.5, 0.1)

# Step 2: Lipid-Lowering Therapy
with st.expander("💊 Step 2: Lipid-Lowering Therapy (Pre-Admission)", expanded=False):
    pre_stat = st.selectbox("Pre-admission Statin", ["None", "Atorvastatin 80mg", "Rosuvastatin 20mg"])
    pre_ez = st.checkbox("Pre-admission Ezetimibe")
    pre_bemp = st.checkbox("Pre-admission Bempedoic acid")

# Step 3: Intensify Lipid Therapy
with st.expander("🚀 Step 3: Intensify Lipid Therapy (New Interventions)", expanded=False):
    new_stat = st.selectbox("Statin initiation/intensification", ["None", "Atorvastatin 80mg", "Rosuvastatin 20mg"])
    new_ez = st.checkbox("Add Ezetimibe")
    new_bemp = st.checkbox("Add Bempedoic acid")
    pcsk9 = st.checkbox("PCSK9 inhibitor", help="Consider if LDL >1.8 mmol/L after statin/ezetimibe")
    inclisiran = st.checkbox("Inclisiran (siRNA)", help="Consider if LDL >1.8 mmol/L after statin/ezetimibe")

# Step 4: Results & Analysis
with st.expander("📈 Step 4: Results & Analysis", expanded=True):
    # Example calculations (replace with your actual logic)
    baseline_risk = 20
    projected_risk = 10

    fig = go.Figure(go.Bar(
        x=["Baseline Risk", "Projected Risk"],
        y=[baseline_risk, projected_risk],
        marker_color=["#e74c3c", "#2ecc71"],
    ))
    fig.update_layout(title="Risk Reduction Visualization", yaxis_title="Risk (%)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"**Absolute Risk Reduction:** {baseline_risk - projected_risk}%")
    st.markdown(f"**Relative Risk Reduction:** {(baseline_risk - projected_risk) / baseline_risk * 100:.1f}%")

# Footer
st.markdown("---")
st.markdown("Created by Samuel Panday — 21/04/2025")
st.markdown("Created by PRIME team (Prevention Recurrent Ischaemic Myocardial Events)")
st.markdown("King's College Hospital, London")
st.markdown("This tool supports discussions with your healthcare provider—it’s not a substitute for professional medical advice.")
