import streamlit as st
import requests

st.title("AI DevSecOps Risk Predictor")

test_pass_rate = st.slider("Test Pass Rate", 0.0, 1.0, 0.8)
vulnerabilities = st.number_input("Vulnerabilities", 0, 10, 1)
build_time = st.number_input("Build Time (sec)", 0, 1000, 100)

if st.button("Predict"):
    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json={
            "test_pass_rate": test_pass_rate,
            "vulnerabilities": vulnerabilities,
            "build_time": build_time
        }
    )
    st.json(response.json())