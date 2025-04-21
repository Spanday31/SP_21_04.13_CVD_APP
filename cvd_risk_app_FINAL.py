import streamlit as st
import os
import pandas as pd
import plotly.graph_objects as go

# ----- Page Configuration & Branding -----
st.set_page_config(layout="wide", page_title="SMART CVD Risk Reduction")

# ----- Logo in Top-Right (Large) -----
col1, col2 = st.columns([7, 1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=600)
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