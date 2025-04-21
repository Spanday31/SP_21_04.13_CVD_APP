import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from datetime import date

# Configure page
st.set_page_config(page_title="PRIME CVD Risk Calculator", layout="wide", page_icon="🫀")

# Constants
EVIDENCE = {
    "smoking": {
        "effect": "2-4x higher risk of recurrent events",
        "source": "Hackshaw et al. BMJ 2018 (PMID: 29367388)"
    },
    "ldl": {
        "effect": "22% RR reduction per 1 mmol/L LDL reduction",
        "source": "CTT Collaboration, Lancet 2010 (PMID: 21067804)"
    },
    "statin_high": {
        "effect": "35% RR reduction vs no statin",
        "source": "TNT Trial, NEJM 2005 (PMID: 15930428)"
    },
    "sbp": {
        "effect": "25% RR reduction with intensive control",
        "source": "SPRINT Trial, NEJM 2015 (PMID: 26551272)"
    }
}

# SMART-2 Risk Calculation (Dorresteijn et al. Eur Heart J 2019)
def calculate_smart2_risk(age, sex, diabetes, smoker, egfr, vasc_count, ldl, sbp):
    coefficients = {
        'intercept': -8.1937,
        'age': 0.0635,
        'female': -0.3372,
        'diabetes': 0.5034,
        'smoker': 0.7862,
        'egfr<30': 0.9235 if egfr < 30 else 0,
        'egfr30-60': 0.5539 if 30 <= egfr < 60 else 0,
        'polyvascular': 0.5434 if vasc_count >= 2 else 0,
        'ldl': 0.2436 * (ldl - 2.5),
        'sbp': 0.0083 * (sbp - 120)
    }
    
    lp = (coefficients['intercept'] + 
          coefficients['age'] * (age - 60) + 
          coefficients['female'] * (1 if sex == "Female" else 0) +
          coefficients['diabetes'] * diabetes +
          coefficients['smoker'] * smoker +
          coefficients['egfr<30'] +
          coefficients['egfr30-60'] +
          coefficients['polyvascular'] +
          coefficients['ldl'] +
          coefficients['sbp'])
    
    risk_percent = 100 * (1 - np.exp(-np.exp(lp) * 10))
    return max(0, min(100, round(risk_percent, 1)))  # Bound between 0-100%

# Logo and Header
col1, col2 = st.columns([5,1])
with col1:
    st.title("PRIME SMART-2 CVD Risk Calculator")
    st.caption("""
    *Estimates 10-year risk of recurrent cardiovascular events in patients with established CVD*  
    *Based on: Dorresteijn JAN et al. Eur Heart J 2019;40(37):3133-3140 [PMID: 31211368]*
    """)
with col2:
    st.image("logo.png", width=150)  # Make sure logo.png is in your app directory

# Sidebar - Patient Characteristics
with st.sidebar:
    st.markdown("### Patient Characteristics")
    age = st.slider("Age (years)", 30, 90, 65)
    sex = st.radio("Sex", ["Male", "Female"])
    diabetes = st.checkbox("Diabetes mellitus")
    smoker = st.checkbox("Current smoker", help=f"{EVIDENCE['smoking']['effect']} | {EVIDENCE['smoking']['source']}")
    
    st.markdown("### Vascular Disease")
    vasc_cor = st.checkbox("Coronary artery disease")
    vasc_cer = st.checkbox("Cerebrovascular disease")
    vasc_per = st.checkbox("Peripheral artery disease")
    vasc_count = sum([vasc_cor, vasc_cer, vasc_per])

# Main Content - Linear Workflow
st.header("1. Clinical Markers", divider="blue")
col1, col2 = st.columns(2)
with col1:
    ldl = st.number_input("LDL-C (mmol/L)", 0.5, 10.0, 3.0, step=0.1,
                         help=f"{EVIDENCE['ldl']['effect']} | {EVIDENCE['ldl']['source']}")
    sbp = st.number_input("Systolic BP (mmHg)", 80, 220, 140, step=1,
                         help=f"{EVIDENCE['sbp']['effect']} | {EVIDENCE['sbp']['source']}")
with col2:
    egfr = st.slider("eGFR (mL/min/1.73m²)", 15, 120, 60)
    hdl = st.number_input("HDL-C (mmol/L)", 0.5, 3.0, 1.3, step=0.1)

st.header("2. Treatment Options", divider="blue")

with st.expander("Lipid Management", expanded=True):
    st.radio("Statin intensity", ["None", "Moderate", "High"],
             index=1, key="statin",
             help=f"{EVIDENCE['statin_high']['effect']} | {EVIDENCE['statin_high']['source']}")
    
    if ldl >= 1.8:  # Only show if clinically relevant
        st.checkbox("PCSK9 inhibitor", key="pcsk9i")
    st.checkbox("Ezetimibe 10mg daily", key="ezetimibe")

with st.expander("Blood Pressure Management"):
    sbp_target = st.slider("Target SBP (mmHg)", 80, 220, 130)
    st.checkbox("ACE inhibitor/ARB")
    st.checkbox("Calcium channel blocker")

with st.expander("Lifestyle Interventions"):
    st.checkbox("Mediterranean diet")
    st.checkbox("Regular exercise (≥150 min/week)")
    if smoker:
        st.checkbox("Smoking cessation program")

# Risk Calculation
st.header("3. Risk Assessment", divider="blue")

# Calculate baseline risk
baseline_risk = calculate_smart2_risk(age, sex, diabetes, smoker, egfr, vasc_count, ldl, sbp)

# Calculate treatment effects
rr_reduction = 0
if st.session_state.statin == "Moderate":
    rr_reduction += 25
elif st.session_state.statin == "High":
    rr_reduction += 35
if st.session_state.ezetimibe:
    rr_reduction += 6
if st.session_state.pcsk9i:
    rr_reduction += 15
if sbp_target < 130:
    rr_reduction += 15

projected_risk = max(0, baseline_risk * (1 - rr_reduction/100))

# Display Results
col1, col2 = st.columns(2)
with col1:
    st.metric("Baseline 10-Year Risk", 
              f"{baseline_risk}%",
              help="Untreated risk of recurrent CVD event")
with col2:
    st.metric("Projected Risk with Treatments", 
              f"{projected_risk:.1f}%", 
              delta=f"-{baseline_risk - projected_risk:.1f}%",
              delta_color="inverse",
              help=f"Estimated {rr_reduction}% relative risk reduction")

# Risk Trend Visualization
risk_data = pd.DataFrame({
    "Scenario": ["Baseline", "With Interventions"],
    "Risk (%)": [baseline_risk, projected_risk]
})

fig = px.bar(risk_data, x="Scenario", y="Risk (%)", 
             color="Scenario", color_discrete_map={
                 "Baseline": "#FF5A5F", 
                 "With Interventions": "#25A55F"
             },
             text="Risk (%)", height=350)
fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
fig.update_layout(showlegend=False, xaxis_title="", 
                 yaxis_title="10-Year Risk (%)",
                 margin=dict(l=20, r=20, t=30, b=20))
st.plotly_chart(fig, use_container_width=True)

# Clinical Recommendations
if projected_risk >= 30:
    st.error("""
    **🔴 Very High Risk (≥30%) Recommendations:**
    - Intensive lipid lowering (target LDL <1.4 mmol/L)
    - Consider PCSK9 inhibitor if LDL remains elevated
    - Multidisciplinary risk factor management
    """)
elif projected_risk >= 20:
    st.warning("""
    **🟠 High Risk (20-29%) Recommendations:**
    - Optimize statin therapy (high-intensity preferred)
    - Target SBP <130 mmHg if tolerated
    - Address all modifiable risk factors
    """)
else:
    st.success("""
    **🟢 Moderate Risk (<20%) Recommendations:**
    - Maintain adherence to current therapies
    - Focus on lifestyle interventions
    - Annual risk reassessment
    """)

# References & Footer
with st.expander("Evidence References"):
    for key, evidence in EVIDENCE.items():
        st.markdown(f"🔹 **{evidence['effect']}**  \n*{evidence['source']}*")

st.divider()
st.caption("""
*Developed by the PRIME Team (Prevention Recurrent Ischaemic Myocardial Events)*  
*King's College Hospital, London • {date.today().strftime('%Y-%m-%d')}*  
*This tool supports clinical discussions but does not replace professional judgment.*
""")
