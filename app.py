# app.py
# This Streamlit application provides an interactive demo comparing
# the decisions of the rule-based "Teacher" (rules_adapter) against
# a trained machine learning "Student" model for the same scenario inputs.

import os
import streamlit as st        # For building the web-based interactive UI
import pandas as pd           # For creating and passing feature rows
import joblib                 # For loading saved ML models

# Imports the adapter so that the Teacher's logic reflects extra features
import rules_adapter as teacher

# Available scenario types and ethical modes
SCENARIOS = ["car_vs_pedestrian", "car_vs_car", "pedestrian_vs_pedestrian"]
MODES = ["utilitarian", "deontological", "virtue"]

# Directory where trained ML models are stored
MODEL_DIR = "models"

@st.cache_resource
def load_model(mode: str):
    """
    Loads and caches the trained ML model for the given ethical mode.
    Prevents reloading the model on every UI interaction.
    """
    return joblib.load(os.path.join(MODEL_DIR, f"{mode}.pkl"))

# Page configuration for Streamlit
st.set_page_config(page_title="Ethical AV Demo", layout="centered")
st.title("Ethical AV Demo (Rule vs ML)")

# --- User Inputs Section ---
# Scenario selection (radio buttons)
name = st.radio("Scenario", SCENARIOS, index=0, horizontal=True)

# Ethical mode selection (radio buttons)
mode = st.radio("Ethical mode", MODES, index=0, horizontal=True)

# Risk and child presence inputs organized into three columns
colA, colB, colC = st.columns(3)
with colA:
    child_present = st.selectbox("Child present?", [0, 1], index=0)
with colB:
    left_risk = st.slider("Left risk", 0.0, 1.0, 0.3, 0.01)
with colC:
    right_risk = st.slider("Right risk", 0.0, 1.0, 0.6, 0.01)

# Speed input slider
speed_kph = st.slider("Speed (kph)", 0, 70, 30, 1)

# Creates a DataFrame row with the same schema as used in training
row = pd.DataFrame([{
    "name": name,
    "child_present": int(child_present),
    "left_risk": float(left_risk),
    "right_risk": float(right_risk),
    "speed_kph": int(speed_kph),
}])

# --- Decision Section ---
# Teacher decision using the rules_adapter logic
teacher_action = teacher.decide_action(mode, row.iloc[0].to_dict())

# Student decision using the trained ML model
model = load_model(mode)
student_action = model.predict(row)[0]

# Displays Teacher vs Student decisions side-by-side
c1, c2 = st.columns(2)
with c1:
    st.subheader("Rule (Teacher)")
    st.write(f"**{teacher_action}**")
with c2:
    st.subheader("ML (Student)")
    st.write(f"**{student_action}**")

# Indicates if the ML model matches the Teacher for this input
if teacher_action == student_action:
    st.success("Match ✓")
else:
    st.error("Mismatch ✗ (model differs from teacher)")

# Expander to show full scenario details
with st.expander("Scenario details"):
    st.json(row.iloc[0].to_dict())

# Caption explaining the relationship between Teacher and Student
st.caption("Note: Adapter refines the original rules using extra features; the ML model learns to imitate the adapter.")
